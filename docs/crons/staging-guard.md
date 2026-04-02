# Staging Divergence Guard — `aec126c5`

**Schedule:** Daily ~18:00 UTC  
**Purpose:** Alert Peter when `static/` files on staging differ from main — meaning real HTML/CSS/JS changes are waiting to be merged.

## What to do

Use `api_credentials=["github"]`.

### Step 1 — Check which files are ahead on staging

```bash
gh api /repos/asym-intel/asym-intel-main/compare/main...staging \
  --jq '[.files[].filename]'
```

### Step 2 — Filter to static/ files only

Hugo auto-rebuild commits regularly push `docs/` changes to staging — this is expected and not actionable. Only `static/` file changes represent real work waiting to be merged.

Count only files that start with `static/`:

```bash
gh api /repos/asym-intel/asym-intel-main/compare/main...staging \
  --jq '[.files[].filename | select(startswith("static/"))] | length'
```

### Step 3 — Apply rules

| Condition | Action |
|---|---|
| 0 `static/` files ahead | Staging is clean. **Silent — end run, no notification.** |
| 1–5 `static/` files ahead AND `behind_by` ≤ 30 | Small change staged, still fresh. **Silent.** |
| `static/` files ahead AND `behind_by` 31–100 | Staged changes drifting. **Send warning notification.** |
| `static/` files ahead AND `behind_by` > 100 | Staged changes critically stale. **Send urgent notification.** |

### Step 4 — If notifying, list only the static/ files

List the `static/` filenames (not `docs/` mirrors — those are Hugo auto-rebuild noise).

**Title:** `Staging branch needs merge — {N} static files ready`

**Body:**
- List the `static/` filenames
- `behind_by` value and what it means
- If `behind_by` > 100: "URGENT: merge soon or staging will be hard to reconcile."
- Always include: "To merge: load asym-intel skill and say 'merge'. Computer applies files directly to main."

## Notes

- `docs/` files being ahead is normal — Hugo auto-rebuilds staging on every push. Ignore them.
- Only `static/` files represent intentional HTML/CSS/JS changes awaiting merge.
- After a direct-file merge, staging is reset to main HEAD. The guard should see 0 static/ files.
- Cron ID: `aec126c5` | Prompt canonical location: `docs/crons/staging-guard.md`
