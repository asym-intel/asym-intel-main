#!/usr/bin/env python3
"""
public_surface_audit.py — IP-leak scanner for asym-intel.info public surface.

Scans the public-served filesystem (static/ and docs/) for sensitive content
that should not be exposed to end users. Read-only; emits findings to stdout
+ JSON. Exits 1 on any HARD-FAIL hit so it can gate CI.

Scope:
  PUBLIC roots (default scan): static/ and docs/
  EXCLUDED:                    .git/, node_modules/, archive/, *.lock

Redline categories (anchored to real 2026-04-20 incident + platform-config):
  L1 CREDENTIAL_TOKEN     [hard-fail] WP app-password shape "XXXX XXXX ... " (4-char groups)
  L2 PLATFORM_USER        [hard-fail] founder email peterhowitt@gmail.com / @ramparts.gi
  L3 INTERNAL_REPO_REF    [hard-fail] "asym-intel-internal", "asym-intel-engine"
  L4 INTERNAL_COMMIT_SHA  [warn]      bare 7-40 hex SHA in HTML/JSON content (excluding pinned action versions)
  L5 METHODOLOGY_LEAK     [hard-fail] phrases that disclose internal incidents/guardrails:
                                       "rest_not_logged_in", "WP_APP_PASS", "WP_USER",
                                       "R1-R5 guardrails", "thin-frontend adapter",
                                       "hallucinated_source", "credential rotated",
                                       "kj_with_sources", "kj_total", "structured_claims"
  L6 INTERNAL_PATH_REF    [warn]      "platform-config.md", "ENGINE-RULES.md", "notes-for-computer.md"
  L7 METHODOLOGY_VOCAB    [hard-fail] pipeline methodology vocabulary on public surface:
                                       "interpret", "interpreter", "compose", "composer",
                                       "applier", "curate", "curator", "reasoner",
                                       "synthesiser", "synthesizer", "chatter",
                                       "weekly-research", "weekly_research",
                                       "phase a", "phase b", "cascade", "challenger",
                                       "pipeline-dispatcher", "dispatcher",
                                       "sonar-pro", "sonar-deep-research", "sonar-reasoning"
                                       Note: "review" and "apply" deliberately excluded
                                       (too common in English; covered indirectly by L6 path patterns).

Allowlist:
  Lines matching tools/public_surface_audit.allowlist (one regex per line) are skipped.
  Used for legitimate exposures: e.g. a public methodology page that names "R1-R5"
  intentionally, after governance review.

Run:
    python3 tools/public_surface_audit.py                  # scan repo root
    python3 tools/public_surface_audit.py --root .         # explicit
    python3 tools/public_surface_audit.py --json           # machine-readable
    python3 tools/public_surface_audit.py --strict         # warns -> hard-fail

Exit codes:
    0  no hard-fail hits
    1  one or more hard-fail hits (CI-blocking)
    2  invocation/IO error

Invoked by:
    .github/workflows/preflight-ci.yml (planned)
    Manual: before every cron unpause / new public page deploy
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Pattern

# ── Configuration ─────────────────────────────────────────────────────────────

# Default scope for this PR: static/ only.
# docs/ contains internal IP that needs a separate triage sprint before being
# brought under this scanner. Override with --public-roots static docs after
# that triage.
DEFAULT_PUBLIC_ROOTS = ("static",)
EXCLUDE_DIRS = {".git", "node_modules", "archive", "session-artefacts", "tools/fixtures"}
SCAN_EXTENSIONS = {".html", ".htm", ".json", ".js", ".css", ".xml", ".txt", ".md"}

# Files we never want to scan even if under public roots
EXCLUDE_FILE_GLOBS = (
    "package-lock.json",
    "*.min.js",
    "*.min.css",
)

# ── Redline patterns ──────────────────────────────────────────────────────────

@dataclass
class Rule:
    id: str
    severity: str           # "hard-fail" | "warn"
    description: str
    pattern: Pattern[str]
    # If the matched line also contains one of these tokens, treat as legitimate
    line_allowlist_substrings: tuple = ()


RULES: List[Rule] = [
    # L1 — WP application-password shape: 6 groups of mixed-alphanumeric (must contain
    # both letters AND digits in the overall sequence to avoid plain-English false positives).
    # WordPress generates app-passwords as 24 chars in 6 groups of 4 with both upper, lower, and digits.
    # Example from leak: "RHD2 dBK6 Ik8a pP9d PbRQ evsa", "W6V9 C3nr 9ogf snGu RR46 Di34"
    # Rejects: "more harm than good" (all-letter), "auto auto auto" (repeat), "rate from 2025 will" (no mixed-class group).
    Rule(
        id="L1_CREDENTIAL_TOKEN",
        severity="hard-fail",
        description="WordPress application-password shape (6 mixed-alnum groups of 4) in public surface",
        # Each group must be 4 chars and contain at least one digit (forces alphanumeric mix).
        # Then require ≥4 such groups in sequence (real WP shape is 6, but 4+ is a strong signal).
        pattern=re.compile(r"\b(?:(?=[A-Za-z0-9]{4}\b)(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{4}\s){3,}(?=[A-Za-z0-9]{4}\b)(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{4}\b"),
    ),
    Rule(
        id="L2_PLATFORM_USER",
        severity="hard-fail",
        description="Founder/operator email exposed in public surface",
        pattern=re.compile(r"peterhowitt@(?:gmail\.com|ramparts\.gi)", re.IGNORECASE),
    ),
    Rule(
        id="L3_INTERNAL_REPO_REF",
        severity="hard-fail",
        description="Internal repo name referenced on public surface",
        pattern=re.compile(r"\basym-intel-(?:internal|engine)\b"),
    ),
    Rule(
        id="L4_INTERNAL_COMMIT_SHA",
        severity="warn",
        description="Bare git SHA in public content (verify intentional)",
        # Match 7-40 hex with at least one letter (excludes all-digit constants/timestamps).
        # Negative lookbehind/lookahead avoids pinned action versions (`@<sha>`) and slashes.
        # URL-context filtering happens in scan_file (L4 lines containing http(s):// are skipped).
        pattern=re.compile(r"(?<![@/\w])\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b(?![\w@])"),
    ),
    Rule(
        id="L5_METHODOLOGY_LEAK",
        severity="hard-fail",
        description="Internal methodology / incident-detail phrase on public surface",
        pattern=re.compile(
            r"\b(?:"
            r"rest_not_logged_in|WP_APP_PASS|WP_USER|"
            r"R1-R5\s+guardrails|thin-frontend\s+adapter|"
            r"hallucinated_source|credential\s+rotated|"
            r"kj_with_sources|kj_total|structured_claims"
            r")\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        id="L6_INTERNAL_PATH_REF",
        severity="warn",
        description="Reference to internal-only doc/config path",
        pattern=re.compile(r"\b(?:platform-config\.md|ENGINE-RULES\.md|notes-for-computer\.md|COMPUTER-core\.md)\b"),
    ),
    # L7 — Pipeline methodology vocabulary on public surface.
    # Triggered by AD-2026-04-28-AZ (Sprint AZ public-surface simplification).
    # The public surface MUST NOT name internal pipeline stations or models.
    # Operator-facing surfaces (asym-intel-internal/, ops.asym-intel.info) are
    # exempt by definition (they're not under static/).
    #
    # Note: "review" and "apply" are deliberately NOT in the term list — they
    # are common English words and would generate too many false positives.
    # The pipeline stations "review" and "apply" instead surface as the
    # per-station JSON paths (e.g. `pipeline/monitors/{slug}/review/`) which
    # L6 already covers under internal-doc-paths.
    Rule(
        id="L7_METHODOLOGY_VOCAB",
        severity="hard-fail",
        description="Pipeline methodology vocabulary on public surface",
        pattern=re.compile(
            r"\b(?:"
            r"interpret|interpreter|"
            r"compose|composer|"
            r"applier|curate|curator|"
            r"reasoner|synthesiser|synthesizer|"
            r"chatter|"
            r"weekly-research|weekly_research|"
            r"phase\s+[ab]|cascade|"
            r"challenger|"
            r"pipeline-dispatcher|dispatcher|"
            r"sonar-pro|sonar-deep-research|sonar-reasoning"
            r")\b",
            re.IGNORECASE,
        ),
    ),
]


# ── Findings ──────────────────────────────────────────────────────────────────

@dataclass
class Finding:
    rule_id: str
    severity: str
    file: str
    line: int
    column: int
    excerpt: str
    matched: str


# ── Walking ───────────────────────────────────────────────────────────────────

def iter_public_files(root: Path, public_roots: tuple) -> List[Path]:
    out: List[Path] = []
    for sub in public_roots:
        base = root / sub
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            # Skip excluded directories anywhere in path
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            # Skip excluded file globs
            if any(p.match(g) for g in EXCLUDE_FILE_GLOBS):
                continue
            if p.suffix.lower() not in SCAN_EXTENSIONS:
                continue
            out.append(p)
    return sorted(out)


def load_allowlist(path: Path) -> List[Pattern[str]]:
    if not path.exists():
        return []
    pats = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            pats.append(re.compile(s))
        except re.error as e:
            print(f"warning: bad allowlist regex {s!r}: {e}", file=sys.stderr)
    return pats


def is_allowlisted(file_rel: str, line_text: str, allowlist: List[Pattern[str]]) -> bool:
    needle = f"{file_rel}:{line_text}"
    return any(p.search(needle) for p in allowlist)


# ── Scan ──────────────────────────────────────────────────────────────────────

def scan_file(path: Path, root: Path, allowlist: List[Pattern[str]]) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"warning: cannot read {path}: {e}", file=sys.stderr)
        return findings

    rel = str(path.relative_to(root))
    for lineno, line in enumerate(text.splitlines(), start=1):
        # Pre-compute: does this line contain a URL? Used to suppress L4 hits on
        # hex IDs inside third-party source URLs (e.g. apnews article slugs).
        line_has_url = ("http://" in line) or ("https://" in line)
        for rule in RULES:
            # L4 false-positive guard: if the line contains a URL, skip L4 entirely.
            # Internal commit SHAs are not normally inside URLs in our content.
            if rule.id == "L4_INTERNAL_COMMIT_SHA" and line_has_url:
                continue
            for m in rule.pattern.finditer(line):
                # L4: skip if match is preceded by '#' (CSS hex colour with alpha,
                # e.g. '#22c55e20' parses as 8 hex). The negative lookbehind in the
                # regex itself is awkward to compose; check here.
                if rule.id == "L4_INTERNAL_COMMIT_SHA":
                    s = m.start()
                    if s > 0 and line[s-1] == "#":
                        continue
                if is_allowlisted(rel, line, allowlist):
                    continue
                excerpt = line.strip()
                if len(excerpt) > 240:
                    excerpt = excerpt[:240] + "…"
                findings.append(Finding(
                    rule_id=rule.id,
                    severity=rule.severity,
                    file=rel,
                    line=lineno,
                    column=m.start() + 1,
                    excerpt=excerpt,
                    matched=m.group(0),
                ))
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="Repo root (default: cwd)")
    ap.add_argument("--public-roots", nargs="+", default=list(DEFAULT_PUBLIC_ROOTS),
                    help="Public-served directories under root")
    ap.add_argument("--allowlist", default="tools/public_surface_audit.allowlist",
                    help="Path to regex allowlist (one regex per line)")
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as hard-fail")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: --root {root} not a directory", file=sys.stderr)
        return 2

    allowlist = load_allowlist(root / args.allowlist)
    files = iter_public_files(root, tuple(args.public_roots))

    all_findings: List[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f, root, allowlist))

    hard_fail = [f for f in all_findings if f.severity == "hard-fail"]
    warns = [f for f in all_findings if f.severity == "warn"]

    if args.json:
        print(json.dumps({
            "scanned_files": len(files),
            "findings": [asdict(f) for f in all_findings],
            "summary": {
                "hard_fail": len(hard_fail),
                "warn": len(warns),
            },
        }, indent=2))
    else:
        # Group by rule
        by_rule = {}
        for f in all_findings:
            by_rule.setdefault(f.rule_id, []).append(f)
        print(f"public_surface_audit — scanned {len(files)} files under {args.public_roots}")
        print(f"  hard-fail hits: {len(hard_fail)}")
        print(f"  warn hits:      {len(warns)}")
        print()
        for rule_id in sorted(by_rule):
            hits = by_rule[rule_id]
            sev = hits[0].severity
            print(f"== {rule_id} [{sev}] — {len(hits)} hit(s) ==")
            for f in hits[:50]:
                print(f"  {f.file}:{f.line}:{f.column}  {f.matched!r}")
                print(f"    | {f.excerpt}")
            if len(hits) > 50:
                print(f"  … {len(hits) - 50} more")
            print()

    if hard_fail or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
