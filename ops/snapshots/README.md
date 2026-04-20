# ops/snapshots/

Rendered-HTML + adapter-output snapshots of Ramparts issue pages. Built after
P-011 (M9 adapter-renderer field-name mismatch produced 21 `undefined`
markers in Issue 4) to catch the same class of regression before readers do.

## Layout

```
ops/snapshots/<issue-slug>/<ISO-timestamp>-<label>/
    rendered.html        # curl of the live WordPress URL (post-JS, post-plugins)
    adapter-output.json  # slice of report-latest.json (meta + module_9)
    metadata.json        # url, timestamp, sha256, sanity results, regressions
```

Retention: last 10 snapshots per issue-slug (older pruned by `tools/snapshot.py`).
Git history preserves everything regardless.

## How it runs

**Automatic** — `ramparts-publisher.yml` runs `tools/snapshot.py` with
`--sanity-check` after every publish. Writes a `post-publish` snapshot and
fails the workflow run on regression unless repo variable
`SNAPSHOT_SOFT_FAIL=true`.

**Manual** — before any adapter or renderer structural change, Computer
captures a `pre-change` baseline, then a `post-change` snapshot after deploy.

```bash
python3 tools/snapshot.py \
  --url https://ramparts.gi/ai-frontier-monitor-issue-2026-04-17/ \
  --issue-slug 2026-04-17 \
  --label pre-change
```

## Sanity checks (enforced when `--sanity-check` is set)

| Check | Hard-fail if | Rationale |
|---|---|---|
| M9 section present | "Law & Guidance" heading missing | Renderer broke |
| M9 `undefined` count | > 0 matches in M9 section | P-011 signature |
| M9 layer count | < 7 Layer N rows | EU AI Act tracker lost entries |
| Regression vs previous | undefineds went up OR layers went down | New bug introduced |

Page-level `undefined` total is a warning only — WordPress plugins
(Complianz cookie banner, Elementor) legitimately contain the string.

## Escape hatch

Set repo variable `SNAPSHOT_SOFT_FAIL=true` in
`Settings → Variables → Actions` to demote hard-fail to warning. Use only
when a known-acceptable regression needs to ship (e.g. intentional M9
redesign in progress). Remove immediately after.

## Extending sanity checks

Add regexes to `_M9_SECTION_PATTERNS`, `_LAYER_PATTERN`, or new per-module
patterns in `tools/snapshot.py`. Each new check should:

1. Be scoped to a single section (not page-wide) to avoid WP plugin noise.
2. Accept HTML entity encodings (`&amp;`, `&#038;`, and literal `&`) — WP
   re-encodes headings.
3. Have both a sanity threshold and a regression comparison against the
   previous snapshot's `metadata.json`.

## Related

- **P-011** — `ops/KNOWN-ISSUES.md` — the bug this was built to prevent
- **§27-L** — `ENGINE-RULES.md` — persistent-state merge invariants
- **ramparts-publisher.yml** — `.github/workflows/` — runs the snapshot step
