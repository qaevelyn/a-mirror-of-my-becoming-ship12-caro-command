#!/usr/bin/env python3
"""
SHIP 12 SCOUT SWEEP — the crawler canon. No server, no versions, no rebuilds.

THE LOOP (CONSOLE FEED LAW, owner ruling Nov 6, 2026 — verbatim intent:
"build it right the first time and have it reading from a dynamic document to
keep itself updated. no versions of software or builds. the crawler is pulling
information around the clock and dumping it on the forms so the console can
read that and populate the data for me"):

  scout agent sweeps the web (read-only, public postings) → captures candidate
  rows into a sweep payload JSON
  → THIS SCRIPT runs every row through the 60-second gate (data/operator.json)
  → survivors become plain-English rows at the TOP of the GO section of
    data/console-data.json (verdict first, reason first)
  → the console (index.html — the frozen build) fetches that file fresh on
    every load and every 20 seconds
  → the owner flips GO switches / leaves notes → SYNC exports
    data/console-state.json → she commits → the agent reads her orders there

WHAT THIS SCRIPT NEVER DOES (absolute rules): it never submits, never contacts,
never opens a form, never touches accounts, and it NEVER touches the owner's
switches or comments (they live in data/console-state.json, not here).

USAGE
  python3 tools/crawler/scout-sweep.py <sweep-payload.json>
  cat payload.json | python3 tools/crawler/scout-sweep.py

SWEEP PAYLOAD SCHEMA (one JSON array; every field optional unless noted):
[
  {
    "title": "Software Tester",                 // required
    "company": "Labelmaster",                   // required
    "url": "https://...",                       // required — at least one working URL
    "payBand": "$70,000 - $85,000",             // or "$33/hr", or "" if unposted
    "where": "Remote (US)",
    "effort": "apply",
    "posted": "Nov 2026",
    "theJob": "one plain paragraph: what the work is all day",
    "fits": ["junior title", "QA lane core"],
    "trade": "the trade-off named in one plain sentence (for CALL rows)",
    "funding": "allIn | partial | selfFunded | silent",
    "fundingLanguage": "verbatim line from the posting about travel/lodging/per diem",
    "requirementsVerbatim": ["line 1", "line 2"],   // the captured requirements block
    "headline": "the verdict reason, plain English",
    "badge": "short badge text (e.g. 'Per diem + lodging', 'Easy Apply')",
    "watch": "what to watch for (optional)"
  }
]

LAWS ENCODED HERE (owner rulings, estate/00-CRAWLER-RULES.md):
  - REQUIREMENTS-CAPTURE LAW: no captured requirements block = BENCH digest line,
    never a PASS row. Any never-claim item required hands-on = auto-kill quoting
    the verbatim line.
  - PHYSICAL-WORK LAW: outdoor craft work = kill regardless of funding.
  - EMPLOYER GATE: Amazon/AWS-as-employer rows die sight-unseen.
  - TOMBSTONE LAW: tombstoned employer+title (data/operator.json) never re-served.
  - NUMBERING: SQ-<n> continues the highest existing SQ in the document — the
    document always wins, never trust a hardcoded number.
  - PLAIN-ENGLISH PRESENTATION LAW: verdict first, reason first, no jargon.
"""
import json
import re
import sys
import os
from datetime import datetime, timezone

REPO_HINTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../tools
REPO_ROOT = os.path.dirname(REPO_HINTS)
DOC_PATH = os.path.join(REPO_ROOT, "data", "console-data.json")
OPS_PATH = os.path.join(REPO_ROOT, "data", "operator.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def money_floor(row, ops):
    """Return (annual_bottom or None, note). Annualizes hourly rates × 2,080."""
    band = str(row.get("payBand") or "")
    min_year = ops["pay"]["minYear"]
    basis = ops["pay"]["hoursBasis"]
    if not band.strip():
        return None, "no posted band — the money score stays capped until the band is verified on a live free channel"
    # hourly: "$30/hr", "$30 per hour", "$30-35/hr"
    m = re.search(r"\$\s?(\d+(?:\.\d+)?)\s*(?:-|–|to)?\s*\$?\s*(\d+(?:\.\d+)?)?\s*(?:/|per\s)?\s*hr", band, re.IGNORECASE)
    if m:
        lo = float(m.group(1))
        annual = lo * basis
        return annual, "$%s/hr bottom = $%s/yr against your $%s minimum" % (
            m.group(1), format(int(annual), ","), format(min_year, ","))
    # annual: "$62,400", "$62,400 - $75,000", "62,400"
    m = re.search(r"\$\s?(\d[\d,]{3,})(?:\s*(?:-|–|to)\s*\$?\s?(\d[\d,]{3,}))?", band)
    if m:
        lo = float(m.group(1).replace(",", ""))
        return lo, "$%s bottom against your $%s minimum" % (
            format(int(lo), ","), format(min_year, ","))
    return None, "posted pay line could not be parsed — verify by hand: %r" % band


def gate(row, ops):
    """Run one candidate through the 60-second gate. Returns (verdict, card_fields, digest_line).

    verdict: GO (all gates pass) | CALL (soft/ambiguous — trade named, owner decides)
             | BENCH/KILL (not queued; digest line only)
    """
    title = str(row.get("title") or "")
    company = str(row.get("company") or "")
    url = str(row.get("url") or "")
    g = ops["gate"]
    pay = ops["pay"]
    min_year = pay["minYear"]

    # --- TOMBSTONE LAW ---
    for t in ops.get("tombstones", {}).get("list", []):
        if (t.get("company", "").lower() in company.lower()
                and t.get("title", "").lower() in title.lower()):
            return None, None, "TOMBSTONED — %s at %s was dropped by the owner (%s); never re-served" % (
                title, company, t.get("reason", "owner ruling"))

    # --- EMPLOYER GATE (dies sight-unseen) ---
    for bad in g["employerKill"]:
        if bad.lower() in company.lower():
            return None, None, "KILLED — %s is the employer (%s); dies on the employer gate sight-unseen" % (company, bad)

    # --- REQUIREMENTS-CAPTURE LAW ---
    reqs = row.get("requirementsVerbatim") or []
    if not reqs:
        return None, None, "BENCH — %s at %s: requirements block not captured — bench until the JD body is read from a live free mirror (%s)" % (
            title, company, url)

    # --- NEVER-CLAIM SCAN (verbatim quote on kill) ---
    claims = [c.lower() for c in g["neverClaim"]]
    allowed = {t.lower() for t in g.get("usedWithReceipts", {}).get("tools", [])}
    for line in reqs:
        ll = str(line).lower()
        for c in claims:
            if c in allowed:
                continue  # Atlassian suite: claimable with receipts
            if re.search(r"(?<![a-z])" + re.escape(c) + r"(?![a-z])", ll):
                return None, None, "KILLED — never-claim required hands-on: \"%s\" (JD line: \"%s\")" % (c, str(line)[:160])

    # --- TITLE TEST ---
    for ban in g["titleBans"]:
        if re.search(r"(?<![a-z])" + re.escape(ban.lower()) + r"(?![a-z])", title.lower()):
            return None, None, "KILLED — title carries a banned level word (%s): %s at %s" % (ban, title, company)

    # --- PHYSICAL-WORK LAW ---
    hay = " ".join([title, str(row.get("theJob") or "")]).lower()
    for kw in g["physicalWork"]["killKeywords"]:
        if kw.lower() in hay:
            return None, None, "KILLED — physical-work law: outdoor/craft work (%s matched \"%s\") — dies regardless of pay or funding" % (kw, title)

    # --- PAY / FLOOR MATH ---
    annual, pay_note = money_floor(row, ops)
    floor_verdict = None
    if annual is None:
        floor_verdict = "CALL"  # no verified band = never a clean GO
    elif annual < min_year:
        return None, None, "KILLED — the bottom of the band ($%s/yr) does not clear your $%s minimum" % (
            format(int(annual), ","), format(min_year, ","))

    # --- FUNDING BRANCHES ---
    funding = str(row.get("funding") or "silent").lower()
    if funding == "selffunded":
        return None, None, "KILLED — self-funded travel/relocation (car-gate law): %s" % (
            str(row.get("fundingLanguage") or "posting asks the candidate to carry the cost")[:160])
    if funding == "partial":
        floor_verdict = "CALL"  # surface with the gap named

    # --- VERDICT ---
    verdict = floor_verdict or "GO"
    annual_s = ("$%s/yr bottom" % format(int(annual), ",")) if annual is not None else "band unverified"
    vs = ""
    if annual is not None:
        diff = int(annual - min_year)
        vs = ("clears your minimum by $%s" % format(diff, ",")) if diff >= 0 else "below your minimum"
    headline = row.get("headline") or (
        "%s — %s %s." % (title, annual_s, vs) if annual is not None
        else "%s — %s" % (title, pay_note))

    card = {
        "title": title,
        "company": company,
        "verdict": verdict,
        "badge": str(row.get("badge") or ("Per diem + lodging + wheels" if funding == "allin" else "")),
        "headline": headline.strip(),
        "pay": {"value": str(row.get("payBand") or ""), "note": pay_note},
        "where": {"value": str(row.get("where") or ""), "note": ""},
        "effort": str(row.get("effort") or "apply"),
        "link": {"url": url, "label": "Open the posting"},
        "theJob": str(row.get("theJob") or ""),
        "fits": row.get("fits") or [],
        "trade": str(row.get("trade") or ""),
        "watch": str(row.get("watch") or ""),
        "requirements": [{"label": "REQUIREMENTS (VERBATIM)", "lines": [str(x) for x in reqs]}],
        "posted": str(row.get("posted") or ""),
    }
    if funding:
        fl = str(row.get("fundingLanguage") or "")
        card["where"]["note"] = {
            "allin": "company-paid travel, lodging and per diem — the gold-mine branch",
            "partial": "PARTIAL funding — the gap is named in the posting; ask who pays transport",
            "silent": "posting is silent on travel funding — never assume; first-contact question stands",
        }.get(funding, "")
        if fl:
            card["requirements"].append({"label": "FUNDING LANGUAGE (VERBATIM)", "lines": [fl]})
    return verdict, card, None


def next_sq(doc):
    """Continue the highest existing SQ number. The document always wins."""
    top = 0
    for j in doc.get("jobs", []):
        m = re.match(r"SQ-(\d+)", str(j.get("sq", "")))
        if m:
            top = max(top, int(m.group(1)))
    return top


def sweep_stamp():
    """Sweep timestamp in the owner's format (ET) — falls back to local zone honestly."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/New_York")).strftime("%b %d, %I:%M %p ET")
    except Exception:
        return datetime.now().astimezone().strftime("%b %d, %I:%M %p %Z")


def main():
    if len(sys.argv) > 1:
        payload = load_json(sys.argv[1])
    else:
        payload = json.load(sys.stdin)

    ops = load_json(OPS_PATH)
    doc = load_json(DOC_PATH)
    if "jobs" not in doc or "feed" not in doc:
        sys.exit("FATAL: %s is not the dynamic console document (missing jobs/feed)" % DOC_PATH)

    counter = next_sq(doc)
    existing = {(str(j.get("company", "")).lower(), str(j.get("title", "")).lower())
                for j in doc.get("jobs", [])}
    now = sweep_stamp()

    queued, feed_lines = [], []
    for row in payload:
        title = str(row.get("title") or "")
        company = str(row.get("company") or "")
        if not title or not company:
            feed_lines.append("Skipped one malformed payload row (missing title or company).")
            continue
        if (company.lower(), title.lower()) in existing:
            feed_lines.append("Skipped a duplicate sighting: %s at %s (already on the board)." % (title, company))
            continue
        verdict, card, digest = gate(row, ops)
        if digest:
            feed_lines.append(digest)
            continue
        counter += 1
        card["sq"] = "SQ-%d" % counter
        card["order"] = counter
        doc["jobs"].insert(0, card)  # new rows sit at the TOP of the document;
        existing.add((company.lower(), title.lower()))
        why = card["headline"]
        label = {"GO": "GO — ready, say the word and the packet is built",
                 "CALL": "YOUR CALL — the trade: %s" % (card["trade"] or "see the posting")}
        feed_lines.append("%s (%s) added as %s: %s." % (title, company, card["sq"], why))
        queued.append(card)

    doc["feed"] = [{"t": now, "line": ln} for ln in feed_lines] + doc.get("feed", [])
    doc["feed"] = doc["feed"][:30]  # the law: keep the feed at ≤ 30 lines, newest first
    doc["updated"] = now

    with open(DOC_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    print("=== SWEEP MERGED — the dynamic document is updated; the build never changed ===")
    print("document : %s" % DOC_PATH)
    print("queued   : %d row(s) -> %s" % (
        len(queued), ", ".join(c["sq"] for c in queued) or "none"))
    for c in queued:
        print("  %s | %s — %s | %s" % (c["sq"], c["title"], c["company"], c["verdict"]))
    print("digest   : %d line(s) (kills, benches, duplicates — see the feed in the document)" % len(feed_lines))
    for ln in feed_lines:
        print("  · %s" % ln)
    print("next step: commit data/console-data.json (the console picks it up on its next 20-second poll)")


if __name__ == "__main__":
    main()
