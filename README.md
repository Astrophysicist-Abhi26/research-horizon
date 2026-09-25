# Research Horizon 🔭

**A research-event radar for every field.** Conferences, schools, workshops, seminars and
webinars are collected every day into one shared database, tagged by subject, and ranked
for the **research profile** you choose: condensed matter, high-energy theory, astrophysics,
cosmology and more. It covers Bengaluru, the rest of India, online events and abroad.

Research areas differ, but the events come from the same institutes, calendars and
aggregators. So there is **one database and many rankings**. A condensed-matter theorist
and a cosmologist see the same events, each in their own order, and nobody's field is
hidden from anybody.

**Live site:** https://astrophysicist-abhi26.github.io/research-horizon/ (updated daily at
08:00 IST)

> **Status:** early development. Physics and astronomy are covered today; mathematics,
> computer science, engineering, biology and chemistry come next (see
> [ROADMAP.md](ROADMAP.md)).

## Research profiles

Pick a profile at the top of the site. Every score, the sort order, the "focus" button and
the tags shown first on each card follow it. The address becomes `…/?p=<profile>`, a link
you can bookmark or send to someone in that field.

| Profile | Ranks first |
|---|---|
| **Explore everything** (default) | every field alike; browse by date |
| **Condensed matter & quantum physics** | condensed matter and statistical physics, quantum matter and information; then mathematical physics and topology |
| **High-energy theory & gravitation** | strings, QFT, holography, particle physics, GR and quantum gravity, early universe |
| **Astronomy & astrophysics** | stars, galaxies, compact objects, gravitational waves, transients |
| **Cosmology & ML for science** | dark energy, large-scale structure, CMB, dark matter; ML for science |

A profile never changes what is collected or how it is tagged. It only changes the
ranking. Each profile is a short block in [`scraper/profiles.yaml`](scraper/profiles.yaml):

- **Weights:** 0–100 per field or sub-field. The most specific one listed wins.
- **Cross-field share:** a boost for events that span a second weighted field.
- **Optional bonuses:** for combinations of topics, for places, and for event types.

An event with no weighted topic scores 0, however close by it is. A mistake in the file
(an unknown topic, region or key) fails the tests before anything is published. The exact
formula is documented at the top of [`scraper/profiles.py`](scraper/profiles.py).

## Topics covered today

| Field | Sub-fields |
|---|---|
| Physics | gravitation & GR · high-energy theory & QFT · quantum physics · condensed matter & statistical mechanics · fluids, plasma & climate · other physics |
| Astrophysics | high-energy astrophysics, compact objects & GW · galaxies & AGN · stars, Sun & planets · general astronomy |
| Cosmology | dark energy · large-scale structure · CMB & early universe · dark matter · general |
| Mathematics | number theory · topology · algebra · geometry · probability & statistics · mathematical physics · analysis & PDE · other |
| AI / ML | ML for science · ML theory · general |

Every event can carry several tags. They come from four kinds of evidence, strongest first:

1. **Subject codes** declared by the organisers (arXiv, INSPIRE and researchseminars.org
   categories).
2. **Keyword rules** matched on whole words in the title and abstract.
3. **A local embedding model** that calibrates itself and costs nothing to run.
4. **Optional:** a Claude classifier that tags topics only.

## How it works

```
GitHub Actions (daily 08:00 IST, on every push to main, and on "Add event" issues)
 ├─ tests                      offline tests; a failure stops the run, so the site
 │                             keeps its last good data
 ├─ scraper/scrape.py
 │   ├─ ~30 sources            each isolated: one broken site never stops the run;
 │   │                         a source that is down keeps its last good events ("stale")
 │   ├─ normalise              drop past and undated events; detect Bengaluru / India /
 │   │                         online / abroad
 │   ├─ de-duplicate           the same event from several sources -> one card
 │   ├─ classify               subject codes + keywords + embeddings [+ Claude]
 │   └─ rank                   one relevance score per research profile
 ├─ publish                    docs/ + events.json to GitHub Pages (when Pages is on)
 └─ health alert               a GitHub Issue only when a source newly breaks
```

The workflow can only read the repository; it **never commits**. The event database exists
only in the published site, and each run reads the previous one back from there to keep
track of which events are new this week.

## Sources

| Source | What it covers |
|---|---|
| INSPIRE conferences and seminars | HEP, GR, cosmology and astrophysics, with subject categories |
| researchseminars.org talks and conferences | mathematics, physics and CS/statistics talks worldwide, with arXiv-style topic codes |
| CADC Astronomy Meetings | worldwide astronomy meetings |
| DESC Cosmology Meetings | curated cosmology calendar |
| AI Deadlines | major ML venues |
| Indian institutes | one entry per page or calendar in [`scraper/institutes.yaml`](scraper/institutes.yaml) |
| Watchlist | hand-added entries in [`scraper/watchlist.yaml`](scraper/watchlist.yaml) |
| "Add event" issue form | events known only from an email or poster; they appear within minutes, with no commits |

The Indian institutes covered today:

- **Bengaluru:** ICTS, IISc (Physics calendars, conferences and schools; Mathematics; CDS;
  institute events), RRI, IIA and JNCASR.
- **Elsewhere in India:** IUCAA, ASI, TIFR DAA and NCRA.

The **Source health** panel at the bottom of the site shows which sources worked on the
last run. You can test any institute source from your own network with
`python scraper/doctor.py`.

## Contributing

Suggestions are welcome: a missing source, a research profile for your field, or an event
that is mislabelled. See [CONTRIBUTING.md](CONTRIBUTING.md). In short:

| I want to… | Do this |
|---|---|
| add a one-off event | open an **Add event** issue, or add it to `scraper/watchlist.yaml` |
| suggest a source | open a **Suggest a source** issue |
| suggest or tune a research profile | open a **Research profile** issue, or edit `scraper/profiles.yaml` |
| fix a mislabelled event | add `["its title", correct.subfield]` to `scraper/labels.yaml` |

## Publishing your own copy

1. Fork this repository (it must be public for GitHub Pages on the free plan).
2. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
3. **Actions → Update events → Run workflow.** The site appears at
   `https://<owner>.github.io/<repository>/` a few minutes later. Links on the page follow
   whichever repository serves it, so a fork works unchanged.

If Pages is not switched on, every run still scrapes, tests, tags and ranks everything; it
just skips the publish step and says so in the run summary.

**Optional: Claude classification.** Add a repository secret named `ANTHROPIC_API_KEY` under
**Settings → Secrets and variables → Actions**. Each event is classified once and cached,
with at most 300 new events per run. Without the key, the site uses subject codes, keyword
rules and the local embedding model, at no cost.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests                  # a few seconds, offline
EH_NO_EMBED=1 python scraper/scrape.py      # skip the embedding model for a quick run
cd docs && python3 -m http.server           # open http://localhost:8000
```

## Origin

Research Horizon grew out of
[Event Horizon](https://github.com/Astrophysicist-Abhi26/event-horizon), a radar built for
cosmology and astrophysics at IISc Bengaluru. Its ranking lives on unchanged as the
**Cosmology & ML for science** profile; a test checks that it reproduces Event Horizon's
scores exactly.

## License

[MIT](LICENSE). Event data belongs to the institutes and aggregators it comes from;
each card links to the original announcement.
