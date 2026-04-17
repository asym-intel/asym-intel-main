#!/usr/bin/env python3
"""
preflight_mobile.py — engine-wide mobile/tablet regression checks.

Governed by: ops/specs/mobile-tablet-spec.md
Incident log: ops/mobile-tablet-log.md

Rules are derived from incidents logged in mobile-tablet-log.md.
Every rule must cite at least one LOG-YYYY-MM-DD-NNN incident in its docstring
(per spec §13 — "rules start narrow, expand as classes recur").

Exit codes:
    0 — all checks passed
    1 — one or more warnings (advisory mode; first 2 weeks per rule)
    2 — one or more failures (enforced mode)

Usage:
    python tools/preflight_mobile.py [--fix-mode]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ─── Rule registry ─────────────────────────────────────────────────────────
# Each rule: (name, description, check_fn, severity, motivating_incidents)
# severity: "warn" (advisory) | "fail" (enforced)

FAILURES: list[str] = []
WARNINGS: list[str] = []


def check_viewport_meta(html_files: list[Path]) -> None:
    """
    R-MV-001: every HTML page must have width=device-width viewport meta.

    Spec §3. Motivating: baseline engine invariant.
    """
    pattern = re.compile(r'<meta\s+name="viewport"[^>]*width=device-width', re.I)
    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "<head" in text and not pattern.search(text):
            FAILURES.append(
                f"R-MV-001 [viewport-meta]: {path.relative_to(REPO_ROOT)} — "
                f"missing <meta name='viewport' content='width=device-width, initial-scale=1'>"
            )


def check_overflow_x_hidden(css_files: list[Path]) -> None:
    """
    R-MV-002: never use `overflow-x: hidden` on body/html/main/layout.

    Spec §4. Engine rule (existing): `overflow-x: clip` instead, preserves
    position:sticky children. Already enforced by validate-blueprint.py on
    asym-intel.info; extending to sister-site CSS via this rule.
    """
    bad = re.compile(
        r'(body|html|main|\.monitor-layout|\.monitor-main|\.ai-main|\.site-layout)'
        r'[^{]*\{[^}]*overflow-x\s*:\s*hidden',
        re.I | re.DOTALL,
    )
    for path in css_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if bad.search(text):
            FAILURES.append(
                f"R-MV-002 [overflow-x-hidden]: {path.relative_to(REPO_ROOT)} — "
                f"use `overflow-x: clip` not `hidden` on body/html/main/layout"
            )


def check_radar_wrap_fixed_height(css_files: list[Path]) -> None:
    """
    R-MV-003: .asym-radar-wrap (and similar grid containers that stack on mobile)
    must reset `height` to auto below the stacking breakpoint.

    Spec §7, §10. Motivating: LOG-2026-04-17-001 — fixed 480px height on
    .asym-radar-wrap caused dim list to overflow into next module-section
    when grid collapsed to single column at max-width: 768px, creating
    "Critical Materials" / "Domain Tracker" visual merge on ESA dashboard.
    """
    for path in css_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        # Look for .asym-radar-wrap with a fixed height
        fixed_height = re.search(
            r'\.asym-radar-wrap\s*\{[^}]*height\s*:\s*\d+\s*(px|rem|em|vh)',
            text, re.I | re.DOTALL,
        )
        if not fixed_height:
            continue
        # Look for an override inside any max-width: 768px or 1024px media query:
        # `.asym-radar-wrap { ... height: auto ... }`.
        # Using a simpler two-step check because nested brace regex is fragile.
        override = False
        for m in re.finditer(r'@media[^{]*max-width\s*:\s*(768|1024)px[^{]*\{', text, re.I):
            # Find the balanced closing brace of this @media block (simple scan).
            start = m.end()
            depth = 1
            i = start
            while i < len(text) and depth > 0:
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                i += 1
            block = text[start:i]
            # Inside the media block, look for .asym-radar-wrap { ... height: auto ... }
            wrap_rules = re.finditer(r'\.asym-radar-wrap\s*\{([^}]*)\}', block, re.I)
            for wr in wrap_rules:
                if re.search(r'height\s*:\s*auto', wr.group(1), re.I):
                    override = True
                    break
            if override:
                break
        if fixed_height and not override:
            FAILURES.append(
                f"R-MV-003 [radar-fixed-height]: {path.relative_to(REPO_ROOT)} — "
                f".asym-radar-wrap has fixed height but no `height: auto` override below 768px. "
                f"Causes section merge on mobile (see LOG-2026-04-17-001)."
            )


def check_nav_logo_nowrap(css_files: list[Path]) -> None:
    """
    R-MV-004: nav/header logo anchors should set white-space: nowrap OR be
    wrapped so domains (e.g. a-i.gi) don't break mid-hyphen.

    Spec §9. Motivating: LOG-2026-04-17-002 — "Asymmetric Intelligence · a-i.gi"
    wrapped to 3 lines at ≤375px with domain broken as `a-` / `i.gi`.

    ADVISORY (warn) — heuristic rule. False positives expected. Promote to fail
    after manual review across sister sites.
    """
    for path in css_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        # Find any .site-header, .nav-brand, .logo, .monitor-nav__brand with white-space: normal
        selectors = ['.site-header', '.nav-brand', '.logo', '.monitor-nav__brand',
                     '.header-brand', '.ai-logo']
        for sel in selectors:
            rule = re.search(
                re.escape(sel) + r'[^{}]*\{[^}]*\}', text, re.DOTALL,
            )
            if rule and 'white-space' not in rule.group(0):
                WARNINGS.append(
                    f"R-MV-004 [nav-logo-wrap]: {path.relative_to(REPO_ROOT)} — "
                    f"{sel} has no `white-space` rule; if it contains a domain, risk of "
                    f"mid-word wrap (see LOG-2026-04-17-002)."
                )


def check_input_font_size(css_files: list[Path]) -> None:
    """
    R-MV-005: form inputs below 16px trigger iOS auto-zoom.

    Spec §5, §11. ADVISORY — future incidents will promote.
    """
    pattern = re.compile(
        r'(input|textarea|select)[^{]*\{[^}]*font-size\s*:\s*(\d+(?:\.\d+)?)\s*px',
        re.I | re.DOTALL,
    )
    for path in css_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            size = float(m.group(2))
            if size < 16:
                WARNINGS.append(
                    f"R-MV-005 [input-font-zoom]: {path.relative_to(REPO_ROOT)} — "
                    f"input font-size {size}px < 16px; triggers iOS auto-zoom."
                )


# ─── Runner ────────────────────────────────────────────────────────────────


def collect_files() -> tuple[list[Path], list[Path]]:
    """Collect HTML and CSS files under static/, layouts/, assets/."""
    html_roots = [REPO_ROOT / "static", REPO_ROOT / "layouts", REPO_ROOT / "assets"]
    css_roots = [REPO_ROOT / "static", REPO_ROOT / "assets"]
    htmls, csss = [], []
    for root in html_roots:
        if root.exists():
            htmls.extend(root.rglob("*.html"))
    for root in css_roots:
        if root.exists():
            csss.extend(root.rglob("*.css"))
    # Exclude docs/ (generated output) and archives
    htmls = [p for p in htmls if "/docs/" not in str(p) and "/archives/" not in str(p)]
    csss = [p for p in csss if "/archives/" not in str(p)]
    return htmls, csss


def main() -> int:
    htmls, csss = collect_files()
    print(f"preflight_mobile: scanning {len(htmls)} HTML + {len(csss)} CSS files")

    check_viewport_meta(htmls)
    check_overflow_x_hidden(csss)
    check_radar_wrap_fixed_height(csss)
    check_nav_logo_nowrap(csss)
    check_input_font_size(csss)

    if WARNINGS:
        print(f"\n⚠️  {len(WARNINGS)} warnings (advisory):")
        for w in WARNINGS:
            print(f"   {w}")
    if FAILURES:
        print(f"\n❌ {len(FAILURES)} failures:")
        for f in FAILURES:
            print(f"   {f}")
        return 2
    if WARNINGS:
        return 1
    print("\n✅ preflight_mobile: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
