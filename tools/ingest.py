#!/usr/bin/env python3
"""
DECK INGEST - drop a file, the deck eats it.
Ship 12 (Caro Command Deck) file scraper, stdlib only (nothing to install).

HOW TO USE (owner):
  1. Drop any session log (.txt, .md, .rtf, .pdf) into  inbox/  in the deck
     repo folder (a-mirror-of-my-becoming-ship12-caro-command/inbox/),
     or anywhere on disk.
  2. Run:   python3 tools/ingest.py            # eats everything in inbox/
        or: python3 tools/ingest.py ~/Downloads/whatever.rtf
        or: python3 tools/ingest.py --dry     # preview, touch nothing
        or: python3 tools/ingest.py --commit  # also git-commit the result
  3. Read the terminal summary. Confident rows become cards (verdict first,
     marks applied, SQ numbers assigned automatically). Anything the scraper
     is not sure about is listed for review - NEVER invented into cards.

LAWS (from data/console-data.json _contract): verdict first, reason first,
plain English, never invent postings, nothing is ever submitted by the
console. This tool only reads your files and writes the deck.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

VERDICTS = [
    ("APPLIED", ["applied", "application submitted", "application was submitted"]),
    ("YOUR CALL", ["your call", "conditional pass", "owner call", "owner switch"]),
    ("KILL", ["kill", "killed", "no-go", "no go", "not advancing", "hard stop", "fail"]),
    ("PASS", ["pass (ladder)", "pass", "passes"]),
    ("YOUR CALL", ["your call"]),
    ("CALL", ["advance to first-contact", "first-contact check", "call"]),
    ("BENCH", ["bench", "benched", "parked"]),
    ("HOLD", ["hold", "held"]),
    ("SKIP", ["skip", "tombstone"]),
]

ROLE_HINTS = r"(engineer|developer|tester|analyst|technician|manager|architect|specialist|associate|consultant|auditor|designer|scientist|admin|support|swe|sdet|qa|data center)"
GATE_RE = re.compile(r"60[- ]second gate", re.I)
URL_RE = re.compile(r"https?://[^\s)\"']+")
EMP_STOP = r"(dice\.com|breezy\.hr|greenhouse\.io|workday|linkedin|indeed|glassdoor|http|www\.)"


def find_repo(start):
    p = os.path.dirname(os.path.abspath(start)) if os.path.isfile(start) else os.path.abspath(start)
    for cand in [p] + list(iter_ancestors(p)):
        if os.path.isfile(os.path.join(cand, "data", "console-data.json")):
            return cand
    raise SystemExit("No deck repo (data/console-data.json) found from " + p)


def iter_ancestors(p):
    while True:
        parent = os.path.dirname(p)
        if parent == p:
            return
        yield parent
        p = parent


def to_text(path):
    ext = os.path.splitext(path)[1].lower()
    raw = open(path, "rb").read()
    if ext == ".pdf":
        for tool in ("pdftotext", "textutil"):
            if shutil.which(tool):
                args = [tool] + (["-convert", "txt", "-stdout", path] if tool == "textutil" else [path, "-"])
                try:
                    return subprocess.run(args, capture_output=True, text=True, timeout=60).stdout
                except Exception:
                    pass
        return ""
    if ext == ".rtf" or raw[:5] == b"{\\rtf":
        if shutil.which("textutil"):  # macOS native
            r = subprocess.run(["textutil", "-convert", "txt", "-stdout", path],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                return r.stdout
        t = raw.decode("utf-8", "ignore")
        t = re.sub(r"\\'([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), t)
        t = re.sub(r"\\[a-zA-Z]+-?\d*\s?", " ", t)
        return re.sub(r"[{}]", "", t)
    return raw.decode("utf-8", "ignore")


def classify(seg):
    s = seg.lower()
    for verdict, keys in VERDICTS:
        if any(k in s for k in keys):
            return verdict
    return None


def short(res, n=90):
    return re.sub(r"\s+", " ", res).strip()[:n]


BAD_EMPL = re.compile(
    r"\b(gate|test|verdict|title|leo|you\b|your|rate|math|car\b|patient|employer gate|deadline|"
    r"row\b|rows|sq#|floor|requirement|sop|workflow|crawler|rules|skip |kill |pass |applied |"
    r"ai:|board|scan|sweep|gates|ladder|rubric|mark|check)\b", re.I)


def clean_line(l):
    l = l.replace("**", " ").replace("\u00a0", " ")
    l = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", l)  # md links
    return re.sub(r"\s+", " ", l).strip()


def company_ok(e):
    if not (3 <= len(e) <= 34):
        return False
    if BAD_EMPL.search(e):
        return False
    if not re.match(r"^[A-Z0-9]", e):
        return False
    if e.endswith((":", ".", ", ", ";")):
        return False
    if len(e.split()) > 5:
        return False
    if re.search(r"[!?]", e):
        return False
    return True


VERDICT_TOKEN = re.compile(
    r"\b(APPLIED|APPLICATION SUBMITTED|CONDITIONAL PASS|YOUR CALL|PASS\s*\(LADDER\)|PASS|"
    r"KILLED?|NO[- ]?GO|NOT ADVANCING|HARD STOP|SKIP|BENCH(?:ED)?|HOLD)\b", re.I)


def find_verdict(line):
    """Verdict only counts at line start, after 'gate:', or in the tail."""
    head = line[:16]
    gate = re.search(r"gate\s*[:\u00b7]\s*(.{0,40})", line, re.I)
    tail = line[-48:]
    for zone, val in ((head, line[:16]), (gate.group(1) if gate else "", gate.group(1) if gate else ""), (tail, tail)):
        m = VERDICT_TOKEN.search(val)
        if m:
            v = m.group(1).upper()
            if v == "PASS" and "LADDER" not in val.upper():
                v = "PASS"
            return v
    return None


def normalize(v):
    v = v.upper()
    if v in ("KILLED", "NO-GO", "NO GO", "NOT ADVANCING", "HARD STOP"):
        return "KILL"
    if v == "BENCHED":
        return "BENCH"
    if v == "APPLICATION SUBMITTED":
        return "APPLIED"
    return v


SECTION_RE = re.compile(
    r"^\*{0,2}(KILLS? (?:WALL)?|KILLED|PASSES?|GOs?|YOURS? CALLS?|HOLDS?|SKIPS?|BENCH(?:ES)?|"
    r"APPLIED|APPLICATIONS? SUBMITTED|NO[- ]?GOS?)\b[^a-z]{0,60}", re.I)


def section_verdict(header):
    h = header.upper()
    if "KILL" in h:
        return "KILL"
    if "PASS" in h:
        return "PASS"
    if "APPLIED" in h or "APPLICATION" in h:
        return "APPLIED"
    if "YOUR CALL" in h or "YOUR CALLS" in h or re.match(r"^GO", h):
        return "YOUR CALL"
    if "HOLD" in h:
        return "HOLD"
    if "BENCH" in h:
        return "BENCH"
    if "SKIP" in h:
        return "SKIP"
    return None


def split_role(txt):
    """'TEKsystems Epic Beacon Analyst' -> ('TEKsystems', 'Epic Beacon Analyst')."""
    txt = txt.strip(" *\u2013\u2014-")
    m = re.match(r"^(.{2,34}?)\s+[A-Za-z0-9&/+\-']*\s*(" + ROLE_HINTS + r"[\w/ ]{0,30})$", txt, re.I)
    if m:
        empl, role = m.group(1).strip(" \u2013\u2014-,"), m.group(2).strip()
        words = empl.split()
        if len(words) >= 2 and company_ok(words[0]) and \
           re.search(ROLE_HINTS, " ".join(words[1:]), re.I) and len(words) <= 4:
            empl, role = words[0], " ".join(words[1:]) + " " + role
        return empl, role
    return txt, ""


NOISE = re.compile(
    r"^(item number|sort$|search this list|job opportunity name|job title$|company$|"
    r"pay/compensation range|remote or in-person|experience level|sorted ascending|"
    r"location \(state|action$|why it fails|.*job opportunities$|open to|apply.*external|"
    r"new$|saved jobs|my jobs|united states$|posted (today|ago)|apply now)", re.I)


def companyish(cell):
    c = cell.strip(" *\u2013\u2014-:|")
    if not c or re.match(r"^SQ-?\d", c, re.I) or c.lower().startswith("sq#"):
        return False
    if re.match(r"^\$", c) or re.match(r"^\d+(\.\d+)?[kK]?\s*[-\u2013/]", c):
        return False
    if NOISE.match(c):
        return False
    if re.fullmatch(r"(remote|hybrid|on[- ]?site|in[- ]?person|entry|full[- ]time|part[- ]time|contract|w2|c2c|temp|perm|onsite|usa|tx\b|fl\b|va\b|ca\b|ga\b|il\b|pa\b|nc\b|ny\b|nj\b|ma\b|az\b|co\b|oh\b|mi\b|wa\b|dc\b|md\b|tx\b|ne\b|ga\b)", c, re.I):
        return False
    if re.fullmatch(r"[\w\s&/'\-\.,]*" + ROLE_HINTS + r"[\w\s]*", c, re.I) and \
       not re.search(r"\b(inc|llc|corp|corporation|systems|solutions|technologies|labs?|consulting|group|alliance|partners|associates|source|first)\b", c, re.I):
        return False  # a bare role name, not a company
    if c.startswith(("Job Opportunity", "All ", "DOOR", "Leo AI", "You:", "GATE", "The deck", "Below the")):
        return False
    if '"' in c or "\"" in c:
        return False
    return company_ok(c)


def parse_file(path, text):
    rows, review = [], []
    lines = [clean_line(l) for l in text.splitlines() if l.strip()]
    cur = None  # verdict of the section we are in
    last_role = None
    for i, line in enumerate(lines):
        if NOISE.match(line):
            continue
        sec = SECTION_RE.match(line)
        if sec:
            cur = section_verdict(sec.group(1))
            continue
        if re.match(r"^(want|next|heres|here's|should i|i (can|may|will)|everything|all \d)", line, re.I):
            cur = None  # prose ends a section run
        if cur:
            bullet = re.match(r"^[-\u2022\u25cf]\s*(?:\*\*(.*?)\*\*)", line) or re.match(r"^[-\u2022\u25cf]\s*(.{2,70})$", line)
            body = (bullet.group(1) if bullet and bullet.group(1) else (bullet.group(2) if bullet else line))
            body = re.split(r"\s\u2014\s|\s--\s", body, 1)[0].strip(" *\u2013\u2014-:|")
            empl = role = ""
            if re.split(r"\s*--\s*", body, 1)[0] != body:  # "Ericsson--Data Center Technicians"
                empl, role = re.split(r"\s*--\s*", body, 1)
            elif bullet or "--" in line:
                empl, role = split_role(body)
            else:
                continue  # attribute / echo line (state, rate, level, role echo)
            if role == last_role and not bullet:
                continue  # role echo of the previous row
            e0 = empl.strip(" *\u2013\u2014-")
            if e0 and companyish(e0) and (role or company_ok(e0)):
                last_role = role or None
                rows.append({"employer": e0, "role": short(role, 60) or "Role not stated",
                             "verdict": cur, "rest": short(line, 160), "url": "",
                             "line": short(line, 200)})
            continue
        # ---- standalone gate / verdict lines (outside sections) ----
        vtok = find_verdict(line)
        if not vtok:
            cells = [c.strip() for c in re.split(r"\||\t", line) if c.strip()]
            if len(cells) >= 3:
                blk_v = None
                for c in cells:
                    if re.fullmatch(VERDICT_TOKEN.pattern, c.strip(), re.I):
                        blk_v = normalize(c.strip())
                        break
                if blk_v:
                    empl = next((c for c in cells if companyish(c)), "")
                    role = next((c for c in cells if re.search(ROLE_HINTS, c, re.I) and c != empl), "")
                    if empl:
                        rows.append({"employer": empl, "role": short(role, 60) or "Role not stated",
                                     "verdict": blk_v, "rest": short(" | ".join(cells), 160), "url": "",
                                     "line": short(line, 200)})
                        continue
            if "--" in line and re.search(ROLE_HINTS, line, re.I):
                ahead = [lines[j] for j in range(i + 1, min(i + 9, len(lines)))]
                blk_v = None
                for a in ahead:
                    if re.fullmatch(VERDICT_TOKEN.pattern, a, re.I):
                        blk_v = normalize(a)
                        break
                if blk_v:
                    empl, role = line.split("--", 1)
                    if company_ok(empl.strip(" *\u2013\u2014-")):
                        rows.append({"employer": empl.strip(" *\u2013\u2014-"), "role": short(role, 60),
                                     "verdict": blk_v, "rest": short(line, 160), "url": "",
                                     "line": short(line, 200)})
                        continue
            continue
        verdict = normalize(vtok)
        lead = re.split(r"\b60[- ]second gate\b|\bGATE VERDICT\b", line, flags=re.I)[0]
        lead = re.sub(VERDICT_TOKEN, " ", lead, count=1)
        lead = re.sub(r"^[\W_]+|[\W_]+$", "", lead).strip(" \u2013\u2014-:|\u00b7")
        lead = re.sub(r"^(?:SKIP|KILL|PASS|HOLD|BENCH|YOUR CALL|APPLIED|GATE)\b\s*[-\u2013\u2014:]*\s*", "", lead, flags=re.I)
        gm = re.search(r"gate\s*:\s*(.{3,100})", line, re.I)  # "...gate: Employer Role ..."
        if gm and not companyish(lead.split("\u2014")[0].split("--")[0]):
            lead = gm.group(1)
        empl = role = ""
        parts = [p.strip(" \u2013\u2014-:|\u00b7*") for p in re.split(r"\||\t|\u00b7|\s{3,}|\s\u2014\s|\s--\s", lead) if p.strip(" \u2013\u2014-:")]
        for p in parts[:3]:
            if not empl and companyish(p.split(",")[0]):
                empl = p.split(",")[0].strip()
            elif empl and re.search(ROLE_HINTS, p, re.I) and not role:
                role = p.strip(" *\u2013\u2014-")
        if empl and not role:
            empl2, role2 = split_role(empl)
            if role2 and not role:
                empl, role = empl2, role2
        if not empl and gm:
            m2 = re.match(r"([A-Za-z][\w&'/+\-\.]{2,28}(?:'s)?)[\s,]+(.+)$", gm.group(1).strip())
            if m2 and company_ok(m2.group(1).rstrip("'s")):
                empl = m2.group(1).rstrip("'s")
                role = m2.group(2).strip(" \u2013\u2014-")
        url = URL_RE.search(line) or (URL_RE.search(lines[i + 1]) if i + 1 < len(lines) else None)
        if not empl or not company_ok(empl):
            review.append(short(line, 200))
            continue
        if not role:
            rm = re.search(r"([A-Z][\w&/+'\- ]{0,48}?" + ROLE_HINTS + r"[\w ]{0,26})", line)
            role = rm.group(1).strip(" *") if rm else ""
        if not role and not (verdict == "APPLIED" and url):
            review.append(short(line, 200))
            continue
        rows.append({"employer": empl, "role": role.strip() or "Role not stated",
                     "verdict": verdict, "rest": short(lead, 160), "url": url.group(0) if url else "",
                     "line": short(line, 200)})
    return rows, review
    return rows, review


def build_card(sq, r, date, src):
    return {"sq": sq,
            "title": r["role"],
            "company": r["employer"],
            "verdict": r["verdict"],
            "badge": r["verdict"] + " \u2726 AUTO-INGEST \u2726 " + date,
            "headline": f"{r['employer']} \u00b7 {r['role']} \u00b7 {r['verdict'].lower()} \u00b7 {date} \u00b7 from {src}",
            "pay": {"value": "", "note": ""},
            "where": {"value": "", "note": ""},
            "link": {"url": r["url"], "label": ("Open the posting" if r["url"] else "")},
            "effort": "",
            "theJob": ("Scraped from " + src + " by the deck ingest. Gate read: " + r["rest"] +
                       (" Full line: \u201c" + r["line"] + "\u201d" if r["line"] else "")),
            "posted": "", "requirements": [], "fits": [], "trade": ""}


def main():
    argv = [a for a in sys.argv[1:]]
    dry = "--dry" in argv
    commit = "--commit" in argv
    push = "--push" in argv
    argv = [a for a in argv if not a.startswith("--")]

    here = os.path.dirname(os.path.abspath(__file__))
    repo = find_repo(here)
    inbox = os.path.join(repo, "inbox")
    os.makedirs(inbox, exist_ok=True)
    os.makedirs(os.path.join(inbox, "done"), exist_ok=True)

    jobs_in = [a for a in argv] or (sorted(os.listdir(inbox))
                                    if os.path.isdir(inbox) else [])
    files = []
    for j in jobs_in:
        p = j if os.path.isabs(j) else os.path.join(inbox, j)
        if os.path.isfile(p) and not p.endswith((".json", ".tsv")):
            files.append(p)
    if not files:
        print("Nothing to eat. Drop files in inbox/ or pass a path.")

    C = json.load(open(os.path.join(repo, "data", "console-data.json"), encoding="utf-8"))
    sq_nums = [int(m.group(1)) for j in C["jobs"] for m in [re.match(r"SQ-(\d+)", j.get("sq") or "") ] if m]
    nxt = (max(sq_nums) if sq_nums else 0) + 1
    stamp = datetime.datetime.now().strftime("%b %d, %Y, %I:%M %p ET").replace(" 0", " ")
    date = datetime.datetime.now().strftime("%b %d")

    new_cards, all_review, fed_from = [], [], []
    existing = {(j.get("company", "").lower(), j.get("verdict")) for j in C["jobs"]}
    for f in files:
        text = to_text(f)
        if not text.strip():
            print(f"(skip: no text extracted from {os.path.basename(f)})")
            continue
        src = os.path.basename(f)
        rows, review = parse_file(f, text)
        seen = set()
        for r in rows:
            key = (r["employer"].lower(), r["verdict"])
            if key in seen or key in existing:
                continue
            seen.add(key)
            if not any(c["company"].lower() == r["employer"].lower() and c["verdict"] == r["verdict"] for c in new_cards):
                new_cards.append(build_card("SQ-%d" % nxt, r, date, src))
                nxt += 1
        all_review += [f"{src}: {t}" for t in review]
        fed_from.append(f"{src} ({len(rows)} rows)")
        if not dry:
            shutil.move(f, os.path.join(inbox, "done", src))

    if not new_cards:
        print("No confident rows found. Review list:", len(all_review), "lines (inbox/review.txt).")
    else:
        C["jobs"] = new_cards[::-1] + C["jobs"]
        counts = {}
        for c in new_cards:
            counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
        line = ("AUTO-INGEST \u2014 " + str(len(new_cards)) + " cards from " + ", ".join(fed_from) +
                " \u2014 " + ", ".join(f"{k} x{v}" for k, v in counts.items()) +
                ". Everything unsure is parked in inbox/review.txt, not invented into cards.")
        C["feed"] = [{"t": stamp, "line": line}] + C["feed"]
        C["updated"] = stamp
        print(line)
        for c in new_cards:
            print(f"  {c['sq']:7} {c['verdict']:9} {c['company'][:30]:30} {c['title'][:40]}")

    if all_review:
        with open(os.path.join(inbox, "review.txt"), "a", encoding="utf-8") as fh:
            fh.write("\n".join(all_review) + "\n")
        print(f"review list: {len(all_review)} lines -> inbox/review.txt")

    if dry:
        print("(dry run - nothing written)")
        return
    if not new_cards:
        print("deck unchanged - nothing to write or commit.")
        return
    json.dump(C, open(os.path.join(repo, "data", "console-data.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    if commit:
        git = ["git", "-C", repo]
        subprocess.run(git + ["add", "data/console-data.json", "inbox"], check=True)
        staged = subprocess.run(git + ["diff", "--cached", "--quiet"]).returncode != 0
        if not staged:
            print("nothing staged - deck unchanged, no commit made.")
            return
        subprocess.run(git + ["commit", "-m", f"deck: auto-ingest {len(new_cards)} cards ({stamp})"], check=True)
        if push:
            subprocess.run(git + ["push"], check=True)
        print("committed" + (" and pushed" if push else " - push when you are ready"))


if __name__ == "__main__":
    main()
