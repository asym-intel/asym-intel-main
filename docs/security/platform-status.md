# docs/security/platform-status.md
## Infrastructure & External Service Status
**Owner:** Platform Security Expert (readable/writable by Computer during session)
**Purpose:** Persistent record of infrastructure decisions, configuration actions, and
their completion state. Survives Housekeeping regeneration. Updated whenever Peter
confirms an action is complete or a new action is identified.

---

## Cloudflare Configuration

| Setting | Required state | Status | Date confirmed |
|---------|---------------|--------|----------------|
| TLS mode | Full (Strict) | ✅ Done | ~Mar 2026 |
| Bot Fight Mode | Enabled, sensitivity High | ✅ Done | 2 Apr 2026 |
| Page Shield | Enabled, monitoring active | ⚠️ Not confirmed | — |
| WAF (OWASP ruleset) | Enabled | ⚠️ Not confirmed | — |
| HSTS | Enabled, min-age 31536000 | ⚠️ Partial — max-age=15552000 observed, below spec | 3 Apr 2026 (HTTP header audit) |
| Security headers (X-Frame-Options etc.) | Via Transform Rules | ⚠️ Not confirmed — X-Frame-Options absent from observed headers | 3 Apr 2026 |
| Content-Security-Policy | Via Transform Rules | ⚠️ Not present in observed headers | 3 Apr 2026 |
| Referrer-Policy | Via Transform Rules | ⚠️ Not present in observed headers | 3 Apr 2026 |
| Fortiguard recategorisation | News and Media / Research | ✅ Submitted | 2 Apr 2026 |
| /pipeline/ WAF block | 404 (not served — no WAF rule needed) | ✅ Not accessible | 3 Apr 2026 |

**Note on HSTS:** HTTP header audit on 3 Apr 2026 shows `strict-transport-security: max-age=15552000; includeSubDomains` (180 days). Role spec requires `min-age=31536000` (365 days). Peter to confirm Cloudflare Transform Rule setting — may need update to 31536000.

**Note on /pipeline/:** Returns HTTP 404 from GitHub Pages infrastructure — `/pipeline/` directory is not included in the Hugo build output and is therefore not publicly served. This is better than a WAF block (content doesn't exist at all). However, `docs/robots.txt` does NOT explicitly disallow `/pipeline/` — add as defence-in-depth (see pending actions).

**Note on Fortiguard:** Submitted via Cloudflare recategorisation tool 2 Apr 2026.
Fortiguard review typically takes 5–10 business days. Check status at:
`https://www.fortiguard.com/webfilter?q=asym-intel.info`
NOTE: Fortiguard site uses AngularJS — category data is loaded dynamically. Direct curl/API check cannot read the category. Peter to verify manually at fortiguard.com/webfilter approximately 12 Apr 2026.
Separate submission to Cisco Umbrella and Symantec still needed — see pending actions.

---

## Filter Vendor Status (Quarterly Checklist — 3 April 2026)

| Vendor | Target category | Last submission | Status | Next check |
|--------|----------------|----------------|--------|------------|
| Fortiguard | News and Media / Research | 2 Apr 2026 (via Cloudflare) | ⏳ Pending (~10 days) | 12 Apr 2026 |
| Cisco Umbrella | News and Media | Not yet submitted | ⚠️ Not started | ASAP |
| Symantec (BlueCoat) | News and Media / Research | Not yet submitted | ⚠️ Not started | ASAP |

**Action required by Peter:**
- Check Fortiguard result ~12 Apr: https://www.fortiguard.com/webfilter?q=asym-intel.info
- Submit Cisco Umbrella: https://investigate.umbrella.com
- Submit Symantec BlueCoat: https://sitereview.bluecoat.com/#/

---

## Google Search Console

| Action | Status | Date confirmed |
|--------|--------|----------------|
| Domain property: DNS TXT record for asym-intel.info | ✅ Done | 2 Apr 2026 |
| Sitemap submitted | ⚠️ Not confirmed | — |
| Coverage report reviewed | ⚠️ Not confirmed | — |

---

## GitHub Repository Security

| Setting | Required state | Status | Date confirmed |
|---------|---------------|--------|----------------|
| MFA on Peter's GitHub account | Enforced | ⚠️ Not confirmed by Security Expert | — |
| Branch protection on main | CI required, even for repo owner | ❌ ABSENT — HIGH FINDING | 3 Apr 2026 |
| Collaborators (asym-intel-main) | Solo owner | ✅ Only Peter-Pink-Howitt (admin) | 3 Apr 2026 |
| Collaborators (asym-intel-internal) | Solo owner | ✅ Only Peter-Pink-Howitt (admin) | 3 Apr 2026 |
| Secrets rotation schedule | Documented | ✅ Established | 3 Apr 2026 |
| PPLX_API_KEY rotation | Quarterly | ⚠️ Not established — first session | 3 Apr 2026 |
| STAGING_DEPLOY_TOKEN rotation | Quarterly | ⚠️ Not established — first session | 3 Apr 2026 |

---

## Third-Party Dependencies (CDN)

| Library | Versions in use | SRI hashes | Last checked | CVE status |
|---------|----------------|-----------|-------------|------------|
| Chart.js (cdn.jsdelivr.net) | 4.4.7, 4.4.4, 4.4.0 | ⚠️ NOT implemented — HIGH finding | 3 Apr 2026 | ✅ No CVEs affecting 4.x |
| Fontshare (api.fontshare.com) | N/A (font API) | ⚠️ Not applicable for CSS links | 3 Apr 2026 | — |
| Google Fonts (fonts.googleapis.com) | N/A (CSS API) | ⚠️ Not applicable for CSS links | 3 Apr 2026 | — |

**Full audit:** `docs/security/third-party-audit.md` — SRI hashes, cert validity dates, CVE status.  
**Google Fonts TLS cert expires 2026-06-01** — monitor for Google renewal.

---

## Integrity Manifest

| Item | Status | Notes |
|------|--------|-------|
| integrity-manifest.json | ❌ DOES NOT EXIST — HIGH finding | Spec at docs/security/integrity-manifest-spec.md |
| Canary statement (About page) | ❌ NOT IMPLEMENTED | Platform Developer task |
| static/fallback/ CDN copies | ❌ NOT IMPLEMENTED | Medium priority |

---

## Pending Actions

### Peter (user action required)
| Action | Priority | Target |
|--------|----------|--------|
| Check Fortiguard recategorisation accepted (fortiguard.com/webfilter) | High | ~12 Apr 2026 |
| Submit Cisco Umbrella recategorisation | High | ASAP |
| Submit Symantec BlueCoat recategorisation | High | ASAP |
| Confirm Page Shield enabled in Cloudflare | High | Next login |
| Confirm WAF (OWASP ruleset) enabled in Cloudflare | High | Next login |
| Update HSTS max-age to 31536000 in Cloudflare Transform Rules | Medium | Next login |
| Add X-Frame-Options, CSP, Referrer-Policy headers via Cloudflare | Medium | Next login |
| Add branch protection on main (require CI, even for owner) | HIGH | ASAP — SEC-009 risk |
| Verify GitHub 2FA uses hardware key | Quarterly | Next quarterly session |

### Platform Developer (implementation required)
| Action | Priority | Notes |
|--------|----------|-------|
| Add SRI integrity= attributes to all 7 Chart.js `<script>` tags | HIGH | Hashes in third-party-audit.md |
| Standardise all monitors to Chart.js 4.4.7 | Medium | ERM currently on 4.4.0 |
| Add `/pipeline/` to docs/robots.txt | Low | Defence-in-depth only |
| Implement integrity manifest GitHub Actions workflow | HIGH | Spec in integrity-manifest-spec.md |
| Add canary statement to About page | Medium | See integrity-manifest-spec.md |
| Create static/fallback/ with pinned CDN copies | Medium | CDN compromise playbook |

---

## History

| Date | Action | Who |
|------|--------|-----|
| ~Mar 2026 | TLS mode changed to Full (Strict). Site healthy post-change | Peter |
| ~Mar 2026 | Gibraltar network filter incident — Fortiguard/Cloudflare Radar/Cisco Umbrella/Symantec identified as filter vendors affecting platform reachability | Computer (previous session) |
| 2 Apr 2026 | DNS TXT record added for GSC domain property verification | Peter |
| 2 Apr 2026 | Bot Fight Mode enabled in Cloudflare | Peter |
| 2 Apr 2026 | Fortiguard recategorisation submitted via Cloudflare tool (News and Media / Research) | Peter |
| 3 Apr 2026 | Security Expert Session 2: full quarterly checklist, docs/security/ created, SRI hashes computed, branch protection gap confirmed (HIGH), integrity manifest gap confirmed (HIGH), no SRI on CDN tags (HIGH), pipeline exposure confirmed benign (404), collaborator audit clean (solo owner) | Platform Security Expert |
