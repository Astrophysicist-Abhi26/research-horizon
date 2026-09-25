# Roadmap

Research Horizon grows in small steps. Each step is one pull request that keeps the site
working and keeps every existing test green.

**Principles**

- **One database, many rankings.** Profiles never change what is collected or how it is
  tagged, only how it is ranked. There is no separate scraper or site per field.
- **Tags describe events; profiles describe people's interests.** Taxonomy and ranking
  stay in separate files.
- **Reliable sources first.** Calendars, APIs, RSS/iCal feeds and Indico servers come
  before scraping web pages. Every new source is checked against the live site before it
  is added.
- **Nothing personal is built in.** Profiles are named after research areas, not people.

---

## ✅ Step 1: profile layer (done)

- Shared database, tagging kept separate from ranking.
- [`scraper/profiles.yaml`](scraper/profiles.yaml) and [`scraper/profiles.py`](scraper/profiles.py):
  every event gets one score per profile.
- Profile picker on the site, with a shareable `?p=<profile>` link.
- Five presets: Explore everything, Condensed matter & quantum physics, High-energy theory &
  gravitation, Astronomy & astrophysics, and Cosmology & ML for science.
- A source that is down keeps its last good events ("stale", up to 14 days).

## Step 2: a finer physics taxonomy

Today all of condensed matter is one sub-field, and so is all of quantum physics. The plan
is to split them. Every current id stays valid through aliases, so existing profiles, labels
and watchlist entries keep working.

| Branch | Proposed sub-fields |
|---|---|
| Condensed matter | topological phases (topological insulators and superconductors, quantum Hall, Berry phase) · strongly correlated systems & magnetism · superconductivity · quantum many-body (tensor networks, MBL, thermalisation) · 2D & quantum materials · soft & active matter · statistical physics |
| Quantum | quantum information & computation · quantum optics, AMO & cold atoms · quantum technologies & sensing |
| Particles & fields | high-energy theory · phenomenology · nuclear physics |
| Mathematical physics | TQFT · CFT · integrable systems · general |
| Other physics | optics & photonics · biological physics · fluids & plasma · physics education & history |

This step also includes:

- Subject-code mappings (for example `cond-mat.str-el`, `cond-mat.mes-hall`, `quant-ph`,
  `physics.atom-ph`, `math-ph`).
- Keywords, labelled examples in `labels.yaml`, and embedding prototypes for each new
  sub-field.

## Step 3: physics sources beyond astronomy and high-energy physics

Candidates (each checked against the live site before it is added):

- **IISc:** CHEP, CeNSE, and the Physics department's condensed-matter and quantum seminars.
- **Bengaluru:** RRI (soft condensed matter, light & matter physics), JNCASR (Theoretical
  Sciences Unit), ICTS programmes (already covered).
- **Rest of India:** TIFR (theoretical physics, condensed matter), HRI, IISERs, IIT physics
  departments. IMSc is on hold: its site blocks automated visitors.
- **International:** ICTP Trieste (Indico), and wider researchseminars.org topic filters.

## Step 4: more physics profiles

AMO & quantum optics · quantum information & computing · soft & biological physics ·
fluids & plasma · mathematical physics. Presets are added only once enough events carry the
matching tags.

## Step 5: other subjects

Each subject gets its own taxonomy branch, sources and presets, one subject at a time:

- **Mathematics:** finer branches, and seminars from ISI, CMI and IISc Mathematics.
- **Computer science & AI:** algorithms and theory, systems, ML theory, reinforcement learning.
- **Electrical & communication engineering:** information theory, communications, signal
  processing, control, optimisation, networks.
- **Computational biology:** genomics, sequence algorithms, computational neuroscience.
- **Chemistry and materials.**

## Step 6: build your own profile

- Sliders on the site to rate topics (top / high / medium / low / hide), saved in the
  browser and shareable as a link. No GitHub account is needed.
- Optional: a calendar (.ics) or RSS feed per profile, to subscribe from Google Calendar.

## Later / optional

- Switch the Claude classifier on with an API key, if keyword rules and embeddings prove
  too coarse for the finer taxonomy. It tags topics only; cost is capped by a cache and a
  per-run limit.
- Publish the site: make the repository public, or use a paid plan for Pages on a private
  repository.
