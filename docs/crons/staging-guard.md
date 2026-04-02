# Staging Divergence Guard — `aec126c5`

**Schedule:** Daily ~18:00 UTC  
**Purpose:** Alert Peter when the staging branch is drifting too far from main and needs merging.

## What to do

Use `api_credentials=["github"]`.

### Step 1 — Check divergence

```bash
gh api /repos/asym-intel/asym-intel-main/compare/main...staging \
  --jq '{ahead_by:.ahead_by, behind_by:.behind_by}'
```

### Step 2 — Apply rules

| Condition | Action |
|---|---|
| `ahead_by == 0` | Staging is clean. **Silent — end run, no notification.** |
| `ahead_by > 0` AND `behind_by <= 30` | Staged changes exist but still close to main. **Silent.** |
| `ahead_by > 0` AND `behind_by 31–100` | Staging is drifting. **Send warning notification.** |
| `ahead_by > 0` AND `behind_by > 100` | Staging is critically stale. **Send urgent notification.** |

### Step 3 — If notifying, also list staged files

```bash
gh api /repos/asym-intel/asym-intel-main/compare/main...staging \
  --jq '[.files[].filename]'
```

### Step 4 — Notification format

**Title:** `Staging branch needs merge — {ahead_by} files ready`

**Body:**
- Staging is `{ahead_by}` commits ahead of main, `{behind_by}` commits behind
- List staged filenames
- If `behind_by > 100`: "URGENT: staging is critically stale and will be very hard to merge cleanly. Merge or reset staging today."
- If `behind_by 31–100`: "Staging is drifting. Consider merging before it gets harder."
- Always include: "To merge: load asym-intel skill and say 'merge'. Computer applies files directly to main (PR merge is blocked at this divergence)."

## Threshold rationale

30 commits ≈ roughly one week of normal main-branch activity (cron runs, pipeline commits, data updates). Beyond that, conflicts become increasingly likely on the next merge attempt.
