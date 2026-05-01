#!/usr/bin/env python3
"""
tools/commons_drift_scan.py — Commons drift scanner (Phase 0.5 stub-and-walk).

Ratified by AD-2026-04-30-BL (W3.5 Phase 0.5).

Walks a calling per-project repo for the eight AD-2026-04-30-BK §D6(b)
forbidden re-implementation classes:

  2.1 Token systems and credibility-tell tokens
  2.2 Formatters (format* regex pattern over JS/TS/Python files)
  2.3 Hydration helpers and freshness-indicator components
  2.4 Empty-state components
  2.5 Three-layer encounter scaffolding
  2.6 Paywall-aware CTA scaffolding
  2.7 methodology_mode / rationale_mode shell wiring
  2.8 Engineering-exposure-zero filters

For each match, the scanner records a hit. At Phase 0.5 the determination
of "is this re-implementing or consuming from commons?" is deferred —
fe-commons/ is empty / nascent, so all matches are reported as advisory.
Phase 1+ closes the determination logic per pattern as primitives land
in fe-commons/.

Exit codes (mode-aware):
  observe-mode:  always 0  (advisory; PR not blocked)
  enforce-mode:  0 if no hits, 1 if any re-implementation hit, 2 internal
                 error. Enforce-mode is gated by AD-BM's 2026-05-14 review
                 trigger and not the default at Phase 0.5.

Usage (called by .github/workflows/commons-drift-lint.yml):

  python3 tools/commons_drift_scan.py \\
      --calling-repo caller \\
      --commons-root asym-intel-main-staging/fe-commons \\
      --scan-paths "." \\
      --report-out caller/_commons-drift-out/commons-drift-report.json \\
      --mode observe
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCANNER_VERSION = "0.5.0-stub"
AD_REFERENCE = "AD-2026-04-30-BL"
AD_BK_REFERENCE = "AD-2026-04-30-BK §D6(b)"

# ─── Pattern classes (AD-BK §D6(b) eight classes) ──────────────────────────
#
# Each pattern is a Phase-0.5 stub: a conservative regex that catches the
# obvious re-implementation shape. Phase 1+ refines each as primitives land
# in fe-commons/ and the "consuming vs. re-implementing" distinction
# becomes meaningful.
#
# File extension scopes: ts/tsx/js/jsx/py/html/css. Adjust per pattern.
# ───────────────────────────────────────────────────────────────────────────

DEFAULT_FILE_GLOBS = ("*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.html", "*.css")

# Files / dirs we never scan.
SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", ".venv", "venv",
    "__pycache__", ".pytest_cache", "_commons-drift-out", "fe-commons-staging",
    "asym-intel-main-staging",
}

# When the calling repo has staged commons under one of these dirs, scanner
# treats matches inside as "consuming-from-commons" and excludes them.
COMMONS_STAGING_HINTS = (
    "site/_commons", "prototype/_commons", "_commons", "fe-commons-staging",
    "asym-intel-main-staging/fe-commons",
)

PATTERNS: tuple[dict, ...] = (
    {
        "id": "D6b.1",
        "name": "Token systems and credibility-tell tokens",
        "regex": re.compile(
            # Match snake_case, kebab-case, camelCase, and PascalCase forms.
            r"(?i)\b(credibility[_\-]?tell\w*|tell[_\-]?token\w*|"
            r"credibilityTell\w*|tellToken\w*|"
            r"design[_\-]?tokens?\w*|designTokens?\w*|"
            r"token[_\-]?(system|registry|map)\w*|"
            r"token(System|Registry|Map)\w*)\b"
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.css", "*.html", "*.py"),
        "hint": "Token systems are commons. Import from fe-commons/tokens/.",
    },
    {
        "id": "D6b.2",
        "name": "Formatters",
        "regex": re.compile(
            r"\bfunction\s+format[A-Z]\w*\s*\(|\bconst\s+format[A-Z]\w*\s*=|"
            r"\bdef\s+format_\w+\s*\("
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.py"),
        "hint": "Formatters are commons. Import from fe-commons/format/.",
    },
    {
        "id": "D6b.3",
        "name": "Hydration helpers and freshness-indicator components",
        "regex": re.compile(
            r"(?i)\b(hydration[_\-]?helper|freshness[_\-]?indicator|"
            r"as[_\-]?of[_\-]?stamp|last[_\-]?updated[_\-]?stamp)\b"
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.html", "*.py"),
        "hint": "Hydration/freshness components are commons. Import from fe-commons/hydration/.",
    },
    {
        "id": "D6b.4",
        "name": "Empty-state components",
        "regex": re.compile(
            r"(?i)\b(empty[_\-]?state|no[_\-]?data[_\-]?(view|panel|component))\b"
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.html"),
        "hint": "Empty-state components are commons. Import from fe-commons/empty-state/.",
    },
    {
        "id": "D6b.5",
        "name": "Three-layer encounter scaffolding",
        "regex": re.compile(
            r"(?i)\b(three[_\-]?layer[_\-]?encounter|encounter[_\-]?scaffold|"
            r"layer[_\-]?one[_\-]?encounter|layer[_\-]?two[_\-]?encounter)\b"
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.html"),
        "hint": "Encounter scaffolding is commons. Import from fe-commons/encounter/.",
    },
    {
        "id": "D6b.6",
        "name": "Paywall-aware CTA scaffolding",
        "regex": re.compile(
            r"(?i)\b(paywall[_\-]?cta|cta[_\-]?paywall|"
            r"paywall[_\-]?aware[_\-]?(cta|button|link))\b"
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.html"),
        "hint": "Paywall-aware CTAs are commons. Import from fe-commons/paywall-cta/.",
    },
    {
        "id": "D6b.7",
        "name": "methodology_mode / rationale_mode shell wiring",
        "regex": re.compile(
            r"\b(methodology_mode|rationale_mode)\b"
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.html", "*.py"),
        "hint": "methodology_mode/rationale_mode shell is commons. Import from fe-commons/mode-shell/.",
    },
    {
        "id": "D6b.8",
        "name": "Engineering-exposure-zero filters",
        "regex": re.compile(
            r"(?i)\b(engineering[_\-]?exposure[_\-]?zero|"
            r"strip[_\-]?engineering[_\-]?(detail|exposure))\b"
        ),
        "scope_globs": ("*.ts", "*.tsx", "*.js", "*.jsx", "*.py", "*.html"),
        "hint": "Engineering-exposure-zero filter is commons. Import from fe-commons/exposure-filter/.",
    },
)


@dataclass
class Hit:
    pattern_id: str
    pattern_name: str
    file: str
    line: int
    excerpt: str
    classification: str  # "advisory" at Phase 0.5; "re-implementation" / "consuming" once determinable
    hint: str


@dataclass
class Report:
    scanner_version: str
    ad_reference: str
    ad_bk_reference: str
    generated_at: str
    mode: str
    calling_repo: str
    commons_root: str
    commons_primitive_count: int
    hits: list[Hit] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


def _file_in_skip_dir(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root)
    return any(part in SKIP_DIRS for part in rel.parts)


def _file_in_commons_staging(path: Path, repo_root: Path) -> bool:
    rel_str = str(path.relative_to(repo_root)).replace("\\", "/")
    return any(rel_str.startswith(hint) or f"/{hint}/" in f"/{rel_str}/" for hint in COMMONS_STAGING_HINTS)


def _iter_candidate_files(repo_root: Path, scan_paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for sp in scan_paths:
        base = (repo_root / sp).resolve()
        if not base.exists():
            continue
        if base.is_file():
            out.append(base)
            continue
        for glob_pat in DEFAULT_FILE_GLOBS:
            for p in base.rglob(glob_pat):
                if not p.is_file():
                    continue
                if _file_in_skip_dir(p, repo_root):
                    continue
                out.append(p)
    # de-dupe while preserving order
    seen: set[Path] = set()
    deduped: list[Path] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def _count_commons_primitives(commons_root: Path) -> int:
    """At Phase 0.5, fe-commons/ may not exist or be empty.

    A 'primitive' is any file under fe-commons/ that is not a README,
    LICENSE, or .md doc. This is a conservative best-effort count;
    refined in Phase 1+ once primitive layout is ratified.
    """
    if not commons_root.exists() or not commons_root.is_dir():
        return 0
    count = 0
    for p in commons_root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in {".md", ".txt"}:
            continue
        if p.name.lower() in {"readme", "license", "license.md"}:
            continue
        count += 1
    return count


def _classify(hit_path: Path, repo_root: Path) -> str:
    """Phase 0.5 classification.

    If the hit is inside a commons-staging directory, classify as
    "consuming" (i.e. the project pulled commons in at build time,
    so a token-system match there is the staged commons itself).

    Otherwise, classify as "advisory" — Phase 0.5 cannot yet distinguish
    re-implementation from consumption-via-import because primitives
    don't exist to compare against. Phase 1+ refines this.
    """
    if _file_in_commons_staging(hit_path, repo_root):
        return "consuming"
    return "advisory"


def scan(repo_root: Path, commons_root: Path, scan_paths: list[str]) -> Report:
    candidate_files = _iter_candidate_files(repo_root, scan_paths)
    primitive_count = _count_commons_primitives(commons_root)

    report = Report(
        scanner_version=SCANNER_VERSION,
        ad_reference=AD_REFERENCE,
        ad_bk_reference=AD_BK_REFERENCE,
        generated_at=datetime.now(timezone.utc).isoformat(),
        mode="",  # filled by main()
        calling_repo=str(repo_root),
        commons_root=str(commons_root),
        commons_primitive_count=primitive_count,
    )

    per_pattern_count: dict[str, int] = {p["id"]: 0 for p in PATTERNS}
    advisory_count = 0
    consuming_count = 0

    for f in candidate_files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(f.relative_to(repo_root))
        for pattern in PATTERNS:
            # Scope check: file extension must match
            if not any(f.match(g) for g in pattern["scope_globs"]):
                continue
            for m in pattern["regex"].finditer(text):
                # locate line number
                line_no = text.count("\n", 0, m.start()) + 1
                line_start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.end())
                if line_end == -1:
                    line_end = len(text)
                excerpt = text[line_start:line_end].strip()[:240]
                classification = _classify(f, repo_root)
                report.hits.append(Hit(
                    pattern_id=pattern["id"],
                    pattern_name=pattern["name"],
                    file=rel,
                    line=line_no,
                    excerpt=excerpt,
                    classification=classification,
                    hint=pattern["hint"],
                ))
                per_pattern_count[pattern["id"]] += 1
                if classification == "advisory":
                    advisory_count += 1
                elif classification == "consuming":
                    consuming_count += 1

    report.summary = {
        "files_scanned": len(candidate_files),
        "total_hits": len(report.hits),
        "advisory_hits": advisory_count,
        "consuming_hits": consuming_count,
        "reimplementation_hits": 0,  # Phase 1+ will populate once classifier learns the distinction
        "per_pattern_count": per_pattern_count,
    }
    return report


def render_summary(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"Scanner: {report.scanner_version}  AD: {report.ad_reference}")
    lines.append(f"Mode:    {report.mode}")
    lines.append(f"Commons primitives detected: {report.commons_primitive_count}")
    lines.append(f"Files scanned: {report.summary['files_scanned']}")
    lines.append(f"Total hits:    {report.summary['total_hits']}  "
                 f"(advisory: {report.summary['advisory_hits']}, "
                 f"consuming: {report.summary['consuming_hits']}, "
                 f"re-implementation: {report.summary['reimplementation_hits']})")
    lines.append("")
    lines.append("Hits per AD-BK §D6(b) class:")
    for pattern in PATTERNS:
        c = report.summary["per_pattern_count"][pattern["id"]]
        lines.append(f"  {pattern['id']}  {pattern['name']:<55} {c}")
    if report.hits:
        lines.append("")
        lines.append("Top hits (first 20):")
        for h in report.hits[:20]:
            lines.append(f"  [{h.classification}] {h.pattern_id} {h.file}:{h.line}  {h.excerpt[:120]}")
    if report.commons_primitive_count == 0:
        lines.append("")
        lines.append("NOTE: fe-commons/ has no primitives yet. Phase 0.5 stub-and-walk: all hits are")
        lines.append("      reported as advisory and the scanner exits 0 in observe-mode.")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Commons drift scanner (Phase 0.5 stub-and-walk)")
    p.add_argument("--calling-repo", required=True, help="Path to the calling per-project repo root")
    p.add_argument("--commons-root", required=True, help="Path to fe-commons/ checked out from asym-intel-main")
    p.add_argument("--scan-paths", default=".", help="Comma-separated paths within calling repo to scan")
    p.add_argument("--report-out", required=True, help="Path to write JSON report")
    p.add_argument("--mode", choices=("observe", "enforce"), default="observe")
    args = p.parse_args()

    repo_root = Path(args.calling_repo).resolve()
    commons_root = Path(args.commons_root).resolve()
    scan_paths = [s.strip() for s in args.scan_paths.split(",") if s.strip()]

    if not repo_root.exists():
        print(f"ERROR: calling repo path does not exist: {repo_root}", file=sys.stderr)
        return 2

    report = scan(repo_root, commons_root, scan_paths)
    report.mode = args.mode

    # write JSON report
    out = Path(args.report_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(report), indent=2, default=str), encoding="utf-8")

    # print summary to stdout (workflow tees this into a file too)
    print(render_summary(report))

    if args.mode == "observe":
        return 0

    # enforce-mode: only block on re-implementation hits.
    # Phase 0.5 cannot distinguish re-implementation from advisory yet, so
    # enforce-mode is effectively dormant until Phase 1+ classifier lands.
    # See AD-2026-04-30-BL review trigger 2026-05-14 for the flip decision.
    if report.summary["reimplementation_hits"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

