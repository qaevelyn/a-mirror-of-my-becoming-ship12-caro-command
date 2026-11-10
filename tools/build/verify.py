#!/usr/bin/env python3
"""
SHIP 12 BUILD VERIFIER — run from any clone of this repo (or a fork):

    python3 tools/build/verify.py

Proves the contract is intact, with zero baked data:

  1. every JSON document parses
  2. the dynamic document carries jobs / feed / ships / standingRules /
     minPayLine / updated — the console must get EVERYTHING from this file
  3. index.html (the frozen build) contains ZERO baked data — no SQ numbers,
     no company names, no job literals — only the wiring
  4. the wiring is present: dynamic-document URL, state URL, 20 s poll,
     REFRESH SCAN, SYNC export, file:// fail-loud banner, kawoosh
  5. the JavaScript parses (node --check) and the crawler compiles (py_compile)
  6. end-to-end HTTP: serves the repo and fetches the dynamic document
     exactly the way the console does

Exit 0 = the build is the build and the data moves. Anything else = fix before
committing. This is the only "build step" this repo will ever have.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fails = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + (("  -- " + detail) if detail else ""))
    if not cond:
        fails.append(name)


def p(rel):
    return os.path.join(REPO_ROOT, rel)


# ---- 1. JSON validity -------------------------------------------------------
for rel in ["data/console-data.json", "data/console-state.json", "data/operator.json", "manifest.json"]:
    try:
        json.load(open(p(rel), encoding="utf-8"))
        check("json valid: " + rel, True)
    except Exception as e:
        check("json valid: " + rel, False, str(e))

# ---- 2. the dynamic document carries everything -----------------------------
try:
    doc = json.load(open(p("data/console-data.json"), encoding="utf-8"))
    check("dynamic document has jobs/feed/ships/updated/minPayLine/standingRules",
          all(k in doc for k in ("jobs", "feed", "ships", "updated", "minPayLine", "standingRules")))
    check("dynamic document has jobs", len(doc.get("jobs", [])) > 0,
          str(len(doc.get("jobs", []))) + " rows")
    check("fleet canon complete (13 ships)", len(doc.get("ships", [])) == 13,
          str(len(doc.get("ships", []))))
    check("ships 6/7 carry repo pointers", all(
        s.get("url") for s in doc["ships"] if s.get("n") in (6, 7)))
except Exception as e:
    check("dynamic document readable", False, str(e))

# ---- 3. zero baked data in the frozen shell ---------------------------------
try:
    html = open(p("index.html"), encoding="utf-8").read()
except Exception as e:
    html = ""
    check("index.html readable", False, str(e))
check("no baked job literals (no SQ- refs)", not re.search(r"SQ-\d+", html))
check("no baked company names", "Crash Champions" not in html and "Labelmaster" not in html)
check("no baked updated stamp", "Nov 9" not in html)
check("no baked jobs array literal", not re.search(r"window\.JOBS_DATA\s*=\s*\[", html))

# ---- 4. the wiring ----------------------------------------------------------
check("dynamic wire declared", "data/console-data.json" in html)
check("state wire declared", "data/console-state.json" in html)
check("20 s poll present", "20000" in html)
check("REFRESH SCAN present", 'id="scanBtn"' in html and "loadDynamic" in html)
check("SYNC TO REPO present", 'id="syncBtn"' in html and "console-state.json" in html)
check("file:// fail-loud banner", "location.protocol === 'file:'" in html)
check("committed-state merge", "mergeCommitted" in html)
check("fleet/feed/rules render client-side", all(
    x in html for x in ('fleet-grid', 'feed-box', 'rules-block', 'dyn-updated')))
check("kawoosh wired", "triggerKawoosh" in html)

# ---- 5. code parses ----------------------------------------------------------
scripts = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
for i, js in enumerate(scripts):
    tmp = "/tmp/ship12_verify_inline_%d.js" % i
    open(tmp, "w").write(js)
    r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    check("inline JS block %d parses (node --check)" % (i + 1), r.returncode == 0,
          (r.stderr or "")[:300])
r2 = subprocess.run(["node", "--check", p("assets/gate-module.js")], capture_output=True, text=True)
check("gate-module.js parses", r2.returncode == 0, (r2.stderr or "")[:200])
rpy = subprocess.run([sys.executable, "-m", "py_compile", p("tools/crawler/scout-sweep.py")],
                     capture_output=True, text=True)
check("crawler compiles (py_compile)", rpy.returncode == 0, (rpy.stderr or "")[:300])
check("stale jobs.json removed", not os.path.exists(p("jobs.json")))

# ---- 6. end-to-end HTTP the way the console does it --------------------------
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8093", "--directory", REPO_ROOT],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)
try:
    with urllib.request.urlopen("http://127.0.0.1:8093/data/console-data.json?t=" + str(int(time.time())),
                                timeout=5) as r:
        body = json.load(r)
        check("HTTP fetch of dynamic document", r.status == 200 and len(body.get("jobs", [])) > 0)
    with urllib.request.urlopen("http://127.0.0.1:8093/data/console-state.json", timeout=5) as r:
        check("HTTP fetch of state document", r.status == 200)
    with urllib.request.urlopen("http://127.0.0.1:8093/index.html", timeout=5) as r:
        check("index.html served", r.status == 200)
finally:
    srv.terminate()

print()
print("RESULT:", "ALL PASS" if not fails else "FAILURES: " + ", ".join(fails))
sys.exit(1 if fails else 0)
