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
| HSTS | Enabled, min-age 31536000 | ⚠️ Not confirmed | — |
| Security headers (X-Frame-Options etc.) | Via Transform Rules | ⚠️ Not confirmed | — |
| Fortiguard recategorisation | News and Media / Research | ✅ Done via Cloudflare | 2 Apr 2026 |
| /pipeline/ WAF block | 403 on direct access | ⚠️ Not confirmed | — |

**Note on Fortiguard:** Submitted via Cloudflare recategorisation tool 2 Apr 2026.
Fortiguard review typically takes 5–10 business days. Check status at:
`https://www.fortiguard.com/webfilter?q=asym-intel.info`
Separate submission to Cisco Umbrella and Symantec may still be needed —
see notes-for-computer.md entry from ~Mar 2026 for full vendor list.

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
| MFA on Peter's GitHub account | Enforced | ⚠️ Not confirmed | — |
| Branch protection on main | CI required | ⚠️ Not confirmed | — |
| Secrets rotation schedule | Documented | ⚠️ Not started | — |
| PERPLEXITY_API_KEY rotation | Quarterly | ⚠️ Not started | — |

---

## Third-Party Dependencies (CDN)

| Library | Status | Last checked |
|---------|--------|--------------|
| Chart.js (cdn.jsdelivr.net) | ⚠️ Not audited | — |
| Fontshare (api.fontshare.com) | ⚠️ Not audited | — |
| Google Fonts | ⚠️ Not audited | — |

**Full audit:** Platform Security Expert role creates `docs/security/third-party-audit.md`
with SRI hashes and vulnerability status on its first session.

---

## Pending User Actions

| Action | Priority | Notes |
|--------|----------|-------|
| Verify Fortiguard recategorisation accepted | Medium | Check ~12 Apr 2026 via fortiguard.com/webfilter |
| Confirm Page Shield enabled in Cloudflare | High | Bot Fight Mode done; Page Shield separate toggle |
| Submit sitemap to GSC | Medium | After DNS TXT propagation confirmed |
| Run Platform Security Expert session | High | Creates docs/security/ audit files, confirms WAF/HSTS/headers |

---

## History

| Date | Action | Who |
|------|--------|-----|
| ~Mar 2026 | TLS mode changed to Full (Strict). Site healthy post-change | Peter |
| ~Mar 2026 | Gibraltar network filter incident — Fortiguard/Cloudflare Radar/Cisco Umbrella/Symantec identified as filter vendors | Computer (previous session) |
| 2 Apr 2026 | DNS TXT record added for GSC domain property verification | Peter |
| 2 Apr 2026 | Bot Fight Mode enabled in Cloudflare | Peter |
| 2 Apr 2026 | Fortiguard recategorisation submitted via Cloudflare tool (News and Media / Research) | Peter |
