#!/usr/bin/env python3
"""
Generate triage strip HTML/CSS for the Asymmetric Intelligence shared monitor library.
Calls Perplexity sonar-pro with a full spec and writes output to docs/generated/.

This is a generation-pass script — output should be reviewed by Computer before
being promoted to static/monitors/shared/css/base.css and per-monitor dashboards.
"""

import os, sys, json, requests, base64, subprocess
from datetime import datetime, timezone

PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
GH_TOKEN     = os.environ.get("GH_TOKEN")
REPO         = "asym-intel/asym-intel-main"
OUTPUT_PATH  = "docs/generated/triage-strip-draft.html"
MODEL        = "sonar-pro"

if not PPLX_API_KEY:
    print("ERROR: PPLX_API_KEY not set"); sys.exit(1)
if not GH_TOKEN:
    print("ERROR: GH_TOKEN not set"); sys.exit(1)

# ── Read reference files from repo ────────────────────────────────────────────
def read_repo_file(path):
    r = subprocess.run(
        ["gh", "api", f"/repos/{REPO}/contents/{path}", "--jq", ".content"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"WARNING: could not read {path}")
        return ""
    return base64.b64decode(r.stdout.strip()).decode("utf-8")

print("Reading reference files...")
base_css       = read_repo_file("static/monitors/shared/css/base.css")
colour_registry = read_repo_file("docs/ux/colour-registry.md")
naming_registry = read_repo_file("docs/ux/section-naming-registry.md")
badge_spec     = read_repo_file("docs/ux/badge-spec.md")
rebuild_spec   = read_repo_file("docs/ux/site-rebuild-spec.md")

# ── Build prompt ──────────────────────────────────────────────────────────────
PROMPT = f"""You are an expert front-end developer building a shared HTML/CSS component for a multi-monitor intelligence platform called Asymmetric Intelligence (asym-intel.info).

Your task: produce a complete, production-ready **triage strip** component — a shared HTML/CSS pattern that will be used at the top of all 7 monitor dashboards.

## What a triage strip is

The triage strip is the first-read experience on every monitor dashboard. It appears above the fold and gives the user immediate situational awareness in 4 zones (left to right):

1. **KPI zone** — single most important metric (e.g. 15 Rapid Decay / CRITICAL stress / 23 Active Operations). Large, bold, immediately readable.
2. **Lead Signal zone** — the week's primary signal headline (1 sentence, from `report-latest.json` `signal_panel.headline`). Medium weight.
3. **Structural snapshot zone** — 2-3 key structural status indicators (small badges/chips showing e.g. recovery/watchlist counts, regime, autonomy score). Compact.
4. **Delta zone** — 1-2 highest-severity items from `delta-strip` data. Severity-badged, with a short label.

The strip must be responsive:
- Desktop (>900px): 4 zones in a single row
- Tablet (600–900px): 2 zones per row
- Mobile (<600px): stacked, each zone full-width

## Design constraints

Use ONLY these CSS variables from the existing `base.css`:
- Typography: `--text-xs`, `--text-sm`, `--text-base`, `--text-lg`, `--text-xl`
- Spacing: `--space-1` through `--space-8`
- Colours: `--color-bg`, `--color-surface`, `--color-border`, `--color-text`, `--color-text-muted`, `--color-text-faint`
- Severity: `--critical`, `--high`, `--moderate`, `--positive`, `--contested` (and their `-bg` variants)
- Monitor accent: `--monitor-accent`, `--monitor-accent-bg` (set by per-monitor `monitor.css`)
- Radius: `--radius`, `--radius-md`
- Shadows: `--shadow-sm`, `--shadow`

**Do NOT use hardcoded colours.** Every colour reference must use a CSS variable.

**Severity badge rules:**
- Severity badges: filled background (`--critical-bg`) + text (`--critical`). Classes: `.severity-badge--critical`, `.severity-badge--high`, `.severity-badge--moderate`, `.severity-badge--positive`, `.severity-badge--watchlist`, `.severity-badge--recovery`

**Confidence badge rules (from badge-spec):**
- Outline only, transparent fill, neutral grey border
- Classes: `.badge-confidence`, `.badge-confidence--confirmed`, `.badge-confidence--high`, `.badge-confidence--assessed`, `.badge-confidence--possible`
- NEVER use severity colours on confidence badges

**Architecture rules:**
- `overflow-x: clip` — NEVER `overflow-x: hidden` (breaks sticky nav)
- No inline styles — all styling via CSS classes
- All data populated via JavaScript from `report-latest.json` — HTML is the shell, JS fills it
- The triage strip shell must have id `triage-strip` and data attribute `data-section="triage"`

## Reference: existing base.css (for CSS variable names and existing patterns)

```css
{base_css[:3000]}
```

## Reference: colour registry

```markdown
{colour_registry[:2000]}
```

## Reference: badge spec

```markdown
{badge_spec}
```

## What to produce

Produce a single HTML file containing:

1. **`<style>` block** — all new CSS classes needed for the triage strip. These will be added to `base.css` during the Computer review pass. Classes must start with `.triage-`:
   - `.triage-strip` — the outer container
   - `.triage-zone` — each of the 4 zones
   - `.triage-zone--kpi` — KPI zone specific styles
   - `.triage-zone--signal` — Lead Signal zone
   - `.triage-zone--snapshot` — Structural snapshot zone
   - `.triage-zone--delta` — Delta zone
   - `.triage-kpi-value` — the large metric number
   - `.triage-kpi-label` — the label below the number
   - `.triage-signal-headline` — the signal headline text
   - `.triage-snapshot-chips` — the chips container
   - `.triage-chip` — individual status chip
   - `.triage-delta-item` — a single delta item
   - Plus any responsive breakpoint rules

2. **HTML shell** — the triage strip markup with placeholder `data-*` attributes and empty render targets. JavaScript fills these from JSON. Example structure:
```html
<div class="triage-strip" id="triage-strip" data-section="triage">
  <div class="triage-zone triage-zone--kpi" id="triage-kpi">
    <!-- JS fills: .triage-kpi-value and .triage-kpi-label -->
  </div>
  <!-- ... etc -->
</div>
```

3. **JavaScript render function** `renderTriageStrip(data)` — accepts the full `report-latest.json` object. Must:
   - Extract the right fields for each zone (note: field names vary by monitor — use `data.signal_panel?.headline || data.signal?.headline || ''`)
   - Apply severity badge classes correctly
   - Handle null/undefined gracefully (empty state with "—" placeholder)
   - Be self-contained (no external dependencies beyond the DOM)

4. **Demo section** — a `<div id="demo">` at the bottom showing the strip rendered with mock data for each of the 7 monitors (WDM, GMM, FCW, ESA, AGM, ERM, SCEM). This is for visual review only.

Mock data for demo:
- WDM: kpi="15 Rapid Decay", signal="Hungary 6 days from pivotal vote; US executive-SCOTUS confrontation enters new phase", chips=["5 Recovery","13 Watch List"], delta=[("Hungary","critical"),("United States","high")]
- GMM: kpi="CRITICAL −0.664", signal="Liberation Day tariff shock activates Cascade Protocol; global stress escalates to CRITICAL", chips=["STAGFLATION","HIGH CONVICTION"], delta=[("EM Equities","critical"),("Bonds","high")]
- SCEM: kpi="4 Active", signal="Gaza ceasefire collapse; Sudan corridor fracture; India-Pakistan LoC exchange", chips=["2 Elevated","1 Critical"], delta=[("Gaza","critical"),("Sudan","high")]
- FCW: kpi="3 Active Ops", signal="Three simultaneous Russian operations targeting Hungary election confirmed", chips=["1 Critical","2 High"], delta=[("SDA Hungary","critical"),("Storm-1516","high")]
- ESA: kpi="47% Defence", signal="EU SAFE instrument passes first reading; US tariff escalation triggers Article 222 consultations", chips=["Energy 62%","Tech 38%"], delta=[("SAFE instrument","high"),("Tariff coercion","high")]
- AGM: kpi="GPT-5 Tier 1", signal="OpenAI GPT-5 release; EU AI Office begins GPAI model evaluation; China deploys military AI", chips=["EU ACT: Amber","US EO: Active"], delta=[("GPT-5","confirmed"),("Military AI","high")]
- ERM: kpi="6/9 Breached", signal="Amazon dieback rate accelerates; AMOC slowdown confirms new precursor threshold", chips=["AMOC: Warning","Amazon: Critical"], delta=[("Amazon","critical"),("AMOC","high")]

## Output rules

- Return ONLY valid HTML — no markdown code fences, no prose before or after
- The file must be self-contained and renderable in a browser without any external files except the Google Fonts import
- Include the Google Fonts import for Satoshi at the top: `@import url('https://api.fontshare.com/v2/css?f[]=satoshi@300,400,500,700&display=swap');`
- Include a meta viewport tag
- Comment each section clearly for the Computer review pass
- At the very top of the file, include a comment block: `<!-- GENERATED BY: generate-triage-strip.py | MODEL: sonar-pro | DATE: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} | STATUS: DRAFT — review before promoting to shared library -->`
"""

print(f"Calling {MODEL}...")
resp = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 0.2,
        "max_tokens": 8000,
    },
    timeout=120
)

if resp.status_code != 200:
    print(f"ERROR: API returned {resp.status_code}: {resp.text[:200]}")
    sys.exit(1)

output = resp.json()["choices"][0]["message"]["content"]

# Strip any markdown fences if model wrapped output
if output.strip().startswith("```"):
    lines = output.strip().split("\n")
    output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

print(f"Generated {len(output)} chars")

# ── Commit to repo ─────────────────────────────────────────────────────────────
encoded = base64.b64encode(output.encode("utf-8")).decode("ascii")

# Check if file exists (for SHA)
existing = subprocess.run(
    ["gh", "api", f"/repos/{REPO}/contents/{OUTPUT_PATH}", "--jq", ".sha"],
    capture_output=True, text=True
)

payload = {
    "message": f"feat(generated): triage-strip draft — sonar-pro {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
    "content": encoded
}
if existing.returncode == 0 and existing.stdout.strip():
    payload["sha"] = existing.stdout.strip().strip('"')

import tempfile, pathlib
tmp = pathlib.Path(tempfile.mktemp(suffix=".json"))
tmp.write_text(json.dumps(payload))

result = subprocess.run(
    ["gh", "api", f"/repos/{REPO}/contents/{OUTPUT_PATH}",
     "--method", "PUT", "--input", str(tmp),
     "--jq", ".commit.sha[:8]"],
    capture_output=True, text=True
)

if result.returncode == 0:
    print(f"Committed to {OUTPUT_PATH}: {result.stdout.strip()}")
else:
    print(f"ERROR committing: {result.stderr.strip()[:200]}")
    sys.exit(1)
