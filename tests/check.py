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

if _failures:
    print(f"\n{len(_failures)} FAILED: " + ", ".join(_failures))
    sys.exit(1)
print("\nall checks passed")
