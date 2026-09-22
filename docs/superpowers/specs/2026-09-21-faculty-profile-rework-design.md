# Faculty Profile Page Rework — Design

**Date:** 2026-09-21
**Subject:** `index.html` — public profile page for Prof. P. Ramkumar, Dept. of Mechanical Engineering, IIT Madras
**Status:** Approved design, pending implementation plan

## 1. Problem

The existing `index.html` is a 784-line single-file profile page with a blueprint/engineering-drawing theme, six tabbed sections, and a password-gated admin edit mode. Four problems motivate the rework:

1. **Content is trapped.** Admin edits persist through `window.storage`, which exists only inside a published Claude artifact. On any other host, edits silently do not save, and content already saved in an artifact cannot be extracted.
2. **Presentation and data are entangled.** Some content lives in the markup, some in a `defaults` object in script. Changing content means editing two places.
3. **The visual design is over-decorated.** Two competing loud accents (`#0000FF` blueprint blue, `#F2A900` copper), grid overlays, and dense panels compete with the content.
4. **Sections are missing.** No research group/students, news, talks, or downloadable CV.

The file also has no `<!doctype html>` and no `<head>` — it is a bare fragment, not a servable page.

## 2. Constraints

- **Hosting is undecided.** The page must work unchanged when opened from disk (`file://`), uploaded to IITM static hosting, or published as a Claude artifact. This constraint drives nearly every decision below.
- **No build step, no dependencies.** The page should outlive whoever maintains it and be publishable by copying one file.
- **Tabbed navigation is retained** by user preference, with its known drawbacks mitigated rather than accepted.

## 3. Approach

**Chosen: a single self-contained `index.html` with content as a data object and a pluggable storage adapter.**

Rejected alternatives:

- **Split files (`index.html` + `content.json` + `app.js` + `styles.css`).** Cleaner separation, but `fetch()` of a local JSON file is blocked under `file://`, so the page breaks when opened by double-click, and it cannot ship as a single artifact. It presumes a host that has not been chosen.
- **Static site generator (Astro / Eleventy).** Best long-term structure, but requires a Node toolchain and a rebuild for every publication added, and browser-based admin editing stops making sense. Disproportionate operational weight for one profile page.

The chosen approach is the only one that keeps the hosting decision open. If a host is later chosen, splitting into the second approach is mechanical.

## 4. Architecture

Single `index.html`, gaining a real `<!doctype html>` and `<head>` (meta viewport, title, description, Open Graph tags, font preconnect).

Five modules inside one `<script>`, in dependency order:

| Module | Responsibility | May not |
|---|---|---|
| `CONTENT` | All page data. The only thing edited when content changes. | — |
| `Storage` | Adapter selection and get/set. | Know about rendering |
| `render` | Pure `data -> DOM`. | Read storage or auth state |
| `router` | Hash to active tab, and back. | Mutate `CONTENT` |
| `admin` | Auth gate, editors, export/import. | Touch the DOM directly |

**The invariant that keeps this maintainable:** `render` never reads storage, and `admin` never manipulates DOM nodes itself — it mutates `CONTENT` and calls `render`. One data flow, one direction. Any bug is therefore either a data bug or a render bug, never both.

### 4.1 Storage adapters

A three-implementation interface, selected at runtime by feature detection, in priority order:

1. `artifactStorage` — uses `window.storage` when present (published artifact).
2. `localStorageAdapter` — uses `localStorage` when available (normal hosting, `file://`).
3. `readOnlyAdapter` — returns baked-in defaults, accepts no writes (private browsing, blocked storage).

Every read and write is wrapped in `try`/`catch`. A failed read returns the baked-in default rather than throwing; a failed write surfaces a visible error in admin mode rather than failing silently. Admin mode displays which adapter is active, so it is never ambiguous whether a save actually persisted.

## 5. Content model

Two row shapes are retained, deliberately. They cover every existing and new section, and refusing a third shape keeps the renderer small.

- **String arrays** — `expertise`, `reviewer`, and the research topic lists.
- **Object rows** `{primary, secondary, meta}` — everything else.

New sections map onto the object-row shape:

| Section | `primary` | `secondary` | `meta` |
|---|---|---|---|
| `studentsCurrent` | Name | Degree and research topic | Years |
| `studentsAlumni` | Name | Degree, topic, current placement | Years |
| `news` | Headline | Detail | ISO date (`YYYY-MM-DD`) |
| `talks` | Talk title | Venue / conference | Date |

`news` is sorted reverse-chronologically by `meta` at render time and formatted for display; the ISO form is what is stored so sorting is reliable.

`CONTENT` is serialized as JSON in a `<script type="application/json" id="pr-content">` block (see section 10.2), parsed once at startup. Scalars move from the markup into `CONTENT.profile`: `name`, `title`, `dept`, `institution`, `email`, `phone`, `lab`, `room`, `bio`, `photo`, `cvUrl`, and a `links` array.

## 6. Visual system

Direction: **modern institutional** — a clean contemporary academic profile, card-based, content-first.

- **Typography.** IBM Plex Sans throughout; hierarchy carried by weight and scale, not color. IBM Plex Mono retained only for data-ish content (dates, patent numbers, identifiers).
- **Color.** Neutral near-white surface, dark slate ink, and a single deep academic blue accent, pinned to `#1B3A6B` (with `#2E5AA8` for hover/active states). The existing blueprint blue and copper are two loud accents competing; copper is demoted to rare emphasis. All colors defined as custom properties on `:root`, redefined under `prefers-color-scheme: dark`.
- **Cards.** Light border, minimal shadow, generous padding. Depth by restraint.
- **Stat tiles.** Publications, sponsored projects, patents, and current students. **Superseded 2026-09-22 (ruling R22).** This clause originally required values "computed from `CONTENT` array lengths at render time, never hardcoded, so they cannot go stale". That was a defect in this spec, not in any implementation of it: the arrays are *curated subsets*, not inventories — `prose.pubIntro` states the publications list is "a representative selection", the grants list holds 8 of the 27 that `prose.researchFunding` cites, and `sections.studentsCurrent` holds 4 category-aggregate rows covering 10 people. Counting them published 15 / 8 / 3 / 4 directly above the professor's own bio saying 55+, three patents, 27 projects and 10 ongoing students. Four task reviews and a self-test assertion all certified that as correct, because they were checking conformance to this line.

  **Current requirement:** tiles read stored, user-confirmed figures from `CONTENT.sections.stats`, sourced from his own prose and editable in admin mode. `renderStats` takes its rows as an argument and has no access to the content arrays, so counting cannot be reintroduced by accident. The accepted cost is that the figures need updating by hand as the real numbers move.
- **Responsive.** Below 720px the tab bar becomes a horizontally scrollable strip, cards stack to one column, and the contact title-block reflows from a two-column table to a list. 16px side gutter, no horizontal page scroll.

## 7. Tabs: retained, with mitigations

Tabs hide content from in-page search and from printing. Both are mitigated rather than accepted:

- **Deep linking.** Tab state syncs with `location.hash` in both directions, so `#publications` opens the right tab and survives refresh and back/forward.
- **Printing.** A print stylesheet expands every section and removes chrome, so the page prints as a complete CV regardless of which tab is active.
- **Searching.** A search box indexes all content across all tabs, and selecting a result switches to the owning tab and scrolls to the match.
- **Accessibility.** Tabs use the ARIA tab pattern with correct roles and arrow-key navigation.

## 8. Editing system

**Authentication.** No password appears in the source. On first admin use the user *sets* a password; only its SHA-256 hash is persisted. The UI states plainly that this gate is a convenience against accidental edits, not a security control, because any client-side check is bypassable by viewing source. This replaces the current hardcoded default of `tribology2026`.

**Editing UX.** Clicking Edit on a row replaces it with labelled `<input>` fields for `primary`, `secondary`, and `meta`, rather than `contenteditable` spans, which lose formatting and offer no undo. Rows gain up/down reordering and delete-with-confirm. A dirty-state indicator and explicit Save / Discard replace the current implicit model.

**Export and import.** Two export actions — download a complete `index.html` with current content serialized in, and download `content.json`. Import accepts a previously exported `content.json`, so exports round-trip. This is the feature that guarantees content can never again be trapped by a hosting choice.

## 9. Content sourcing

Existing content is carried across faithfully as the baseline. On top of that:

- The user will supply corrections to existing entries.
- The user will supply source material for `studentsCurrent`, `studentsAlumni`, `news`, and `talks`, none of which exist in the current file. Where material is not supplied, these sections are scaffolded with whatever is publicly verifiable and left ready to populate through admin mode.
- A verification pass reconciles existing content against the IITM homepage, Google Scholar, and ORCID, flagging disagreements for the user to adjudicate rather than silently overwriting.

**Open item:** the user's corrections and new-section material have not yet been provided. Implementation of the page structure does not depend on them; populating content does. Sections are built against the content model and filled when material arrives.

## 10. Testing

### 10.1 Environment constraint (discovered 2026-09-21)

This machine has **no JavaScript runtime**: no Node, Deno, QuickJS, or `d8`; no `pip`, so no `playwright`, `selenium`, or `dukpy`; and headless Firefox exits without producing a screenshot. Python 3.14 is available.

Consequently the page's JavaScript **cannot be executed during development**. Any plan claiming automated coverage of the JS would be claiming coverage that does not exist. Testing is therefore split into two honestly-labelled tiers.

### 10.2 Tier 1 — automated, runs here (Python, stdlib only)

`tests/check.py` validates everything reachable without executing JS. This is the TDD loop: tests written first, run with `python3 tests/check.py`, watched to fail, then made to pass.

To make this tier meaningful, **`CONTENT` is stored in a `<script type="application/json" id="pr-content">` block** rather than as a JavaScript object literal. This makes the real content parseable by the test suite, makes export a direct serialize rather than code generation, and keeps content inspectable without splitting the file.

Tier 1 covers:

- **Content schema.** The JSON block parses; every section key is present; every object row has exactly `primary`, `secondary`, `meta`; string-array sections contain only strings; `news` dates match `YYYY-MM-DD` and sort correctly; `profile` has every required scalar.
- **Content preservation.** Every entry present in the original `index.html` (captured at commit `01bb885`) is still present after the rework. This is the regression guard against silent content loss.
- **Structural integrity.** Every `data-page` value on a tab button has exactly one matching `<section>`; every element `id` referenced from the script exists in the markup; the document has a doctype, `<html lang>`, charset, and viewport.
- **Serialization safety.** No content string contains a raw `</script>`; the JSON block is checked for the escaped form.
- **Secret absence.** No password literal appears anywhere in the source. Specifically asserts `tribology2026` is absent.
- **Token integrity.** Every CSS custom property referenced via `var(--x)` is defined on `:root`, and every one defined for light mode has a dark-mode counterpart.

### 10.3 Tier 2 — in-browser, requires the user

`?selftest=1` runs in-page assertions over the pure JS logic named in section 11 as risky: export round-trip and `</script>` escaping, storage adapter selection and fallback, search indexing, and hash-routing agreement in both directions. Results render as pass/fail text in the page.

**This tier cannot be run by the implementer on this machine.** It is run by opening `index.html?selftest=1` in Firefox. The plan's final task is a handoff asking the user to run it and report results, and no work is described as verified until they do.

Visual, responsive, print, and accessibility behaviour is likewise verified by the user in a browser against an explicit checklist, not asserted by the implementer.

## 11. Known risks

1. **Export serialization corruption.** A content string containing `</script>` would terminate the script block early and produce a broken exported file. Escaping is required and is covered by a self-test.
2. **Hotlinked photograph.** The avatar loads from `home.iitm.ac.in`. If the file moves or the host blocks hotlinking, it breaks. Mitigation: an initials fallback on image error. Optionally inline as base64 for a fully self-contained file, at a cost in file size.
3. **Storage silently unavailable.** Private browsing or blocked site data can make writes fail. Mitigation: admin mode displays the active adapter and surfaces write failures visibly.

## 12. Success criteria

- The single file renders correctly opened from disk, from static hosting, and as a published artifact.
- All existing content survives the rework with no loss.
- `#publications` and every other section deep-link correctly.
- The page prints as a complete CV with all sections expanded.
- Admin edits can be exported and re-imported without loss.
- No password appears anywhere in the source.
- Stat tile numbers match the figures stated in the professor's own prose, and are **not** equal to the lengths of the curated lists below them. (Superseded 2026-09-22 — this criterion previously read "match actual content counts", which is what made the defect above pass every review. See ruling R22.)
- The page has no horizontal scroll at 360px width.
- `?selftest=1` reports all assertions passing.
