# tools/ - the deck eats files

`ingest.py` scrapes a session log into cards: verdict first, marks applied,
SQ numbers assigned, feed line prepended, stamp bumped. Anything it is not
sure about goes to inbox/review.txt - never invented into cards.

    python3 tools/ingest.py                 # eats everything in inbox/
    python3 tools/ingest.py ~/Downloads/x.rtf
    python3 tools/ingest.py --dry          # preview only
    python3 tools/ingest.py --commit       # also commits (push stays yours)

Drop the file, run the command, read the summary, push when ready.
