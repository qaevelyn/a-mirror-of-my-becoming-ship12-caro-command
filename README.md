# A Mirror of My Becoming™ — Ship 12 · Caro Command (SGC Command Deck™)

**The build is the build. The data moves. Nothing else.**

A job-scouting command console that needs **no server, no database, and no rebuilds — ever**.
One frozen HTML build reads one dynamic JSON document. A crawler updates that document
around the clock. The owner sees fresh jobs on every visit. She flips switches and leaves
notes in the browser; one button exports her orders as a file she commits back to the
repo. The loop closes with no infrastructure at all beyond GitHub Pages.

**This instance (the owner's):** https://qaevelyn.github.io/a-mirror-of-my-becoming-ship12-caro-command/
**The pattern:** belongs to the world — fork it, edit one config file, and it is yours.

This came from an owner ruling (Nov 6, 2026): *"build it right the first time and have it
reading from a dynamic document to keep itself updated. no versions of software or builds.
the crawler is pulling information around the clock and dumping it on the forms so the
console can read that and populate the data for me."*

---

## What this is

The fleet console for Commander E. Caro: 13 ships, 13 chevrons. The SGC gate-room
control deck — monitor up (a live Stargate event horizon: water ripple, twinkling
starfield; click the gate to fire the kawoosh), control board down (the job board).
Tap a ship in the manifest to lock its chevron — lock all 13 and the ring dials,
the wormhole opens, and Ship 13 (TriviaGate™) rides through as the payload.

---

## The two kinds of files

### FROZEN — the build (never regenerated for data, never versioned)

| File | Role |
| --- | --- |
| `index.html` | The console. Contains **zero data** — structure, styles, and the wiring that fetches the dynamic document on load and every 20 seconds. |
| `assets/gate-module.css` | The SGC control-room skin. |
| `assets/gate-module.js` | The gate-room overlay: DIAL THE GATE / VIEW THE GATE, fleet chips, the event-horizon canvas + the kawoosh, and the overlay job strip — which also reads the dynamic document. |
| `manifest.json` | Static fleet-canon snapshot for tools and humans. The main console does not read it — the page renders from the dynamic document; only the gate-overlay's fleet chips use this snapshot. |

### DYNAMIC — the moving parts (the only things that ever change)

| File | Role |
| --- | --- |
| `data/console-data.json` | **THE DYNAMIC DOCUMENT.** Ships, jobs, feed, standing rules, pay floor. The crawler writes it; the console reads it; nothing else exists as a data source. |
| `data/console-state.json` | **The owner's orders of record.** Exported by the console's `SYNC TO REPO` button (her switches + notes). The agent reads this before building anything. A comment overrides a switch. |
| `data/operator.json` | **The requirements canon** — the 60-second gate as data: pay floor, never-claim list, employer kills, funding branches, watchlist, contact rules, absolute rules. Fork this file and the whole pipeline obeys YOUR requirements. |
| `tools/crawler/scout-sweep.py` | **The crawler canon.** Takes a sweep payload (candidate rows captured from public postings) and merges the survivors into the dynamic document after running every one through the gate in `data/operator.json`. |
| `tools/build/verify.py` | **The build verifier.** The only "build step" this repo will ever have: run it any time to prove the contract — every document parses, the shell carries zero baked data, the wiring is present, the code compiles, and the document is fetchable over HTTP exactly the way the console fetches it. |

---

## The template and the instance

This repo is a **template**: the structure, the workflow, and the logical flow —
nothing in the frozen shell or the crawler code knows whose board it is. The
personalized layer is **data**, and it lives in exactly two files (plus your URL):

| Layer | What it is | Where it lives |
| --- | --- | --- |
| **TEMPLATE — belongs to the world** | the console shell, the crawler logic, the gate as code, the verifier, the loop itself | `index.html`, `assets/`, `tools/`, `manifest.json`, this README |
| **INSTANCE — yours alone** | who you are, your pay floor, your never-claim list, your kill-listed employers, your tombstones, your watchlist, your contact rules | `data/operator.json` |
| **INSTANCE — yours alone** | your actual board: fleet, jobs, feed, standing rules, every update | `data/console-data.json` |

Change `data/operator.json` and every gate in the crawler re-aims at YOUR
requirements — no code edits, no rebuilds. Even the footer signature on the page
reads `operator.name` from that file: the frozen shell carries no personal
strings at all. That is the entire personalization surface.

---

## The loop

```
        ┌──────────────────────────────────────────────────────────────┐
        │                                                              │
        ▼                                                              │
  scout sweep (web, read-only, public postings only)                   │
        │  candidate rows → sweep payload JSON                         │
        ▼                                                              │
  tools/crawler/scout-sweep.py                                         │
        │  runs the 60-second gate from data/operator.json:            │
        │    title test → pay floor → requirements scan → funding      │
        │    → physical-work law → employer gate → tombstones          │
        │  survivors = plain-English rows, verdict first,              │
        │  new SQ numbers, TOP of the GO section                       │
        ▼                                                              │
  data/console-data.json  ←────── the one dynamic document             │
        │                                                              │
        ▼                                                              │
  index.html (the frozen build)                                        │
        │  fetches on load + every 20 s + REFRESH SCAN button          │
        ▼                                                              │
  the owner reads the board                                            │
        │  flips GO switches · leaves notes in the cards               │
        ▼                                                              │
  SYNC TO REPO button → downloads console-state.json                   │
        │  she commits + pushes it (she presses every button)          │
        ▼                                                              │
  the agent reads data/console-state.json = orders of record ──────────┘
        builds the authorized packets, appends the feed line
```

**Sort law on the board:** GO (newest on top) → CALL → APPLIED → SKIP → DEAD (bottom).
New rows the crawler queues land at the top of GO, because they are the newest GOs.

**Precedence law on verdicts:** committed `console-state.json` fills any browser that
has never seen a switch; the live browser's own state stays the in-hand truth while
she is using it.

---

## The 60-second gate (as code, in `scout-sweep.py`)

1. **Title test** — no Senior / Lead / II / III / Principal / Staff / Manager.
2. **Rate test** — bottom of band × 2,080 vs the pay floor in `data/operator.json`
   ($62,400 = $30/hr). No posted band = never a clean GO; capped until verified
   on a live free channel.
3. **Requirements line** — the captured requirements block is scanned against the
   never-claim list. Any hit = auto-kill **quoting the verbatim JD line**. The
   Atlassian suite (Jira · Confluence · Trello) is claimable with receipts.
4. **Requirements-capture law** — no captured block = BENCH digest line, never a
   queue row.
5. **Car gate** — remote, or 100%-travel company-paid, or transit corridor **with
   employer-paid transit**.
6. **Patient gate** — no end-user / help-desk support.
7. **Employer gate** — kill-listed employers (operator.json) die sight-unseen.
8. **Physical-work law** — indoor desk/machine work only; outdoor craft dies
   regardless of pay or funding.
9. **Schedule gate** — retired; start dates are captured, never used to reject.
10. **Funding branches** — all-in (gold mine) / partial (gap named) / self-funded
    (kill) / silent (never assume funding).
11. **Exception clause** — a tripped hard gate is not silent when the package is
    exceptional: it becomes **YOUR CALL** with the trade named, owner decides.

Every row surfaces in plain English: **GO** / **YOUR CALL** / **SKIP**, reason first.
No scores, no jargon, no checkmark cascades in the owner-facing layer.

---

## For the world: fork this

1. Fork the repo (it works on GitHub Pages as-is — a static site with a fetch).
2. Edit `data/operator.json` — your name, your pay floor, your never-claim list,
   your kill-listed employers, your lanes. **The crawler and console obey it
   automatically.**
3. Edit `data/console-data.json` — your fleet, your standing rules, your first
   rows (or start with an empty `jobs: []` and `feed: []`).
4. Feed candidate rows to `tools/crawler/scout-sweep.py` (the payload schema is
   in its docstring) from any source you scout with. Commit the document it
   writes. Run `python3 tools/build/verify.py` to prove the wiring.
5. The console updates itself. You never rebuild. You never version.
6. Your switches and notes export from the console; commit them back; your agent
   (or you) reads `data/console-state.json` as the orders of record.

That is the whole contract: **the build is the build; the data is the only thing
that moves; and the owner presses every button that matters.**

---

## Run it locally

The console reads its data over HTTP (that is the point — no stale snapshots):

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

Opening `index.html` by double-click (`file://`) shows a loud banner explaining
this instead of silently showing stale data. That is deliberate.

## Put it on GitHub Pages

1. Repo **Settings → Pages**
2. Source: **Deploy from a branch** · Branch: **main** · Folder: **/ (root)** → **Save**
3. Wait about a minute — `https://<username>.github.io/<repo-name>/` is live.

Keep the filename `index.html` so Pages serves it at the root.

---

Canon note (from the deck itself): a real gate ring carries 9 chevrons — the 13 lock
slots here are ours, one per ship, one fleet. Ship names marked DRAFT are placeholders
built from real, on-the-record work; rename anything and re-issue the console.

**Owner:** Evelyn Caro · **Ship:** 12 of 13 · License: AGPL-3.0-only or commercial (see `LICENSE`)
