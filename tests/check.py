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

if _failures:
    print(f"\n{len(_failures)} FAILED: " + ", ".join(_failures))
    sys.exit(1)
print("\nall checks passed")
