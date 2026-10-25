"""Temporary: run candidate sources through the real adapters (not merged)."""
import re, sys, time, yaml, datetime as dt
sys.path.insert(0, "scraper")
from bs4 import BeautifulSoup
from common import get, today
import sources_india as SI

MON = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
DATE = re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MON},?\s+20\d\d|\b{MON}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+20\d\d"
                  rf"|\b20\d\d-\d\d-\d\d|\b\d{{1,2}}[./-]\d{{1,2}}[./-]20\d\d")
T = today().isoformat()

def page_report(url, insecure=False):
    try:
        r = get(url, insecure_ok=True, timeout=25)
    except Exception as e:
        print(f"    PAGE ERROR {type(e).__name__}: {str(e)[:160]}"); return
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.title.get_text(" ", strip=True) if soup.title else "")[:90]
    hints = sorted(set(re.findall(r"""(?:https?:)?//[^\s"'<>]*(?:calendar\.google|\.ics|ical|indico|wp-json|tribe|/feed|rss)[^\s"'<>]*""", r.text)))[:8]
    for s in soup(["script", "style", "nav", "footer", "header"]): s.decompose()
    txt = re.sub(r"\s+", " ", soup.get_text(" "))
    ds = DATE.findall(txt)
    years = [d for d in ds if re.search(r"202[6-7]", d)]
    print(f"    page {r.status_code} {r.url} {len(r.content)//1024}KB title={title!r}")
    print(f"    dates: {len(ds)} (2026-27: {len(years)}) e.g. {years[:6]}")
    if hints: print(f"    feeds: {hints}")
    m = next((m for m in DATE.finditer(txt) if re.search(r"202[6-7]", m.group(0))), None)
    i = max(0, m.start() - 250) if m else 0
    print(f"    text: {txt[i:i+900]}")

def links_report(cfg):
    try:
        r = get(cfg["url"], insecure_ok=bool(cfg.get("insecure_ok")), timeout=25)
    except Exception as e:
        print(f"  PAGE ERROR {type(e).__name__}: {str(e)[:160]}"); return
    print(f"  page {r.status_code} {r.url} {len(r.content)//1024}KB")
    soup = BeautifulSoup(r.text, "html.parser")
    seen = set()
    for a in soup.find_all("a", href=True):
        t = a.get_text(" ", strip=True)[:60]; h = a["href"].strip()
        if re.search(r"seminar|colloqui|event|conference|workshop|talk|calendar|lecture|meeting|school|symposi|indico", t + " " + h, re.I) and h not in seen:
            seen.add(h); print(f"    {t!r} -> {h[:140]}")
            if len(seen) >= 30: break
    srcs = re.findall(r'<script[^>]+src="([^"]+)"', r.text)
    apis = sorted(set(re.findall(r"""["'](/?[A-Za-z0-9_/.-]*(?:api|Api|API|json|Json|ajax|Service|service)[A-Za-z0-9_/.?=&-]*)["']""", r.text)))[:25]
    if apis: print(f"    api-like strings: {apis}")
    if "{{" in r.text: print(f"    JS app; scripts: {srcs[-8:]}")


def main():
    cands = yaml.safe_load(open("probe/candidates.yaml"))["sources"]
    only = [a.lower() for a in sys.argv[1:]]
    for cfg in cands:
        if only and not any(w in cfg["name"].lower() for w in only):
            continue
        t0 = time.time()
        print(f"\n### {cfg['name']}  [{cfg['kind']}]  {cfg.get('url') or cfg.get('base') or cfg.get('calendar')}", flush=True)
        if cfg["kind"] == "links":
            links_report(cfg); continue
        if cfg["kind"] == "iiserpune_raw":
            import json as _j
            from common import HTTP
            try:
                page = get("https://www.iiserpune.ac.in/events", timeout=25).text
                tok = re.search(r'data-request-validation-token="([^"]+)"', page).group(1)
                for nav in cfg.get("navs", ["upcoming"]):
                    payload = {"Category": None, "Pg": 1, "Departments": [], "OutreachAndTrainings": [],
                               "CalendarDate": dt.datetime.now().isoformat(), "CalendarView": "month",
                               "SelectedNav": nav}
                    r = HTTP.post("https://www.iiserpune.ac.in/events?handler=search", data=_j.dumps(payload),
                                  headers={"content-type": "application/json", "RequestVerificationToken": tok},
                                  timeout=(10, 30))
                    print(f"  POST {nav}: {r.status_code} {r.headers.get('content-type')} {len(r.content)}B")
                    print("    " + r.text[:cfg.get("chars", 3500)])
            except Exception as e:
                print(f"  ERROR {type(e).__name__}: {e}")
            continue
        if cfg["kind"] == "grep":
            try:
                body = get(cfg["url"], timeout=25).text
                if cfg.get("whole"):
                    a = cfg.get("start", 0)
                    if isinstance(a, str):
                        a = max(0, body.find(a) - 300)
                    print(body[a:a + cfg["whole"]]); continue
                for m in list(re.finditer(cfg["pattern"], body))[:12]:
                    print("    ..." + body[max(0, m.start()-160):m.end()+220].replace("\n", " ") + "...")
            except Exception as e:
                print(f"  ERROR {e}")
            continue
        try:
            evs = SI.run_source(cfg)
            up = sorted((e for e in evs if (e.get("end_date") or e.get("start_date") or "") >= T),
                        key=lambda e: e.get("start_date") or "")
            print(f"  RESULT raw={len(evs)} upcoming={len(up)} ({time.time()-t0:.1f}s)")
            for e in up[:6]:
                print(f"    {e.get('start_date')}  {(e.get('title') or '')[:85]}  <{(e.get('url') or '')[:70]}>"
                      + (f"  [speaker: {e['speaker'][:50]}]" if e.get("speaker") else ""))
        except Exception as e:
            print(f"  RESULT ERROR {type(e).__name__}: {str(e)[:200]} ({time.time()-t0:.1f}s)")
            up = []
        if not up and evs:
            past = sorted(evs, key=lambda e: e.get("start_date") or "")[-3:]
            for e in past:
                print(f"    past: {e.get('start_date')}  {(e.get('title') or '')[:85]}"
                      + (f"  [speaker: {e['speaker'][:40]}]" if e.get("speaker") else ""))
        if cfg["kind"] in ("listing", "table") and len(up) < 3 and not cfg.get("quiet"):
            page_report(cfg["url"])
        elif cfg["kind"] == "indico" and not up:
            page_report(cfg["base"].rstrip("/") + "/")
        sys.stdout.flush()

main()
