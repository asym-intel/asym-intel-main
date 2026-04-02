# docs/security/secrets-rotation-schedule.md
## GitHub Actions Secrets Rotation Schedule
**Owner:** Platform Security Expert  
**Last audited:** 2026-04-03  
**Next full audit:** 2026-07-02 (90 days)  
**Audit method:** Workflow file inspection via GitHub API — all `.github/workflows/*.yml` files read

---

## Summary

| Secret | Workflows using it | Purpose | Last rotated | Status | Next rotation |
|--------|-------------------|---------|--------------|--------|---------------|
| `PPLX_API_KEY` | 14 workflows (see below) | Perplexity API authentication for all Collector/Reasoner pipeline scripts | NOT ESTABLISHED | ⚠️ Rotation date unknown — first session | **2026-07-02** |
| `STAGING_DEPLOY_TOKEN` | `staging-deploy.yml` | Personal access token for pushing to `asym-intel/asym-intel-staging` repo | NOT ESTABLISHED | ⚠️ Rotation date unknown — first session | **2026-07-02** |

---

## Detailed Secret Audit

### Secret: `PPLX_API_KEY`

**Type:** API key (Perplexity AI)  
**Naming convention compliance:** Non-standard — should follow `MONITOR_ACRONYM_STAGE_KEYTYPE` pattern (e.g. `PERPLEXITY_COLLECTOR_API_KEY`). Currently used as a single shared key across all monitors and pipeline layers.  
**Exposure method:** Injected as environment variable `PPLX_API_KEY` in each workflow job step. Never echoed to logs (confirmed by grep audit — no `echo ${{ secrets.` patterns found).  
**Failure notification:** NONE — no `if: failure()` step in any workflow using this secret (SEC-005 risk — stale credentials remain active on silent failure).

**Workflows using `PPLX_API_KEY` (14 total):**

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `fcw-chatter.yml` | Daily 06:00 UTC | FCW daily chatter signal collection |
| `fcw-collector.yml` | Daily 07:00 UTC | FCW daily Collector (sonar) |
| `fcw-reasoner.yml` | Wednesday 20:00 UTC | FCW Reasoner (sonar-deep-research) |
| `fcw-weekly-research.yml` | Wednesday 18:00 UTC | FCW weekly research (sonar-pro) |
| `gmm-collector.yml` | Daily 06:00 UTC | GMM daily Collector (sonar) |
| `gmm-reasoner.yml` | Monday 20:00 UTC | GMM Reasoner (sonar-deep-research) |
| `gmm-weekly-research.yml` | Monday 18:00 UTC | GMM weekly research (sonar-pro) |
| `gmm-weekly-test.yml` | On-demand | GMM pipeline test workflow |
| `scem-collector.yml` | Daily 06:00 UTC | SCEM daily Collector (sonar) |
| `scem-daily-test.yml` | On-demand | SCEM pipeline test workflow |
| `scem-reasoner.yml` | Saturday 20:00 UTC | SCEM Reasoner (sonar-deep-research) |
| `scem-weekly-research.yml` | Saturday 18:00 UTC | SCEM weekly research (sonar-pro) |
| `wdm-collector.yml` | Daily 07:00 UTC | WDM daily Collector (sonar) |
| `wdm-reasoner.yml` | Sunday 20:00 UTC | WDM Reasoner (sonar-deep-research) |
| `wdm-weekly-research.yml` | Sunday 18:00 UTC | WDM weekly research (sonar-pro) |

**Risk assessment:** `PPLX_API_KEY` is the most high-value secret in the pipeline. All 4 active GitHub Actions monitor pipelines (FCW, GMM, SCEM, WDM) use it. Compromise = all monitor data collection stops silently (SEC-005) or is poisoned. The key is injected correctly (via env vars, not echoed) but has **no rotation history** and **no failure alerting**.

**Rotation procedure (requires Peter's approval):**
1. Generate new API key at perplexity.ai
2. Update the `PPLX_API_KEY` secret in both GitHub repo settings → Secrets → Actions
3. Verify one Collector run succeeds before deleting the old key
4. Update this file with rotation date

---

### Secret: `STAGING_DEPLOY_TOKEN`

**Type:** GitHub Personal Access Token (PAT)  
**Purpose:** Authorises the `staging-deploy.yml` workflow to push built static files to the `asym-intel/asym-intel-staging` external repository.  
**Exposure method:** Passed to `peaceiris/actions-gh-pages@v4` as `personal_token`. Not echoed in logs.  
**Permissions required:** `repo` scope on `asym-intel/asym-intel-staging`.  
**Failure notification:** NONE — no `if: failure()` step.  
**Least-privilege assessment:** PAT likely has `repo` (full) scope. A fine-grained PAT scoped only to `asym-intel-staging` contents write would be more secure. Flag for Peter to review on next token rotation.

**Workflow using it:**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `staging-deploy.yml` | Push to `staging` branch | Builds Hugo site and deploys to staging.asym-intel.info |

**Rotation procedure (requires Peter's approval):**
1. Generate new fine-grained PAT scoped to `asym-intel-staging` repo, contents: write only
2. Update `STAGING_DEPLOY_TOKEN` secret in repo settings
3. Trigger a staging deploy to confirm the new token works
4. Update this file with rotation date and scope used

---

## Workflows Without Secrets

The following workflows use no secrets (confirmed clean):

| Workflow | Purpose |
|----------|---------|
| `build.yml` | Hugo production build (uses implicit `GITHUB_TOKEN` from Actions context) |
| `compress-images.yml` | Image compression utility |
| `inject-network-bar.yml` | Injects network nav bar into monitor pages |

**Note on `GITHUB_TOKEN`:** The implicit `GITHUB_TOKEN` provided by GitHub Actions is not a user-managed secret and rotates automatically per-job. It does not appear in `secrets.*` references in workflows. No action needed.

---

## SEC-005 Finding: No Failure Notification Steps

**Severity:** MEDIUM  
**Finding:** Zero of the 14 workflows using `PPLX_API_KEY` have an `if: failure()` notification step. If a Perplexity API call fails (expired key, rate limit, network error), the workflow silently fails — no alert is sent to Peter. Stale credentials remain active until the next manual check.

**Remediation:** Add a failure notification step to each Collector/Reasoner/Research workflow. Requires Peter's approval as a workflow change. Proposed draft:
```yaml
- name: Notify on failure
  if: failure()
  run: |
    echo "WORKFLOW FAILURE: ${{ github.workflow }} failed at $(date -u)" >> /tmp/failure.log
    # In production: send to webhook or email
```
**Platform Developer should implement** once Peter approves the pattern. Log to notes-for-computer.md.

---

## Finding: Version Inconsistency in Test Workflows

**Severity:** LOW  
**Finding:** `gmm-weekly-test.yml` and `scem-daily-test.yml` appear to be development/test artefacts that remain in the live pipeline directory. `scem-daily-test.yml` uses `PPLX_API_KEY` and runs on-demand — consuming API quota without producing permanent output.

**Recommendation:** Evaluate whether test workflows should be retained in production `.github/workflows/`. If retained, document their purpose and ensure they are not scheduled to run automatically.

---

## Rotation Calendar

| Secret | Last rotation | Next rotation | Days until due |
|--------|--------------|---------------|---------------|
| `PPLX_API_KEY` | NOT ESTABLISHED | 2026-07-02 | ~90 days |
| `STAGING_DEPLOY_TOKEN` | NOT ESTABLISHED | 2026-07-02 | ~90 days |

**Rotation policy:** 90-day rotation for all secrets. First audit baseline set 2026-04-03.

---

## First-Session Baseline Notes

This is the first Platform Security Expert session. No prior rotation history exists.  
All secrets are documented as "NOT ESTABLISHED" for last-rotated date.  
The 90-day rotation clock starts from this audit date: **2026-04-03**.  
Next mandatory rotation: **2026-07-02**.

*This file is the authoritative rotation log. Update it whenever a secret is rotated.*
