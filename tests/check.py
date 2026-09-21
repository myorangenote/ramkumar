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
    for curly, plain in (("’", "'"), ("‘", "'"),
                         ("“", '"'), ("”", '"')):
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

section("content schema")
STRING_ARRAY_KEYS = [
    "expertise", "automotive", "windTurbine", "gearbox",
    "wearModelling", "surfaceEng", "reviewer",
]
ROW_KEYS = [
    "education", "facilities", "grants", "publications",
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

news = sections_data.get("news") or []
check("every news date is YYYY, YYYY-MM or YYYY-MM-DD",
      all(re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", r.get("meta", "")) for r in news))
check("no news date has suspected invented day precision",
      not any(r.get("meta", "").endswith("-01-01") for r in news))

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
# Compare against the string VALUES, not the JSON text. json.dumps escapes
# embedded double quotes to \", so a baseline entry like
# 'IMechE "Mission of Tribology", UK' would never match the serialized form
# and would be reported as lost content that had in fact migrated fine.
def all_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from all_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from all_strings(value)


# \x00 separates entries so a match cannot span two of them; norm()'s
# whitespace collapsing leaves it intact.
blob = norm("\x00".join(all_strings(data or {})))
missing = [s for s in baseline if norm(s) not in blob]
check(f"all {len(baseline)} baseline strings survived the rework",
      not missing,
      f"{len(missing)} missing, first five: {missing[:5]}")

section("serialization safety")
raw_json = json.dumps(data, ensure_ascii=False)
check("no raw </script> in content", "</script>" not in raw_json.lower())
check("legacy block removed", "LEGACY-START" not in HTML)

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

section("structural fidelity")
structure = json.loads(
    (ROOT / "tests" / "baseline_structure.json").read_text(encoding="utf-8")
)
live = (data or {}).get("sections", {})
for key, expected in structure.items():
    got = live.get(key)
    if expected and isinstance(expected[0], list):
        got_rows = [[r.get("primary", ""), r.get("secondary", ""),
                     r.get("meta", "")] for r in (got or [])]
    else:
        got_rows = got or []
    check(f"{key} is structurally unchanged", got_rows == expected,
          f"expected {len(expected)} rows, got {len(got_rows)}")

section("tab accessibility and routing")
check("tablist role present", 'role="tablist"' in HTML)
check("tab buttons have role=tab", HTML.count('role="tab"') >= 6)
check("panels have role=tabpanel", HTML.count('role="tabpanel"') >= 6)
check("tabs are keyboard navigable", "ArrowRight" in HTML and "ArrowLeft" in HTML)
check("showTab is defined", "function showTab" in HTML)
check("router listens for hashchange", "hashchange" in HTML)
check("aria-selected is managed", "aria-selected" in HTML)

section("storage adapters")
check("three adapters named", all(
    f'"{n}"' in HTML or f"'{n}'" in HTML
    for n in ("artifact", "local", "readonly")))
check("feature-detects window.storage", "window.storage" in HTML)
# Scoped to the Storage IIFE. A file-wide count would pass on three
# unrelated try-blocks elsewhere and stop verifying storage entirely.
_storage_block = re.search(r"const Storage = \(\(\) => \{([\s\S]*?)\n\}\)\(\);", HTML)
_storage_src = _storage_block.group(1) if _storage_block else ""
check("Storage block found", _storage_block is not None)
check("every storage path is guarded",
      _storage_src.count("try{") + _storage_src.count("try {") >= 6,
      "artifact get/set, local available/get/set must each be in try/catch")
check("active adapter is surfaced in the UI", "pr-storage-label" in HTML)

section("admin auth")
check("no password literal anywhere", "tribology2026" not in HTML)
check("uses SHA-256 via Web Crypto", "crypto.subtle.digest" in HTML
      and "SHA-256" in HTML)
check("no DEFAULT_ADMIN_PASSWORD constant", "DEFAULT_ADMIN_PASSWORD" not in HTML)
check("first-run sets a password", "pr-setpass" in HTML)
check("states the gate is not security",
      re.search(r"not a security|convenience", HTML, re.I) is not None,
      "the UI must be honest that a client-side gate is bypassable")

section("fixes carried over from review")
check("formatNewsDate is actually called, not just defined",
      HTML.count("formatNewsDate(") >= 2,
      "defining it without calling it renders raw '2023-02' instead of 'February 2023'")
check("safeUrl is defined", "function safeUrl" in HTML)
check("every content-derived URL passes through safeUrl",
      "safeUrl(link.url)" in HTML and "safeUrl(p.photo)" in HTML
      and "safeUrl(p.cvUrl)" in HTML,
      "an unguarded href lets an edited javascript: URL execute on click")
check("tabs and panels are ARIA-associated",
      "aria-controls" in HTML and "aria-labelledby" in HTML,
      "aria-selected alone gives a screen reader no link from panel to tab")
check("history.replaceState is guarded",
      re.search(r"try\s*\{[^}]*history\.replaceState", HTML, re.S) is not None,
      "the top-level showTab() call would abort the script")

section("admin editing")
for fn in ("openEditor", "addRow", "moveRow", "deleteRow",
           "markDirty", "saveAll", "discardAll"):
    check(f"{fn} is defined", f"function {fn}" in HTML)
check("editors use real inputs, not contenteditable",
      "contenteditable" not in HTML.lower(),
      "contentEditable was the old approach and must be gone")
check("delete is confirmed", "confirm(" in HTML)
check("dirty state has a UI element", "pr-dirty" in HTML)

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

section("search")
check("buildSearchIndex is defined", "function buildSearchIndex" in HTML)
check("runSearch is defined", "function runSearch" in HTML)
check("search box exists", 'id="pr-search"' in HTML)
check("results host exists", 'id="pr-search-results"' in HTML)
check("every section key maps to a tab",
      "SECTION_TAB" in HTML,
      "search results must know which tab to open")

_data = content_json()
_m = re.search(r"const SECTION_TAB\s*=\s*\{(.*?)\};", HTML, re.S)
check("SECTION_TAB literal is present", _m is not None)
if _m and _data is not None:
    _pairs = re.findall(r"(\w+)\s*:\s*'([^']+)'", _m.group(1))
    _map = dict(_pairs)
    _content_keys = set(_data["sections"].keys())
    _mapped_keys = set(_map.keys())
    check("SECTION_TAB has no 'books' entry", "books" not in _map,
          "the books section was removed; SECTION_TAB must not reference it")
    check("SECTION_TAB covers every content section key",
          _content_keys <= _mapped_keys,
          f"missing: {sorted(_content_keys - _mapped_keys)}")
    check("SECTION_TAB has no keys outside the content sections",
          _mapped_keys <= _content_keys,
          f"extra: {sorted(_mapped_keys - _content_keys)}")
    _known_tabs = {"about", "research", "publications", "teaching",
                   "activities", "contact", "group"}
    check("SECTION_TAB only points at known tabs",
          set(_map.values()) <= _known_tabs,
          f"unknown tabs: {sorted(set(_map.values()) - _known_tabs)}")

check("search results are built with textContent, not innerHTML",
      "item.textContent = entry.label" in HTML
      or "item.textContent" in HTML,
      "a result rendered via innerHTML would be an injection point")
check("search index is rebuilt inside renderAll",
      re.search(r"function renderAll\(\)\{.*?buildSearchIndex\(\).*?\n\}",
                HTML, re.S) is not None,
      "admin edits must become searchable without a reload")
check("clicking a result switches tabs then scrolls its section into view",
      "showTab(entry.tab)" in HTML and "scrollIntoView" in HTML)
check("a missing section host cannot throw when a result is clicked",
      re.search(r"function goToSearchResult\(entry\)\{.*?if\(!host\) return;",
                HTML, re.S) is not None,
      "sections without a host yet (Task 11) must be guarded like "
      "renderTags/renderRows already guard a missing host")

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

section("index-stability fixes (Task 11 prep)")
check("rendered rows carry their storage index",
      "dataset.index" in HTML,
      "news renders from a sorted copy, so DOM position is NOT the array index")
check("admin controls read the stamped index, not child position",
      "items.forEach((item, index)" not in HTML,
      "deriving the index from child order edits the wrong row for news")
check("renderStats tolerates a missing section key",
      "Array.isArray(s[key])" in HTML or "const count =" in HTML,
      "an unguarded .length throws mid-render on an older saved blob")

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

section("self-test suite")
check("selftest is gated behind a query parameter", "selftest" in HTML)
check("selftest covers export round-trip", "serializeContent" in HTML
      and "selftest" in HTML)
check("selftest results render in-page", 'id="pr-selftest"' in HTML)

if _failures:
    print(f"\n{len(_failures)} FAILED: " + ", ".join(_failures))
    sys.exit(1)
print("\nall checks passed")
