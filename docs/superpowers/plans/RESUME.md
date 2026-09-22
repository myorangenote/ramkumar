# Resume point — faculty profile rework

**Date paused:** 2026-09-22
**Branch:** `rework-profile-page` (29 commits, branched from `master` at `760129f`)
**Original page:** recoverable at any time with `git show 01bb885:index.html`

## Where things stand

All 13 planned tasks are implemented and reviewed. The final whole-branch
review returned **"ship with named fixes"**; every named fix has now landed.
`python3 tests/check.py` passes — 230 checks. The page has also been run in
a real browser and passes its own 17 in-page self-tests.

Content is provably intact: 229 of 229 baseline strings preserved, all 19
original sections structurally unchanged (same rows, same order, same
fields). Two independent parsers re-derived this from the original file.

Working tree clean. Nothing is in flight.

## What landed since the last resume point

**Commit `ddd059f`** — the fix wave that was uncommitted when we paused:
uncaught async first paint, loose `importJson` validation that could brick
the page, unguarded `crypto.subtle` on plain `http://`, Firefox-unsafe
`download()`, plus the `mailto:`/empty-href sinks, admin bar wrap at 360px,
and the double confirm on discard. Handoff corrections too.

**Commit `afaa2fb`** — both user decisions, and two new bugs:

- **R22, the publication blocker.** Stat tiles were counted from curated
  lists, publishing 15 / 8 / 3 / 4 above his own prose saying 55+ / 27 /
  three / 10. Counts now live in `CONTENT.sections.stats`, so they travel
  through save/export/import and are editable in admin like any other row.
  The self-test assertion that had *certified* the wrong numbers is gone,
  replaced by one that fails if counting is ever reintroduced.
- **Export chrome gated behind admin**, so a visitor sees his name rather
  than developer buttons. Trade: losing the password loses the in-page
  route to a backup. Called out at the top of the handoff.
- **The footer was never wired.** Nothing in the file wrote `#pr-year` or
  `#pr-footer-name`; the page shipped a bare `©`.
- **`hidden` did not hide.** `.btn{display:inline-block}` beats the UA's
  `[hidden]{display:none}`, so `#pr-cv` rendered as a visible "Download CV"
  button while being set hidden — and with `cvUrl` empty it had no `href`,
  so it was a dead control on the public page. Fixed globally with
  `[hidden]{display:none !important}`; the print rule is more specific, so
  panels still expand.

## The constraint that turned out to be false

Every earlier note in this project — including the previous version of this
file — said no JavaScript could ever be executed here: no Node, no browser,
no package manager. **Firefox 154 is installed.** It had simply never been
looked for.

It runs headless and takes screenshots:

```
mkdir -p ~/ff-scratch/profile
timeout 150 firefox --headless --no-remote --new-instance \
  --profile ~/ff-scratch/profile \
  --window-size=1280,3000 \
  --screenshot ~/ff-scratch/out.png \
  "file:///home/varun/Desktop/ramkumar/index.html?selftest=1"
```

The scratch directory is disposable — create it fresh and delete it when
done; nothing depends on it persisting.

Three things to know about that command. Firefox here is a **snap**, so it
cannot see `/tmp` — the profile and the output path must both live under
`$HOME`. `--no-remote --new-instance` is required or it refuses with
"Firefox is already running"; if it says that anyway, `pkill -9 -f firefox`
and delete `<profile>/.parentlock`. The first run takes a while, so give it
a 150s timeout.

One more trap, learned the hard way: **`--screenshot` captures immediately
after the `load` event.** Anything a probe defers with `setTimeout` has not
happened yet and the picture comes back empty, which looks exactly like the
script failing to run. Do the work synchronously inside the `load` handler.

What this buys: the in-page self-test result, and a picture of the rendered
page at any width, in light or dark (`user_pref("ui.systemUsesDarkTheme", 1)`
in `<profile>/user.js`).

It also buys more than screenshots. Copy `index.html` to a scratch file and
append a `<script>` before `</body>` that calls internal functions directly
and prints results into a `<pre>` at the top of the body — that is how the
import validator, the render-error banner and the admin control strips were
all verified without a driver. Anything reachable from the page's top-level
scope (`enterAdmin`, `openEditor`, `importShapeProblems`, `showRenderError`,
`Storage`, `CONTENT`) can be exercised this way.

What it does not buy: genuine clicking. There is no geckodriver or Selenium
here, so real tab switching, search, export downloads and the full editing
flow still cannot be exercised end to end — those remain the user's job in
section 2 of the handoff.

**The point worth carrying forward:** the first screenshot ever taken of
this page showed two faults that 200+ text checks and five reviews had all
passed. Text checks ask "does this element exist?"; they cannot ask "does
anything put content into it?" Take the screenshot early.

## Then, to finish

- Scoped re-review of `ddd059f..afaa2fb` (the fix wave plus both decisions)
- Hand the user `docs/superpowers/plans/HANDOFF.md`. Section 2 is now about
  ten minutes; items 2, 7 and 8 are marked confirmed and skippable.

## Still unconfirmed by the user

- **The four stat tiles now read 55+ / 27 / 3 / 10.** He asked for real
  numbers rather than list counts, but has not seen the result. Handoff
  item 1 asks him to confirm all four.
- The three "Invited talks" entries: all three were derived from award
  records, not from a list of talks
- `Scopus ID: 12345166600`, `Total citations: 1038`, `h-index: 18` — these
  came from the original page, not from this rework, but the Scopus ID looks
  unusual and the figures will go stale
- The five generated "News" entries

## Files worth reading first

- `.superpowers/sdd/2026-09-21-faculty-profile-rework/progress.md` — the full
  ledger: every commit, every ruling, and what each ruling costs if wrong
- `docs/superpowers/specs/2026-09-21-faculty-profile-rework-design.md` — the design
- `docs/superpowers/plans/HANDOFF.md` — what the user actually needs to do
