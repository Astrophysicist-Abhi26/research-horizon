# Research Horizon 🔭

A research-event radar for every field. Conferences, schools, workshops, seminars and
webinars are collected daily into **one shared database**, tagged by subject, and ranked
for the **research profile** you choose — in Bengaluru, across India, online and abroad.

It grew out of [Event Horizon](https://github.com/Astrophysicist-Abhi26/event-horizon), a
cosmology-focused radar, and is being widened step by step: **physics first**, then
mathematics, biology, chemistry, computer science and engineering.

**Live site:** https://astrophysicist-abhi26.github.io/research-horizon/

## How it works

```
GitHub Actions (daily 08:00 IST, on every push to main, and on "Add event" issues)
 ├─ restore state              yesterday's events.json read back from the live site
 ├─ tests                      offline regression tests; a failure stops the run,
 │                             so the site keeps yesterday's good data
 ├─ scraper/scrape.py
 │   ├─ ~30 sources            each isolated: one broken site never kills the run;
 │   │                         a source that is down keeps its last good events ("stale")
 │   ├─ normalise              drop past + undated events, detect Bengaluru/India/online/abroad
 │   ├─ de-duplicate           same event from several sources -> one card, sources merged
 │   ├─ classify               1 declared subject codes (arXiv / INSPIRE / tags)
 │   │                         2 word-bounded keyword rules (title + abstract)
 │   │                         3 [B] local embedding classifier, self-calibrating (free)
 │   │                         4 [C] Claude classifier, optional (needs API key)
 │   └─ rank                   one relevance score per research profile (profiles.yaml)
 ├─ deploy                     docs/ (incl. the fresh events.json) straight to GitHub Pages
 └─ health alert               a GitHub Issue only when a source newly breaks
```

The workflow is read-only on the repository: it **never commits**. The event database
lives only in the deployed site.

## Research profiles

The same events, ranked differently. Pick a profile at the top of the site; the address
changes to `…/?p=<profile>`, a link you can bookmark or send to someone in that field.

| Profile | Ranks first |
|---|---|
| Explore everything (default) | every field alike — browse by date |
| Condensed matter & quantum physics | condensed matter, statistical physics, quantum matter and information |
| High-energy theory & gravitation | strings, QFT, holography, particle physics, GR, early universe |
| Astronomy & astrophysics | stars, galaxies, compact objects, GW, transients |
| Cosmology & ML for science | dark energy, large-scale structure, CMB, dark matter, ML for science |

A profile never changes what is collected or how it is tagged — only the ranking. Each is a
short block in [`scraper/profiles.yaml`](scraper/profiles.yaml): a weight (0–100) per field
or sub-field (the most specific one listed wins), a share for events spanning a second field,
optional bonuses for combinations, places and event types. Events with no weighted topic
score 0, however close by. A mistake in the file (an unknown topic, region or key) fails
the tests before anything is deployed. How a score is computed is documented at the top
of [`scraper/profiles.py`](scraper/profiles.py).

**Coming next:** a finer physics tree (topological phases, strongly correlated systems,
quantum information, AMO, soft matter …), physics sources beyond astronomy and high-energy
physics, then other subjects.

## Sources

| Source | What it covers |
|---|---|
| DESC Cosmology Meetings | curated cosmology calendar (LSST DESC) |
| CADC Astronomy Meetings | worldwide astronomy meetings |
| INSPIRE conferences / seminars | HEP, GR, cosmology, astro — with subject categories |
| researchseminars.org talks / conferences | math, physics, CS/stats talks worldwide, with arXiv-style topic codes |
| AI Deadlines | major ML venues (NeurIPS, ICML, ICLR, COLT, AISTATS, UAI …) |
| Indian institutes | registry-driven (`scraper/institutes.yaml`), one health line each |
| Watchlist | hand-added entries (`scraper/watchlist.yaml`) |
| "Add event" issue form | events known only from an email or poster — appear within minutes, **zero commits** |

Indian institutes today: ICTS · IISc (Physics calendars, conferences, schools; Mathematics;
CDS; institute events) · RRI · IIA · JNCASR · IUCAA · ASI · TIFR DAA · NCRA. Check any of
them from your own network with `python scraper/doctor.py`.

## Contributing an event or a source

| I want to… | Do this |
|---|---|
| add a one-off event | open an **Add event** issue (link at the bottom of the site), or add it to `scraper/watchlist.yaml` |
| add an institute's events page | add an entry to `scraper/institutes.yaml`, then `python scraper/doctor.py <name>` |
| add or tune a research profile | a block in `scraper/profiles.yaml`, then `python -m pytest -q tests` |
| fix a mislabelled event | add `["its title", correct.subfield]` to `scraper/labels.yaml` |
| add vocabulary for a field | `RULES` in `scraper/taxonomy.py` (then run the tests) |

## Run your own copy

1. Fork this repository.
2. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
3. **Actions → Update events → Run workflow.** The site appears at
   `https://<your-user>.github.io/<repo>/` a few minutes later; links on the page follow
   whichever repository serves it.
4. Optional — Claude classification (Option C): **Settings → Secrets and variables → Actions →
   New repository secret** named `ANTHROPIC_API_KEY`. Each event is classified once and
   cached; at most 300 new events per run. Without it the site uses subject codes, keyword
   rules and the local embedding model, at no cost.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests                  # ~1 s, offline
EH_NO_EMBED=1 python scraper/scrape.py      # skip the embedding model for a quick run
cd docs && python3 -m http.server           # open http://localhost:8000
```
