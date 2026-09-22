# Your profile page — what to check before you trust it

This page was rebuilt from your old profile. Every piece of text, every
publication, every award, was carried over and checked by machine against
the original — that part is verified and solid.

**Update — the page has now been run in a real browser.** Earlier versions
of this document told you nothing about how the page *behaves* had ever been
tested, because the machine it was built on was believed to have no browser
on it. It turns out Firefox is installed. The page has now been loaded in it
and photographed, which immediately turned up two faults that months of
text-only checking had missed — a footer that printed a bare "©" with no year
or name, and a dead "Download CV" button that showed on your public page
despite being switched off in code. Both are fixed.

So the list below is shorter than it was. What is now confirmed working:
the page loads and fills itself in, the built-in self-test passes all 17 of
its checks, your photo loads, the footer is correct, the four number tiles
are correct, nothing overflows sideways on a phone-width screen, and dark
mode is readable.

What still needs **you** is everything that requires actually clicking:
switching tabs, the keyboard, search, print preview, downloading the
exports, and the whole editing flow. A browser can be told to open a page
and take a picture of it from a command line; it cannot be told to click a
button. That is the line. This should now take about ten minutes.

---

## 1. Run the built-in self-test first

**This has already been run and it passed — all 17 checks.** Please still
run it once yourself. It costs you thirty seconds and it is not redundant:
it ran here in a brand-new, empty browser profile, and yours has your own
saved content, your own settings and your own extensions, any of which can
change the result. If it passes for you too, that is the version that counts.

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

**Before anything else: export a backup.** Click "Admin" and set a password
— **write that password down somewhere safe.** The Export buttons are now
only visible once you're logged in, so if you lose the password you also
lose the only way to get a backup out of the page from inside it. Once
you're in, click "Export JSON" and save that file somewhere you'll find it
again. Item 10 below has you edit, reorder, delete and save real content —
do this backup first, before touching anything, so there's always a way back
to exactly where you started.

1. **Header and numbers.** At the top, check your name, title, and
   institution are right. The four number tiles should read **55+
   Publications, 27 Sponsored projects, 3 Patents, 10 Current scholars**.
   These are no longer counted from the lists further down the page — the
   lists are deliberately partial (the publications list says so itself:
   "a representative selection"), so counting them was publishing 15, 8, 3
   and 4, which contradicted your own bio on the same page. The four numbers
   above come from your bio ("over 55 peer-reviewed journal papers", "three
   patents"), your funding line ("across 27 projects") and your
   research-guidance line (3 + 3 + 3 + 1 ongoing = 10). **Please confirm all
   four are what you want published.** Because they're now stored rather
   than counted, they will need updating by hand as the real figures move —
   you can edit them in Admin mode like any other row.
2. **Photo.** *(Confirmed loading here.)* Your photo should load in the
   header. Worth a glance anyway — it is hotlinked from `home.iitm.ac.in`,
   so a network that blocks that host would show your initials in a plain
   circle instead. That fallback is correct behaviour, not a fault.
3. **All seven tabs.** Click through each one, in this order: About,
   Research, Group, Publications, Teaching, Professional activities,
   Contact. Confirm the web address in the bar updates to match (e.g. it
   should end in `#publications`), and that reloading the page keeps you on
   the same tab instead of bouncing back to About.
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
7. **Narrow window.** *(Confirmed here at 360 pixels — no sideways
   scrolling, the number tiles stack two-by-two and the tab strip scrolls.)*
   Skip unless you want to see it for yourself.
8. **Dark mode.** *(Confirmed here — readable.)* Skip unless you want to
   see it for yourself.
9. **Export — do this before the editing step below, even though you
    already made the backup at the top of this section.** You must be
    logged into Admin for the Export buttons to be visible. Click
    "Export JSON" and separately "Export HTML". Two files should download.
    Open the exported HTML file in a **private/incognito window** (or a
    completely different browser from the one you've been using) — not a
    normal tab in your regular browser. This matters: your regular browser
    may already have a copy of test edits saved in its storage, and the
    exported page's own startup code checks that storage first and would
    quietly overwrite the file's baked-in content with it — so a broken
    export could still look perfectly fine in a normal tab and you'd never
    know. A private window starts with no storage, so what you see there is
    genuinely what's inside the exported file. Confirm it's a complete,
    working copy of your page with no missing pieces — it should not depend
    on the original file at all.
10. **Editing.** Click the "Admin" button.
    - The first time, it will ask you to set a password — set one.
    - Edit one row of content (any row) and confirm the change shows on the
      page.
    - Reorder a row (move it up or down) and delete a different row.
    - Save your changes.
    - Reload the page and confirm all of those changes — the edit, the
      reorder, and the deletion — are still there.
    - When you're done testing, use Import to load the JSON backup you
      exported (in step 9, or at the very top of this section) and get your
      real content back, or just re-edit the rows back by hand.

---

## 3. Content needing your confirmation

Most of the page's content came straight from your existing page and is
already verified. A handful of entries were newly added while building this
page and are flagged here because their source is different from
everything else — please look them over.

**Already confirmed by you (2026-09-21) — no action needed:**

- The ten rows under "Current scholars" and "Alumni" (in the Group tab) are
  **counts by degree type, not individual names** — for example "Ph.D.
  scholars — 3 ongoing." These numbers come directly from a line in your own
  research-guidance text, so the counts themselves are accurate. Names were
  never available in the source material and were deliberately left out
  rather than guessed. You've already told me to keep these as counts, so
  no change is needed — this is just a record of that decision.
- The "Books" section that used to be on your page has been removed
  entirely, at your request. It never had any content in it to begin with.
- The fourth header tile reads **"Current scholars"**, not "Current
  students", at your request (2026-09-22). It matches the section heading in
  the Group tab, and it is strictly accurate: the 10 it counts includes a
  postdoctoral researcher, who is not a student.

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

## 4. What I could and could not check on my end

Being precise about this, because the earlier version of this section was
wrong in a way worth naming.

**Confirmed by actually running the page** (Firefox 154, headless, fresh
empty profile): it loads and fills itself in without errors; the self-test
passes 17 of 17; your photo loads; the footer reads "© 2026 Prof. P.
Ramkumar"; the four tiles read 55+, 27, 3, 10; all seven tabs are present
and only the open one shows; nothing overflows sideways at 360 pixels; dark
mode is legible.

**Still only checked as text** — written, reviewed, but never watched
working: clicking between tabs and the address bar following along, reload
landing you back on the same tab, the arrow keys, clicking a search result,
print preview unfolding every section, the two Export buttons actually
producing files, and the entire editing flow (password, edit, reorder,
delete, save, reload, import). Section 2 is still the first real test of
all of that.

**Why this matters more than it sounds.** For most of this project the
working assumption was that no code here could ever be executed, so every
check was a program reading the file as text. That assumption cost real
money twice. Once, a `</script>` sitting inside a *comment* silently cut
the page's main program in half — four separate reviews and 179 text checks
all passed it, because none of them were reading the file the way a browser
does. And the moment the page was finally opened in a browser, two more
faults were visible in the first screenshot: the empty footer and the dead
CV button. Both had passed every text check, because those checks asked
"does this element exist?" and never "does anything put content in it?"

The lesson is not that the text checks were bad — they caught a great deal
and they still guard against regressions. It is that they cannot see a
category of fault that one screenshot shows instantly. Anything in the
"still only checked as text" list above is in exactly that blind spot, so
please do treat those as "should work" rather than "confirmed working"
until you've clicked through them.
