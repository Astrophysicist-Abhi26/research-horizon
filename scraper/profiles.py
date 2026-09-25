"""
Research profiles: one tagged event database, ranked differently per profile.

A profile never changes which events are collected or how they are tagged; it
only turns an event's tags (plus where and what kind of event it is) into a
0-100 relevance score for that profile. Every event carries one precomputed
score per profile, so the site switches profiles instantly.

Score of an event for a profile
-------------------------------
  w(tag)   weight of the most specific node listed in `interests` that is the
           tag itself or one of its ancestors (sub-field, then field); 0 if none
  best     highest positive w over the event's tags
  second   highest positive w among tags in a different field from `best`
  score  = best + cross_field * second
         + synergies (within one `group` only the largest applicable bonus)
         + places[region] + types[event type]
         + the most negative w, if any tag has one (a penalty)
  An event with no positively weighted tag scores 0: location or format never
  make an off-topic event relevant. Events tagged by the embedding classifier
  alone are multiplied by EMBEDDING_ONLY. The result is rounded, 0-100.

With Event Horizon's original weights and bonuses, the `cosmology-ml` profile
reproduces its ranking exactly (tests/test_profiles.py checks this).

Profiles live in profiles.yaml; see the comments there for the format.
"""

import os
from dataclasses import dataclass, field

import yaml

import taxonomy as T

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles.yaml")
EMBEDDING_ONLY = 0.85        # judged by the embedding alone: slightly less sure
PIN_FLOOR = 60               # pinned (watchlist / "Add event") events, where relevant
REGIONS = {"bengaluru", "india", "online", "abroad", "unknown"}
TYPES = {"Conference", "Workshop", "School", "Talk / Seminar", "Lecture series"}
LEVELS = {"top": 100, "very_high": 85, "high": 70, "medium": 45, "low": 20,
          "none": 0, "avoid": -40}
PROFILE_KEYS = {"label", "blurb", "focus", "focus_label", "interests", "cross_field",
                "synergies", "places", "types"}


class ProfileError(ValueError):
    pass


@dataclass
class Synergy:
    when: list                # [[node, ...], ...]: every group must match one node
    bonus: float
    group: str = ""


@dataclass
class Profile:
    id: str
    label: str
    blurb: str = ""
    focus: list = field(default_factory=list)
    focus_label: str = ""
    interests: dict = field(default_factory=dict)
    cross_field: float = 0.25
    synergies: list = field(default_factory=list)
    places: dict = field(default_factory=dict)
    types: dict = field(default_factory=dict)

    def weight(self, tag):
        for node in T.ancestors(tag):
            if node in self.interests:
                return self.interests[node]
        return 0

    def score(self, tags, region=None, etype=None, basis=()):
        if not tags:
            return 0
        weighted = [(self.weight(t), T.ancestors(t)[-1]) for t in tags]
        pos = sorted((wf for wf in weighted if wf[0] > 0), reverse=True)
        if not pos:
            return 0
        best_w, best_field = pos[0]
        second = next((w for w, f in pos if f != best_field), 0)
        s = best_w + self.cross_field * second
        present = {n for t in tags for n in T.ancestors(t)}
        grouped = {}
        for syn in self.synergies:
            if all(any(n in present for n in alts) for alts in syn.when):
                if syn.group:
                    grouped[syn.group] = max(grouped.get(syn.group, 0), syn.bonus)
                else:
                    s += syn.bonus
        s += sum(grouped.values())
        s += self.places.get(region or "unknown", 0)
        s += self.types.get(etype, 0)
        s += min(0, min(w for w, _ in weighted))
        if set(basis) == {"embedding"}:
            s *= EMBEDDING_ONLY
        return int(round(min(100, max(0, s))))


@dataclass
class Profiles:
    default: str
    by_id: dict

    def __iter__(self):
        return iter(self.by_id.values())

    def __getitem__(self, pid):
        return self.by_id[pid]


# ---------------------------------------------------------------------------
# Loading and validation (a typo in profiles.yaml must fail the tests loudly,
# not silently rank everything at zero)
# ---------------------------------------------------------------------------
def _num(value, where):
    if isinstance(value, bool):
        raise ProfileError(f"{where}: expected a number or level, got {value!r}")
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str) and value in LEVELS:
        return LEVELS[value]
    raise ProfileError(f"{where}: {value!r} is not a number or one of {sorted(LEVELS)}")


def _node(node, where):
    if not T.is_node(node):
        raise ProfileError(f"{where}: unknown taxonomy node {node!r} "
                           f"(fields: {', '.join(T.FIELDS)}; sub-fields in taxonomy.py)")
    return node


def _profile(pid, raw):
    where = f"profiles.yaml: profile {pid!r}"
    if not isinstance(raw, dict):
        raise ProfileError(f"{where}: expected a mapping")
    unknown = set(raw) - PROFILE_KEYS
    if unknown:
        raise ProfileError(f"{where}: unknown key(s) {sorted(unknown)}")
    if not raw.get("label"):
        raise ProfileError(f"{where}: needs a label")
    interests = {_node(n, f"{where} interests"): _num(v, f"{where} interests.{n}")
                 for n, v in (raw.get("interests") or {}).items()}
    if not any(v > 0 for v in interests.values()):
        raise ProfileError(f"{where}: interests need at least one positive weight")
    synergies = []
    for i, syn in enumerate(raw.get("synergies") or []):
        w = f"{where} synergies[{i}]"
        if not isinstance(syn, dict) or set(syn) - {"when", "bonus", "group"} or "when" not in syn:
            raise ProfileError(f"{w}: expected {{when: [...], bonus: n, group: optional}}")
        when = [[_node(n, w) for n in (alt if isinstance(alt, list) else [alt])]
                for alt in syn["when"]]
        synergies.append(Synergy(when, _num(syn.get("bonus", 0), w), str(syn.get("group") or "")))
    places = {}
    for r, v in (raw.get("places") or {}).items():
        if r not in REGIONS:
            raise ProfileError(f"{where} places: unknown region {r!r} (one of {sorted(REGIONS)})")
        places[r] = _num(v, f"{where} places.{r}")
    types = {}
    for t, v in (raw.get("types") or {}).items():
        if t not in TYPES:
            raise ProfileError(f"{where} types: unknown event type {t!r} (one of {sorted(TYPES)})")
        types[t] = _num(v, f"{where} types.{t}")
    cross = _num(raw.get("cross_field", 0.25), f"{where} cross_field")
    if not 0 <= cross <= 1:
        raise ProfileError(f"{where}: cross_field must be between 0 and 1")
    return Profile(id=pid, label=str(raw["label"]), blurb=str(raw.get("blurb") or ""),
                   focus=[_node(n, f"{where} focus") for n in raw.get("focus") or []],
                   focus_label=str(raw.get("focus_label") or ""),
                   interests=interests, cross_field=cross, synergies=synergies,
                   places=places, types=types)


def load(path=PATH):
    with open(path) as f:
        raw = yaml.safe_load(f) or {}
    profs = raw.get("profiles") or {}
    if not profs:
        raise ProfileError("profiles.yaml: no profiles defined")
    by_id = {str(pid): _profile(str(pid), p) for pid, p in profs.items()}
    default = str(raw.get("default") or next(iter(by_id)))
    if default not in by_id:
        raise ProfileError(f"profiles.yaml: default profile {default!r} is not defined")
    return Profiles(default=default, by_id=by_id)


def pinned_score(score, pinned):
    """Watchlist / "Add event" entries rank at least PIN_FLOOR for every
    profile they are relevant to, and are left alone for the rest."""
    return max(score, PIN_FLOOR) if pinned and score > 0 else score


def export_for_frontend(profiles):
    """The site's profile picker, focus button and "why it matched" chips."""
    return {
        "default": profiles.default,
        "list": [{"id": p.id, "label": p.label, "blurb": p.blurb, "focus": p.focus,
                  "focus_label": p.focus_label,
                  "weights": {n: w for n, w in p.interests.items()}}
                 for p in profiles],
    }
