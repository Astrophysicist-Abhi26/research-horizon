"""Indian institute sources: generic listing fixes and per-source filters."""
import datetime as dt

import sources_india as SI
from listing import extract_listing, labelled_title

SOON = dt.date.today() + dt.timedelta(days=20)
D = f"{SOON.day:02d} {SOON:%B} {SOON.year}"


def test_labelled_title_and_speaker():
    text = ("Department Seminar : Speaker : Dr. Ananya Adhikari, Postdoctoral Researcher at "
            "CENTRA, Lisbon Title : Two faces of numerical relativity, Venue : Seminar Room")
    title, who = labelled_title(text)
    assert title == "Two faces of numerical relativity"
    assert who == "Dr. Ananya Adhikari, Postdoctoral Researcher at CENTRA, Lisbon"
    assert labelled_title("Black holes in the cosmic web") == ("Black holes in the cosmic web", None)


def test_listing_uses_labelled_title():
    html = f"""<html><body><ul>
      <li><a href="/phy/weekly_seminar.php">{D}, 02:30 PM: Department Seminar : Speaker : Dr. A. B,
          Lisbon Title : Two faces of numerical relativity, Venue : Seminar Room</a></li>
      <li><a href="/phy/other.php">Some other page about the department</a></li>
    </ul></body></html>"""
    evs = extract_listing("https://www.iitg.ac.in/phy/seminar.php", "IITG", "IIT Guwahati", html=html)
    assert [e["title"] for e in evs] == ["Two faces of numerical relativity"]
    assert evs[0]["speaker"].startswith("Dr. A. B") and evs[0]["start_date"] == SOON.isoformat()


def test_click_for_more_details_takes_the_heading():
    html = f"""<html><body>
      <div><h4>Recent trends in QFT and GR</h4><p>{D}</p>
           <a href="https://sites.google.com/view/qft-gr">Click for more details</a></div>
      <div><h4>Frontiers of Physical Chemistry</h4><p>{D}</p>
           <a href="https://fpc2026.in/">Click for more details</a></div>
    </body></html>"""
    evs = extract_listing("https://newweb.bose.res.in/", "SNB", "Kolkata", html=html)
    assert sorted(e["title"] for e in evs) == ["Frontiers of Physical Chemistry",
                                               "Recent trends in QFT and GR"]


def test_exclude_drops_matching_titles(monkeypatch):
    fake = [dict(title="Ph.D. Thesis Defense"), dict(title="Electric-field-driven dissipative structures")]
    monkeypatch.setitem(SI.ADAPTERS, "listing", lambda cfg: list(fake))
    cfg = {"name": "x", "kind": "listing", "url": "https://x", "exclude": "thesis defen[cs]e"}
    assert [e["title"] for e in SI.run_source(cfg)] == ["Electric-field-driven dissipative structures"]
    assert len(SI.run_source({"name": "x", "kind": "listing", "url": "https://x"})) == 2


# ---------------------------------------------------------------------------
# table / rss / IISER Pune adapters (markup copied from the live pages, 2026-10-25)
# ---------------------------------------------------------------------------
def test_table_with_thead_without_row_iacs():
    html = f"""<table><thead><th>SL</th> <th>Title </th> <th>Advertisement uploaded date</th>
      <th>Event date</th><th>Detail</th></thead><tbody>
      <tr><td>1</td><td>National Conference on Electronic Structure (NCES 2026) (NEW)</td>
          <td>2026-08-25</td><td>{SOON.isoformat()} to {(SOON + dt.timedelta(days=1)).isoformat()}</td>
          <td><a href="nces2026/nces.php">Open</a></td></tr></tbody></table>"""
    cfg = {"name": "IACS", "location": "IACS, Kolkata, India"}
    evs = SI.table_from_html(cfg, html, "https://iacs.res.in/Event")
    assert len(evs) == 1 and evs[0]["url"] == "https://iacs.res.in/nces2026/nces.php"
    assert evs[0]["start_date"] == SOON.isoformat()          # the event date, not the upload date
    assert evs[0]["end_date"] == (SOON + dt.timedelta(days=1)).isoformat()


def test_table_title_speaker_date_and_repeated_rows():
    d = f"{SOON.day:02d} {SOON:%b} {SOON.year}, 4:30 PM"
    html = f"""<table><tr><th>Title</th><th>Speaker</th><th>Date</th><th>Link</th></tr>
      <tr><td>Just a Little Bit of Twist</td><td>Rajdeep Sensarma</td><td>{d}</td><td>-</td></tr>
      <tr><td>To Be Announced</td><td>Surjeet Singh</td><td>{d}</td><td>-</td></tr>
      <tr><td>Just a Little  Bit of Twist</td><td>Rajdeep Sensarma</td><td>{d}</td><td>-</td></tr>
      <tr><td>Untitled lab tour</td><td>-</td><td>{d}</td><td>-</td></tr></table>"""
    cfg = {"name": "IITM", "location": "IIT Madras, Chennai, India", "type": "colloquium"}
    evs = SI.table_from_html(cfg, html, "https://physics.iitm.ac.in/events/x.html")
    assert [e["title"] for e in evs] == ["Just a Little Bit of Twist — Rajdeep Sensarma",
                                         "Untitled lab tour"]
    assert evs[0]["speaker"] == "Rajdeep Sensarma" and evs[1]["speaker"] is None


def test_rss_merges_multi_day_rows():
    day = lambda n: (SOON + dt.timedelta(days=n)).strftime("%d %b %Y")
    xml = f"""<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel>
      <item><title>{day(0)} 11:00 : BIO-CCU 2026 – National Conference</title>
            <link>https://www.iisermohali.ac.in/event-details/eventdetail/730/-/bio</link></item>
      <item><title>{day(1)} 11:00 : BIO-CCU 2026 – National Conference</title>
            <link>https://www.iisermohali.ac.in/event-details/eventdetail/730/-/bio</link></item>
      <item><title>{day(2)} 09:00 : No Garland Neuroscience 2026</title>
            <link>https://www.iisermohali.ac.in/event-details/eventdetail/736/-/ngn</link></item>
    </channel></rss>"""
    evs = SI.rss_events({"name": "IISER Mohali", "url": "u", "location": "IISER Mohali"}, xml)
    bio = next(e for e in evs if e["title"].startswith("BIO-CCU"))
    assert (bio["start_date"], bio["end_date"]) == (SOON.isoformat(), (SOON + dt.timedelta(days=1)).isoformat())
    assert len(evs) == 2


def test_iiser_pune_search(monkeypatch):
    import common
    page = '<script id="EventsJs" data-request-validation-token="TOKEN1" src="/js/events.js"></script>'
    sent = []

    class R:
        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    def fake_post(url, data=None, headers=None, timeout=None):
        import json
        body = json.loads(data)
        sent.append((body["SelectedNav"], headers["RequestVerificationToken"]))
        items = [] if body["SelectedNav"] == "today" else [{
            "Id": 1, "Category": "Seminars", "Title": " Brain-Inspired Pattern Recognition",
            "Summary": "By Chetan Ralekar, MIT", "StartDate": SOON.isoformat(),
            "EndDate": SOON.isoformat(), "URL": "/events/1/brain",
            "Venue": "<p>Online seminar <a href='https://zoom.us/j/1'>zoom</a> passcode: 644599</p>"}]
        return R({"EventItems": items, "NoOfPages": 1, "RequestValidationToken": "TOKEN2"})

    monkeypatch.setattr(SI, "get", lambda url, **kw: type("P", (), {"text": page})())
    monkeypatch.setattr(common.HTTP, "post", fake_post)
    evs = SI.ADAPTERS["iiser_pune"]({"name": "IISER Pune", "location": "IISER Pune, Pune, India"})
    assert sent == [("today", "TOKEN1"), ("upcoming", "TOKEN2")]
    e = evs[0]
    assert e["title"] == "Brain-Inspired Pattern Recognition" and e["speaker"] == "Chetan Ralekar, MIT"
    assert e["url"] == "https://www.iiserpune.ac.in/events/1/brain"
    assert e["online"] and e["location"] == "Online" and "644599" not in str(e)   # no passcodes


def test_badges_and_include(monkeypatch):
    fake = [dict(title="Small Sciences Symposium (NEW)"), dict(title="Tender for guest house")]
    monkeypatch.setitem(SI.ADAPTERS, "listing", lambda cfg: [dict(x) for x in fake])
    cfg = {"name": "x", "kind": "listing", "url": "https://x", "include": "symposi|conference"}
    assert [e["title"] for e in SI.run_source(cfg)] == ["Small Sciences Symposium"]


def test_title_in_description(monkeypatch):
    desc = ("Description: Commutative Algebra seminar Speaker: Kaushik Khamari, IIT Bombay Host: X "
            "Title: On licci monomial ideals II Time, day and date: 11:30 AM Venue: Ramanujan Hall")
    monkeypatch.setitem(SI.ADAPTERS, "ical", lambda cfg: [dict(title="Kaushik Khamari, IIT Bombay",
                                                                description=desc, speaker=None)])
    e = SI.run_source({"name": "x", "kind": "ical", "url": "u", "title_in_description": True})[0]
    assert e["title"] == "On licci monomial ideals II — Kaushik Khamari, IIT Bombay"
    assert e["speaker"] == "Kaushik Khamari, IIT Bombay"


def test_ordinal_day_ranges():
    from common import parse_date_range
    assert parse_date_range("to host the symposium from 8th - 10th December 2026.") == \
        ("2026-12-08", "2026-12-10")
    assert parse_date_range("Tuesday, 1st December, 2026") == ("2026-12-01", "2026-12-01")


def test_registry_has_the_new_institutes():
    names = {n for n, _, _ in SI.india_sources()}
    for n in ["TIFR SciTalks (Indico)", "NISER (Indico)", "IIT Bombay Mathematics seminars",
              "IIT Delhi Physics talks", "IISER Pune events", "IISER Mohali events", "IACS events",
              "ARIES seminars"]:
        assert n in names, n
