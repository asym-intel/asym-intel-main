#!/usr/bin/env python3
"""
tools/preflight.py — Automated pre-flight checks for asym-intel pipeline.

Run after every batch fix to catch common errors before they reach production.
Designed to run locally or in CI. Exits 0 if all checks pass, 1 if any fail.

Checks:
  1. Workflow–script consistency (every workflow references existing files)
  2. Prompt preamble safety (no pipe-delimited headers that trigger sonar filter)
  3. Workflow infrastructure (GH_TOKEN, git pull --rebase, search_recency_filter)
  4. Chatter schedule consistency (all 7 daily, staggered)
  5. Collector schedule consistency (all 7 daily, staggered)
  6. Python script imports (required imports present)
  7. JSON data integrity (schema_version, no future dates)
  8. Cron prompt file existence (every analyst cron references a file that exists)

Usage:
  python3 tools/preflight.py                    # run from repo root
  python3 tools/preflight.py --check workflows  # run specific check group
  python3 tools/preflight.py --verbose          # show passing checks too
"""

import argparse
import json
import os
import re
import sys
import glob
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ──────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent  # tools/ is one level deep

MONITORS = {
    "fcw": "fimi-cognitive-warfare",
    "gmm": "macro-monitor",
    "wdm": "democratic-integrity",
    "scem": "conflict-escalation",
    "esa": "european-strategic-autonomy",
    "agm": "ai-governance",
    "erm": "environmental-risks",
}

PIPELINE_STAGES = ["chatter", "collector", "weekly-research", "reasoner", "synthesiser"]

# Expected daily stagger for chatters (minute offsets)
CHATTER_STAGGER = {"fcw": 0, "gmm": 5, "wdm": 10, "scem": 15, "esa": 20, "agm": 25, "erm": 30}
# Expected daily stagger for collectors (minute offsets)
COLLECTOR_STAGGER = {"wdm": 0, "gmm": 5, "esa": 10, "fcw": 15, "agm": 20, "erm": 25, "scem": 30}

# ─── Result tracking ────────────────────────────────────────────

class Results:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def ok(self, check, detail=""):
        self.passed.append((check, detail))

    def fail(self, check, detail):
        self.failed.append((check, detail))

    def warn(self, check, detail):
        self.warnings.append((check, detail))

    def summary(self, verbose=False):
        if verbose:
            for check, detail in self.passed:
                print(f"  ✅ {check}" + (f" — {detail}" if detail else ""))
        for check, detail in self.warnings:
            print(f"  ⚠️  {check} — {detail}")
        for check, detail in self.failed:
            print(f"  ❌ {check} — {detail}")
        print()
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        print(f"  {len(self.passed)}/{total} passed, {len(self.warnings)} warnings, {len(self.failed)} failures")
        return len(self.failed) == 0

# ─── Check Groups ───────────────────────────────────────────────

def check_workflows(r: Results):
    """Verify workflow files reference scripts and prompts that exist."""
    wf_dir = REPO_ROOT / ".github" / "workflows"
    if not wf_dir.exists():
        r.fail("WORKFLOWS", f"Workflow directory not found: {wf_dir}")
        return

    for wf_file in sorted(wf_dir.glob("*.yml")):
        name = wf_file.name
        # Skip non-pipeline workflows
        if name in ("build.yml", "staging-deploy.yml", "compress-images.yml",
                     "inject-network-bar.yml", "generate-triage-strip.yml"):
            continue

        content = wf_file.read_text()

        # Check: workflow references a Python script that exists
        py_matches = re.findall(r'python3?\s+([\w/.-]+\.py)', content)
        for script_path in py_matches:
            full_path = REPO_ROOT / script_path
            if not full_path.exists():
                r.fail(f"WF-SCRIPT:{name}", f"References {script_path} which does not exist")
            else:
                r.ok(f"WF-SCRIPT:{name}", f"{script_path} exists")

        # Check: cron schedule is present and parseable
        cron_match = re.search(r'cron:\s*"([^"]+)"', content)
        if cron_match:
            cron_expr = cron_match.group(1)
            parts = cron_expr.split()
            if len(parts) != 5:
                r.fail(f"WF-CRON:{name}", f"Invalid cron expression: '{cron_expr}' (expected 5 fields)")
            else:
                r.ok(f"WF-CRON:{name}", f"Schedule: {cron_expr}")


def check_prompt_preambles(r: Results):
    """Verify no prompt files have pipe-delimited preamble headers (sonar safety trigger)."""
    # Check pipeline prompt files
    prompt_patterns = [
        REPO_ROOT / "pipeline" / "monitors" / "**" / "*-api-prompt.txt",
        REPO_ROOT / "pipeline" / "synthesisers" / "**" / "*-api-prompt.txt",
    ]

    checked = 0
    for pattern in prompt_patterns:
        for prompt_file in glob.glob(str(pattern), recursive=True):
            prompt_path = Path(prompt_file)
            content = prompt_path.read_text()
            checked += 1

            # Check FIRST 5 LINES ONLY for pipe-delimited preamble
            # (e.g., "# PROMPT: ... | VERSION: ... | UPDATED: ...")
            # Bottom-of-file version metadata comments are fine — sonar only reads
            # the top of the prompt for safety filtering.
            first_lines = "\n".join(content.split("\n")[:5])
            if re.search(r'^#\s+\w+:.*\|.*\w+:', first_lines, re.MULTILINE):
                r.fail(f"PREAMBLE:{prompt_path.name}",
                       "Contains pipe-delimited preamble header in first 5 lines — triggers sonar safety filter")
            else:
                r.ok(f"PREAMBLE:{prompt_path.name}", "Clean preamble")

    if checked == 0:
        r.warn("PREAMBLE", "No prompt files found to check")


def check_workflow_infrastructure(r: Results):
    """Verify all pipeline workflows have GH_TOKEN and git pull --rebase."""
    wf_dir = REPO_ROOT / ".github" / "workflows"
    if not wf_dir.exists():
        return

    pipeline_wfs = []
    for wf_file in sorted(wf_dir.glob("*.yml")):
        name = wf_file.name
        # Only check pipeline workflows (monitor-stage patterns)
        if not any(name.startswith(abbr + "-") for abbr in MONITORS):
            continue
        pipeline_wfs.append(wf_file)

    for wf_file in pipeline_wfs:
        name = wf_file.name
        content = wf_file.read_text()

        # Check: GH_TOKEN secret (needed for cross-repo reads)
        # Chatters and collectors that don't read from internal repo don't need GH_TOKEN
        needs_token = any(stage in name for stage in ["weekly-research", "reasoner", "collector"])
        if "secrets.GH_TOKEN" in content or "secrets.GITHUB_TOKEN" in content:
            r.ok(f"INFRA-TOKEN:{name}", "Has GH_TOKEN or GITHUB_TOKEN")
        elif "GH_TOKEN" in content:
            r.ok(f"INFRA-TOKEN:{name}", "Has GH_TOKEN env var")
        elif needs_token:
            r.warn(f"INFRA-TOKEN:{name}", "No GH_TOKEN — may fail on cross-repo reads")

        # Check: git pull --rebase (push race fix)
        if "git push" in content:
            if "git pull" in content and "rebase" in content:
                r.ok(f"INFRA-REBASE:{name}", "Has git pull --rebase before push")
            else:
                r.fail(f"INFRA-REBASE:{name}",
                       "Has git push but no git pull --rebase — push race risk")


def check_chatter_schedules(r: Results):
    """Verify all 7 chatters are daily with correct stagger."""
    wf_dir = REPO_ROOT / ".github" / "workflows"

    for abbr, expected_minute in CHATTER_STAGGER.items():
        wf_file = wf_dir / f"{abbr}-chatter.yml"
        if not wf_file.exists():
            r.fail(f"CHATTER-EXISTS:{abbr}", f"{abbr}-chatter.yml not found")
            continue

        content = wf_file.read_text()
        cron_match = re.search(r'cron:\s*"([^"]+)"', content)
        if not cron_match:
            r.fail(f"CHATTER-CRON:{abbr}", "No cron expression found")
            continue

        cron_expr = cron_match.group(1)
        parts = cron_expr.split()

        # Verify daily: day-of-week should be * (not a specific day)
        if parts[4] != "*":
            r.fail(f"CHATTER-DAILY:{abbr}",
                   f"Not daily — day-of-week is '{parts[4]}', expected '*'. Cron: {cron_expr}")
        else:
            r.ok(f"CHATTER-DAILY:{abbr}", f"Daily schedule confirmed: {cron_expr}")

        # Verify stagger minute
        actual_minute = int(parts[0]) if parts[0].isdigit() else -1
        if actual_minute != expected_minute:
            r.warn(f"CHATTER-STAGGER:{abbr}",
                   f"Minute is {actual_minute}, expected {expected_minute}. Cron: {cron_expr}")
        else:
            r.ok(f"CHATTER-STAGGER:{abbr}", f"Stagger correct: minute {actual_minute}")


def check_collector_schedules(r: Results):
    """Verify all 7 collectors are daily with correct stagger."""
    wf_dir = REPO_ROOT / ".github" / "workflows"

    for abbr, expected_minute in COLLECTOR_STAGGER.items():
        wf_file = wf_dir / f"{abbr}-collector.yml"
        if not wf_file.exists():
            r.fail(f"COLLECTOR-EXISTS:{abbr}", f"{abbr}-collector.yml not found")
            continue

        content = wf_file.read_text()
        cron_match = re.search(r'cron:\s*"([^"]+)"', content)
        if not cron_match:
            r.fail(f"COLLECTOR-CRON:{abbr}", "No cron expression found")
            continue

        cron_expr = cron_match.group(1)
        parts = cron_expr.split()

        if parts[4] != "*":
            r.fail(f"COLLECTOR-DAILY:{abbr}",
                   f"Not daily — day-of-week is '{parts[4]}'. Cron: {cron_expr}")
        else:
            r.ok(f"COLLECTOR-DAILY:{abbr}", f"Daily schedule confirmed: {cron_expr}")

        actual_minute = int(parts[0]) if parts[0].isdigit() else -1
        if actual_minute != expected_minute:
            r.warn(f"COLLECTOR-STAGGER:{abbr}",
                   f"Minute is {actual_minute}, expected {expected_minute}. Cron: {cron_expr}")
        else:
            r.ok(f"COLLECTOR-STAGGER:{abbr}", f"Stagger correct: minute {actual_minute}")


def check_python_scripts(r: Results):
    """Verify pipeline Python scripts have required imports and patterns."""
    pipeline_dir = REPO_ROOT / "pipeline" / "monitors"
    if not pipeline_dir.exists():
        r.warn("PY-SCRIPTS", "pipeline/monitors/ directory not found")
        return

    required_imports = {"json", "os", "pathlib"}

    for py_file in sorted(pipeline_dir.rglob("*.py")):
        name = py_file.relative_to(REPO_ROOT)
        content = py_file.read_text()

        # Check required imports
        found_imports = set()
        for line in content.split("\n"):
            imp_match = re.match(r'^import\s+(\w+)', line)
            if imp_match:
                found_imports.add(imp_match.group(1))
            frm_match = re.match(r'^from\s+(\w+)', line)
            if frm_match:
                found_imports.add(frm_match.group(1))

        missing = required_imports - found_imports
        if missing:
            r.warn(f"PY-IMPORTS:{py_file.name}", f"Missing imports: {', '.join(sorted(missing))}")
        else:
            r.ok(f"PY-IMPORTS:{py_file.name}", "All required imports present")

        # Check for hardcoded local paths (should use relative or env var)
        if "/home/user/" in content or "C:\\" in content:
            r.fail(f"PY-PATHS:{py_file.name}", "Contains hardcoded local path")
        else:
            r.ok(f"PY-PATHS:{py_file.name}", "No hardcoded local paths")


def check_json_data(r: Results):
    """Verify JSON data files have required fields and no future dates."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for slug in MONITORS.values():
        data_dir = REPO_ROOT / "static" / "monitors" / slug / "data"
        if not data_dir.exists():
            continue

        report_file = data_dir / "report-latest.json"
        if report_file.exists():
            try:
                with open(report_file) as f:
                    data = json.load(f)

                # Check schema_version
                sv = data.get("schema_version") or data.get("meta", {}).get("schema_version")
                if sv == "2.0":
                    r.ok(f"JSON-SCHEMA:{slug}", "schema_version 2.0")
                elif sv:
                    r.warn(f"JSON-SCHEMA:{slug}", f"schema_version is '{sv}', expected '2.0'")
                else:
                    r.warn(f"JSON-SCHEMA:{slug}", "No schema_version field found")

                # Check for future dates
                date_field = data.get("date") or data.get("meta", {}).get("date")
                if date_field and date_field > today:
                    r.fail(f"JSON-DATE:{slug}", f"Future date: {date_field} (today is {today})")
                elif date_field:
                    r.ok(f"JSON-DATE:{slug}", f"Date: {date_field}")

            except json.JSONDecodeError as e:
                r.fail(f"JSON-PARSE:{slug}", f"report-latest.json parse error: {e}")
        else:
            r.warn(f"JSON-EXISTS:{slug}", "report-latest.json not found")


def check_cron_prompts(r: Results):
    """Verify cron prompt files referenced in docs/crons/ exist."""
    crons_dir = REPO_ROOT / "docs" / "crons"
    if not crons_dir.exists():
        r.warn("CRON-PROMPTS", "docs/crons/ directory not found")
        return

    for md_file in sorted(crons_dir.glob("*-slimmed-analyst-cron.md")):
        name = md_file.name
        # These are the actual prompts — verify they're not redirect stubs
        content = md_file.read_text()
        if "Moved to asym-intel-internal" in content:
            r.fail(f"CRON-STUB:{name}", "File is a redirect stub — cron will load stub instead of prompt")
        elif len(content) < 500:
            r.warn(f"CRON-SIZE:{name}", f"Suspiciously small ({len(content)} bytes) — may be a stub")
        else:
            r.ok(f"CRON-PROMPT:{name}", f"Prompt file present ({len(content)} bytes)")


def check_monitor_completeness(r: Results):
    """Verify each monitor has all expected pipeline components."""
    for abbr, slug in MONITORS.items():
        monitor_dir = REPO_ROOT / "pipeline" / "monitors" / slug

        # Check expected files exist
        expected_scripts = ["collect.py", "weekly-research.py", f"{abbr}-reasoner.py"]
        for script in expected_scripts:
            script_path = monitor_dir / script
            if script_path.exists():
                r.ok(f"COMPLETENESS:{abbr}/{script}", "Exists")
            else:
                r.warn(f"COMPLETENESS:{abbr}/{script}", "Missing")

        # Check expected prompt files
        expected_prompts = [f"{abbr}-collector-api-prompt.txt", f"{abbr}-chatter-api-prompt.txt"]
        for prompt in expected_prompts:
            prompt_path = monitor_dir / prompt
            if prompt_path.exists():
                content = prompt_path.read_text()
                if len(content) < 50:
                    r.warn(f"COMPLETENESS:{abbr}/{prompt}", f"Empty or near-empty ({len(content)} bytes)")
                else:
                    r.ok(f"COMPLETENESS:{abbr}/{prompt}", "Exists")
            else:
                r.warn(f"COMPLETENESS:{abbr}/{prompt}", "Missing")



def check_frontend_patterns(r: Results):
    """SL-08 - Validate Sprint 1 shared library usage patterns in monitor HTML."""
    import re

    monitors_html_dir = REPO_ROOT / "static" / "monitors"
    if not monitors_html_dir.exists():
        r.warn("FE-SL08:frontend-patterns", "static/monitors dir not found - skipping")
        return

    SEVERITY_VARS = ["--critical", "--high", "--moderate", "--positive", "--contested"]
    html_files = list(monitors_html_dir.rglob("*.html"))
    r.ok("FE-SL08:html-files-found", f"{len(html_files)} HTML files scanned")

    badge_violations = []
    triage_incomplete = []
    radar_inline_css = []

    for html_path in html_files:
        try:
            text = html_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = html_path.relative_to(REPO_ROOT)

        # Rule 1: badge-confidence elements must not reference severity colour vars
        for m in re.finditer("badge-confidence", text):
            ctx_start = max(0, m.start() - 200)
            ctx_end = min(len(text), m.end() + 200)
            ctx = text[ctx_start:ctx_end]
            for svar in SEVERITY_VARS:
                if svar in ctx:
                    badge_violations.append(
                        f"{rel}: severity token {svar!r} found near badge-confidence"
                    )
                    break

        # Rule 2: triage-strip completeness
        if "triage-strip" in text:
            zone_pattern = 'data-triage-zone='
            zones = []
            for zm in re.finditer(zone_pattern, text):
                after = text[zm.end():zm.end() + 20].strip('"').strip("'").split('"')[0].split("'")[0]
                zones.append(after)
            required = {"kpis", "signal", "structural", "delta"}
            missing = required - set(zones)
            if missing:
                triage_incomplete.append(f"{rel}: missing triage zones {missing}")

        # Rule 3: inline radar CSS injection should be removed
        if "asym-radar-css" in text and "createElement" in text:
            radar_inline_css.append(str(rel))

    if badge_violations:
        for v in badge_violations:
            r.fail("FE-SL08:badge-confidence-severity", v)
    else:
        r.ok("FE-SL08:badge-confidence-no-severity", "No severity vars on badge-confidence elements")

    if triage_incomplete:
        for v in triage_incomplete:
            r.warn("FE-SL08:triage-strip-incomplete", v)
    else:
        r.ok("FE-SL08:triage-strip-zones", "All triage-strip elements have required zones (or none present)")

    if radar_inline_css:
        for v in radar_inline_css:
            r.warn("FE-SL08:radar-inline-css", f"{v}: inline asym-radar-css injection found - remove (CSS in base.css)")
    else:
        r.ok("FE-SL08:radar-inline-css-clean", "No inline radar CSS injection found")

# ─── Main ───────────────────────────────────────────────────────

CHECK_GROUPS = {
    "workflows": check_workflows,
    "preambles": check_prompt_preambles,
    "infrastructure": check_workflow_infrastructure,
    "chatters": check_chatter_schedules,
    "collectors": check_collector_schedules,
    "python": check_python_scripts,
    "json": check_json_data,
    "crons": check_cron_prompts,
    "completeness": check_monitor_completeness,
    "frontend": check_frontend_patterns,
}


def main():
    parser = argparse.ArgumentParser(description="Pre-flight checks for asym-intel pipeline")
    parser.add_argument("--check", choices=list(CHECK_GROUPS.keys()),
                        help="Run only a specific check group")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show passing checks too")
    args = parser.parse_args()

    print(f"\n  🛫 asym-intel preflight — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Repo root: {REPO_ROOT}\n")

    r = Results()

    groups = {args.check: CHECK_GROUPS[args.check]} if args.check else CHECK_GROUPS

    for group_name, check_fn in groups.items():
        print(f"  ── {group_name} ──")
        check_fn(r)
        print()

    print("  ── Summary ──")
    all_passed = r.summary(verbose=args.verbose)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
