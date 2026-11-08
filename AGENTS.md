# A Mirror of My Becoming™ — Ship 12 · standing orders

## Language — English only (owner directive, 2026-10-26)

Every AI session on this repository wakes in English and stays in English: replies, analysis, code comments, commit messages, every artifact. No other language appears in any output, no exceptions. Read this file first, every session, before any other work.

## Deployment — blue and green (ruling 2026-11-08)

Green is main: what GitHub Pages serves. Green never carries unverified bytes — it is the rollback. Blue is the blue branch: the staging lane. Every repair commits to blue, pushes to origin, and lands only after raw receipts match: git rev-parse blue equals git ls-remote origin refs/heads/blue, and the raw fetch shasum equals the local file shasum. Promotion is the owner's word only: fast-forward main to a verified blue. No agent promotes, no agent pushes main.

## Registry of Marks — the check before anything goes out (ruling 2026-11-08)

No document, product, or name leaves this repo without the mark pass. The master SOP is the Registry of Marks — Table of Terms, kept by the sweep; the live table of terms is index-of-terms.html on the portfolio site. The sign lands on first use of a name in each work and on title and header uses; filenames, URLs, slugs and storage keys stay unmarked — identifiers, not prose. Two seats: Caro Command Deck™ outside the page — repo, About, release, lookbook, manifest; SGC Command Deck™ inside the page. The repo slug stays caro-command. Builds carry no version numbers.

## Canon

Fleet names come from the portfolio registry ships/manifest.json and nowhere else. The FLEET array in index.html is regenerated from it: public hulls carry their repo URL, sealed hulls carry none.
