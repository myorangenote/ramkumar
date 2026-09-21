"""Extract every content string from the pre-rework index.html.

Reads the original from git so it cannot be affected by the rework in
progress. Produces tests/baseline_strings.json, used by check.py to prove
no content was silently dropped.
"""
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

# Object rows: primary:'...', secondary:'...', meta:'...'
for field in ("primary", "secondary", "meta"):
    for m in re.finditer(rf"{field}\s*:\s*'((?:[^'\\]|\\.)*)'", original):
        value = m.group(1).replace("\\'", "'").replace("\\u2019", "'")
        if value.strip():
            strings.add(value.strip())

# String arrays: key: ['a','b','c']
for m in re.finditer(r"^\s{4}(\w+)\s*:\s*\[([^\]]*)\]", original, re.M):
    for sm in re.finditer(r"'((?:[^'\\]|\\.)*)'", m.group(2)):
        value = sm.group(1).replace("\\'", "'")
        if value.strip() and ":" not in value[:3]:
            strings.add(value.strip())

OUT.write_text(json.dumps(sorted(strings), indent=1, ensure_ascii=False))
print(f"extracted {len(strings)} baseline strings -> {OUT}")
