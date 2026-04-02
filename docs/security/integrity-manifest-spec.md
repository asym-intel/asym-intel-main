# docs/security/integrity-manifest-spec.md
## SHA-256 Output Integrity Manifest — Implementation Specification
**Owner:** Platform Security Expert  
**Created:** 2026-04-03 (Session 2 — First Security Expert session)  
**Status:** SPECIFICATION ONLY — implementation required by Platform Developer (acting on notes-for-computer.md flag)  
**Priority:** HIGH — build before platform reaches prominence

---

## Purpose

A SHA-256 integrity manifest provides a cryptographic audit trail of every monitor output at publication time. This is the primary defence against SEC-008 (Fabricated Output Attack): if a fabricated screenshot claims asym-intel.info published a different finding, the manifest + git commit history provides verifiable proof of the actual published content.

The manifest is committed to GitHub, which provides an independent timestamp via git history. This makes the proof tamper-evident: the manifest content and the commit timestamp are bound together and cannot be retroactively altered without detection.

---

## Threat Scenario

1. State actor monitors asym-intel.info because it tracks their operations (FCW monitor).
2. Actor fabricates a screenshot showing asym-intel.info with a modified or false finding — designed to discredit the platform or create confusion about what was actually published.
3. Without a manifest: the platform has no machine-verifiable proof of what was published on a given date.
4. With the manifest: any third party can compute `sha256sum` of the actual committed `report-latest.json` and compare to the manifest entry for that date. The git commit timestamp is a cryptographic proof of when the manifest was created.

---

## Manifest Schema

**File path:** `static/monitors/shared/integrity-manifest.json`  
**Also served at:** `https://asym-intel.info/monitors/shared/integrity-manifest.json`  
**Updated:** Weekly, after all 7 Analyst crons have published (Monday Housekeeping run is the natural trigger)

```json
{
  "generated": "2026-04-07T08:00:00Z",
  "generated_by": "Platform Housekeeping (cron 7e058f57)",
  "schema_version": "1.0",
  "monitors": {
    "democratic-integrity": {
      "file": "static/monitors/democratic-integrity/data/report-latest.json",
      "report_date": "2026-04-07",
      "sha256": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
      "size_bytes": 12345,
      "git_commit": "abc12345"
    },
    "macro-monitor": {
      "file": "static/monitors/macro-monitor/data/report-latest.json",
      "report_date": "2026-04-08",
      "sha256": "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3",
      "size_bytes": 11234,
      "git_commit": "def23456"
    },
    "fimi-cognitive-warfare": {
      "file": "static/monitors/fimi-cognitive-warfare/data/report-latest.json",
      "report_date": "2026-04-10",
      "sha256": "c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
      "size_bytes": 9876,
      "git_commit": "ghi34567"
    },
    "european-strategic-autonomy": {
      "file": "static/monitors/european-strategic-autonomy/data/report-latest.json",
      "report_date": "2026-04-09",
      "sha256": "d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5",
      "size_bytes": 8765,
      "git_commit": "jkl45678"
    },
    "ai-governance": {
      "file": "static/monitors/ai-governance/data/report-latest.json",
      "report_date": "2026-04-11",
      "sha256": "e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6",
      "size_bytes": 10234,
      "git_commit": "mno56789"
    },
    "environmental-risks": {
      "file": "static/monitors/environmental-risks/data/report-latest.json",
      "report_date": "2026-04-12",
      "sha256": "f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1",
      "size_bytes": 7654,
      "git_commit": "pqr67890"
    },
    "conflict-escalation": {
      "file": "static/monitors/conflict-escalation/data/report-latest.json",
      "report_date": "2026-04-06",
      "sha256": "a2b3c4d5e6f7a2b3c4d5e6f7a2b3c4d5e6f7a2b3c4d5e6f7a2b3c4d5e6f7a2b3",
      "size_bytes": 11456,
      "git_commit": "stu78901"
    }
  }
}
```

---

## Implementation Approach

### Option A: Housekeeping cron generates the manifest (Recommended)

Extend the Platform Housekeeping cron (7e058f57, Monday 08:00 UTC) to compute SHA-256 hashes of all 7 `report-latest.json` files and write `static/monitors/shared/integrity-manifest.json`.

**Python implementation sketch for Housekeeping cron prompt:**

```python
import hashlib, json, subprocess

monitors = [
    "democratic-integrity", "macro-monitor", "fimi-cognitive-warfare",
    "european-strategic-autonomy", "ai-governance", "environmental-risks",
    "conflict-escalation"
]

manifest = {
    "generated": datetime.utcnow().isoformat() + "Z",
    "generated_by": "Platform Housekeeping (cron 7e058f57)",
    "schema_version": "1.0",
    "monitors": {}
}

for slug in monitors:
    path = f"static/monitors/{slug}/data/report-latest.json"
    # Read from GitHub API
    content = get_file_content(path)
    sha256 = hashlib.sha256(content.encode()).hexdigest()
    report_data = json.loads(content)
    manifest["monitors"][slug] = {
        "file": path,
        "report_date": report_data.get("report_date", "unknown"),
        "sha256": sha256,
        "size_bytes": len(content.encode()),
        "git_commit": get_latest_commit_sha(path)
    }

# Commit manifest to repo
commit_file(
    "static/monitors/shared/integrity-manifest.json",
    json.dumps(manifest, indent=2),
    f"security(manifest): weekly integrity manifest — {datetime.utcnow().strftime('%Y-%m-%d')}"
)
```

### Option B: Standalone GitHub Actions workflow

A dedicated workflow `generate-integrity-manifest.yml` that runs Monday 09:00 UTC (after Housekeeping at 08:00 UTC). Simpler to implement without modifying the Housekeeping cron prompt.

**Recommendation:** Option B is safer — it doesn't risk breaking the Housekeeping cron. Platform Developer should build this as a standalone GitHub Actions workflow. Requires Peter's approval as a new workflow.

---

## Response Protocol for Fabricated Output Attacks (SEC-008)

When a fabricated screenshot or claim appears:

1. **Identify the claim:** Which monitor, which date, what specific finding is alleged?
2. **Locate manifest entry:** Check `integrity-manifest.json` for the `sha256` of `report-latest.json` on that date. If the date is historical, use git log to find the manifest commit for that week.
3. **Compute the hash of the actual committed file:**
   ```bash
   gh api /repos/asym-intel/asym-intel-main/contents/static/monitors/{slug}/data/report-{date}.json \
     --jq '.content' | base64 -d | sha256sum
   ```
4. **Compare:** If hashes match manifest — the actual published content is confirmed. If the fabrication differs, the manifest proves the discrepancy.
5. **Document:** Create `docs/security/incidents/incident-{date}.md` — include the fabricated claim, the manifest hash, the git commit hash, and the verified truth.
6. **FCW escalation check:** A fabricated output attack against asym-intel.info may itself be a FIMI signal. Flag to FCW via notes-for-computer.md for consideration in FCW weekly scoring.

---

## Canary Statement

The Platform Security Expert is responsible for verifying and re-dating the following canary statement on the About page every quarter:

> *"Asymmetric Intelligence has never been subject to a government order to modify, suppress, or alter any published finding. This statement is updated quarterly. Last updated: April 2026."*

**Current status:** NOT YET IMPLEMENTED. The About page should include this statement.  
**Action required:** Platform Developer to add to the About page template (`layouts/` or `static/monitors/*/about.html`). Platform Security Expert to verify and update the date quarterly.  
**Removal = signal:** If this statement is ever removed without an explicit update in this file, its absence should be treated as a potential compromise indicator.

---

## Implementation Timeline

| Task | Owner | Priority | Target |
|------|-------|----------|--------|
| Create `generate-integrity-manifest.yml` GitHub Actions workflow | Platform Developer | HIGH | Q2 2026 |
| Wire into Housekeeping as Check 16 | Platform Developer / Computer | HIGH | Q2 2026 |
| Add canary statement to About page | Platform Developer | MEDIUM | Q2 2026 |
| Create `static/fallback/` with pinned CDN copies | Platform Developer | MEDIUM | Q2 2026 |
| First real manifest generated and committed | Computer / Housekeeping | HIGH | Week of 2026-04-07 |

---

*Flagged to Computer via notes-for-computer.md for implementation scheduling.*
