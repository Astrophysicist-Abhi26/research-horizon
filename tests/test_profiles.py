"""Research profiles: same tagged events, different rankings."""
import datetime as dt
import itertools
import json
import os

import pytest

import profiles as P
import scrape as S
import taxonomy as T
from classify import classify

PROFILES = P.load()
FX = os.path.join(os.path.dirname(__file__), "fixtures")


# ---------------------------------------------------------------------------
# Event Horizon's scorer, frozen exactly as it was (classify.score_event in v5)
# ---------------------------------------------------------------------------
LEGACY_W = {
    "cosmo.de": 68, "cosmo.lss": 64, "cosmo.early": 62, "cosmo.dm": 60, "cosmo.general": 60,
    "ai.science": 52, "ai.theory": 40, "ai.general": 30,
    "astro.he": 40, "astro.galactic": 40, "astro.stellar": 32, "astro.general": 36,
    "math.nt": 34, "math.topology": 34, "math.algebra": 32, "math.geometry": 30,
    "math.probability": 32, "math.mathphys": 30, "math.analysis": 24, "math.other": 20,
    "phys.gr": 40, "phys.hepth": 28, "phys.quantum": 18, "phys.condmat": 12,
    "phys.fluids": 12, "phys.general": 10,
}


def legacy_score(subfields, region, etype, basis):
    if not subfields:
        return 0
    weights = sorted(((LEGACY_W[s], T.parent(s)) for s in subfields), reverse=True)
    best_w, best_f = weights[0]
    other = [w for w, f in weights if f != best_f]
    s = best_w + (0.25 * other[0] if other else 0)
    fams = {T.parent(x) for x in subfields}
    if "cosmo" in fams and "ai" in fams:
        s += 25
    elif "astro" in fams and "ai" in fams:
        s += 18
    if "cosmo" in fams and ("math.probability" in subfields or "ai.theory" in subfields):
        s += 10
    if region == "bengaluru":
        s += 10
    elif region == "india":
        s += 5
    if etype in ("School", "Workshop"):
        s += 5
    if basis == {"embedding"}:
        s *= 0.85
    return int(round(min(100, s)))


def test_cosmology_ml_reproduces_event_horizon_exhaustively():
    """Every combination of up to 3 sub-fields x region x type x basis."""
    prof = PROFILES["cosmology-ml"]
    subs = list(T.SUBFIELDS)
    combos = itertools.chain.from_iterable(itertools.combinations(subs, k) for k in (1, 2, 3))
    regions = ["bengaluru", "india", "online", "abroad", "unknown", None]
    types = ["School", "Workshop", "Conference", "Talk / Seminar", "Lecture series"]
    bases = [{"keywords"}, {"embedding"}, {"declared", "keywords"}, {"embedding", "keywords"}]
    n = 0
    for tags in combos:
        tags = list(tags)
        for region, etype, basis in itertools.product(regions, types, bases):
            assert prof.score(tags, region, etype, basis) == legacy_score(tags, region, etype, basis), \
                (tags, region, etype, basis)
            n += 1
    assert n > 350_000


def test_cosmology_ml_reproduces_real_event_horizon_scores():
    """All 441 events of Event Horizon's last committed database (up to 9 tags)."""
    with open(os.path.join(FX, "event_horizon_scores.json")) as f:
        rows = json.load(f)["events"]
    prof = PROFILES["cosmology-ml"]
    for r in rows:
        got = P.pinned_score(prof.score(r["subfields"], r["region"], r["type"], r["basis"]),
                             r["priority"])
        assert got == r["score"], r
    assert len(rows) == 441


def test_profiles_file_is_valid():
    assert PROFILES.default in PROFILES.by_id
    for p in PROFILES:
        assert p.label and any(w > 0 for w in p.interests.values())
        for node in list(p.interests) + p.focus:
            assert T.is_node(node), (p.id, node)
        assert p.score(["phys.condmat"], "abroad", "Conference", ["keywords"]) >= 0


def test_event_types_match_the_pipeline():
    produced = {label for _, label in S.TYPE_RULES} | {"Talk / Seminar", "Conference"}
    assert P.TYPES == produced


def test_most_specific_node_wins():
    p = P._profile("t", {"label": "t", "interests": {"physics": 30, "phys.condmat": 100}})
    assert p.weight("phys.condmat") == 100
    assert p.weight("phys.gr") == 30
    assert p.weight("cosmo.de") == 0


def _score(title, pid, **kw):
    subs, _, basis = classify({"title": title, **kw})
    return PROFILES[pid].score(subs, kw.get("region"), kw.get("type"), basis)


def test_same_events_rank_differently_per_profile():
    cm = "Superconductivity and quantum magnetism in twisted bilayers"
    cosmo = "Dark energy and the Hubble tension"
    assert _score(cm, "condensed-quantum") > _score(cosmo, "condensed-quantum")
    assert _score(cosmo, "cosmology-ml") > _score(cm, "cosmology-ml")
    assert _score("String theory and holography", "hep-gravitation") >= 90
    assert _score("Galaxy formation and AGN feedback", "astrophysics") >= 90


def test_off_topic_scores_zero_even_locally():
    """Location and format never make an off-topic event relevant."""
    assert _score("Dark energy and the Hubble tension", "condensed-quantum",
                  region="bengaluru", type="School") == 0


def test_explore_ranks_all_fields_alike():
    a = _score("Dark energy and the Hubble tension", "explore")
    b = _score("Superconductivity in twisted bilayers", "explore")
    assert a == b == 50


def test_pinned_floor_only_where_relevant():
    assert P.pinned_score(12, True) == P.PIN_FLOOR
    assert P.pinned_score(0, True) == 0          # off-topic for this profile: not pushed up
    assert P.pinned_score(12, False) == 12


def test_negative_weight_is_a_penalty():
    p = P._profile("t", {"label": "t", "interests": {"physics": 60, "phys.fluids": "avoid"}})
    assert p.score(["phys.condmat"]) == 60
    assert p.score(["phys.condmat", "phys.fluids"]) == 60 - 40
    assert p.score(["phys.fluids"]) == 0


def test_synergy_groups_take_the_largest_bonus():
    p = P._profile("t", {"label": "t", "interests": {"cosmo": 50, "astro": 50, "ai": 10},
                         "cross_field": 0,
                         "synergies": [{"when": ["cosmo", "ai"], "bonus": 25, "group": "ml"},
                                       {"when": ["astro", "ai"], "bonus": 18, "group": "ml"}]})
    assert p.score(["cosmo.de", "astro.he", "ai.general"]) == 50 + 25


@pytest.mark.parametrize("bad, msg", [
    ({"label": "x", "interests": {"phys.nonsense": 50}}, "unknown taxonomy node"),
    ({"label": "x", "interests": {"physics": "lots"}}, "not a number"),
    ({"label": "x", "interests": {"physics": 50}, "places": {"mars": 5}}, "unknown region"),
    ({"label": "x", "interests": {"physics": 50}, "types": {"Party": 5}}, "unknown event type"),
    ({"label": "x", "interests": {"physics": 50}, "colour": "red"}, "unknown key"),
    ({"interests": {"physics": 50}}, "needs a label"),
    ({"label": "x", "interests": {"physics": 0}}, "positive weight"),
])
def test_profile_mistakes_fail_loudly(bad, msg):
    with pytest.raises(P.ProfileError, match=msg):
        P._profile("x", bad)


def test_rank_all_stores_one_score_per_profile(monkeypatch):
    monkeypatch.setenv("EH_NO_EMBED", "1")
    soon = (dt.date.today() + dt.timedelta(days=30)).isoformat()
    e = S.normalise([dict(title="Workshop on topological superconductivity", url="https://x",
                          start_date=soon, end_date=None, deadline=None,
                          location="IISc, Bengaluru, India", country=None, online=False, tz=None,
                          description="", speaker=None, source="S", raw_type=None,
                          declared=[], priority=False)])
    S.classify_all(e)
    S.rank_all(e, PROFILES)
    assert set(e[0]["scores"]) == set(PROFILES.by_id)
    assert e[0]["score"] == e[0]["scores"][PROFILES.default]
    assert e[0]["scores"]["condensed-quantum"] > e[0]["scores"]["cosmology-ml"]


def test_export_for_frontend():
    out = P.export_for_frontend(PROFILES)
    assert out["default"] == PROFILES.default
    ids = [p["id"] for p in out["list"]]
    assert ids[0] == "explore" and "cosmology-ml" in ids
    json.dumps(out)                              # serialisable
