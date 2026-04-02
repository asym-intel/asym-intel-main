# docs/security/third-party-audit.md
## Third-Party CDN Dependency Audit
**Owner:** Platform Security Expert  
**Last audited:** 2026-04-03  
**Next audit:** 2026-05-03 (30-day cert check cycle) / 2026-07-02 (full quarterly audit)  
**Audit scope:** All external CDN resources loaded by monitor HTML pages

---

## Summary Table

| Library | URL | Version(s) used | SRI hash present | SRI verified | CVE status | TLS cert expiry | Status |
|---------|-----|-----------------|-----------------|--------------|------------|----------------|--------|
| Chart.js | `cdn.jsdelivr.net/npm/chart.js` | 4.4.7, 4.4.4, 4.4.0 | ❌ NO | N/A | ✅ No CVEs affecting ≥4.x | N/A (CDN cert) | ⚠️ HIGH: No SRI |
| Google Fonts | `fonts.googleapis.com` | N/A (CSS API) | ❌ NO | N/A | N/A | **2026-06-01** | ✅ Valid |
| Fontshare | `api.fontshare.com` | N/A (font API) | ❌ NO | N/A | N/A | **2027-02-27** | ✅ Valid |

---

## Chart.js Audit

### Versions in use

| Monitor | Dashboard version | Latest available |
|---------|------------------|-----------------|
| `fimi-cognitive-warfare` | 4.4.7 | 4.5.1 |
| `democratic-integrity` | 4.4.4 | 4.5.1 |
| `macro-monitor` | 4.4.4 | 4.5.1 |
| `european-strategic-autonomy` | 4.4.4 | 4.5.1 |
| `ai-governance` | 4.4.4 | 4.5.1 |
| `conflict-escalation` | 4.4.4 | 4.5.1 |
| `environmental-risks` | 4.4.0 | 4.5.1 |

**Version inconsistency finding:** Three different versions are in production (4.4.7, 4.4.4, 4.4.0). `environmental-risks` is running the oldest version (4.4.0). All should be standardised to the same pin. Recommended: pin all monitors to 4.4.7 with SRI (see below) then evaluate upgrading to 4.5.1 after SRI is in place.

### SRI Hash Verification (computed 2026-04-03)

All hashes computed with: `curl -s <url> | openssl dgst -sha384 -binary | openssl base64 -A`

| Version | CDN URL | SHA-384 hash | Ready to use |
|---------|---------|-------------|-------------|
| 4.4.7 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js` | `vsrfeLOOY6KuIYKDlmVH5UiBmgIdB1oEf7p01YgWHuqmOHfZr374+odEv96n9tNC` | ✅ |
| 4.4.4 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js` | `NrKB+u6Ts6AtkIhwPixiKTzgSKNblyhlk0Sohlgar9UHUBzai/sgnNNWWd291xqt` | ✅ |
| 4.4.0 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js` | `e6nUZLBkQ86NJ6TVVKAeSaK8jWa3NhkYWZFomE39AvDbQWeie9PlQqM3pmYW5d1g` | ✅ |

**npm package integrity for 4.4.7 (from npm registry):**  
`sha512-pwkcKfdzTMAU/+jNosKhNL2bHtJc/sSmYgVbuGTEDhzkrhmyihmP7vUc/5ZK9WopidMDHNe3Wm7jOd/WhuHWuw==`  
(Note: npm uses SHA-512, SRI in HTML uses SHA-384 — both computed above from live CDN download.)

**Implementation format for HTML `<script>` tags:**
```html
<!-- Chart.js 4.4.7 — SRI pinned -->
<script
  src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"
  integrity="sha384-vsrfeLOOY6KuIYKDlmVH5UiBmgIdB1oEf7p01YgWHuqmOHfZr374+odEv96n9tNC"
  crossorigin="anonymous">
</script>

<!-- Chart.js 4.4.4 — SRI pinned -->
<script
  src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"
  integrity="sha384-NrKB+u6Ts6AtkIhwPixiKTzgSKNblyhlk0Sohlgar9UHUBzai/sgnNNWWd291xqt"
  crossorigin="anonymous">
</script>
```

**Action required:** Platform Developer to add `integrity=` and `crossorigin="anonymous"` attributes to all 7 Chart.js `<script>` tags. This is a HIGH finding — see findings section. Requires staging → PR → visual sign-off → merge.

### CVE Status

| Finding | Affected versions | Status |
|---------|-----------------|--------|
| GHSA-h68q-55jf-x68w: Prototype pollution | < 2.9.4 | ✅ NOT AFFECTED — all versions in use are 4.x |

**OSV database check:** 0 vulnerabilities affecting Chart.js 4.x. Source: [api.osv.dev](https://api.osv.dev)  
**npm registry:** Chart.js 4.4.7 is NOT deprecated.  
**Latest available:** 4.5.1 (released post-audit). No security advisory for 4.4.x → 4.5.x upgrade identified. Monitor quarterly.

---

## Google Fonts Audit

**Resource:** `https://fonts.googleapis.com` (Inter, JetBrains Mono via CSS API)  
**Load pattern:** CSS font-face declarations loaded via `<link rel="stylesheet">` from `fonts.googleapis.com`. Actual font files served from `fonts.gstatic.com`.  
**SRI on `<link>` tags:** Not currently implemented (checking `<link rel="stylesheet" integrity="...">` is supported but not widely used).  
**Tracking risk:** Google Fonts requests log visitor IPs at Google — this is a known privacy consideration for GDPR-sensitive audiences. At current platform scale, this is acceptable but should be noted.

### TLS Certificate Validity

| Host | Certificate issued | Certificate expires | Days remaining |
|------|--------------------|-------------------|----------------|
| `fonts.googleapis.com` | 2026-03-09 | **2026-06-01** | ~59 days |
| `fonts.gstatic.com` | (serves font files — not separately checked) | — | — |

**⚠️ ALERT:** Google Fonts TLS certificate expires **2026-06-01** — approximately 59 days from this audit. Google manages this certificate and renews it automatically. Monitor at next 30-day check (2026-05-03). If not renewed by 2026-05-25, escalate to Peter.

**Action:** Add `fonts.googleapis.com` cert check to the 30-day monitoring cycle. Google has a strong track record of timely renewal but this is a dependency on an external party.

---

## Fontshare Audit

**Resource:** `https://api.fontshare.com` (Satoshi or other fonts — usage confirmed by platform)  
**Load pattern:** Font CSS loaded via `<link>` from `api.fontshare.com`; font files served from the same domain.  
**SRI on `<link>` tags:** Not currently implemented.

### TLS Certificate Validity

| Host | Certificate issued | Certificate expires | Days remaining |
|------|--------------------|-------------------|----------------|
| `api.fontshare.com` | 2026-01-29 | **2027-02-27** | ~331 days |

**Status: ✅ Valid** — Certificate has ~331 days remaining. No action required until next quarterly audit.

---

## HIGH Finding: No SRI Attributes on Any CDN Tag

**Severity:** HIGH  
**Finding:** All 7 monitor dashboard pages load Chart.js from `cdn.jsdelivr.net` without `integrity=` (SRI) attributes. Google Fonts and Fontshare `<link>` tags also lack integrity attributes.

**Risk:** If `cdn.jsdelivr.net` is compromised or a BGP hijack redirects CDN traffic, a malicious version of Chart.js could be served without detection. This would affect all monitor dashboards simultaneously. For a FIMI-monitoring platform, code injection via CDN is a specific threat model (SEC-003, SEC-010).

**SRI hashes for implementation are computed above.** Recommended implementation:
1. Platform Developer adds `integrity=` + `crossorigin="anonymous"` to all Chart.js `<script>` tags
2. Standardise all monitors to Chart.js 4.4.7 (currently 3 different versions)
3. Update SRI hashes in this file whenever Chart.js version is bumped

**Decision required from Peter:** Whether to upgrade to 4.5.1 at the same time as adding SRI. If yes, Platform Developer computes new hash and implements both changes in one PR.

---

## MEDIUM Finding: Version Inconsistency

**Severity:** MEDIUM  
**Finding:** Three different Chart.js versions are in production (4.4.0, 4.4.4, 4.4.7). This creates maintenance burden and means `environmental-risks` (4.4.0) is 3 minor versions behind. All monitors should be pinned to the same version.

**Action:** Standardise to 4.4.7 when SRI is added (see HIGH finding above). No security impact identified from the version difference, but standardisation reduces audit complexity.

---

## LOW Finding: Missing `/pipeline/` in robots.txt

**Severity:** LOW (with positive context — see pipeline exposure section)  
**Finding:** `docs/robots.txt` contains:
```
User-agent: *
Allow: /
Disallow: /admin/
```
`/pipeline/` is NOT listed in `Disallow`. However, `/pipeline/` returns HTTP 404 (not served by GitHub Pages), so crawlers cannot access it regardless of robots.txt.

**Status:** Not an active risk — `/pipeline/` is physically absent from the served site. However, best practice is to explicitly disallow it in robots.txt as a defence-in-depth measure. If the pipeline directory were ever accidentally added to the Hugo build, the robots.txt disallow would be the last line of defence.

**Recommended addition to robots.txt:**
```
Disallow: /pipeline/
Disallow: /data/
```
This requires Platform Developer → SEO Expert review, since robots.txt changes can affect search indexing.

---

## Security Headers Audit (from HTTP response, 2026-04-03)

HTTP headers observed at `https://asym-intel.info/`:

| Header | Value | Status |
|--------|-------|--------|
| `strict-transport-security` | `max-age=15552000; includeSubDomains` | ⚠️ PRESENT but below recommended `max-age=31536000` |
| `x-content-type-options` | `nosniff` | ✅ Present |
| `x-frame-options` | **NOT PRESENT** | ⚠️ Missing |
| `content-security-policy` | **NOT PRESENT** | ⚠️ Missing |
| `referrer-policy` | **NOT PRESENT** | ⚠️ Missing |

**HSTS status:** Present but `max-age=15552000` (180 days) — the role spec requires `min-age=31536000` (365 days). This is a medium finding. Either the Cloudflare Transform Rule is configured with a shorter value, or GitHub Pages is overriding the Cloudflare setting.

**CSP, X-Frame-Options, Referrer-Policy:** Not present in observed headers. These should be set via Cloudflare Transform Rules → Response Headers. Not confirmed as active. Peter to verify in Cloudflare dashboard.

---

## CDN Fallback Status

**`static/fallback/` directory:** Does NOT exist. The CDN compromise response playbook (Enhancement Addenda v1.0) requires local pinned copies of CDN dependencies in `static/fallback/` for emergency failover within 1 hour of a confirmed CDN compromise.

**Action:** Create `static/fallback/` with pinned Chart.js, Fontshare, and document the CDN compromise procedure. This is a Platform Developer task — flag in notes-for-computer.md. Medium priority — the SRI implementation provides first-line defence; fallback copies provide second-line.

---

## Audit Log

| Date | Auditor | Scope | Key findings |
|------|---------|-------|-------------|
| 2026-04-03 | Platform Security Expert (Session 2) | All monitor dashboards, CDN deps, certs | No SRI on any CDN tag (HIGH); version inconsistency (MEDIUM); Google Fonts cert expiry 2026-06-01; no Chart.js CVEs affecting 4.x |

*Update this table with each audit session.*
