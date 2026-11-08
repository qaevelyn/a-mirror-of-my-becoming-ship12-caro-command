# A Mirror of My Becoming™ — Ship 12 · Caro Command (SGC Command Deck™)

The fleet console for Commander E. Caro: 13 ships, 13 chevrons.
Tap a ship in the manifest to lock its chevron — lock all 13 and the ring dials,
the wormhole opens, and Ship 13 (TriviaGate™) rides through as the payload.

One folder: `index.html` plus the gate module (`assets/`) and the job feed (`jobs.json`). No build step, no dependencies.

## Why this exists

This is the mirror itself: the record of a becoming, drafted by Carter (second in
command) from Evelyn Caro's real application history during Per Scholas AWS re/Start.
Thirteen ships, thirteen chevrons — every one built from on-the-record work. Locking all
thirteen dials the gate, and Ship 13 (TriviaGate™) rides through as the payload.

## What's inside

| File | What it is |
| --- | --- |
| `index.html` | The entire command deck — fleet manifest, chevron locks, dial sequence, gate-room window, "on the other side" reveal |
| `assets/gate-module.js` | Gate module — DIAL THE GATE / VIEW THE GATE strip, fleet chips, job-board auto-feed (polls `jobs.json` every 60s) |
| `assets/gate-module.css` | Gate module styling |
| `jobs.json` | Job-board feed — rows land here, the console reads them |

## Run it locally

Double-click `index.html`. That is the whole install.

## Put it on GitHub Pages

1. Repo **Settings → Pages**
2. Source: **Deploy from a branch** · Branch: **main** · Folder: **/ (root)** → **Save**
3. Wait about a minute, then your shareable URL is:
   `https://<username>.github.io/a-mirror-of-my-becoming-ship12-caro-command/`

## Updating later

Edit `index.html`, commit, push — Pages redeploys automatically. Keep the filename `index.html` so Pages serves it at the root.

## How the fleet stays current

Ship builds are finished as is. Updates land in each ship's README — every public hull
in the fleet manifest points at the living README inside its repo (the .md that gets
the updates), and that is how the template stays current. Sealed hulls (S08 DV14™,
S09 Radiology Companion™) stay unlinked, and Ship 13 (TriviaGate™) points at the
live game, not the repo.

---

Canon note (from the deck itself): a real gate ring carries 9 chevrons — the 13 lock
slots here are ours, one per ship, one fleet. Ship names marked DRAFT are placeholders
built from real, on-the-record work; rename anything and re-issue the console.
