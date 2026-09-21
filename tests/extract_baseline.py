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


# Scope row/array extraction to the `defaults` object literal only. The rest
# of the script (e.g. prAddRow's `{primary:'New entry', ...}`) uses the same
# field names for its own purposes -- those are code defaults, not content,
# and must not be swept in here.
defaults_match = re.search(
    r"^\s{2}const defaults = \{\n(.*?)\n\s{2}\};$", original, re.S | re.M
)
assert defaults_match, "could not locate the `defaults` object literal"
defaults_block = defaults_match.group(1)

# Object rows: primary:'...', secondary:'...', meta:'...'
for field in ("primary", "secondary", "meta"):
    for m in re.finditer(rf"{field}\s*:\s*'((?:[^'\\]|\\.)*)'", defaults_block):
        value = decode_js(m.group(1)).strip()
        if value:
            strings.add(value)

# String arrays: key: ['a','b','c'] -- single line only. [^\]\n]* rather than
# [^\]]* because the latter spans newlines and re-swallows every multi-line
# object array, re-extracting its values through this weaker path.
for m in re.finditer(r"^\s{4}(\w+)\s*:\s*\[([^\]\n]*)\]", defaults_block, re.M):
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
