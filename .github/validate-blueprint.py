#!/usr/bin/env python3
"""
validate-blueprint.py  — Blueprint v2.1 structural validator
Runs as a CI step before Hugo build. Exits non-zero on any FAIL.
WARNs are printed but do not block the build.
"""
import os, re, json, sys, glob

MONITORS_DIR = "static/monitors"
STANDARD_PAGES = ["about", "archive", "dashboard", "methodology",
                  "overview", "persistent", "report", "search"]
AGM_EXTRA_PAGES = ["digest"]
MONITOR_SLUGS = [
    "ai-governance", "conflict-escalation", "democratic-integrity",
    "environmental-risks", "european-strategic-autonomy",
    "fimi-cognitive-warfare", "macro-monitor"
]

errors   = []   # FAIL — blocks build
warnings = []   # WARN — printed, build continues

def fail(msg):  errors.append(f"  FAIL  {msg}")
def warn(msg):  warnings.append(f"  WARN  {msg}")

# ── Check 1: All standard pages exist per monitor ─────────────────────────
print("Check 1: Standard pages exist per monitor")
for slug in MONITOR_SLUGS:
    pages = STANDARD_PAGES + (AGM_EXTRA_PAGES if slug == "ai-governance" else [])
    for page in pages:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path):
            fail(f"{slug}/{page}.html — MISSING")

# ── Check 2: No inline padding-top:40px style blocks ─────────────────────
print("Check 2: No inline offset style blocks (should be in base.css)")
for slug in MONITOR_SLUGS:
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as f: c = f.read()
        if "padding-top:40px" in c or "padding-top: 40px" in c:
            warn(f"{slug}/{page}.html — inline padding-top:40px (stale; base.css owns this)")

# ── Check 3: nav.js referenced on every page ─────────────────────────────
print("Check 3: nav.js referenced on every page")
for slug in MONITOR_SLUGS:
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as f: c = f.read()
        if "shared/js/nav.js" not in c:
            fail(f"{slug}/{page}.html — nav.js not referenced (network bar won't inject)")

# ── Check 4: base.css referenced on every page ───────────────────────────
print("Check 4: base.css referenced on every page")
for slug in MONITOR_SLUGS:
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as f: c = f.read()
        if "shared/css/base.css" not in c:
            fail(f"{slug}/{page}.html — base.css not referenced")

# ── Check 5: monitor.css is accent-only (under 40 lines) ─────────────────
print("Check 5: monitor.css accent-only (≤40 lines)")
for slug in MONITOR_SLUGS:
    path = f"{MONITORS_DIR}/{slug}/assets/monitor.css"
    if not os.path.exists(path):
        warn(f"{slug}/assets/monitor.css — MISSING")
        continue
    with open(path) as f: lines = f.readlines()
    if len(lines) > 40:
        warn(f"{slug}/assets/monitor.css — {len(lines)} lines (should be accent-only ≤40 lines)")

# ── Check 6: JSON files are valid JSON ───────────────────────────────────
print("Check 6: JSON files are valid")
for slug in MONITOR_SLUGS:
    data_dir = f"{MONITORS_DIR}/{slug}/data"
    if not os.path.exists(data_dir): continue
    for jf in glob.glob(f"{data_dir}/*.json"):
        try:
            with open(jf) as f: json.load(f)
        except json.JSONDecodeError as e:
            fail(f"{jf} — invalid JSON: {e}")

# ── Check 7: report-latest.json has schema_version 2.0 ───────────────────
print("Check 7: report-latest.json schema_version == 2.0")
for slug in MONITOR_SLUGS:
    path = f"{MONITORS_DIR}/{slug}/data/report-latest.json"
    if not os.path.exists(path):
        fail(f"{slug}/data/report-latest.json — MISSING")
        continue
    with open(path) as f:
        try: d = json.load(f)
        except: continue
    sv = d.get("meta", {}).get("schema_version") or d.get("_meta", {}).get("schema_version")
    if sv != "2.0":
        warn(f"{slug}/data/report-latest.json — schema_version is '{sv}' (expected 2.0)")

# ── Check 8: No stale inline network bar HTML ─────────────────────────────
print("Check 8: No stale inline network bar HTML")
for slug in MONITOR_SLUGS:
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as f: c = f.read()
        if "<nav data-asym-network-bar" in c:
            warn(f"{slug}/{page}.html — stale inline network bar (nav.js handles this now)")

# ── Check 9: report-latest.json published date is not future ─────────────
print("Check 9: report-latest.json not future-dated")
from datetime import datetime, timezone
today = datetime.now(timezone.utc).date()
for slug in MONITOR_SLUGS:
    path = f"{MONITORS_DIR}/{slug}/data/report-latest.json"
    if not os.path.exists(path): continue
    with open(path) as f:
        try: d = json.load(f)
        except: continue
    pub = d.get("meta", {}).get("published", "")
    if pub:
        try:
            pub_date = datetime.fromisoformat(pub.replace("Z", "+00:00")).date()
            if pub_date > today:
                fail(f"{slug}/data/report-latest.json — published date {pub_date} is FUTURE (Hugo will skip it)")
        except: pass


# ── Check 10: base.css has body padding-top:40px ─────────────────────
print("Check 10: base.css has body padding-top:40px")
base_css_path = f"{MONITORS_DIR}/../../../static/monitors/shared/css/base.css"
# Adjust path for CI context
import glob as _glob
base_candidates = _glob.glob("static/monitors/shared/css/base.css")
if base_candidates:
    with open(base_candidates[0]) as _f: _base = _f.read()
    if 'padding-top: 40px' not in _base and 'padding-top:40px' not in _base:
        fail("base.css — body padding-top:40px MISSING (network bar offset not set)")
    else:
        pass  # OK

# ── Check 11: main.css network-bar is position:fixed ─────────────────
print("Check 11: main.css network-bar is position:fixed")
main_candidates = _glob.glob("assets/css/main.css")
if main_candidates:
    with open(main_candidates[0]) as _f: _main = _f.read()
    if 'position: fixed' not in _main and '.network-bar' in _main:
        fail("assets/css/main.css — .network-bar is not position:fixed (Hugo pages bar will scroll away)")

# ── Check 12: monitor-nav has explicit top:40px ───────────────────────
print("Check 12: base.css monitor-nav has top:40px")
if base_candidates:
    import re as _re
    mn = _re.search(r'\.monitor-nav\s*\{[^}]+\}', _base)
    if mn and 'top: 40px' not in mn.group() and 'top:40px' not in mn.group():
        warn("base.css — .monitor-nav missing explicit top:40px (may hide behind network bar)")


# ── Check 13: nav.js is in <head> (not body) on every page ───────────────────
print("Check 13: nav.js in <head> on every page")
import re as _re2
for slug in MONITOR_SLUGS:
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as _f: _c = _f.read()
        _head_end = _c.find('</head>')
        _nav_pos  = _c.find('nav.js')
        if _nav_pos == -1:
            fail(f"{slug}/{page}.html — nav.js not referenced at all")
        elif _nav_pos > _head_end:
            fail(f"{slug}/{page}.html — nav.js in <body> not <head> (network bar won't inject before paint)")

# ── Check 14: Chart.js CDN loaded on pages using <canvas> ────────────────────
print("Check 14: Chart.js CDN present on pages using <canvas>")
for slug in MONITOR_SLUGS:
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as _f: _c = _f.read()
        if '<canvas' in _c or 'new Chart(' in _c:
            if 'cdn.jsdelivr.net/npm/chart.js' not in _c and 'chart.umd' not in _c:
                fail(f"{slug}/{page}.html — uses Chart.js but CDN not loaded (Chart is not defined error)")

# ── Check 15: No overflow-x:hidden on layout containers in inline styles ──────
print("Check 15: No overflow-x:hidden on monitor-layout/monitor-main in inline styles")
for slug in MONITOR_SLUGS:
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as _f: _c = _f.read()
        _styles = _re2.findall(r'<style[^>]*>(.*?)</style>', _c, _re2.DOTALL)
        for _s in _styles:
            _hits = _re2.findall(r'(?:monitor-layout|monitor-main|\.monitor-layout|\.monitor-main)[^}]*overflow[^}]*hidden', _s, _re2.DOTALL)
            if _hits:
                fail(f"{slug}/{page}.html — overflow:hidden on monitor-layout/main in inline style (breaks sticky nav)")

# ── Check 16: Page titles contain full monitor name and brand ─────────────
print("Check 16: Page titles contain monitor name and brand suffix")
MONITOR_FULL_NAMES = {
    'democratic-integrity': 'World Democracy Monitor',
    'macro-monitor': 'Global Macro Monitor',
    'fimi-cognitive-warfare': 'FIMI & Cognitive Warfare Monitor',
    'european-strategic-autonomy': 'European Strategic Autonomy Monitor',
    'ai-governance': 'AI Governance Monitor',
    'environmental-risks': 'Environmental Risks Monitor',
    'conflict-escalation': 'Strategic Conflict & Escalation Monitor',
}
import re as _re3
for slug, full_name in MONITOR_FULL_NAMES.items():
    for page in STANDARD_PAGES:
        path = f"{MONITORS_DIR}/{slug}/{page}.html"
        if not os.path.exists(path): continue
        with open(path) as _f: _c = _f.read()
        _title_m = _re3.search(r'<title>([^<]+)</title>', _c)
        if not _title_m:
            warn(f"{slug}/{page}.html — missing <title> tag")
            continue
        _title = _title_m.group(1)
        _name_clean = full_name.replace('&', '&amp;')
        if full_name.lower() not in _title.lower() and _name_clean.lower() not in _title.lower():
            warn(f"{slug}/{page}.html — title missing full monitor name: '{_title}'")
        if 'asymmetric intelligence' not in _title.lower():
            warn(f"{slug}/{page}.html — title missing '· Asymmetric Intelligence' suffix: '{_title}'")

# ── Summary ───────────────────────────────────────────────────────────────
print()
if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings: print(w)
    print()

if errors:
    print(f"FAILURES ({len(errors)}) — build blocked:")
    for e in errors: print(e)
    print()
    print("Fix all FAIL items before merging.")
    sys.exit(1)
else:
    print(f"All checks passed. {len(warnings)} warning(s).")
    sys.exit(0)
