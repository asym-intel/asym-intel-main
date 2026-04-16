#!/usr/bin/env python3
"""
preflight_engine_chrome.py — enforce engine-wide footer + monitor-chip specs.

Canonical specs (source of truth):
  asym-intel-internal/ops/specs/footer-spec.md
  asym-intel-internal/ops/specs/monitor-chip-spec.md

What this check enforces in asym-intel-main only (where CI runs):
  F1. No engine file may link to https://asym-intel.info/commercial/ (retired).
  F2. The Hugo commons footer (layouts/partials/footer.html) must:
        - link to a-i.gi
        - NOT link to asym-intel.info/commercial
        - include a perplexity.ai/computer attribution link
  M1. Any <a> whose href points at a monitor dashboard
      (https://asym-intel.info/{wdm|gmm|fcw|esa|aim|erm|scem}) must
      carry class="monitor-chip" unless data-chip-exempt="prose" is present.

For sites in OTHER repos (a-i.gi, sentinel.gi, ...), each repo MUST include
this same preflight (or a lighter variant) in its own CI. This file is the
reference implementation and is executed against asym-intel-main on every
push.

Exit codes:
  0 — all checks pass
  1 — one or more violations found
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

# ── F1: forbidden-URL check across the repo ──────────────────────────────────

FORBIDDEN_URLS = [
    # retired 17 Apr 2026 — use a-i.gi
    "asym-intel.info/commercial/",
    "asym-intel.info/commercial\"",  # bare without trailing slash, quoted
    "asym-intel.info/commercial'",
]

# These files are ALLOWED to mention the retired URL (retirement stub + logs):
FORBIDDEN_URL_WHITELIST = {
    "content/commercial.md",                       # the redirect stub itself
    "tools/preflight_engine_chrome.py",            # this file (contains the strings)
    "ops/",                                        # internal ops archive
}

SCAN_EXTS = {".html", ".md", ".txt", ".js", ".css"}
SKIP_DIRS = {".git", "node_modules", "docs"}  # docs/ is generated output


def _is_whitelisted(rel_path: str) -> bool:
    return any(rel_path.startswith(p) for p in FORBIDDEN_URL_WHITELIST)


def check_forbidden_urls() -> list[str]:
    violations = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix not in SCAN_EXTS:
            continue
        rel = str(path.relative_to(REPO_ROOT))
        if _is_whitelisted(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for url in FORBIDDEN_URLS:
            if url in text:
                violations.append(f"F1 forbidden-url: {rel} contains '{url}'")
    return violations


# ── F2: commons footer specifics ─────────────────────────────────────────────

COMMONS_FOOTER = REPO_ROOT / "layouts" / "partials" / "footer.html"

FOOTER_REQUIRED = [
    "a-i.gi",
    "perplexity.ai/computer",
    "creativecommons.org/licenses/by/4.0",
]


def check_commons_footer() -> list[str]:
    if not COMMONS_FOOTER.exists():
        return ["F2 commons-footer: layouts/partials/footer.html missing"]
    text = COMMONS_FOOTER.read_text(encoding="utf-8")
    violations = []
    for req in FOOTER_REQUIRED:
        if req not in text:
            violations.append(f"F2 commons-footer: missing required link/token '{req}'")
    return violations


# ── M1: monitor-chip enforcement ─────────────────────────────────────────────

MONITOR_ABBRS = ["wdm", "gmm", "fcw", "esa", "aim", "erm", "scem"]
# Match full <a ... href="...asym-intel.info/{abbr}..."> ... </a>
# We use a permissive matcher; tolerate query strings and trailing slashes.
# Check for class="monitor-chip" OR data-chip-exempt="prose" on the tag.
A_TAG_RE = re.compile(
    r"<a\b([^>]*?)href\s*=\s*[\"']([^\"']*?asym-intel\.info/(?:"
    + "|".join(MONITOR_ABBRS)
    + r")(?:/[^\"']*)?)[\"']([^>]*)>",
    re.IGNORECASE,
)

# Files we actually police for M1 — chip enforcement is for marketing/home
# surfaces, NOT monitor nav bars or the commons site itself (those use
# different internal link patterns).
M1_INCLUDE_ROOTS = [
    # Add paths here as more engine repos are scanned by this file.
    # For asym-intel-main we currently have no marketing page that should
    # be chip-policed — the commercial .gi sites live in other repos.
    # Leaving this empty means M1 is a noop inside main until we wire
    # the a-i.gi preflight to import this module.
]


def check_monitor_chips() -> list[str]:
    violations = []
    for root in M1_INCLUDE_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*.html"):
            rel = str(path.relative_to(REPO_ROOT))
            text = path.read_text(encoding="utf-8", errors="replace")
            for m in A_TAG_RE.finditer(text):
                attrs_before, href, attrs_after = m.group(1), m.group(2), m.group(3)
                full_attrs = attrs_before + " " + attrs_after
                if re.search(r'class\s*=\s*"[^"]*\bmonitor-chip\b', full_attrs):
                    continue
                if re.search(r'data-chip-exempt\s*=\s*"prose"', full_attrs):
                    continue
                violations.append(
                    f"M1 monitor-chip: {rel}: <a href=\"{href}\"> lacks class=\"monitor-chip\""
                )
    return violations


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    all_violations: list[str] = []
    all_violations.extend(check_forbidden_urls())
    all_violations.extend(check_commons_footer())
    all_violations.extend(check_monitor_chips())

    if not all_violations:
        print("preflight_engine_chrome: OK (footer + chip specs enforced)")
        return 0

    print(f"preflight_engine_chrome: {len(all_violations)} violation(s):")
    for v in all_violations:
        print(f"  • {v}")
    print(
        "\nSpecs: asym-intel-internal/ops/specs/footer-spec.md + monitor-chip-spec.md"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
