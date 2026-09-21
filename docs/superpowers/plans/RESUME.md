# Resume point — faculty profile rework

**Date paused:** 2026-09-21
**Branch:** `rework-profile-page` (27 commits, branched from `master` at `760129f`)
**Original page:** recoverable at any time with `git show 01bb885:index.html`

## Where things stand

All 13 planned tasks are implemented and reviewed. The final whole-branch
review returned **"ship with named fixes"**. `python3 tests/check.py` passes.

Content is provably intact: 229 of 229 baseline strings preserved, all 19
original sections structurally unchanged (same rows, same order, same
fields). Two independent parsers re-derived this from the original file.

## What was still in flight when we paused

A fix wave was running and left **uncommitted edits** to `index.html` and
`docs/superpowers/plans/HANDOFF.md`. Check them with `git diff` before doing
anything else. They address, from the final review:

1. The first paint hangs off an uncaught async handler — a throw loads a blank page
2. `importJson` validates too loosely; a bad import can permanently brick the page
3. `crypto.subtle` is unguarded, so admin silently dies on a plain `http://` origin
4. `download()` may not fire in Firefox (anchor not appended, blob revoked too early)
5. Handoff: backup step came after the edit step; export check couldn't actually verify
6. Small ones: `mailto:` sink, empty `href`, admin bar wrap at 360px, double confirm

If the diff looks incomplete, the cleanest recovery is
`git checkout -- index.html docs/superpowers/plans/HANDOFF.md` and re-run
that fix wave from this list.

## Two user decisions made, NOT yet applied

**1. Stat tiles — this is a publication blocker.**

The header currently publishes numbers that contradict the page's own prose:

| Tile | Shows | His own text says |
|---|---|---|
| Publications | 15 | "over 55 peer-reviewed journal papers" |
| Sponsored projects | 8 | "across 27 projects" |
| Patents | 3 | "three patents" (correct) |
| Current students | 4 | guidance line totals 10 ongoing |

The lists are curated subsets, not inventories — `pubIntro` literally says
"a representative selection". Every automated check passes this because the
spec told them to verify "tile equals array length", which is exactly the
wrong thing to verify.

**Decision: use the real numbers.** Add a confirmed-counts field to the
content (55+, 27, 3, 10), sourced from his bio and research-guidance line,
editable in admin mode. Update `renderStats` to read it, and update the
self-test assertion that currently checks tile-equals-array-length.

**2. Admin chrome.** Export JSON / Export HTML currently sit above his name
on the public page. **Decision: hide them behind admin login**, so a visitor
sees only his name, title and photo.

## Then, to finish

- Scoped re-review of the fix wave plus the two decisions above
- Hand the user `docs/superpowers/plans/HANDOFF.md` and have them run
  `index.html?selftest=1` in Firefox

## The thing to keep in mind

**No JavaScript has ever been executed in this project.** There is no Node,
no browser automation and no package manager on this machine. Every check is
Python doing static analysis. That constraint already hid one severe bug: a
literal `</script>` inside a JavaScript *comment* silently terminated the
main script element, killing ~100 lines of code, and four independent
reviews plus 179 string-matching checks all passed it.

Nothing interactive — editing, export, search, tab routing, printing — has
been confirmed to work. The browser checklist is the first real test.

## Still unconfirmed by the user

- The three "Invited talks" entries: all three were derived from award
  records, not from a list of talks
- `Scopus ID: 12345166600`, `Total citations: 1038`, `h-index: 18` — these
  came from the original page, not from this rework, but the Scopus ID looks
  unusual and the figures will go stale

## Files worth reading first tomorrow

- `.superpowers/sdd/2026-09-21-faculty-profile-rework/progress.md` — the full
  ledger: every commit, every ruling, and what each ruling costs if wrong
- `docs/superpowers/specs/2026-09-21-faculty-profile-rework-design.md` — the design
- `docs/superpowers/plans/HANDOFF.md` — what the user actually needs to do
