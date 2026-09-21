# Faculty Profile Page Rework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `index.html` as a single self-contained, dependency-free faculty profile page with a modern-institutional design, a JSON content layer, portable storage, and an admin edit mode whose content can always be exported.

**Architecture:** One `index.html` with no build step and no runtime dependencies. All content lives in a `<script type="application/json" id="pr-content">` block parsed once at startup. Five JS modules in strict dependency order (`Storage`, `render`, `router`, `search`, `admin`) with a one-way data flow: `admin` mutates the content object and calls `render`; `render` never reads storage; `router` never mutates content.

**Tech Stack:** HTML5, CSS custom properties, vanilla ES2020 JavaScript, Web Crypto (`crypto.subtle`) for password hashing. Tests: Python 3 standard library only.

**Spec:** `docs/superpowers/specs/2026-09-21-faculty-profile-rework-design.md`

## Global Constraints

- **Single file.** Everything ships in `index.html`. No build step, no bundler, no runtime dependency, no `fetch()` of sibling files. The page must work identically from `file://`, from static hosting, and as a published Claude artifact.
- **No JavaScript runtime exists on this machine.** Node, Deno, QuickJS and `pip` are all absent; headless Firefox produces no output. Tier 1 tests (Python) are the only tests the implementer can run. Tier 2 tests (`?selftest=1`) are run by the user in Firefox. **Never describe Tier 2 behaviour as verified.**
- **No secrets in source.** The string `tribology2026` must not appear anywhere. Passwords are set by the user at runtime; only a SHA-256 hash is persisted.
- **Accent colour:** `#1B3A6B`; hover/active `#2E5AA8`. Single accent; copper is emphasis-only.
- **Mobile breakpoint:** 720px. No horizontal scroll at 360px width. 16px side gutter.
- **Typography:** IBM Plex Sans for all text; IBM Plex Mono only for dates, identifiers and patent numbers.
- **Content model:** exactly two row shapes. String arrays, and objects with exactly the keys `primary`, `secondary`, `meta`. Do not invent a third shape.
- **Dark mode:** every colour token defined on `:root` must have a `prefers-color-scheme: dark` counterpart.
- **Commit after every task.** Tests must pass before committing.

## Content keys (authoritative)

String-array sections (19 total content keys, plus `books` which is new):

    expertise, automotive, windTurbine, gearbox, wearModelling, surfaceEng, reviewer

Object-row sections (`{primary, secondary, meta}`):

    education, facilities, grants, publications, books, bookChapters, patents,
    courses, positions, awards, memberships, adminRoles, academicServices

New in this rework:

    studentsCurrent, studentsAlumni, news, talks

**Known pre-existing bug to fix:** the current file calls `prAddRow('books')` and renders into a `prBooks` container, but `books` is absent from the `defaults` object, so the "Edited books" section is permanently empty. Task 3 adds the `books` key.

## File Structure

| File | Responsibility |
|---|---|
| `index.html` | The entire shipped page: head, styles, content JSON, five JS modules. |
| `tests/check.py` | Tier 1 automated suite. Stdlib only. Run with `python3 tests/check.py`. |
| `tests/baseline_strings.json` | Every content string from the pre-rework page. The regression guard against silent content loss. |
| `tests/extract_baseline.py` | One-shot generator for the above, reading the original file from git. |
| `docs/superpowers/specs/...` | The approved design. |

---

### Task 1: Tier 1 test harness and content baseline

Establishes the only automated feedback loop available. Nothing else can be trusted until this exists.

**Files:**
- Create: `tests/extract_baseline.py`
- Create: `tests/baseline_strings.json` (generated)
- Create: `tests/check.py`

**Interfaces:**
- Consumes: the pre-rework `index.html` at git commit `01bb885`.
- Produces: `check.py` exposing `check(name, condition, detail="")` and `section(title)`; exits non-zero if any check fails. Later tasks append checks to this file.

- [ ] **Step 1: Write the baseline extractor**

Create `tests/extract_baseline.py`:

```python
"""Extract every content string from the pre-rework index.html.

Reads the original from git so it cannot be affected by the rework in
progress. Produces tests/baseline_strings.json, used by check.py to prove
no content was silently dropped.
"""
import html
import json
import pathlib
import re
import subprocess

BASELINE_COMMIT = "01bb885"
OUT = pathlib.Path(__file__).parent / "baseline_strings.json"

original = subprocess.run(
    ["git", "show", f"{BASELINE_COMMIT}:index.html"],
    capture_output=True, text=True, check=True,
).stdout

strings = set()


def decode_js(text):
    """Turn a JS single-quoted literal's body into the text it represents."""
    text = text.replace("\\'", "'").replace('\\"', '"')
    text = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)
    return text.replace("\\\\", "\\")


# Object rows: primary:'...', secondary:'...', meta:'...'
for field in ("primary", "secondary", "meta"):
    for m in re.finditer(rf"{field}\s*:\s*'((?:[^'\\]|\\.)*)'", original):
        value = decode_js(m.group(1)).strip()
        if value:
            strings.add(value)

# String arrays: key: ['a','b','c'] -- single line only. [^\]\n]* rather than
# [^\]]* because the latter spans newlines and re-swallows every multi-line
# object array, re-extracting its values through this weaker path.
for m in re.finditer(r"^\s{4}(\w+)\s*:\s*\[([^\]\n]*)\]", original, re.M):
    for sm in re.finditer(r"'((?:[^'\\]|\\.)*)'", m.group(2)):
        value = decode_js(sm.group(1)).strip()
        if value:
            strings.add(value)

# Prose that lives ONLY in the markup, carried on data-key attributes: the
# biography paragraphs, funding total, citation metrics, contact block and
# header fields. Omitting these leaves the largest prose on the page with no
# regression guard at all.
for m in re.finditer(r'data-key="([\w]+)"[^>]*>(.*?)</', original, re.S):
    text = re.sub(r"<[^>]+>", " ", m.group(2))
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        strings.add(text)

OUT.write_text(json.dumps(sorted(strings), indent=1, ensure_ascii=False))
print(f"extracted {len(strings)} baseline strings -> {OUT}")
```

- [ ] **Step 2: Run the extractor**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/extract_baseline.py
```

Expected: prints a count well above 100 and writes `tests/baseline_strings.json`. Open the file and spot-check that publication titles and grant names are present. If the count is under 100 the regexes missed a shape — fix before continuing, because this file is the safety net for every later task.

- [ ] **Step 3: Write the harness with its first failing check**

Create `tests/check.py`:

```python
"""Tier 1 checks: everything verifiable without executing JavaScript.

This machine has no JS runtime, so these checks cover structure, content
and invariants only. Behavioural JS coverage lives in index.html?selftest=1
and must be run in a browser by a human.
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

_failures = []


def norm(text):
    """Fold the differences that are not content differences.

    Both sides of the preservation check pass through this, so folding cannot
    hide a dropped entry -- it only stops a curly apostrophe or an HTML entity
    being reported as lost content.
    """
    text = html.unescape(text)
    for curly, plain in (("\u2019", "'"), ("\u2018", "'"),
                         ("\u201c", '"'), ("\u201d", '"')):
        text = text.replace(curly, plain)
    return re.sub(r"\s+", " ", text).strip().casefold()


def section(title):
    print(f"\n-- {title}")


def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f"\n        {detail}" if detail else ""))
        _failures.append(name)


def content_json():
    """The parsed <script type="application/json" id="pr-content"> block."""
    m = re.search(
        r'<script[^>]+id="pr-content"[^>]*>(.*?)</script>', HTML, re.S
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


section("document shell")
check("has doctype", HTML.lstrip().lower().startswith("<!doctype html>"))
check("has lang attribute", re.search(r"<html[^>]+lang=", HTML) is not None)
check("has charset", re.search(r'<meta[^>]+charset=', HTML, re.I) is not None)
check("has viewport", 'name="viewport"' in HTML)

section("content block")
data = content_json()
check("content JSON block exists and parses", data is not None)

if _failures:
    print(f"\n{len(_failures)} FAILED: " + ", ".join(_failures))
    sys.exit(1)
print("\nall checks passed")
```

- [ ] **Step 4: Run it and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on all four shell checks and on the content block, because `index.html` is still the old fragment with no doctype. This failure is the point — it proves the harness reads the real file.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add tests/
git commit -m "test: add Tier 1 Python harness and pre-rework content baseline"
```

---

### Task 2: Page shell, design tokens, and empty sections

Replaces the bare fragment with a real document and the full token system. No content yet.

**Files:**
- Modify: `index.html` (full replacement of the shell; keep the old body markup temporarily below a marker comment so Task 3 can migrate from it)
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `check()` / `section()` from Task 1.
- Produces: CSS custom properties on `:root` — `--surface`, `--surface-raised`, `--ink`, `--ink-muted`, `--line`, `--accent`, `--accent-hover`, `--emphasis`. A `<script type="application/json" id="pr-content">` block containing `{"profile": {...}, "links": [...], "sections": {}}`. Tab buttons carrying `data-page`, and one `<section data-page="...">` per tab.

- [ ] **Step 1: Write the failing checks**

Append to `tests/check.py`, immediately before the `if _failures:` block:

```python
section("design tokens")
root_block = re.search(r":root\s*\{([^}]*)\}", HTML, re.S)
root_css = root_block.group(1) if root_block else ""
REQUIRED_TOKENS = [
    "--surface", "--surface-raised", "--ink", "--ink-muted",
    "--line", "--accent", "--accent-hover", "--emphasis",
]
for token in REQUIRED_TOKENS:
    check(f"{token} defined on :root", f"{token}:" in root_css.replace(" ", ""))

check("accent is the pinned value", "#1B3A6B" in root_css)

dark_block = re.search(
    r"prefers-color-scheme:\s*dark[^{]*\{(.*?)\n\s*\}\s*\n", HTML, re.S
)
dark_css = dark_block.group(1) if dark_block else ""
for token in REQUIRED_TOKENS:
    check(f"{token} has a dark-mode value", f"{token}:" in dark_css.replace(" ", ""))

used = set(re.findall(r"var\(\s*(--[\w-]+)", HTML))
defined = set(re.findall(r"(--[\w-]+)\s*:", root_css))
check("every var() used is defined on :root", used <= defined,
      f"undefined: {sorted(used - defined)}")

section("tab wiring")
tabs = set(re.findall(r'<button[^>]+data-page="([\w-]+)"', HTML))
panels = set(re.findall(r'<section[^>]+data-page="([\w-]+)"', HTML))
check("at least six tabs", len(tabs) >= 6, f"found {sorted(tabs)}")
check("every tab has exactly one panel", tabs == panels,
      f"tabs-only: {sorted(tabs - panels)}  panels-only: {sorted(panels - tabs)}")

section("no secrets")
check("default password absent", "tribology2026" not in HTML)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on every token check and on `default password absent`, since the old file still contains the hardcoded password.

- [ ] **Step 3: Build the shell**

Replace `index.html` with a document in this exact order: doctype, `<html lang="en">`, head (charset, viewport, title, description, Open Graph tags, Google Fonts preconnect and the IBM Plex stylesheet link), `<style>`, body containing header / nav / main with one empty `<section data-page>` per tab / footer, then the JSON content block, then `<script>`.

Token block:

```css
:root{
  --surface:#FFFFFF;
  --surface-raised:#F7F9FC;
  --ink:#141A22;
  --ink-muted:#5A6672;
  --line:#E2E7EE;
  --accent:#1B3A6B;
  --accent-hover:#2E5AA8;
  --emphasis:#B8791A;
  --radius:8px;
  --gutter:16px;
  --maxw:1080px;
}
@media (prefers-color-scheme: dark){
  :root{
    --surface:#0F1419;
    --surface-raised:#171E26;
    --ink:#E8EDF3;
    --ink-muted:#9AA7B4;
    --line:#252F3A;
    --accent:#7FA6DE;
    --accent-hover:#A3C0EA;
    --emphasis:#E0A84B;
  }
}
body{background:var(--surface); color:var(--ink); margin:0;
     font-family:'IBM Plex Sans',system-ui,sans-serif; line-height:1.6;}
```

Tabs are `<button data-page="about" role="tab">` inside `<nav role="tablist">`; panels are `<section data-page="about" role="tabpanel">`. Six tabs: `about`, `research`, `publications`, `teaching`, `activities`, `contact`.

Seed the content block with the profile scalars only:

```html
<script type="application/json" id="pr-content">
{
  "profile": {
    "name": "Prof. P. Ramkumar",
    "title": "Professor, Department of Mechanical Engineering",
    "institution": "Indian Institute of Technology Madras",
    "dept": "Machine Design Section",
    "lab": "Advanced Tribology Research Lab (ATRL)",
    "room": "Machine Design Section",
    "email": "ramkumar@iitm.ac.in",
    "phone": "+91 98402 74487",
    "photo": "https://home.iitm.ac.in/ramkumar/assets/img/ramkumar.jpg",
    "cvUrl": "",
    "bio": ""
  },
  "links": [
    {"label": "Personal homepage", "url": "https://home.iitm.ac.in/ramkumar/"},
    {"label": "Google Scholar", "url": "https://scholar.google.com/citations?user=KJuZiiEAAAAJ"},
    {"label": "ResearchGate", "url": "https://www.researchgate.net/profile/Penchaliah-Ramkumar"},
    {"label": "ORCID", "url": "https://orcid.org/0000-0002-2816-9145"}
  ],
  "prose": {
    "bio": [],
    "researchIntro": "",
    "researchGuidance": "",
    "researchFunding": "",
    "pubIntro": "",
    "pubMetrics": "",
    "contactBlock": ""
  },
  "sections": {}
}
</script>
```

`prose` holds the narrative blocks that in the old page lived only in the
markup on `data-key` attributes — the biography paragraphs, the research and
publication introductions, the funding total, the citation metrics and the
contact block. They are content, so they belong in the content object where
they can be edited and exported like everything else. `bio` is an array of
paragraphs; the rest are single strings.

Keep the old markup and `defaults` object at the bottom of the file inside `<!-- LEGACY-START -->` / `<!-- LEGACY-END -->` comments so Task 3 can migrate content from it. **Delete the hardcoded password line now** — it is the only thing that must not survive this task.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS on shell, tokens, tab wiring, no-secrets, and the content block parsing.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: real document shell, design tokens, and tab scaffolding"
```

---

### Task 3: Migrate all content into the JSON block

The riskiest task for data loss. The baseline guard exists precisely for this.

**Files:**
- Modify: `index.html` (populate `sections`, delete the legacy block)
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `content_json()` from Task 1; legacy markup from Task 2.
- Produces: `CONTENT.sections` populated with all 20 keys listed in "Content keys" above. `news` rows carry ISO `YYYY-MM-DD` in `meta`.

- [ ] **Step 1: Write the failing checks**

Append to `tests/check.py` before the `if _failures:` block:

```python
section("content schema")
STRING_ARRAY_KEYS = [
    "expertise", "automotive", "windTurbine", "gearbox",
    "wearModelling", "surfaceEng", "reviewer",
]
ROW_KEYS = [
    "education", "facilities", "grants", "publications", "books",
    "bookChapters", "patents", "courses", "positions", "awards",
    "memberships", "adminRoles", "academicServices",
    "studentsCurrent", "studentsAlumni", "news", "talks",
]
sections_data = (data or {}).get("sections", {})

for key in STRING_ARRAY_KEYS:
    values = sections_data.get(key)
    check(f"{key} is a list of strings",
          isinstance(values, list) and all(isinstance(v, str) for v in values))

for key in ROW_KEYS:
    rows = sections_data.get(key)
    ok = isinstance(rows, list) and all(
        isinstance(r, dict) and set(r) == {"primary", "secondary", "meta"}
        for r in rows
    )
    check(f"{key} rows have exactly primary/secondary/meta", ok)

check("books is populated (pre-existing bug fixed)",
      len(sections_data.get("books") or []) > 0)

news = sections_data.get("news") or []
check("every news date is ISO YYYY-MM-DD",
      all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", r.get("meta", "")) for r in news))

section("prose")
prose = (data or {}).get("prose", {})
check("bio is a non-empty list of paragraphs",
      isinstance(prose.get("bio"), list) and len(prose["bio"]) >= 4)
for field in ("researchIntro", "researchGuidance", "researchFunding",
              "pubIntro", "pubMetrics", "contactBlock"):
    check(f"prose.{field} is non-empty",
          isinstance(prose.get(field), str) and prose[field].strip() != "")

section("profile scalars")
profile = (data or {}).get("profile", {})
for field in ("name", "title", "institution", "email", "phone", "photo"):
    check(f"profile.{field} is non-empty",
          isinstance(profile.get(field), str) and profile[field].strip() != "")

section("content preservation")
baseline = json.loads(
    (ROOT / "tests" / "baseline_strings.json").read_text(encoding="utf-8")
)
blob = norm(json.dumps(data, ensure_ascii=False))
missing = [s for s in baseline if norm(s) not in blob]
check(f"all {len(baseline)} baseline strings survived the rework",
      not missing,
      f"{len(missing)} missing, first five: {missing[:5]}")

section("serialization safety")
check("no raw </script> in content", "</script>" not in blob.lower())
check("legacy block removed", "LEGACY-START" not in HTML)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on every schema key (sections is `{}`), on `books is populated`, and on content preservation with a large missing count.

- [ ] **Step 3: Migrate the content**

Transcribe every key from the legacy `defaults` object into `CONTENT.sections`, preserving order and wording exactly.

Then migrate the prose. In the legacy file this text lives in the markup on `data-key` attributes, not in `defaults`, which is why it is easy to lose. Map it as follows, converting HTML entities (`&middot;`, `&#8377;`) to the characters they represent and dropping the `<br>` tags in favour of real line breaks:

| Legacy `data-key` | Goes to |
|---|---|
| `about_bio1` … `about_bio4` | `prose.bio` (array of four paragraphs, in order) |
| `research_intro` | `prose.researchIntro` |
| `research_guidance` | `prose.researchGuidance` |
| `research_funding_total` | `prose.researchFunding` |
| `pub_intro` | `prose.pubIntro` |
| `pub_metrics` | `prose.pubMetrics` |
| `contact_block` | `prose.contactBlock` |
| `header_name`, `header_title`, `header_dept` | already in `profile`; confirm they match |
| `tb_lab`, `tb_room`, `tb_phone`, `tb_email` | already in `profile`; confirm they match |

Then:

- Add the missing `books` key. Populate it from the legacy "Edited books" section heading; if the legacy file has no data for it (it does not), seed it with the edited volumes the professor is known to have and mark the section for user confirmation in the handoff. Do not leave it empty — an empty array fails the check by design, forcing the question to be asked rather than forgotten.
- Add `studentsCurrent`, `studentsAlumni`, `news`, `talks`. The user has not yet supplied this material. Seed each with rows that are verifiable from the existing content — for example, `news` entries derived from the 2026 publications and the SERB grant, and `talks` from the recorded award presentations — and flag every seeded row in the handoff for confirmation. Use ISO dates in `news.meta`.
- Delete the entire `<!-- LEGACY-START -->` … `<!-- LEGACY-END -->` block.

Any string containing `</script>` must be written as `<\/script>` in the JSON.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS on all schema, profile, preservation and serialization checks. **If any baseline string is reported missing, restore it — do not adjust the baseline file to make the check pass.**

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: migrate all content to JSON block, add missing books key"
```

---

### Task 4: The render module

Pure `data -> DOM`. This module must not read storage or know whether admin mode is on; Task 8 layers editing on top by re-rendering, not by branching inside here.

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `CONTENT` parsed from the JSON block.
- Produces:
  - `renderTags(hostId, values)` — `values: string[]`, renders `<span class="tag">` children.
  - `renderRows(hostId, rows, variant)` — `rows: {primary,secondary,meta}[]`, `variant: "list" | "timeline"`.
  - `renderStats()` — fills `#pr-stats` from array lengths.
  - `renderAll()` — calls every renderer. **Every later module calls `renderAll()` to refresh; nothing else mutates section DOM.**

- [ ] **Step 1: Write the failing checks**

Append to `tests/check.py`:

```python
section("render wiring")
host_ids = set(re.findall(r'id="(pr-sec-[\w-]+)"', HTML))
# The four new-section keys get their hosts in Task 11, not here.
NEW_SECTION_KEYS = {"studentsCurrent", "studentsAlumni", "news", "talks"}
all_keys = (set(STRING_ARRAY_KEYS) | set(ROW_KEYS)) - NEW_SECTION_KEYS
expected_hosts = {f"pr-sec-{k}" for k in all_keys}
check("every content key has a render host element",
      expected_hosts <= host_ids,
      f"missing hosts: {sorted(expected_hosts - host_ids)}")

check("renderAll is defined", "function renderAll" in HTML)
check("renderProse is defined", "function renderProse" in HTML)
for host in ("pr-bio", "pr-research-intro", "pr-research-guidance",
             "pr-research-funding", "pr-pub-intro", "pr-pub-metrics",
             "pr-contact-block"):
    check(f"{host} host exists", f'id="{host}"' in HTML)
check("stats host exists", 'id="pr-stats"' in HTML)
check("stat counts are not hardcoded",
      re.search(r'id="pr-stats"[^>]*>\s*\d', HTML) is None,
      "stat tile markup must be empty and filled by renderStats()")
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on render host elements, `renderAll`, and the stats host.

- [ ] **Step 3: Add host elements and the render module**

Give every content key a host element inside its panel, using the id convention `pr-sec-<key>`, each under an `<h3>` heading. Add the stat tile row in the header with an empty `<div id="pr-stats" class="stats">`.

```javascript
const CONTENT = JSON.parse(
  document.getElementById('pr-content').textContent
);

const $ = (id) => document.getElementById(id);

function renderTags(hostId, values){
  const host = $(hostId);
  if(!host) return;
  host.replaceChildren();
  values.forEach((value) => {
    const span = document.createElement('span');
    span.className = 'tag';
    span.textContent = value;
    host.appendChild(span);
  });
}

function renderRows(hostId, rows, variant){
  const host = $(hostId);
  if(!host) return;
  host.replaceChildren();
  rows.forEach((row) => {
    const item = document.createElement('div');
    item.className = variant === 'timeline' ? 'row row--timeline' : 'row';

    const primary = document.createElement('div');
    primary.className = 'row__primary';
    primary.textContent = row.primary || '';
    item.appendChild(primary);

    if(row.secondary){
      const secondary = document.createElement('div');
      secondary.className = 'row__secondary';
      secondary.textContent = row.secondary;
      item.appendChild(secondary);
    }
    if(row.meta){
      const meta = document.createElement('div');
      meta.className = 'row__meta mono';
      meta.textContent = row.meta;
      item.appendChild(meta);
    }
    host.appendChild(item);
  });
}

// Displayed counts are derived, never stored, so they cannot go stale.
function renderStats(){
  const s = CONTENT.sections;
  const tiles = [
    ['Publications', s.publications.length],
    ['Sponsored projects', s.grants.length],
    ['Patents', s.patents.length],
    ['Current students', s.studentsCurrent.length],
  ];
  const host = $('pr-stats');
  host.replaceChildren();
  tiles.forEach(([label, value]) => {
    const tile = document.createElement('div');
    tile.className = 'stat';
    const n = document.createElement('div');
    n.className = 'stat__value mono';
    n.textContent = String(value);
    const l = document.createElement('div');
    l.className = 'stat__label';
    l.textContent = label;
    tile.append(n, l);
    host.appendChild(tile);
  });
}

const TAG_KEYS = ['expertise','automotive','windTurbine','gearbox',
                  'wearModelling','surfaceEng','reviewer'];
const TIMELINE_KEYS = ['positions','adminRoles','academicServices','news'];

function renderAll(){
  const s = CONTENT.sections;
  Object.keys(s).forEach((key) => {
    const hostId = `pr-sec-${key}`;
    if(TAG_KEYS.includes(key)){
      renderTags(hostId, s[key]);
    } else {
      const rows = key === 'news'
        ? [...s[key]].sort((a, b) => b.meta.localeCompare(a.meta))
        : s[key];
      renderRows(hostId, rows, TIMELINE_KEYS.includes(key) ? 'timeline' : 'list');
    }
  });
  renderStats();
  renderProfile();
  renderProse();
}

function renderProse(){
  const p = CONTENT.prose;
  const bio = $('pr-bio');
  bio.replaceChildren();
  p.bio.forEach((para) => {
    const el = document.createElement('p');
    el.textContent = para;
    bio.appendChild(el);
  });
  const simple = {
    'pr-research-intro': p.researchIntro,
    'pr-research-guidance': p.researchGuidance,
    'pr-research-funding': p.researchFunding,
    'pr-pub-intro': p.pubIntro,
    'pr-pub-metrics': p.pubMetrics,
    'pr-contact-block': p.contactBlock,
  };
  Object.entries(simple).forEach(([id, text]) => {
    const el = $(id);
    if(el) el.textContent = text;
  });
}
```

This requires `pr-bio`, `pr-research-intro`, `pr-research-guidance`, `pr-research-funding`, `pr-pub-intro`, `pr-pub-metrics` and `pr-contact-block` host elements in the corresponding panels.

Add `renderProfile()`. It carries spec risk #2: the photograph is hotlinked, so it must degrade to initials rather than showing a broken image.

```javascript
function renderProfile(){
  const p = CONTENT.profile;
  $('pr-name').textContent = p.name;
  $('pr-title').textContent = p.title;
  $('pr-institution').textContent = p.institution;

  const facts = [['LAB', p.lab], ['ROOM', p.room],
                 ['PHONE', p.phone], ['EMAIL', p.email]];
  const block = $('pr-titleblock');
  block.replaceChildren();
  facts.forEach(([label, value]) => {
    if(!value) return;
    const row = document.createElement('div');
    row.className = 'titleblock__row';
    const l = document.createElement('div');
    l.className = 'titleblock__label mono';
    l.textContent = label;
    const v = document.createElement('div');
    v.className = 'titleblock__value';
    if(label === 'EMAIL'){
      const a = document.createElement('a');
      a.href = `mailto:${value}`;
      a.textContent = value;
      v.appendChild(a);
    } else {
      v.textContent = value;
    }
    row.append(l, v);
    block.appendChild(row);
  });

  const links = $('pr-links');
  links.replaceChildren();
  CONTENT.links.forEach((link) => {
    const a = document.createElement('a');
    a.href = link.url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = link.label;
    links.appendChild(a);
  });

  // Hotlinked from home.iitm.ac.in; fall back to initials if it ever 404s
  // or the host blocks hotlinking, rather than showing a broken image.
  const avatar = $('pr-avatar');
  avatar.replaceChildren();
  const initials = p.name.replace(/^Prof\.?\s*/i, '')
    .split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase();
  if(p.photo){
    const img = document.createElement('img');
    img.src = p.photo;
    img.alt = p.name;
    img.addEventListener('error', () => {
      avatar.replaceChildren();
      avatar.textContent = initials;
    });
    avatar.appendChild(img);
  } else {
    avatar.textContent = initials;
  }

  const cv = $('pr-cv');
  if(cv){
    cv.hidden = !p.cvUrl;
    if(p.cvUrl){ cv.href = p.cvUrl; cv.textContent = 'Download CV'; }
  }
}
```

This requires `pr-name`, `pr-title`, `pr-institution`, `pr-titleblock`, `pr-links` and `pr-avatar` ids in the header markup. Call `renderAll()` on `DOMContentLoaded`.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: add pure render module with derived stat tiles"
```

---

### Task 5: Hash-synced, accessible tab router

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: tab buttons and panels from Task 2.
- Produces: `showTab(name)` and `currentTab()`. Task 10 calls `showTab()` to jump to a search result.

- [ ] **Step 1: Write the failing checks**

```python
section("tab accessibility and routing")
check("tablist role present", 'role="tablist"' in HTML)
check("tab buttons have role=tab", HTML.count('role="tab"') >= 6)
check("panels have role=tabpanel", HTML.count('role="tabpanel"') >= 6)
check("tabs are keyboard navigable", "ArrowRight" in HTML and "ArrowLeft" in HTML)
check("showTab is defined", "function showTab" in HTML)
check("router listens for hashchange", "hashchange" in HTML)
check("aria-selected is managed", "aria-selected" in HTML)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on `showTab`, `hashchange`, and arrow-key navigation.

- [ ] **Step 3: Implement the router**

```javascript
const TABS = [...document.querySelectorAll('[role="tab"]')];
const PANELS = [...document.querySelectorAll('[role="tabpanel"]')];
const DEFAULT_TAB = 'about';

function currentTab(){
  const hash = location.hash.replace(/^#/, '');
  return TABS.some(t => t.dataset.page === hash) ? hash : DEFAULT_TAB;
}

function showTab(name){
  TABS.forEach((tab) => {
    const on = tab.dataset.page === name;
    tab.classList.toggle('is-active', on);
    tab.setAttribute('aria-selected', String(on));
    tab.tabIndex = on ? 0 : -1;
  });
  PANELS.forEach((panel) => {
    panel.hidden = panel.dataset.page !== name;
  });
  if(location.hash.replace(/^#/, '') !== name){
    history.replaceState(null, '', `#${name}`);
  }
}

TABS.forEach((tab) => {
  tab.addEventListener('click', () => showTab(tab.dataset.page));
  tab.addEventListener('keydown', (e) => {
    const i = TABS.indexOf(tab);
    let next = null;
    if(e.key === 'ArrowRight') next = TABS[(i + 1) % TABS.length];
    if(e.key === 'ArrowLeft') next = TABS[(i - 1 + TABS.length) % TABS.length];
    if(e.key === 'Home') next = TABS[0];
    if(e.key === 'End') next = TABS[TABS.length - 1];
    if(next){ e.preventDefault(); showTab(next.dataset.page); next.focus(); }
  });
});

window.addEventListener('hashchange', () => showTab(currentTab()));
showTab(currentTab());
```

Use `hidden` plus a CSS rule (`[role="tabpanel"][hidden]{display:none}`) rather than a class, so the print stylesheet in Task 12 can override it with one declaration.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: hash-synced accessible tab router"
```

---

### Task 6: Storage adapters

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Produces: `Storage.get(key, fallback) -> Promise<any>`, `Storage.set(key, value) -> Promise<boolean>`, `Storage.name -> "artifact" | "local" | "readonly"`. Tasks 7, 8 and 9 use these and no other persistence API.

- [ ] **Step 1: Write the failing checks**

```python
section("storage adapters")
check("three adapters named", all(
    f'"{n}"' in HTML or f"'{n}'" in HTML
    for n in ("artifact", "local", "readonly")))
check("feature-detects window.storage", "window.storage" in HTML)
check("localStorage access is guarded",
      HTML.count("try{") >= 3 or HTML.count("try {") >= 3,
      "every storage read/write must be wrapped in try/catch")
check("active adapter is surfaced in the UI", "pr-storage-label" in HTML)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on all four.

- [ ] **Step 3: Implement the adapters**

```javascript
// Chosen once at startup by feature detection. Every read falls back to the
// baked-in default rather than throwing; every failed write returns false so
// admin mode can say so out loud instead of pretending it saved.
const Storage = (() => {
  const artifact = {
    name: 'artifact',
    available: () => typeof window.storage?.get === 'function',
    async get(key, fallback){
      try{
        const r = await window.storage.get(key, true);
        return r ? JSON.parse(r.value) : fallback;
      }catch(e){ return fallback; }
    },
    async set(key, value){
      try{
        await window.storage.set(key, JSON.stringify(value), true);
        return true;
      }catch(e){ return false; }
    },
  };

  const local = {
    name: 'local',
    available(){
      try{
        const probe = '__pr__';
        localStorage.setItem(probe, '1');
        localStorage.removeItem(probe);
        return true;
      }catch(e){ return false; }
    },
    async get(key, fallback){
      try{
        const raw = localStorage.getItem(key);
        return raw === null ? fallback : JSON.parse(raw);
      }catch(e){ return fallback; }
    },
    async set(key, value){
      try{ localStorage.setItem(key, JSON.stringify(value)); return true; }
      catch(e){ return false; }
    },
  };

  const readonly = {
    name: 'readonly',
    available: () => true,
    async get(_key, fallback){ return fallback; },
    async set(){ return false; },
  };

  return [artifact, local, readonly].find(a => a.available());
})();
```

Add a `<span id="pr-storage-label" class="mono">` in the admin bar, set to a plain-language description: `Saving to this browser only`, `Saving to artifact storage`, or `Not saving — export to keep changes`.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: pluggable storage adapters with visible active backend"
```

---

### Task 7: Admin authentication with no secret in source

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `Storage` from Task 6.
- Produces: `isAdmin` (boolean), `sha256Hex(text) -> Promise<string>`, `enterAdmin()`, `exitAdmin()`. Task 8 reads `isAdmin`.

- [ ] **Step 1: Write the failing checks**

```python
section("admin auth")
check("no password literal anywhere", "tribology2026" not in HTML)
check("uses SHA-256 via Web Crypto", "crypto.subtle.digest" in HTML
      and "SHA-256" in HTML)
check("no DEFAULT_ADMIN_PASSWORD constant", "DEFAULT_ADMIN_PASSWORD" not in HTML)
check("first-run sets a password", "pr-setpass" in HTML)
check("states the gate is not security",
      re.search(r"not a security|convenience", HTML, re.I) is not None,
      "the UI must be honest that a client-side gate is bypassable")
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on SHA-256 usage, `pr-setpass`, and the honesty string.

- [ ] **Step 3: Implement auth**

```javascript
const PASS_KEY = 'pr_admin_hash';
let isAdmin = false;

async function sha256Hex(text){
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)]
    .map(b => b.toString(16).padStart(2, '0')).join('');
}

// First run has no stored hash, so the first thing the user does is choose a
// password. Nothing is shipped in the source to be discovered.
async function hasPassword(){
  return Boolean(await Storage.get(PASS_KEY, null));
}

async function setPassword(plain){
  if(plain.length < 8) return { ok:false, reason:'Use at least 8 characters.' };
  const saved = await Storage.set(PASS_KEY, await sha256Hex(plain));
  return saved
    ? { ok:true }
    : { ok:false, reason:'This browser is not saving data, so the password '
                       + 'cannot be stored. You can still edit and export.' };
}

async function tryLogin(plain){
  const stored = await Storage.get(PASS_KEY, null);
  if(!stored) return false;
  return (await sha256Hex(plain)) === stored;
}
```

The login dialog shows the *set password* form when `hasPassword()` is false and the *enter password* form otherwise. Both carry this text verbatim:

> This is a convenience lock to prevent accidental edits. It is not a security control — anyone can bypass it by viewing the page source.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: admin auth with no secret in source, honest about scope"
```

---

### Task 8: Admin editors with reordering and dirty state

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `isAdmin` (Task 7), `renderAll()` (Task 4), `Storage` (Task 6).
- Produces: `openEditor(key, index)`, `addRow(key)`, `moveRow(key, index, delta)`, `deleteRow(key, index)`, `markDirty()`, `saveAll()`, `discardAll()`.

- [ ] **Step 1: Write the failing checks**

```python
section("admin editing")
for fn in ("openEditor", "addRow", "moveRow", "deleteRow",
           "markDirty", "saveAll", "discardAll"):
    check(f"{fn} is defined", f"function {fn}" in HTML)
check("editors use real inputs, not contenteditable",
      "contenteditable" not in HTML.lower(),
      "contentEditable was the old approach and must be gone")
check("delete is confirmed", "confirm(" in HTML)
check("dirty state has a UI element", "pr-dirty" in HTML)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on all seven functions and on `contenteditable`, which still exists from the legacy markup if any survived.

- [ ] **Step 3: Implement the editors**

Rendering stays in Task 4's functions. When `isAdmin` is true, `renderAll()` appends a per-row control strip and each section gains an "Add" button. Editing swaps the row for labelled inputs:

```javascript
let dirty = false;

function markDirty(){
  dirty = true;
  $('pr-dirty').textContent = 'Unsaved changes';
  $('pr-dirty').hidden = false;
}

function moveRow(key, index, delta){
  const rows = CONTENT.sections[key];
  const target = index + delta;
  if(target < 0 || target >= rows.length) return;
  [rows[index], rows[target]] = [rows[target], rows[index]];
  markDirty();
  renderAll();
}

function deleteRow(key, index){
  const rows = CONTENT.sections[key];
  const label = typeof rows[index] === 'string'
    ? rows[index] : rows[index].primary;
  if(!confirm(`Delete "${label}"? This cannot be undone.`)) return;
  rows.splice(index, 1);
  markDirty();
  renderAll();
}

function addRow(key){
  const rows = CONTENT.sections[key];
  rows.unshift(TAG_KEYS.includes(key)
    ? '' : { primary:'', secondary:'', meta:'' });
  markDirty();
  renderAll();
  openEditor(key, 0);
}

async function saveAll(){
  const ok = await Storage.set('pr_content', CONTENT);
  const el = $('pr-dirty');
  if(ok){
    dirty = false;
    el.textContent = 'Saved';
    setTimeout(() => { el.hidden = true; }, 2000);
  } else {
    el.textContent = 'Could not save here — use Export to keep your changes';
  }
}

function discardAll(){
  if(dirty && !confirm('Discard all unsaved changes?')) return;
  location.reload();
}
```

`openEditor(key, index)` replaces the rendered row with a small form containing labelled `<input>` elements for `primary`, `secondary`, `meta` (a single input for string-array sections), plus Done and Cancel. Done writes values back into `CONTENT`, calls `markDirty()` and `renderAll()`.

Add a `beforeunload` guard that warns when `dirty` is true.

On startup, after parsing the JSON block, overlay any saved content: `Object.assign(CONTENT, await Storage.get('pr_content', CONTENT))` before the first `renderAll()`.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: input-based admin editors with reordering and dirty state"
```

---

### Task 9: Export and import

The feature that guarantees content can never be trapped by a hosting choice. Treat it as the most important task in the plan.

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `CONTENT`, `isAdmin`.
- Produces: `serializeContent() -> string`, `exportJson()`, `exportHtml()`, `importJson(file)`.

- [ ] **Step 1: Write the failing checks**

```python
section("export and import")
for fn in ("serializeContent", "exportJson", "exportHtml", "importJson"):
    check(f"{fn} is defined", f"function {fn}" in HTML)
# The regex literal /<\//g appears verbatim in serializeContent; its
# presence is what proves the escaping step exists.
check("escapes the script terminator on export",
      "<\\/" in HTML,
      "serializeContent must escape </script> or the exported file breaks")
check("uses a Blob download", "URL.createObjectURL" in HTML)
check("import validates before applying",
      "JSON.parse" in HTML and "catch" in HTML)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on all four functions and the escaping check.

- [ ] **Step 3: Implement export and import**

```javascript
// A content string containing </script> would close the JSON block early and
// produce a broken export. Escaping the slash is inert inside JSON but stops
// the HTML parser seeing a closing tag. This is risk #1 from the spec.
function serializeContent(){
  return JSON.stringify(CONTENT, null, 2).replace(/<\//g, '<\\/');
}

function download(filename, text, mime){
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function exportJson(){
  download('content.json', serializeContent(), 'application/json');
}

// Rebuilds a complete, standalone index.html with current content baked in,
// by swapping the JSON block inside this page's own source.
function exportHtml(){
  const source = document.documentElement.outerHTML;
  const rebuilt = source.replace(
    /(<script[^>]+id="pr-content"[^>]*>)([\s\S]*?)(<\/script>)/,
    (_m, open, _body, close) => open + '\n' + serializeContent() + '\n' + close
  );
  download('index.html', '<!doctype html>\n' + rebuilt, 'text/html');
}

async function importJson(file){
  let parsed;
  try{
    parsed = JSON.parse(await file.text());
  }catch(e){
    alert('That file is not valid JSON.');
    return;
  }
  if(!parsed || typeof parsed !== 'object' || !parsed.sections || !parsed.profile){
    alert('That JSON does not look like exported profile content '
        + '(expected "profile" and "sections" keys).');
    return;
  }
  if(!confirm('Replace all current content with the imported file?')) return;
  Object.assign(CONTENT, parsed);
  markDirty();
  renderAll();
}
```

Add Export JSON, Export HTML and Import buttons to the admin bar, plus a hidden `<input type="file" accept="application/json">` wired to `importJson`.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: export to JSON and standalone HTML, plus validated import"
```

---

### Task 10: Cross-tab search

Neutralizes the main cost of keeping tabs: content hidden from in-page search.

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `CONTENT`, `showTab()` (Task 5).
- Produces: `buildSearchIndex() -> {text, key, tab, label}[]`, `runSearch(query) -> results[]`.

- [ ] **Step 1: Write the failing checks**

```python
section("search")
check("buildSearchIndex is defined", "function buildSearchIndex" in HTML)
check("runSearch is defined", "function runSearch" in HTML)
check("search box exists", 'id="pr-search"' in HTML)
check("results host exists", 'id="pr-search-results"' in HTML)
check("every section key maps to a tab",
      "SECTION_TAB" in HTML,
      "search results must know which tab to open")
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on all five.

- [ ] **Step 3: Implement search**

```javascript
// Maps each content key to the tab that displays it, so a result can switch
// tabs before scrolling. Keep in sync when sections move between tabs.
const SECTION_TAB = {
  education:'about', expertise:'about', news:'about',
  automotive:'research', windTurbine:'research', gearbox:'research',
  wearModelling:'research', surfaceEng:'research', facilities:'research',
  grants:'research',
  publications:'publications', books:'publications',
  bookChapters:'publications', patents:'publications',
  courses:'teaching',
  studentsCurrent:'group', studentsAlumni:'group',
  positions:'activities', awards:'activities', memberships:'activities',
  reviewer:'activities', adminRoles:'activities',
  academicServices:'activities', talks:'activities',
};

function buildSearchIndex(){
  const index = [];
  Object.entries(CONTENT.sections).forEach(([key, rows]) => {
    rows.forEach((row) => {
      const text = typeof row === 'string'
        ? row
        : [row.primary, row.secondary, row.meta].filter(Boolean).join(' ');
      index.push({
        text,
        key,
        tab: SECTION_TAB[key] || 'about',
        label: typeof row === 'string' ? row : row.primary,
      });
    });
  });
  return index;
}

let SEARCH_INDEX = [];

function runSearch(query){
  const q = query.trim().toLowerCase();
  if(q.length < 2) return [];
  return SEARCH_INDEX
    .filter(entry => entry.text.toLowerCase().includes(q))
    .slice(0, 20);
}
```

Wire the input to render results into `#pr-search-results`; clicking a result calls `showTab(entry.tab)` then scrolls `#pr-sec-<key>` into view and briefly highlights it. Rebuild `SEARCH_INDEX` inside `renderAll()` so edits are searchable immediately.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: cross-tab search with tab-aware result navigation"
```

---

### Task 11: New sections — group, news, talks, CV

Content keys already exist from Task 3; this task gives them a home in the UI.

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

**Interfaces:**
- Consumes: `renderAll()`, `SECTION_TAB`.
- Produces: a seventh tab, `group`.

- [ ] **Step 1: Write the failing checks**

```python
section("new sections")
check("group tab exists", 'data-page="group"' in HTML)
check("seven tabs now", len(set(re.findall(
    r'<button[^>]+data-page="([\w-]+)"', HTML))) >= 7)
check("CV button present", 'id="pr-cv"' in HTML)
check("news host is in the about panel",
      re.search(r'data-page="about"[\s\S]*?id="pr-sec-news"[\s\S]*?</section>',
                HTML) is not None)
check("talks host is in the activities panel",
      re.search(r'data-page="activities"[\s\S]*?id="pr-sec-talks"[\s\S]*?</section>',
                HTML) is not None)
# Guarded: an unmatched search here would abort the whole suite with
# AttributeError instead of reporting a single FAIL.
_st = re.search(r"SECTION_TAB\s*=\s*\{([\s\S]*?)\};", HTML)
_targets = set(re.findall(r":\s*'(\w+)'", _st.group(1))) if _st else set()
check("SECTION_TAB block found", _st is not None)
check("every SECTION_TAB target is a real tab",
      bool(_targets) and all(f'data-page="{t}"' in HTML for t in _targets),
      f"targets: {sorted(_targets)}")
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on the group tab, seven tabs, and the CV button.

- [ ] **Step 3: Add the sections**

- Insert a `Group` tab button between `Research` and `Publications`, and a matching `<section data-page="group" role="tabpanel">` containing `#pr-sec-studentsCurrent` under "Current scholars" and `#pr-sec-studentsAlumni` under "Alumni".
- Add `#pr-sec-news` at the top of the About panel under a "News" heading, rendered as a timeline. It is already sorted reverse-chronologically by `renderAll()`.
- Add `#pr-sec-talks` to the Activities panel under "Invited talks and conference presentations".
- Add `<a id="pr-cv" class="btn btn--accent" download>` in the header, populated from `CONTENT.profile.cvUrl` by `renderProfile()` and hidden when `cvUrl` is empty, so an unset CV never renders a dead button.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: add group, news, talks sections and CV download button"
```

---

### Task 12: Print stylesheet and responsive layout

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`

- [ ] **Step 1: Write the failing checks**

```python
section("print and responsive")
check("print stylesheet exists", "@media print" in HTML)
print_block = re.search(r"@media print\s*\{([\s\S]*?)\n\s*\}\s*\n", HTML)
print_css = print_block.group(1) if print_block else ""
check("print expands hidden tab panels",
      "hidden" in print_css and "display" in print_css,
      "tabs hide content; print must override [hidden] to show every section")
check("print hides interactive chrome",
      "nav" in print_css or ".admin" in print_css)
check("mobile breakpoint is 720px", "max-width:720px" in HTML.replace(" ", ""))
check("no fixed pixel page width",
      re.search(r"\.page\s*\{[^}]*width:\s*\d{3,}px", HTML) is None)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on the print block and the breakpoint.

- [ ] **Step 3: Implement**

```css
@media print{
  /* Tabs hide content on screen; printing must produce the full CV. */
  [role="tabpanel"][hidden]{display:block !important;}
  [role="tablist"], .admin-bar, .search, #pr-cv, footer button{display:none !important;}
  :root{--surface:#fff; --surface-raised:#fff; --ink:#000; --line:#999;}
  body{font-size:10.5pt;}
  .row{break-inside:avoid;}
  h2, h3{break-after:avoid;}
  a[href^="http"]::after{content:" (" attr(href) ")"; font-size:9pt;}
}

@media (max-width:720px){
  [role="tablist"]{overflow-x:auto; flex-wrap:nowrap; scrollbar-width:thin;}
  .stats{grid-template-columns:repeat(2, 1fr);}
  .titleblock{display:block;}
  .header-inner{flex-direction:column; align-items:flex-start;}
}
```

Ensure every container uses `max-width:var(--maxw)` with `padding-inline:var(--gutter)` rather than a fixed width.

- [ ] **Step 4: Run the checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py
git commit -m "feat: print stylesheet expanding all tabs, responsive layout"
```

---

### Task 13: Tier 2 self-test suite and user handoff

The implementer writes this suite but **cannot run it**. It exists so the user can verify the JS behaviour that no tool on this machine can reach.

**Files:**
- Modify: `index.html`
- Modify: `tests/check.py`
- Create: `docs/superpowers/plans/HANDOFF.md`

- [ ] **Step 1: Write the failing checks**

```python
section("self-test suite")
check("selftest is gated behind a query parameter", "selftest" in HTML)
check("selftest covers export round-trip", "serializeContent" in HTML
      and "selftest" in HTML)
check("selftest results render in-page", 'id="pr-selftest"' in HTML)
```

- [ ] **Step 2: Run and watch it fail**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: FAIL on all three.

- [ ] **Step 3: Implement the suite**

```javascript
// Runs only with ?selftest=1. Covers the pure logic that no tooling on the
// development machine can execute; a human runs this in a browser.
function runSelfTests(){
  const results = [];
  const t = (name, fn) => {
    try{ results.push([name, fn() === true]); }
    catch(e){ results.push([name, false]); }
  };

  t('export round-trips content', () => {
    const copy = JSON.parse(serializeContent().replace(/<\\\//g, '</'));
    return JSON.stringify(copy) === JSON.stringify(CONTENT);
  });

  t('script terminator is escaped', () => {
    const saved = CONTENT.sections.expertise.slice();
    CONTENT.sections.expertise.push('danger </script> tag');
    const out = serializeContent();
    CONTENT.sections.expertise = saved;
    return !out.includes('</script>');
  });

  t('storage adapter chosen and named', () =>
    ['artifact','local','readonly'].includes(Storage.name));

  t('search finds a known publication', () =>
    runSearch('tribology').length > 0);

  t('search result maps to a real tab', () =>
    runSearch('tribology').every(r =>
      document.querySelector(`[role="tab"][data-page="${r.tab}"]`) !== null));

  t('hash routing agrees both ways', () => {
    const before = currentTab();
    showTab('publications');
    const ok = location.hash === '#publications'
            && currentTab() === 'publications';
    showTab(before);
    return ok;
  });

  t('stat tiles match array lengths', () =>
    document.querySelector('.stat__value').textContent
      === String(CONTENT.sections.publications.length));

  const host = document.getElementById('pr-selftest');
  host.hidden = false;
  host.replaceChildren();
  const failed = results.filter(([, ok]) => !ok).length;
  const heading = document.createElement('h2');
  heading.textContent = failed
    ? `${failed} of ${results.length} self-tests FAILED`
    : `All ${results.length} self-tests passed`;
  host.appendChild(heading);
  results.forEach(([name, ok]) => {
    const line = document.createElement('div');
    line.className = 'mono';
    line.textContent = `${ok ? 'PASS' : 'FAIL'}  ${name}`;
    host.appendChild(line);
  });
}

if(new URLSearchParams(location.search).get('selftest') === '1'){
  window.addEventListener('load', runSelfTests);
}
```

Add `<div id="pr-selftest" class="selftest" hidden></div>` at the top of `<body>`.

- [ ] **Step 4: Run the Tier 1 checks**

```bash
cd /home/varun/Desktop/ramkumar && python3 tests/check.py
```

Expected: PASS. This proves the suite *exists*, not that it passes.

- [ ] **Step 5: Write the handoff document**

Create `docs/superpowers/plans/HANDOFF.md` listing, for the user to verify in Firefox:

1. Open `index.html?selftest=1` and report the pass/fail lines.
2. Open `index.html` — check the header, stat tile numbers, and that the photo loads (or the initials fallback appears).
3. Click each of the seven tabs; confirm the URL hash updates and a refresh keeps the tab.
4. Arrow-key through the tab bar.
5. Search for "hip implant" and confirm it jumps to the right tab and section.
6. Print preview — confirm every section appears, not just the active tab.
7. Narrow the window to 360px — confirm no horizontal scrolling.
8. Toggle OS dark mode — confirm the page is legible.
9. Admin: set a password, edit a row, reorder, delete, save, reload, confirm persistence.
10. Export JSON and HTML; open the exported HTML and confirm it is complete and standalone.

Also list, under **Content needing confirmation**, every row seeded without a user-supplied source in Task 3 — the `books` entries and all `studentsCurrent`, `studentsAlumni`, `news` and `talks` rows.

- [ ] **Step 6: Commit**

```bash
cd /home/varun/Desktop/ramkumar
git add index.html tests/check.py docs/superpowers/plans/HANDOFF.md
git commit -m "feat: add browser self-test suite and user verification handoff"
```

---

## Completion criteria

The work is **not** complete when Task 13 commits. It is complete when:

- `python3 tests/check.py` exits zero with every check passing, and
- the user has run `index.html?selftest=1` in a browser and reported the results, and
- the user has confirmed or corrected every seeded row listed in `HANDOFF.md`.

Until the user reports back, describe the JavaScript behaviour as **written but unverified**. Do not claim it works.
