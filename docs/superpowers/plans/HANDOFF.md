# Your profile page — what to check before you trust it

This page was rebuilt from your old profile. Every piece of text, every
publication, every award, was carried over and checked by machine against
the original — that part is verified and solid.

What could **not** be checked is anything that only happens when the page
runs in an actual browser: clicking tabs, searching, editing your own
content, saving, exporting. The computer used to build this page cannot run
a web browser or execute the page's code at all, so none of that has ever
actually been switched on and watched. This document is how you do that
final check yourself. It should take about fifteen minutes.

---

## 1. Run the built-in self-test first

Open the page with `?selftest=1` added to the end of the address, for
example:

```
file:///home/varun/Desktop/ramkumar/index.html?selftest=1
```

Please use **Firefox** for this.

A box will appear at the top of the page listing a series of lines, each
starting with `PASS` or `FAIL`, followed by a heading that says either:

- **"All N self-tests passed"** — everything the page's own code can check
  about itself came back clean, or
- **"N of M self-tests FAILED"** — something is broken, and each `FAIL`
  line names what.

Please copy the full contents of that box (or a screenshot) back to me,
whichever line it ends on. If anything says FAIL, send me the exact text —
don't paraphrase it, the wording tells me exactly which check tripped.

---

## 2. Then check the page itself, step by step

Open the page normally this time (no `?selftest=1`) and work through this
list. For each item, a quick "yes, that's right" or "no, here's what I saw"
is all I need.

1. **Header and numbers.** At the top, check your name, title, and
   institution are right, and that the four number tiles (Publications,
   Sponsored projects, Patents, Current students) show numbers that look
   plausible to you.
2. **Photo.** Your photo should load in the header. If it doesn't load (a
   broken image, or your network blocks the source site), you should see
   your initials in a plain circle instead — not a broken-image icon.
3. **All seven tabs.** Click through each one: About, Research,
   Publications, Teaching, Group, Activities, Contact. Confirm the web
   address in the bar updates to match (e.g. it should end in
   `#publications`), and that reloading the page keeps you on the same tab
   instead of bouncing back to About.
4. **Keyboard tab switching.** Click into the row of tab buttons, then use
   the left/right arrow keys. The highlighted tab and the panel below
   should move together.
5. **Search.** Type "hip implant" into the search box. Confirm a result
   appears, and clicking it jumps to the right tab and scrolls to the right
   entry.
6. **Print preview.** Open your browser's print preview (Ctrl+P / Cmd+P).
   Confirm you can see **every** section of the page in the preview, not
   just whichever tab happened to be open when you printed — print view is
   supposed to unfold everything onto one long page.
7. **Narrow window.** Shrink your browser window (or use your browser's
   mobile/responsive preview) down to about 360 pixels wide — roughly a
   phone screen. Confirm nothing forces you to scroll sideways.
8. **Dark mode.** If your operating system has a dark mode, switch to it
   (or back to light mode, whichever you're not currently in) and reopen
   the page. Confirm the text stays easy to read against the background.
9. **Editing.** Click the "Admin" button.
   - The first time, it will ask you to set a password — set one.
   - Edit one row of content (any row) and confirm the change shows on the
     page.
   - Reorder a row (move it up or down) and delete a different row.
   - Save your changes.
   - Reload the page and confirm all of those changes — the edit, the
     reorder, and the deletion — are still there.
   - (If you want to undo your test edits afterwards, use Import — see
     below — with a JSON file you exported before you started, or just
     re-edit the rows back.)
10. **Export.** Click "Export JSON" and separately "Export HTML". Two files
    should download. Open the exported HTML file on its own (double-click
    it, or drag it into a browser tab) and confirm it's a complete, working
    copy of your page with no missing pieces — it should not depend on the
    original file at all.

---

## 3. Content needing your confirmation

Most of the page's content came straight from your existing page and is
already verified. A handful of entries were newly added while building this
page and are flagged here because their source is different from
everything else — please look them over.

**Already confirmed by you (2026-09-21) — no action needed:**

- The ten rows under "Current students" and "Alumni" (in the Group tab) are
  **counts by degree type, not individual names** — for example "Ph.D.
  scholars — 3 ongoing." These numbers come directly from a line in your own
  research-guidance text, so the counts themselves are accurate. Names were
  never available in the source material and were deliberately left out
  rather than guessed. You've already told me to keep these as counts, so
  no change is needed — this is just a record of that decision.
- The "Books" section that used to be on your page has been removed
  entirely, at your request. It never had any content in it to begin with.

**Still needs your decision:**

- **Three entries under "Invited talks" (Activities tab).** All three were
  built from your award records, because a talk and an award are usually
  the same event. All three are actually award entries — a **Best Paper
  award**, a **Best Poster award**, and a **Best Presentation award** — not
  plain invited talks, so it's your call whether any of them belong in the
  "Invited talks" list at all, or whether they should move somewhere else
  (e.g. purely under Awards) or be relabeled. Please check all three, not
  just the ones that look most obviously award-like. The three are:
  1. "Bio-tribological Performance of Heat Treated and DLC Coated Ti6Al4V…" —
     ITRS 2021, Chennai (Best Paper Award)
  2. "Analysis on Hydrogen Uptake into Steel from Lubricated Sliding
     Contact…" — ICRIDME 2018, NIT Meghalaya (Best Poster Presentation
     Award)
  3. "Mission of Tribology" — IMechE, UK (Best Presentation Award)
- **Five entries in the "News" list (About tab).** These weren't on your
  original page at all — they were generated from four recent publications
  and one grant that were already in your data, on the reasoning that a new
  publication or a new grant is newsworthy. Please check the wording reads
  the way you'd want it announced. Their dates are written exactly as
  precisely as they were known and no more: four are dated just "2026" (no
  month or day was available), and the grant is dated "February 2023" (year
  and month only — no day was invented).
- **Scopus ID, citation count, and h-index** (shown in the Publications
  tab: "Total citations: 1038 · h-index: 18 · Scopus ID: 12345166600").
  These numbers came from your **original** page as-is — they were not
  looked up or changed during this rework. Two things worth flagging: the
  Scopus ID has an unusual number of digits and is worth double-checking
  against your actual Scopus profile, and all three numbers (citations,
  h-index, and the ID) will naturally drift out of date over time since
  they're stored as fixed text rather than pulled live from anywhere.

---

## 4. What I could not check on my end

I want to be upfront about the limits of what's been verified so far. The
computer this page was built on has no way to run JavaScript or open a
browser — it can only read and check text. That means everything about how
the page *behaves* — tabs switching, search working, the editor saving
changes, exports producing a working file — has been written but has never
once actually been run or watched happen. Sections 1 and 2 above are the
first real test of any of it. Until you've gone through them and reported
back, please treat the interactive features as "should work" rather than
"confirmed working."
