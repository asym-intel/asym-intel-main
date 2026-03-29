# Asymmetric Intelligence — Publishing Workflow

**Last updated:** 2026-03-29  
**Applies to:** asym-intel.info (main site)  
**Stack:** Hugo → GitHub → GitHub Actions → GitHub Pages → Cloudflare

---

## Overview

Content flows in one direction:

```
CMS editor → GitHub (commit) → GitHub Actions (build) → docs/ → GitHub Pages → asym-intel.info
```

The CMS is a browser-based editor. It does not build or deploy anything itself — it writes Markdown files to the GitHub repository. GitHub Actions handles the build automatically on every push to `main`.

---

## The Seven Monitors

Each monitor publishes one weekly executive briefing on a fixed day:

| Monitor | Day | Slug |
|---------|-----|------|
| AI Governance | Monday | `ai-governance` |
| Democratic Integrity | Tuesday | `democratic-integrity` |
| European Strategic Autonomy | Wednesday | `european-strategic-autonomy` |
| Illicit Finance & Financial Crime | Thursday | `illicit-finance` |
| Global Governance Under Stress | Friday | `global-governance` |
| Rule of Law & Judicial Independence | Saturday | `rule-of-law` |
| Philosophy & Politics of Technology | Sunday | `technology-society` |

---

## Writing and Publishing a Briefing

### Via the CMS (recommended)

1. Go to [asym-intel.info/admin/](https://asym-intel.info/admin/)
2. Log in with GitHub (you must be a member of the `asym-intel` organisation)
3. In the left sidebar, click the monitor you are writing for (e.g. **AI Governance**)
4. Click **New AI Governance** (or the relevant monitor name)
5. Fill in the fields:
   - **Title** — e.g. `AI Governance — Week of 29 March 2026`
   - **Date** — set to the publication date (the relevant weekday)
   - **One-line Summary** — one sentence, appears on the homepage feed card
   - **Draft** — leave `false` to publish immediately, set `true` to save without publishing
   - **Full Briefing** — the full markdown content
6. Click **Publish** (or **Save** if draft)
7. The CMS commits the file to GitHub. GitHub Actions picks it up within seconds and rebuilds the site. The briefing appears on the homepage feed within 1–2 minutes.

### Via GitHub directly (advanced)

Create a Markdown file at:
```
content/monitors/{monitor-slug}/YYYY-MM-DD-{title-slug}.md
```

With this front matter:
```yaml
---
title: "AI Governance — Week of 29 March 2026"
date: 2026-03-29T00:00:00Z
summary: "One sentence summary for the homepage feed card."
draft: false
---
```

Commit and push to `main`. GitHub Actions rebuilds automatically.

---

## Draft Workflow

Set `draft: true` in the front matter to save a briefing without publishing it.

- Drafts are committed to GitHub but Hugo excludes them from the build output
- To publish a draft: open it in the CMS, set **Draft** to `false`, click **Publish**
- Alternatively edit the file directly on GitHub and change `draft: false`

---

## What GitHub Actions Does (Stage 6b)

On every push to `main`, the GitHub Actions workflow:

1. Checks out the repository
2. Installs Hugo extended
3. Runs `hugo --minify`
4. Commits the updated `docs/` directory back to `main`
5. GitHub Pages serves the new build within ~30 seconds

**Until Stage 6b is set up:** after the CMS commits content, you must manually rebuild:
```bash
git pull
hugo --minify
git add docs/
git commit -m "build: rebuild after content update"
git push
```

---

## Topic Pages

Topic pages live at `asym-intel.info/topics/{slug}` and provide standing context for each monitor domain. They are edited (not created) via the CMS under **Topic Pages**.

Topic pages are not time-stamped briefings — they are living documents updated as context evolves. Update the **Last Updated** date when making substantive changes.

---

## The Homepage Feed

The homepage shows the most recent briefing from each monitor, sorted by date. It updates automatically after each build. No manual curation required.

---

## File Naming Convention

Briefing files follow this pattern:
```
content/monitors/ai-governance/2026-03-29-ai-governance-week-of-29-march-2026.md
```

- Date prefix ensures chronological sorting in the filesystem
- The CMS generates this automatically from the title and date fields
- Do not rename files after publishing — URLs are permanent

---

## URLs

Briefings are served at:
```
https://asym-intel.info/monitors/{monitor-slug}/{filename-without-extension}/
```

Example:
```
https://asym-intel.info/monitors/ai-governance/2026-03-29-ai-governance-week-of-29-march-2026/
```

---

## Access Control

- CMS login requires a GitHub account that is a member of the `asym-intel` organisation
- To add a contributor: invite them to the `asym-intel` org on GitHub and give them write access to `asym-intel-main`
- OAuth is handled by the Cloudflare Worker at `asym-intel-oauth.peterhowitt.workers.dev`

---

## If Something Breaks

**CMS login fails:**
- Check the Cloudflare Worker is running: [asym-intel-oauth.peterhowitt.workers.dev](https://asym-intel-oauth.peterhowitt.workers.dev)
- Check the GitHub OAuth App is active: github.com/organizations/asym-intel/settings/applications

**Content published but not appearing on site:**
- Until Stage 6b: rebuild manually (see above)
- After Stage 6b: check the GitHub Actions run at github.com/asym-intel/asym-intel-main/actions

**Build errors:**
- Check Hugo version in the Actions workflow matches local version
- Run `hugo --minify` locally to reproduce the error

**Site showing old content:**
- Cloudflare may be caching — purge cache at dash.cloudflare.com → Caching → Purge Everything
- Or wait up to 4 hours for TTL expiry

---

## Network

| Site | Repo | CMS |
|------|------|-----|
| asym-intel.info | asym-intel/asym-intel-main | /admin/ |
| compossible.asym-intel.info | asym-intel/asym-intel-compossible | /admin/ (Stage 8b) |
| whitespace.asym-intel.info | asym-intel/asym-intel-whitespace | /admin/ (future) |
