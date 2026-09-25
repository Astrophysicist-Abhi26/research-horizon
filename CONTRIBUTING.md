# Contributing

Thank you for helping. Most contributions are one small edit to a YAML file. You don't need
to know the scraper code.

## Quick ways to help (no code)

- **An event you heard about by email or poster:** open an **Add event** issue. It appears
  on the site within minutes and disappears when the issue is closed.
- **A source we should read:** open a **Suggest a source** issue with the page or calendar
  link.
- **A research profile for your field:** open a **Research profile** issue listing the
  topics that matter, roughly in order.
- **A mislabelled event:** open an issue with the event title and the topic it should have.

## Adding or tuning a research profile

Profiles live in [`scraper/profiles.yaml`](scraper/profiles.yaml). A minimal profile:

```yaml
  my-field:                        # id: lowercase, used in the link ?p=my-field
    label: Soft & biological physics
    blurb: Soft matter, active matter and biological physics first; then statistical physics.
    focus: [phys.condmat]          # optional: what the "focus" button and sort mean
    focus_label: soft matter
    interests:                     # field or sub-field -> weight 0-100
      phys.condmat: 100
      math.probability: 40
      physics: 30                  # every other physics sub-field
    places: {bengaluru: 10, india: 5}
    types: {School: 5, Workshop: 5}
```

Rules worth knowing:

- For each tag, the **most specific** node listed wins: `physics: 30` together with
  `phys.condmat: 100` gives condensed matter 100 and all other physics 30.
- Topics that are not listed, not even through their field, score **0**. Location and event
  type never make an off-topic event relevant.
- Level names can replace numbers: `top` 100, `very_high` 85, `high` 70, `medium` 45,
  `low` 20, `avoid` −40.
- The available fields and sub-fields are listed in
  [`scraper/taxonomy.py`](scraper/taxonomy.py) (`FIELDS`, `SUBFIELDS`).
- **Profiles are named after research areas, never after people.**

Then run the tests (below). A typo, such as an unknown topic, region, event type or key,
fails with a message that says what is wrong.

## Adding a source

Institute pages and calendars go in [`scraper/institutes.yaml`](scraper/institutes.yaml).
Each entry picks an adapter with `kind`:

| kind | Use for |
|---|---|
| `ical` / `google_calendar` | any public calendar feed (preferred: it doesn't break when the page is redesigned) |
| `indico` | an Indico server (JSON export, falling back to the public iCal feed) |
| `wp_events` | WordPress sites using "The Events Calendar" |
| `listing` | an HTML page that lists upcoming events (last resort) |

Check a new entry against the live site before opening a pull request:

```bash
python scraper/doctor.py "<part of the source name>"
```

It prints how many events the source returns and the next three upcoming ones. If the site
blocks automated visitors or needs JavaScript, say so in the pull request; such sources are
kept with `enabled: false` and a comment explaining why.

Global aggregators (INSPIRE, researchseminars.org and so on) live in
[`scraper/sources.py`](scraper/sources.py).

## Fixing a mislabelled event

Add `["the event title", correct.subfield]` to [`scraper/labels.yaml`](scraper/labels.yaml).
The embedding classifier learns from these examples on the next run, and the tests use them
to check classification accuracy. For a whole class of mistakes, add or adjust a keyword
rule in `RULES` in [`scraper/taxonomy.py`](scraper/taxonomy.py).

## Running the tests

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests
```

The tests are offline and take a few seconds. They also run automatically on every pull
request.

## Pull requests

- Keep each pull request to one change: a profile, a source, or a fix.
- Never commit `docs/events.json`: the workflow builds it and publishes it with the site.
- Describe what you checked (for example the `doctor.py` output for a new source).
