"""
India sources — driven by scraper/institutes.yaml — plus the two manual
channels: the watchlist file and "Add event" GitHub issues.

Every registry entry becomes its OWN source (own line in the health panel),
and picks one of five adapters with `kind:`

  listing          any HTML page that lists upcoming events (generic extractor)
  ical             any public iCal feed (.ics)
  google_calendar  a public Google Calendar, by calendar id
  wp_events        WordPress "The Events Calendar" sites (REST API, iCal fallback)
  indico           an Indico server (JSON export API)

Structured feeds (ical / google_calendar / wp_events / indico) are preferred
whenever an institute offers one: they do not break when a page is redesigned.
"""

import datetime as dt
import os
import re

import yaml
from bs4 import BeautifulSoup

from common import (clean, first_url, get, ics_end_date, iso, parse_date_range,
                    parse_ics, today)
from listing import extract_listing

HERE = os.path.dirname(os.path.abspath(__file__))
INSTITUTES = os.path.join(HERE, "institutes.yaml")
WATCHLIST = os.path.join(HERE, "watchlist.yaml")
INDICO_HORIZON_DAYS = 540
ICAL_HORIZON_DAYS = 400
RECUR_WINDOW_DAYS = 45       # recurring calendar series: only the next few weeks
RECUR_MAX = 3


def _load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def _urls(cfg):
    """`url` or `urls`, with {year} / {next_year} filled in (for pages such as
    .../Seminars{year}.html that move every January)."""
    raw = cfg.get("urls") or [cfg["url"]]
    y = today().year
    out = []
    for u in raw:
        for yy in ([y, y + 1] if "{year}" in u and today().month >= 11 else [y]):
            out.append(u.format(year=yy, next_year=yy + 1))
    return list(dict.fromkeys(out))


def _event(cfg, title, url, start, end=None, location=None, description="",
           raw_type=None, speaker=None, online=False, tz=None):
    return dict(title=clean(title), url=url, start_date=start, end_date=end or start,
                deadline=None, location=clean(location) or cfg.get("location"),
                country=None, online=online, tz=tz,
                description=clean(description)[:1500], speaker=speaker,
                source=cfg["name"], raw_type=raw_type or cfg.get("type"),
                declared=[], priority=False)


# ---------------------------------------------------------------------------
# listing — generic HTML extractor
# ---------------------------------------------------------------------------
def _listing(cfg):
    out = []
    for url in _urls(cfg):
        out += extract_listing(url, cfg["name"], cfg.get("location", "India"),
                               href_filter=cfg.get("href_filter"),
                               raw_type=cfg.get("type"),
                               insecure_ok=bool(cfg.get("insecure_ok")))
    return out


# ---------------------------------------------------------------------------
# ical / google_calendar
# ---------------------------------------------------------------------------
def _gcal_url(cal_id):
    return (f"https://calendar.google.com/calendar/ical/"
            f"{cal_id.replace('@', '%40')}/public/basic.ics")


def _expand(ev, start):
    """Upcoming occurrences of a recurring (RRULE) event, capped."""
    from dateutil.rrule import rrulestr
    try:
        rule = rrulestr(ev["RRULE"], dtstart=dt.datetime.fromisoformat(start))
    except (ValueError, TypeError):
        return []
    lo = dt.datetime.combine(today(), dt.time())
    hi = lo + dt.timedelta(days=RECUR_WINDOW_DAYS)
    return [d.date().isoformat() for d in rule.between(lo, hi, inc=True)][:RECUR_MAX]


def ical_events(cfg, text):
    calname = re.search(r"^X-WR-CALNAME:(.+)$", text, re.M)
    calname = clean(calname.group(1)) if calname else ""
    t = today().isoformat()
    horizon = (today() + dt.timedelta(days=ICAL_HORIZON_DAYS)).isoformat()
    out = []
    for ev in parse_ics(text):
        title = clean(ev.get("SUMMARY"))
        start = iso(ev.get("DTSTART"))
        if not title or not start or ev.get("STATUS", "").upper() == "CANCELLED":
            continue
        all_day = len(re.sub(r"\D", "", ev.get("DTSTART", ""))) == 8
        end = ics_end_date(start, ev.get("DTEND"), all_day)
        starts = _expand(ev, start) if ev.get("RRULE") else [start]
        desc = clean(ev.get("DESCRIPTION"))
        url = ev.get("URL") or first_url(desc) or cfg.get("page") or cfg.get("url")
        loc = ev.get("LOCATION") or ""
        for s in starts:
            if s > horizon or (end if s == start else s) < t:
                continue
            e = end if s == start else s
            out.append(_event(cfg, title, url, s, e, cfg.get("location"),
                              description=" · ".join(x for x in (calname, loc, desc) if x),
                              online=bool(re.search(r"zoom|meet\.google|teams", loc, re.I))))
    return out


def _ical(cfg):
    out = []
    for url in _urls(cfg):
        out += ical_events(cfg, get(url, insecure_ok=bool(cfg.get("insecure_ok"))).text)
    return out


def _google_calendar(cfg):
    ids = cfg.get("calendars") or [cfg["calendar"]]
    out, errors = [], []
    for cal in ids:
        try:
            out += ical_events(cfg, get(_gcal_url(cal)).text)
        except Exception as exc:        # one private calendar must not hide the rest
            errors.append(f"{cal[:12]}…: {exc.__class__.__name__}")
    if errors and not out:
        raise RuntimeError("; ".join(errors))
    return out


# ---------------------------------------------------------------------------
# wp_events — WordPress "The Events Calendar" (tribe) sites
# ---------------------------------------------------------------------------
def wp_events_from_json(cfg, data):
    out = []
    for e in data.get("events") or []:
        venue = e.get("venue") if isinstance(e.get("venue"), dict) else {}
        loc = ", ".join(x for x in (venue.get("venue"), venue.get("city")) if x) or None
        cats = [c.get("name", "") for c in e.get("categories") or [] if isinstance(c, dict)]
        out.append(_event(cfg, e.get("title"), e.get("url") or cfg["base"],
                          iso(e.get("start_date")), iso(e.get("end_date")), loc,
                          description=e.get("description") or e.get("excerpt") or "",
                          raw_type=" ".join(cats) or None))
    return out


def _wp_events(cfg):
    base = cfg["base"].rstrip("/")
    insecure = bool(cfg.get("insecure_ok"))
    try:
        url = f"{base}/wp-json/tribe/events/v1/events"
        params = {"start_date": today().isoformat(), "per_page": 50,
                  "end_date": (today() + dt.timedelta(days=ICAL_HORIZON_DAYS)).isoformat()}
        out = []
        for _ in range(4):                               # at most 200 events
            data = get(url, params=params, insecure_ok=insecure).json()
            out += wp_events_from_json(cfg, data)
            url, params = data.get("next_rest_url"), None
            if not url:
                break
        return out
    except Exception:
        # REST API switched off on some sites -> the plugin's iCal export
        text = get(f"{base}/{cfg.get('events_path', 'events').strip('/')}/?ical=1",
                   insecure_ok=insecure).text
        return ical_events(cfg, text)


# ---------------------------------------------------------------------------
# indico
# ---------------------------------------------------------------------------
def _indico(cfg):
    """JSON export first; many servers (IIA, since 2026) now demand an API key
    for it, so fall back to the category's public iCal feed, which does not."""
    frm = today().isoformat()
    to = (today() + dt.timedelta(days=INDICO_HORIZON_DAYS)).isoformat()
    cats = cfg.get("categories") or [cfg.get("category", 0)]
    base = cfg["base"].rstrip("/")
    insecure = bool(cfg.get("insecure_ok"))
    out = []
    for cat in cats:
        try:
            data = get(f"{base}/export/categ/{cat}.json",
                       params={"from": frm, "to": to, "limit": 500},
                       insecure_ok=insecure).json()
            if not isinstance(data, dict) or "results" not in data:
                raise ValueError("no results in Indico export")
        except Exception:
            text = get(f"{base}/category/{cat}/events.ics", insecure_ok=insecure).text
            out += ical_events(dict(cfg, page=f"{base}/category/{cat}/"), text)
            continue
        for e in data["results"]:
            start = iso(e.get("startDate"))
            out.append(_event(cfg, e.get("title"), e.get("url") or base, start,
                              iso(e.get("endDate")),
                              clean(e.get("location") or e.get("room") or ""),
                              description=e.get("description") or "",
                              raw_type=e.get("type"), tz=e.get("timezone")))
    return [e for e in out if e["title"]]


# ---------------------------------------------------------------------------
# labelled_list — pages listing each talk as a <li> with "Date:", "Time:",
# "Venue:" lines, the series name above and the speaker in <strong> (CMI)
# ---------------------------------------------------------------------------
_LABEL = re.compile(r"^(date|time|venue|place)\s*:\s*(.*)$", re.I)
_DMY = re.compile(r"^(\d{1,2})-(\d{1,2})-(\d{2})$")


def labelled_list_from_html(cfg, html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for li in soup.find_all("li"):
        for f in li.find_all("form"):
            f.decompose()
        lines = [clean(x) for x in li.get_text("\n").split("\n") if clean(x)]
        labels = {m.group(1).lower(): m.group(2) for m in map(_LABEL.match, lines) if m}
        if "date" not in labels:
            continue
        strong = li.find("strong")
        speaker = clean(strong.get_text(" ")) if strong else None
        first = next(i for i, x in enumerate(lines) if _LABEL.match(x))
        last = max(i for i, x in enumerate(lines) if _LABEL.match(x))
        series = next((x for x in reversed(lines[:first]) if not _DMY.match(x)), "")
        rest = [x for x in lines[last + 1:] if x != speaker]
        if not rest:
            continue
        title, affil = rest[0], " ".join(rest[1:])
        start = parse_date_range(labels["date"])[0]
        code = next((m for m in map(_DMY.match, lines[:first]) if m), None)
        if code:                                    # "30-09-26": authoritative when the
            d, mth, yy = map(int, code.groups())    # "Date:" line has no year
            try:
                start = start or dt.date(2000 + yy, mth, d).isoformat()
            except ValueError:
                pass
        who = f"{speaker} ({affil.rstrip('.')})" if speaker and affil else speaker
        loc = ", ".join(x for x in (labels.get("venue") or labels.get("place"),
                                     cfg.get("location")) if x)
        out.append(_event(cfg, f"{title} — {speaker}" if speaker else title, page_url, start,
                          location=loc, description=series, raw_type=cfg.get("type"),
                          speaker=who))
    return out


def _labelled_list(cfg):
    out = []
    for url in _urls(cfg):
        out += labelled_list_from_html(cfg, get(url, insecure_ok=bool(cfg.get("insecure_ok"))).text, url)
    return out


# ---------------------------------------------------------------------------
# table — pages that list events as an HTML table with a header row
# (IIT Madras "Title | Speaker | Date", IIT Delhi "Date | Time | Speaker | ... |
# Title", IACS "Title | uploaded date | Event date", PRL "Date | Day | Event").
# Columns are recognised by their header words, so one adapter fits them all.
# ---------------------------------------------------------------------------
_COLS = [  # (field, header pattern); first match wins per column
    ("date", re.compile(r"event\s*date|^date|date\s*(?:&|and)\s*time|^when|schedule", re.I)),
    ("skip", re.compile(r"upload|posted|publish|sl\.?$|s\.?\s*no|^#$|^no\.?$|^day$|^time$", re.I)),
    ("title", re.compile(r"title|topic|^event|programme|program|seminar|lecture|subject", re.I)),
    ("speaker", re.compile(r"speaker|presenter|lecturer|^by$|^name", re.I)),
    ("affil", re.compile(r"affiliation|institut|university|from$", re.I)),
    ("venue", re.compile(r"venue|place|location|room", re.I)),
    ("desc", re.compile(r"abstract|details?|description|summary", re.I)),
]


def _columns(header_cells):
    cols = {}
    for i, h in enumerate(header_cells):
        h = clean(h)
        for field, pat in _COLS:
            if pat.search(h):
                if field != "skip" and field not in cols:
                    cols[field] = i
                break
    return cols


def table_from_html(cfg, html, page_url):
    from urllib.parse import urljoin
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        thead = table.find("thead")
        if thead is not None and not thead.find("tr"):      # <thead><th>..</th></thead> (IACS)
            head = thead.find_all("th")
            rows = [None] + [r for r in rows if r.find("td")]
        elif rows:
            head = rows[0].find_all(["th", "td"])
        if len(rows) < 2:
            continue
        cols = _columns([c.get_text(" ") for c in head])
        if "date" not in cols or "title" not in cols:
            continue
        for tr in rows[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) <= max(cols.values()):
                continue
            def cell(f):
                v = clean(cells[cols[f]].get_text(" ")) if f in cols else ""
                return "" if re.fullmatch(r"[-–—]+|n/?a|tba|tbd", v, re.I) else v
            title = cell("title")
            start, end = parse_date_range(cell("date"))
            key = (start, re.sub(r"\W+", "", title.lower()))
            if not title or not start or key in seen or re.fullmatch(r"(?i)to be announced", title):
                continue          # (a pop-up abstract often repeats the row: IIT Delhi)
            seen.add(key)
            a = cells[cols["title"]].find("a", href=True) or next(
                (x for x in tr.find_all("a", href=True)
                 if not x["href"].startswith(("#", "javascript:", "mailto:"))), None)
            url = urljoin(page_url, a["href"]) if a and not a["href"].startswith("#") else page_url
            who = cell("speaker")
            if who and cell("affil"):
                who = f"{who} ({cell('affil')})"
            loc = ", ".join(x for x in (cell("venue"), cfg.get("location")) if x)
            out.append(_event(cfg, f"{title} — {cell('speaker')}" if cell("speaker") else title,
                              url, start, end, location=loc, description=cell("desc"),
                              raw_type=cfg.get("type"), speaker=who or None))
    return out


def _table(cfg):
    out = []
    for url in _urls(cfg):
        out += table_from_html(cfg, get(url, insecure_ok=bool(cfg.get("insecure_ok"))).text, url)
    return out


# ---------------------------------------------------------------------------
# rss — RSS feeds of upcoming events whose item titles start with the date
# (Joomla JEvents "latest events": "30 Oct 2026 11:00 : BIO-CCU 2026 - ...").
# A multi-day event appears once per day; those rows are merged into a range.
# ---------------------------------------------------------------------------
_RSS_DATE_PREFIX = re.compile(r"^\s*(\d{1,2}\s+\w{3,9}\.?\s+\d{4})(?:\s+\d{1,2}[:.]\d{2}(?:\s*[ap]m)?)?\s*[:\-–]\s*", re.I)


def rss_events(cfg, xml_text):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    merged = {}
    for item in root.iter("item"):
        raw = clean(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip() or cfg.get("page") or cfg["url"]
        m = _RSS_DATE_PREFIX.match(raw)
        start = parse_date_range(m.group(1))[0] if m else parse_date_range(raw)[0]
        title = raw[m.end():] if m else raw
        if not title or not start:
            continue
        key = (link, title.lower())
        desc = BeautifulSoup(item.findtext("description") or "", "html.parser").get_text(" ")
        if key in merged:
            e = merged[key]
            e["start_date"] = min(e["start_date"], start)
            e["end_date"] = max(e["end_date"], start)
        else:
            merged[key] = _event(cfg, title, link, start, description=desc, raw_type=cfg.get("type"))
    return list(merged.values())


def _rss(cfg):
    out = []
    for url in _urls(cfg):
        out += rss_events(cfg, get(url, insecure_ok=bool(cfg.get("insecure_ok"))).text)
    return out


# ---------------------------------------------------------------------------
# iiser_pune — IISER Pune's events page is a Vue app that POSTs a search to
# /events?handler=search with the anti-forgery token embedded in the page.
# ---------------------------------------------------------------------------
def _iiser_pune(cfg):
    import json
    from urllib.parse import urljoin
    from common import HTTP
    base = cfg.get("base", "https://www.iiserpune.ac.in").rstrip("/")
    page = get(f"{base}/events").text            # also sets the anti-forgery cookie
    m = re.search(r'data-request-validation-token="([^"]+)"', page)
    if not m:
        raise ValueError("IISER Pune events page has no request token")
    token, out, seen = m.group(1), [], set()
    for nav in ("today", "upcoming"):
        for pg in range(1, 11):
            payload = {"Category": None, "Pg": pg, "Departments": [], "OutreachAndTrainings": [],
                       "CalendarDate": dt.datetime.now().isoformat(), "CalendarView": "month",
                       "SelectedNav": nav}
            r = HTTP.post(f"{base}/events?handler=search", data=json.dumps(payload),
                          headers={"content-type": "application/json",
                                   "RequestVerificationToken": token}, timeout=(10, 30))
            r.raise_for_status()
            data = r.json()
            token = data.get("RequestValidationToken") or token
            for it in data.get("EventItems") or []:
                if it.get("Id") in seen:
                    continue
                seen.add(it.get("Id"))
                venue = clean(BeautifulSoup(it.get("Venue") or "", "html.parser").get_text(" "))
                online = bool(re.search(r"zoom|online|webex|google meet|teams", venue, re.I))
                who = re.sub(r"^\s*by\s+", "", clean(it.get("Summary") or ""), flags=re.I) or None
                start = iso(it.get("StartDate")) or parse_date_range(it.get("StartDateTime") or "")[0]
                end = iso(it.get("EndDate")) or parse_date_range(it.get("EndDateTime") or "")[0]
                # never copy meeting links or passcodes: an online venue is just "Online"
                loc = "Online" if online else ", ".join(x for x in (venue[:120], cfg.get("location")) if x)
                out.append(_event(cfg, it.get("Title"), urljoin(base, it.get("URL") or "/events"),
                                  start, end, location=loc, description=clean(it.get("Summary") or ""),
                                  raw_type=it.get("Category") or cfg.get("type"), speaker=who,
                                  online=online))
            if pg >= int(data.get("NoOfPages") or 1):
                break
    return [e for e in out if e["title"] and e["start_date"]]


ADAPTERS = {"iiser_pune": _iiser_pune, "rss": _rss, "table": _table, "listing": _listing, "ical": _ical, "google_calendar": _google_calendar,
            "wp_events": _wp_events, "indico": _indico, "labelled_list": _labelled_list}


def _registry(include_disabled=False):
    cfg = _load(INSTITUTES)
    entries = list(cfg.get("sources") or [])
    # v5 layout, still accepted
    entries += [dict(p, kind="listing") for p in cfg.get("pages") or []]
    entries += [dict(i, kind="indico") for i in cfg.get("indico") or []]
    if not include_disabled:
        entries = [e for e in entries if e.get("enabled", True)]
    return entries


FEED_KINDS = {"ical", "google_calendar", "wp_events", "indico", "rss", "iiser_pune"}


def empty_ok_names():
    """Structured feeds answer authoritatively: zero upcoming events from a feed
    that responded means "nothing announced", not "scraper broken"."""
    return {e["name"] for e in _registry(True) if e.get("kind", "listing") in FEED_KINDS}


_DESC_TITLE = re.compile(r"\bTitle\s*:\s*(.+?)\s*(?=\b(?:Time|Venue|Abstract|Speaker|Host|"
                         r"Date|Location)\b[^:]{0,20}:|$)", re.I | re.S)


_LEADING_DATES = re.compile(r"^\s*(?:\d{1,2}(?:st|nd|rd|th)?\s+\w+,?\s+\d{4}"
                            r"(?:\s*(?:to|-|–)\s*\d{1,2}(?:st|nd|rd|th)?\s+\w+,?\s+\d{4})?\s*)+", re.I)
_BADGE = re.compile(r"\s*\(\s*new\s*\)\s*$|^\s*new\s*[:!\-–]\s*", re.I)
# "... (ICEMD 2026) : 21st - 23rd December 2026", "... C4SOS-26 to be held during 21–23 Dec 2026"
_TRAILING_DATE = re.compile(r"(?:\s+[:|]\s*|\s+(?:to be )?(?:held|scheduled)\s+(?:during|on|from|between)\s+)"
                            r"([^:|]{4,45})$", re.I)
_DATE_WORDS = re.compile(r"\b(?:\d{1,4}(?:st|nd|rd|th)?|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|"
                         r"january|february|march|april|june|july|august|september|october|november|"
                         r"december|\w+day|to|and|from|till|until)\b", re.I)


def _drop_trailing_date(title):
    """Cut a date the site appended to the title; the card shows the dates anyway."""
    m = _TRAILING_DATE.search(title)
    if m and m.start() >= 12 and parse_date_range(m.group(1))[0] \
            and not re.sub(r"[\W_]+", "", _DATE_WORDS.sub("", m.group(1))):
        return title[:m.start()].rstrip(" ,;–-")
    return title


def run_source(cfg):
    """Run one registry entry. `include` (a regex) keeps only items whose title
    matches it; `exclude` drops matching ones (thesis defences, tenders, ...)."""
    evs = ADAPTERS[cfg.get("kind", "listing")](cfg) or []
    for e in evs:                            # "(NEW)" badges are not part of a title (IACS)
        e["title"] = _drop_trailing_date(_BADGE.sub("", e.get("title") or "").strip())
    if cfg.get("title_in_description"):     # calendar entry named after the speaker,
        for e in evs:                        # "Title: ..." in its description (IIT Bombay)
            m = _DESC_TITLE.search(e.get("description") or "")
            if m:
                who = e["title"]
                e["title"] = f"{m.group(1).strip(' .,;')} — {who}"
                e["speaker"] = e.get("speaker") or who
    if cfg.get("title_label"):               # "Details: <full name>" beside a generic
        pat = re.compile(rf"\b{re.escape(cfg['title_label'])}\s*:\s*(.+)", re.I | re.S)
        for e in evs:                        # heading such as "International Conference"
            m = pat.search(e.get("description") or "")
            if not m:
                continue
            full = _LEADING_DATES.sub("", m.group(1))
            full = re.split(r"\s+(?:read more|know more|view details)\b", full, flags=re.I)[0].strip(" .,;")
            if len(full) >= 12:
                e["title"] = full
    if cfg.get("include"):              # notice boards: keep only real events
        pat = re.compile(cfg["include"], re.I)
        evs = [e for e in evs if pat.search(e.get("title") or "")]
    if cfg.get("exclude"):
        pat = re.compile(cfg["exclude"], re.I)
        evs = [e for e in evs if not pat.search(e.get("title") or "")]
    return evs


def india_sources(include_disabled=False):
    """-> list of (name, fn, min_expected)"""
    out = []
    for e in _registry(include_disabled):
        kind = e.get("kind", "listing")
        if kind not in ADAPTERS:
            raise ValueError(f"institutes.yaml: unknown kind '{kind}' for {e.get('name')}")
        out.append((e["name"], (lambda c=e: run_source(c)), int(e.get("min_expected", 0))))
    return out


# ---------------------------------------------------------------------------
# Manual channel 1: watchlist.yaml (permanent entries, edited by you)
# ---------------------------------------------------------------------------
def _manual_event(it, source):
    url = str(it.get("url") or "").strip()
    title, start, end = it.get("title"), iso(it.get("start")), iso(it.get("end"))
    if url and (not title or not start):   # URL-only entry: read what we can from the page
        try:
            html = get(url).text
            if not title:
                m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
                title = clean(m.group(1)) if m else None
            if not start:
                start, end = parse_date_range(re.sub(r"<[^>]+>", " ", html)[:20000])
        except Exception as exc:
            print(f"  {source}: fetch failed for {url}: {exc}")
    if not url:     # poster/email-only event: link to where it was recorded
        repo = os.environ.get("GITHUB_REPOSITORY", "Astrophysicist-Abhi26/research-horizon")
        url = f"https://github.com/{repo}/blob/main/scraper/watchlist.yaml"
    return dict(
        title=title or url, url=url, start_date=start, end_date=end or start,
        deadline=iso(it.get("deadline")), location=it.get("location"),
        country=it.get("country"), online=bool(it.get("online")), tz=None,
        description=clean(it.get("notes") or ""), speaker=None,
        source=source, raw_type=it.get("type"),
        declared=[f"field:{x}" for x in it.get("fields") or []],
        priority=True)


def scrape_watchlist():
    items = _load(WATCHLIST)
    if isinstance(items, dict):
        items = items.get("events") or []
    return [_manual_event(it, "Watchlist") for it in items or []
            if isinstance(it, dict) and (it.get("url") or it.get("title"))]


# ---------------------------------------------------------------------------
# Manual channel 2: "Add event" GitHub issues (phone-friendly, no commits)
# ---------------------------------------------------------------------------
INTAKE_LABEL = "add-event"
_FIELD_KEYS = {
    "event name": "title", "title": "title", "link": "url", "url": "url",
    "start date": "start", "end date": "end", "deadline": "deadline",
    "registration / abstract deadline": "deadline", "where": "location",
    "location": "location", "type": "type", "fields": "fields",
    "research fields": "fields", "notes": "notes",
}
_FIELD_IDS = {     # first match wins, so specific labels come first ("fairness" contains "ai")
    "llm": "ai.genai", "generative": "ai.genai", "nlp": "ai.nlp", "language & speech": "ai.nlp",
    "computer vision": "ai.vision", "reinforcement": "ai.rl", "safety": "ai.trust",
    "fairness": "ai.trust", "algorithms": "cs.theory", "computer science": "cs.general",
    "quantum": "phys.quantum", "condensed matter": "phys.condmat",
    "dark energy": "cosmo.de", "large-scale structure": "cosmo.lss",
    "cmb": "cosmo.early", "early universe": "cosmo.early", "dark matter": "cosmo.dm",
    "cosmology": "cosmo.general", "astrophysics": "astro.general",
    "gravitational": "astro.he", "ml for science": "ai.science",
    "ml theory": "ai.theory", "ai": "ai.general", "machine learning": "ai.general",
    "mathematics": "math.other", "number theory": "math.nt", "topology": "math.topology",
    "algebra": "math.algebra", "geometry": "math.geometry",
    "probability": "math.probability", "statistics": "math.probability",
    "mathematical physics": "math.mathphys", "general relativity": "phys.gr",
    "gravitation": "phys.gr", "high-energy": "phys.hepth", "qft": "phys.hepth",
    "physics": "phys.general",
}


def parse_issue_form(title, body):
    """GitHub issue-form body ('### Label\\n\\nvalue') -> watchlist-style dict."""
    it = {}
    for label, value in re.findall(r"^###\s+(.+?)\s*\n+(.*?)(?=^###\s|\Z)", body or "",
                                   re.S | re.M):
        key = _FIELD_KEYS.get(label.strip().lower())
        value = value.strip()
        if not key or not value or value == "_No response_":
            continue
        if key == "fields":
            chosen = re.findall(r"- \[[xX]\]\s*(.+)", value) or re.split(r",\s*", value)
            ids = []
            for c in chosen:
                for k, v in _FIELD_IDS.items():
                    if k in c.lower() and v not in ids:
                        ids.append(v)
                        break
            it["fields"] = ids
        elif key in ("start", "end", "deadline"):
            it[key] = parse_date_range(value)[0] or iso(value)
        else:
            it[key] = value
    if not it.get("title"):
        it["title"] = re.sub(r"^\s*\[?(event|add event)\]?\s*[:\-–]?\s*", "", title or "",
                             flags=re.I).strip() or None
    return it


def scrape_issue_intake():
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not repo:
        return []                       # local run: nothing to read
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    issues = get(f"https://api.github.com/repos/{repo}/issues",
                 params={"labels": INTAKE_LABEL, "state": "open", "per_page": 100},
                 headers=headers).json()
    out = []
    for iss in issues if isinstance(issues, list) else []:
        it = parse_issue_form(iss.get("title"), iss.get("body"))
        if not it.get("url"):
            it["url"] = iss.get("html_url")   # poster-only events: the issue holds the poster
        ev = _manual_event(it, "Added by you")
        ev["description"] = (ev["description"] + f" (issue #{iss.get('number')})").strip()
        out.append(ev)
    return out
