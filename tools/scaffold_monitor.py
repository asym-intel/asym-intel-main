#!/usr/bin/env python3
"""
tools/scaffold_monitor.py — G-MONITOR-SCAFFOLD Gate Closure

Generates the full 11-file GitHub Actions workflow suite for a new monitor.
All templates are parameterized from the WDM reference workflows and produce
byte-for-byte equivalent output when invoked with WDM values.

Usage:
    python tools/scaffold_monitor.py \\
        --abbr fim \\
        --slug financial-integrity \\
        --display-name "Financial Integrity Monitor" \\
        --day WED \\
        --reasoner-name "FIM Reasoner — Financial Stress Pattern Analysis" \\
        --interpreter-name "FIM Interpreter" \\
        --reviewer-name "FIM Reviewer" \\
        --applier-name "FIM Applier"

Self-test (verifies WDM parity):
    python tools/scaffold_monitor.py --self-test
"""

import argparse
import difflib
import os
import pathlib
import sys
import tempfile

# ---------------------------------------------------------------------------
# Day name expansion (abbreviation → full name for use in schedule comments)
# ---------------------------------------------------------------------------
DAY_NAMES = {
    "MON": "Monday",
    "TUE": "Tuesday",
    "WED": "Wednesday",
    "THU": "Thursday",
    "FRI": "Friday",
    "SAT": "Saturday",
    "SUN": "Sunday",
}


def expand_day(day: str) -> str:
    """Expand abbreviated day (MON) to full name (Monday), pass through if already full."""
    return DAY_NAMES.get(day.upper(), day)


# ---------------------------------------------------------------------------
# T1 — collector
# ---------------------------------------------------------------------------
T1_COLLECTOR = """\
name: {ABBR} Collector — Tier 0 daily pre-verification

on:
  workflow_dispatch:        # allow manual trigger from Actions tab for testing

jobs:
  collect:
    name: {ABBR} Tier 0 Collection
    runs-on: ubuntu-latest
    permissions:
      contents: write       # required to commit pipeline/ output back to repo

    steps:
      - name: Checkout repo
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests

      - name: Run {ABBR} Collector
        env:
          PPLX_API_KEY: ${{{{ secrets.PPLX_API_KEY }}}}
        run: python pipeline/monitors/{slug}/collect.py

      - name: Commit Collector output
        run: |
          git config user.name  "{ABBR} Collector Bot"
          git config user.email "{abbr}-collector@asym-intel.info"
          git add pipeline/monitors/{slug}/daily/
          git diff --staged --quiet && echo "No new findings to commit" && exit 0
          git commit -m "data({abbr}-collector): Tier 0 daily pre-verification — $(date -u +%Y-%m-%d)"
          for attempt in 1 2 3; do
            git pull --rebase --autostash origin main
            git push && break
            echo "Push attempt $attempt/3 failed — retrying in ${{attempt}}0s..."
            sleep $((attempt * 10))
          done
"""

# ---------------------------------------------------------------------------
# T2 — chatter
# ---------------------------------------------------------------------------
T2_CHATTER = """\
name: {ABBR} Chatter — Daily Signal

on:
  workflow_dispatch:  # Schedule DISABLED 13 Apr 2026 — replaced by unified-chatter.yml

jobs:
  chatter:
    name: {ABBR} Daily Chatter (sonar)
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install requests
      - name: Run {ABBR} Chatter
        env:
          PPLX_API_KEY: ${{{{ secrets.PPLX_API_KEY }}}}
        run: python pipeline/monitors/{slug}/{abbr}-chatter.py
      - name: Commit chatter output
        uses: ./.github/actions/authenticated-push
        with:
          gh-token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          commit-message: "data({abbr}-chatter): daily signal — $(date -u +%Y-%m-%d)"
          add-paths: "static/monitors/{slug}/data/chatter*.json"
          bot-name: "{ABBR} Chatter Bot"
          bot-email: "{abbr}-chatter@asym-intel.info"
"""

# ---------------------------------------------------------------------------
# T3 — weekly-research
# ---------------------------------------------------------------------------
T3_WEEKLY_RESEARCH = """\
name: {ABBR} Weekly Deep Research

on:
  workflow_dispatch:        # allow manual trigger from Actions tab

jobs:
  research:
    name: {ABBR} Weekly Deep Research
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}

      # ── Phase B Step 6 cutover — engine + bespoke config live in internal ──
      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests pyyaml anthropic

      # The engine reads bespoke files via paths like
      # `pipeline/monitors/{{slug}}/weekly-research-prompt.txt`, resolved
      # relative to the process CWD (public-main root). Stage those files
      # from the internal checkout into the expected public-root path.
      # §15 IP boundary preserved — they are never committed back.
      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml                pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/weekly-research-prompt.txt  pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/weekly-research-domain.md   pipeline/monitors/{slug}/ || true
          cp -v internal/pipeline/monitors/{slug}/weekly-research-schema.json pipeline/monitors/{slug}/ || true

      - name: Run weekly deep research (engine dispatch)
        env:
          PPLX_API_KEY:      ${{{{ secrets.PPLX_API_KEY }}}}
          ANTHROPIC_API_KEY: ${{{{ secrets.ANTHROPIC_API_KEY }}}}
          GH_TOKEN:          ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          PYTHONPATH:        internal
        run: python -m pipeline.engine.weekly_research_base --monitor {slug}

      - name: Commit research output
        run: |
          git config user.name  "{ABBR} Research Bot"
          git config user.email "{abbr}-research@asym-intel.info"
          git pull --rebase --autostash origin main
          # Only stage output dirs — bespoke files in-tree are ephemeral-runtime only
          git add pipeline/monitors/{slug}/weekly/
          git diff --staged --quiet && echo "No research output to commit" && exit 0
          git commit -m "data({abbr}-research): weekly deep research — $(date -u +%Y-%m-%d)"
          git push

      - name: Archive prompt exchanges to internal repo
        if: always()
        env:
          GH_TOKEN:      ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          GITHUB_RUN_ID: ${{{{ github.run_id }}}}
        run: python tools/commit_exchange_log.py
"""

# ---------------------------------------------------------------------------
# T4 — reasoner
# ---------------------------------------------------------------------------
T4_REASONER = """\
name: {reasoner_name}

on:
  workflow_dispatch:        # allow manual trigger from Actions tab

jobs:
  reason:
    name: {ABBR} Deterioration Pattern Reasoning
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}

      # ── Phase B Step 6 cutover — engine + bespoke config live in internal ──
      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests pyyaml

      - name: Fetch identity card from internal repo
        env:
          GH_TOKEN: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
        run: |
          mkdir -p docs/identity
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/identities/IDENTITY-{ABBR}.md" \\
            -o docs/identity/{abbr}-identity.md \\
            && echo "Identity card fetched ($(wc -c < docs/identity/{abbr}-identity.md) bytes)" \\
            || echo "WARNING: Identity card not found — continuing without it"

      # The engine reads bespoke files via paths resolved relative to CWD
      # (public-main root). Stage the internal checkout's bespoke files there.
      # §15 IP boundary preserved — they are never committed back.
      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml             pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/reasoner-prompt.txt      pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/reasoner-instructions.md pipeline/monitors/{slug}/ || true
          cp -v internal/pipeline/monitors/{slug}/reasoner-schema.json     pipeline/monitors/{slug}/ || true

      - name: Run {ABBR} Reasoner (engine dispatch)
        env:
          PPLX_API_KEY: ${{{{ secrets.PPLX_API_KEY }}}}
          GH_TOKEN:     ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          PYTHONPATH:   internal
        run: python -m pipeline.engine.reasoner_base --monitor {slug}

      - name: Commit reasoner output
        run: |
          git config user.name  "{ABBR} Reasoner Bot"
          git config user.email "{abbr}-reasoner@asym-intel.info"
          git add pipeline/monitors/{slug}/reasoner/
          git diff --staged --quiet && echo "No reasoner output to commit" && exit 0
          git commit -m "data({abbr}-reasoner): deterioration pattern analysis — $(date -u +%Y-%m-%d)"
          for attempt in 1 2 3; do
            git pull --rebase --autostash origin main
            git push && break
            echo "Push attempt $attempt/3 failed — retrying in ${{attempt}}0s..."
            sleep $((attempt * 10))
          done
"""

# ---------------------------------------------------------------------------
# T5 — synthesiser
# NOTE: The addendum fetch URL uses {slug}-vdem-2026.md (WDM-specific artifact
# name preserved from the reference workflow for byte-for-byte parity).
# ---------------------------------------------------------------------------
T5_SYNTHESISER = """\
name: "{display_name} Synthesiser"

on:
  workflow_dispatch:
    inputs:
      model:
        description: 'Override model (optional; blank = use metadata.yml default)'
        required: false
        default: ''

jobs:
  synthesise:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}

      # ── Phase B Step 6 cutover — engine + bespoke config live in internal ──
      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Fetch {ABBR} methodology + identity from internal repo
        env:
          GH_TOKEN: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
        run: |
          mkdir -p docs/methodology docs/identity

          # Identity card (analytical quality standard)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/identities/IDENTITY-{ABBR}.md" \\
            -o docs/identity/{abbr}-identity.md \\
            && echo "Identity card fetched ($(wc -c < docs/identity/{abbr}-identity.md) bytes)" \\
            || echo "WARNING: Identity card not found — continuing without it"

          # Methodology (private IP — stays in internal repo)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/methodology/{slug}-full.md" \\
            -o docs/methodology/{slug}-full.md
          echo "{ABBR} methodology fetched ($(wc -c < docs/methodology/{slug}-full.md) bytes)"

          # Addendum (optional — don't fail if absent)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/methodology/{slug}-vdem-2026.md" \\
            -o docs/methodology/{slug}-addendum.md \\
            && echo "{ABBR} addendum fetched ($(wc -c < docs/methodology/{slug}-addendum.md) bytes)" \\
            || echo "No addendum found — continuing without it"

      - name: Set up Python 3.12
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests pyyaml

      # The engine reads bespoke files via paths resolved relative to CWD
      # (public-main root). Stage the internal checkout's bespoke files there.
      # §15 IP boundary preserved — they are never committed back.
      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml             pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/synthesiser-prompt.txt   pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/synthesiser-schema.json  pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/synthesiser-domain.md    pipeline/monitors/{slug}/ || true

      - name: Run {ABBR} synthesiser (engine dispatch)
        env:
          PPLX_API_KEY: ${{{{ secrets.PPLX_API_KEY }}}}
          GH_TOKEN:     ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          REPO_ROOT:    ${{{{ github.workspace }}}}
          SYNTH_MODEL:  ${{{{ github.event.inputs.model }}}}
          PYTHONPATH:   internal
        run: python -m pipeline.engine.synth_base --monitor {slug}

      - name: Commit synthesis output
        run: |
          git config user.name  "monitor-bot"
          git config user.email "monitor-bot@asym-intel.info"
          git add pipeline/monitors/{slug}/synthesised/
          git diff --cached --quiet || git commit -m "chore({abbr}): synthesiser run $(date -u +%Y-%m-%d)"
          git pull --rebase --autostash origin main
          git push
"""

# ---------------------------------------------------------------------------
# T6 — interpreter
# NOTE: Sprint-specific header comments preserved verbatim from WDM reference
# for byte-for-byte parity. {ABBR} parameterizes the monitor abbreviation.
# ---------------------------------------------------------------------------
T6_INTERPRETER = """\
name: "{interpreter_name}"

# ── Sprint AN — {ABBR} Interpreter role ──
# Chained after {ABBR} Reasoner success, extending the cron-dispatched
# chain. Reads weekly-latest.json + reasoner-latest.json (the two
# artefacts the Interpreter consumes via paths.weekly_latest +
# paths.reasoner_latest) and produces interpret-latest.json.
# Topology mirrors AGM Interpreter (AD-2026-04-26-AN).
# Sprint AN adds workflow_run trigger on {ABBR} Reasoner so cron-dispatched
# {ABBR} runs cascade automatically: Reasoner → Interpreter → Reviewer →
# Composer → Applier → Curator end-to-end.
# {ABBR} publishes Monday 06:00 UTC (cron-dispatched separately).

on:
  workflow_dispatch:
    inputs:
      model:
        description: 'Override model (optional; blank = use metadata.yml default)'
        required: false
        default: ''
      weekly-file:
        description: 'Override weekly bundle filename (e.g. weekly-2026-04-28.json). Empty = use weekly-latest.json.'
        required: false
        default: ''
  workflow_run:
    workflows: ["{reasoner_name}"]
    types:
      - completed

jobs:
  interpret:
    # Gate: only run if upstream reasoner actually succeeded.
    # workflow_dispatch runs always pass this guard.
    if: ${{{{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}}}
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          ref: main

      # ── {ABBR} Interpreter — engine + bespoke config live in internal repo ──
      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Fetch {ABBR} methodology + identity from internal repo
        env:
          GH_TOKEN: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
        run: |
          mkdir -p docs/methodology docs/identity

          # Identity card (analytical quality standard)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/identities/IDENTITY-{ABBR}.md" \\
            -o docs/identity/{abbr}-identity.md \\
            && echo "Identity card fetched ($(wc -c < docs/identity/{abbr}-identity.md) bytes)" \\
            || echo "WARNING: Identity card not found — continuing without it"

          # Methodology (private IP — stays in internal repo)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/methodology/{slug}-full.md" \\
            -o docs/methodology/{slug}-full.md
          echo "{ABBR} methodology fetched ($(wc -c < docs/methodology/{slug}-full.md) bytes)"

          # Addendum (optional — don't fail if absent)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/methodology/{slug}-addendum.md" \\
            -o docs/methodology/{slug}-addendum.md \\
            && echo "{ABBR} addendum fetched ($(wc -c < docs/methodology/{slug}-addendum.md) bytes)" \\
            || echo "No addendum found — continuing without it"

      - name: Set up Python 3.12
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests pyyaml

      # The engine reads bespoke files via paths resolved relative to CWD
      # (public-main root). Stage the internal checkout's bespoke files there.
      # §15 IP boundary preserved — they are never committed back.
      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml             pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/interpreter-prompt.txt   pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/interpreter-schema.json  pipeline/monitors/{slug}/

      - name: Run {ABBR} interpreter (engine dispatch)
        env:
          PPLX_API_KEY:             ${{{{ secrets.PPLX_API_KEY }}}}
          GH_TOKEN:                 ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          REPO_ROOT:                ${{{{ github.workspace }}}}
          SYNTH_MODEL:              ${{{{ github.event.inputs.model }}}}
          WEEKLY_FILE_OVERRIDE:     ${{{{ github.event.inputs.weekly-file }}}}
          monitor:                  {slug}
          PYTHONPATH:               internal
        run: python -m pipeline.engine.interpret_base --monitor {slug}

      - name: Commit interpret output
        run: |
          git config user.name  "monitor-bot"
          git config user.email "monitor-bot@asym-intel.info"
          git add pipeline/monitors/{slug}/synthesised/
          git diff --cached --quiet || git commit -m "chore({abbr}): interpreter run $(date -u +%Y-%m-%d)"
          git pull --rebase --autostash origin main
          git push
"""

# ---------------------------------------------------------------------------
# T7 — reviewer
# NOTE: Sprint-specific header comments preserved verbatim from WDM reference.
# ---------------------------------------------------------------------------
T7_REVIEWER = """\
name: "{reviewer_name}"

# ── Sprint AM — {ABBR} Reviewer role ──
# Chained after {ABBR} Interpreter success, upstream of {ABBR} Composer.
# Reads interpret-latest.json and produces review-latest.json with a
# deterministic verdict (set by rule engine R1–R7 in review_base.py)
# plus LLM-advisory notes[]. The Composer downstream honours the
# verdict: REJECT / SKIP_ERROR_CYCLE → early exit; APPROVE /
# APPROVE_WITH_FLAGS / SKIP_NULL_CYCLE → normal render path.
# Mirrors AGM Reviewer topology (AD-2026-04-26-AM).

on:
  workflow_dispatch:
    inputs:
      model:
        description: 'Override reviewer model (optional; blank = use metadata.yml default)'
        required: false
        default: ''
      no_llm:
        description: 'Skip LLM call (rule engine only) — "1" to enable'
        required: false
        default: ''
  workflow_run:
    workflows: ["{interpreter_name}"]
    types:
      - completed

jobs:
  review:
    # Gate: only run if upstream interpreter actually succeeded.
    # workflow_dispatch runs always pass this guard.
    if: ${{{{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}}}
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          ref: main

      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Fetch {ABBR} identity from internal repo
        env:
          GH_TOKEN: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
        run: |
          mkdir -p docs/identity

          # Identity card (analytical quality standard — shared across roles)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/identities/IDENTITY-{ABBR}.md" \\
            -o docs/identity/{abbr}-identity.md \\
            && echo "Identity card fetched ($(wc -c < docs/identity/{abbr}-identity.md) bytes)" \\
            || echo "WARNING: Identity card not found — continuing without it"

      - name: Set up Python 3.12
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests pyyaml

      # The engine reads bespoke files via paths resolved relative to CWD
      # (public-main root). Stage the internal checkout's bespoke files
      # there. §15 IP boundary preserved — they are never committed back.
      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml          pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/reviewer-prompt.txt   pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/reviewer-schema.json  pipeline/monitors/{slug}/

      # Skip-on-missing guard. If upstream Interpreter didn't produce
      # interpret-latest.json, exit 0 so the chain doesn't block.
      - name: Check upstream interpret output
        id: check
        run: |
          INTERPRET_PATH="pipeline/monitors/{slug}/synthesised/interpret-latest.json"
          if [ ! -f "$INTERPRET_PATH" ]; then
            echo "skip=true"   >> "$GITHUB_OUTPUT"
            echo "reason=missing-interpret-latest" >> "$GITHUB_OUTPUT"
            echo "No interpret-latest.json found — skipping Reviewer."
            exit 0
          fi
          echo "skip=false" >> "$GITHUB_OUTPUT"

      - name: Run {ABBR} reviewer (engine dispatch)
        if: steps.check.outputs.skip != 'true'
        env:
          PPLX_API_KEY:    ${{{{ secrets.PPLX_API_KEY }}}}
          GH_TOKEN:        ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          REPO_ROOT:       ${{{{ github.workspace }}}}
          REVIEW_MODEL:    ${{{{ github.event.inputs.model }}}}
          REVIEWER_NO_LLM: ${{{{ github.event.inputs.no_llm }}}}
          monitor:         {slug}
          PYTHONPATH:      internal
        run: python -m pipeline.engine.review_base --monitor {slug}

      - name: Commit review output
        if: steps.check.outputs.skip != 'true'
        run: |
          git config user.name  "monitor-bot"
          git config user.email "monitor-bot@asym-intel.info"
          git add pipeline/monitors/{slug}/synthesised/
          git diff --cached --quiet || git commit -m "chore({abbr}): reviewer run $(date -u +%Y-%m-%d)"
          git pull --rebase --autostash origin main
          git push
"""

# ---------------------------------------------------------------------------
# T8 — composer
# NOTE: Sprint-specific header comments preserved verbatim from WDM reference.
# ---------------------------------------------------------------------------
T8_COMPOSER = """\
name: "{ABBR} Composer"

# ── Sprint AM — {ABBR} Composer role ──
# Chained after {ABBR} Reviewer success. Reads interpret-latest.json +
# review-latest.json and composes a grounded weekly brief draft (no
# new claims; claim_trace[] tied to interpreter claim IDs).
#
# Reviewer verdict handling:
#   APPROVE / APPROVE_WITH_FLAGS / SKIP_NULL_CYCLE → normal render.
#   REJECT / SKIP_ERROR_CYCLE                     → skip (publisher fallback).
#
# Chain-depth note: GitHub limits workflow_run-triggered chains to
# 3 levels deep. At Composer, the chain is depth 3 (Interpreter →
# Reviewer → Composer). Composer therefore triggers Applier via
# explicit `gh workflow run` (chain-depth reset), mirroring AGM
# topology (AD-2026-04-26-AM).

on:
  workflow_dispatch:
    inputs:
      model:
        description: 'Override composer model (optional; blank = use metadata.yml default)'
        required: false
        default: ''
  workflow_run:
    workflows: ["{reviewer_name}"]
    types:
      - completed

jobs:
  compose:
    # Gate: only run if upstream reviewer actually succeeded.
    # workflow_dispatch runs always pass this guard.
    if: ${{{{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}}}
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          ref: main

      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Fetch {ABBR} identity from internal repo
        env:
          GH_TOKEN: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
        run: |
          mkdir -p docs/identity

          # Identity card (analytical quality standard — shared across roles)
          curl -sf -H "Authorization: token ${{GH_TOKEN}}" \\
            -H "Accept: application/vnd.github.v3.raw" \\
            "https://api.github.com/repos/asym-intel/asym-intel-internal/contents/identities/IDENTITY-{ABBR}.md" \\
            -o docs/identity/{abbr}-identity.md \\
            && echo "Identity card fetched ($(wc -c < docs/identity/{abbr}-identity.md) bytes)" \\
            || echo "WARNING: Identity card not found — continuing without it"

      - name: Set up Python 3.12
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests pyyaml

      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml          pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/composer-prompt.txt   pipeline/monitors/{slug}/
          cp -v internal/pipeline/monitors/{slug}/composer-schema.json  pipeline/monitors/{slug}/

      # Skip-on-disposition guard. Two layers (workflow + engine) keep the
      # chain honest.
      # Interpreter disposition: error_cycle → skip.
      # Reviewer verdict: REJECT / SKIP_ERROR_CYCLE → skip.
      # Missing review-latest.json → proceed (pre-reviewer behaviour).
      - name: Check interpreter disposition + reviewer verdict
        id: disposition
        run: |
          INTERPRET_PATH="pipeline/monitors/{slug}/synthesised/interpret-latest.json"
          REVIEW_PATH="pipeline/monitors/{slug}/synthesised/review-latest.json"

          if [ ! -f "$INTERPRET_PATH" ]; then
            echo "skip=true"       >> "$GITHUB_OUTPUT"
            echo "reason=missing-interpret-latest" >> "$GITHUB_OUTPUT"
            echo "No interpret-latest.json found — skipping Composer."
            exit 0
          fi
          DISPOSITION=$(python -c "import json; d=json.load(open('$INTERPRET_PATH')); print((d.get('_meta') or {{}}).get('cycle_disposition',''))")
          echo "disposition=$DISPOSITION"
          if [ "$DISPOSITION" = "error_cycle" ]; then
            echo "skip=true"   >> "$GITHUB_OUTPUT"
            echo "reason=error_cycle" >> "$GITHUB_OUTPUT"
            echo "Interpreter reported error_cycle — skipping Composer."
            exit 0
          fi

          if [ -f "$REVIEW_PATH" ]; then
            VERDICT=$(python -c "import json; d=json.load(open('$REVIEW_PATH')); print(d.get('verdict',''))")
            echo "verdict=$VERDICT"
            if [ "$VERDICT" = "REJECT" ]; then
              echo "skip=true" >> "$GITHUB_OUTPUT"
              echo "reason=reviewer_reject" >> "$GITHUB_OUTPUT"
              echo "Reviewer verdict=REJECT — skipping Composer."
              exit 0
            fi
            if [ "$VERDICT" = "SKIP_ERROR_CYCLE" ]; then
              echo "skip=true" >> "$GITHUB_OUTPUT"
              echo "reason=reviewer_skip_error_cycle" >> "$GITHUB_OUTPUT"
              echo "Reviewer verdict=SKIP_ERROR_CYCLE — skipping Composer."
              exit 0
            fi
          else
            echo "verdict=(no review-latest.json; proceeding on Interpreter disposition alone)"
          fi

          echo "skip=false" >> "$GITHUB_OUTPUT"
          echo "reason=ok"  >> "$GITHUB_OUTPUT"

      - name: Run {ABBR} composer (engine dispatch)
        if: steps.disposition.outputs.skip != 'true'
        env:
          PPLX_API_KEY: ${{{{ secrets.PPLX_API_KEY }}}}
          GH_TOKEN:     ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          REPO_ROOT:    ${{{{ github.workspace }}}}
          SYNTH_MODEL:  ${{{{ github.event.inputs.model }}}}
          monitor:      {slug}
          PYTHONPATH:   internal
        run: python -m pipeline.engine.compose_base --monitor {slug}

      - name: Commit compose output
        if: steps.disposition.outputs.skip != 'true'
        run: |
          git config user.name  "monitor-bot"
          git config user.email "monitor-bot@asym-intel.info"
          git add pipeline/monitors/{slug}/synthesised/
          git diff --cached --quiet || git commit -m "chore({abbr}): composer run $(date -u +%Y-%m-%d)"
          git pull --rebase --autostash origin main
          git push

      # Trigger Applier via direct API dispatch (chain-depth reset).
      # GitHub limits workflow_run-triggered chains to 3 levels; Composer
      # is depth 3. Using `gh workflow run` resets depth to 0, enabling
      # Applier → Curator [wf_run-1] to complete. Mirrors AGM topology.
      - name: Trigger Applier (chain-depth reset)
        if: steps.disposition.outputs.skip != 'true'
        env:
          GH_TOKEN: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
        run: |
          gh workflow run {abbr}-applier.yml \\
            --repo ${{{{ github.repository }}}} \\
            --ref main
"""

# ---------------------------------------------------------------------------
# T9 — applier
# NOTE: Sprint-specific header comments preserved verbatim from WDM reference.
# ---------------------------------------------------------------------------
T9_APPLIER = """\
name: "{ABBR} Applier"

# ── Sprint AM — {ABBR} Applier role ──
# Triggered by {ABBR} Composer via explicit `gh workflow run` (chain-depth
# reset; mirrors AGM Applier topology, AD-2026-04-26-AM). Reads all three
# upstream artefacts (interpret-latest.json, review-latest.json,
# compose-latest.json) and produces:
#   - apply-YYYY-MM-DD.json + apply-latest.json (cycle manifest)
#   - chains-YYYY-MM-DD.json + chains-latest.json (public claim→review→
#     patch→evidence chains, one per structured_claim)
# LLM-FREE — deterministic stitching only. No PPLX_API_KEY needed.
# No prompt/schema staging needed. Replay-safe.

on:
  workflow_dispatch: {{}}

jobs:
  apply:
    if: ${{{{ github.event_name == 'workflow_dispatch' }}}}
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          ref: main

      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Set up Python 3.12
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install pyyaml

      # Stage bespoke metadata. No prompt/schema staging (LLM-free).
      # §15 IP boundary preserved — never committed back.
      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml \\
                pipeline/monitors/{slug}/

      # Skip-on-missing guard. All three upstream artefacts required;
      # if any is absent exit 0 so the chain doesn't block.
      - name: Check upstream artefacts
        id: check
        run: |
          I="pipeline/monitors/{slug}/synthesised/interpret-latest.json"
          R="pipeline/monitors/{slug}/synthesised/review-latest.json"
          C="pipeline/monitors/{slug}/synthesised/compose-latest.json"
          MISSING=""
          [ -f "$I" ] || MISSING="${{MISSING}} interpret-latest"
          [ -f "$R" ] || MISSING="${{MISSING}} review-latest"
          [ -f "$C" ] || MISSING="${{MISSING}} compose-latest"
          if [ -n "$MISSING" ]; then
            echo "skip=true"   >> "$GITHUB_OUTPUT"
            echo "reason=missing:${{MISSING}}" >> "$GITHUB_OUTPUT"
            echo "Missing upstream artefacts:${{MISSING}} — skipping Applier."
            exit 0
          fi
          echo "skip=false" >> "$GITHUB_OUTPUT"

      - name: Run {ABBR} applier (engine dispatch)
        if: steps.check.outputs.skip != 'true'
        env:
          REPO_ROOT:        ${{{{ github.workspace }}}}
          monitor:          {slug}
          PYTHONPATH:       internal
          INTERPRET_RUN_ID: ${{{{ github.event.workflow_run.id }}}}
          REVIEW_RUN_ID:    ${{{{ github.event.workflow_run.id }}}}
          COMPOSE_RUN_ID:   ${{{{ github.event.workflow_run.id }}}}
        run: python -m pipeline.engine.apply_base --monitor {slug}

      - name: Commit applier output
        if: steps.check.outputs.skip != 'true'
        run: |
          git config user.name  "monitor-bot"
          git config user.email "monitor-bot@asym-intel.info"
          rm -f pipeline/monitors/{slug}/applied/apply-debug-*.json
          git add pipeline/monitors/{slug}/applied/
          git diff --cached --quiet || git commit -m "chore({abbr}): applier run $(date -u +%Y-%m-%d)"
          git pull --rebase --autostash origin main
          git push
"""

# ---------------------------------------------------------------------------
# T10 — curator
# NOTE: Sprint-specific header comments preserved verbatim from WDM reference.
# The "disabled for {ABBR}" comment is parameterized since {ABBR} appears there.
# ---------------------------------------------------------------------------
T10_CURATOR = """\
name: "{ABBR} Curator"

# ── Sprint AM — {ABBR} Curator role ──
# Chained after {ABBR} Applier success (workflow_run depth 0 → 1, valid
# because Applier enters via workflow_dispatch chain-depth reset).
# Reads interpret-latest.json + chains-latest.json + apply-latest.json
# plus prior N cycles' archives and produces:
#   - drift-register-YYYY-MM-DD.json (immutable per-cycle)
#   - drift-register-latest.json (rolling pointer)
# LLM-FREE — deterministic drift detection only. Four typed triggers:
#   T1 — schema-shape change ≥2 in window without methodology bump
#   T2 — tracked rating flip without fresh T1 evidence (disabled for {ABBR}
#         initially — T2 tracked_predicates empty until first material cycle)
#   T3 — entity silent drop from registry
#   T4 — carry-forward rate ≥ 0.80 on a non-null cycle
# NON-BLOCKING (advisory only). Mirrors AGM Curator topology (AD-2026-04-26-AM).

on:
  workflow_dispatch: {{}}
  workflow_run:
    workflows: ["{applier_name}"]
    types:
      - completed

jobs:
  curate:
    # Gate: only run if upstream applier actually succeeded.
    # workflow_dispatch runs always pass this guard.
    if: ${{{{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}}}
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Checkout public repo (asym-intel-main)
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          ref: main
          # Curator needs prior cycle history to compute T1/T4 windows.
          # Fetch full history so archives from prior cycles are available.
          fetch-depth: 0

      - name: Checkout internal repo (engine + bespoke config)
        uses: actions/checkout@v5
        with:
          repository: asym-intel/asym-intel-internal
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
          path: internal
          sparse-checkout: |
            pipeline/engine
            pipeline/policy
            pipeline/monitors/{slug}
          sparse-checkout-cone-mode: false

      - name: Set up Python 3.12
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install pyyaml jsonschema

      # Stage bespoke metadata. No prompt/schema staging (LLM-free).
      # §15 IP boundary preserved — never committed back.
      - name: Stage bespoke config into expected paths
        run: |
          mkdir -p pipeline/monitors/{slug}
          cp -v internal/pipeline/monitors/{slug}/metadata.yml \\
                pipeline/monitors/{slug}/

      # Skip-on-missing guard.
      - name: Check upstream artefacts
        id: check
        run: |
          A="pipeline/monitors/{slug}/applied/apply-latest.json"
          I="pipeline/monitors/{slug}/synthesised/interpret-latest.json"
          MISSING=""
          [ -f "$A" ] || MISSING="${{MISSING}} apply-latest"
          [ -f "$I" ] || MISSING="${{MISSING}} interpret-latest"
          if [ -n "$MISSING" ]; then
            echo "skip=true"   >> "$GITHUB_OUTPUT"
            echo "reason=missing:${{MISSING}}" >> "$GITHUB_OUTPUT"
            echo "Missing upstream artefacts:${{MISSING}} — skipping Curator."
            exit 0
          fi
          echo "skip=false" >> "$GITHUB_OUTPUT"

      - name: Run {ABBR} curator (engine dispatch)
        if: steps.check.outputs.skip != 'true'
        env:
          REPO_ROOT:      ${{{{ github.workspace }}}}
          monitor:        {slug}
          PYTHONPATH:     internal
          CURATOR_RUN_ID: ${{{{ github.event.workflow_run.id }}}}
          GITHUB_SHA:     ${{{{ github.sha }}}}
        run: python -m pipeline.engine.curator_base --monitor {slug}

      - name: Commit curator output
        if: steps.check.outputs.skip != 'true'
        run: |
          git config user.name  "monitor-bot"
          git config user.email "monitor-bot@asym-intel.info"
          git add pipeline/monitors/{slug}/curator/
          git diff --cached --quiet || git commit -m "chore({abbr}): curator run $(date -u +%Y-%m-%d)"
          git pull --rebase --autostash origin main
          git push
"""

# ---------------------------------------------------------------------------
# T11 — publisher
# ---------------------------------------------------------------------------
T11_PUBLISHER = """\
name: {ABBR} Publisher — Weekly Report

on:
  # Schedule: {day} 06:00 UTC (after synthesiser completes)
  workflow_dispatch:          # manual trigger for testing

jobs:
  publish:
    name: Publish {ABBR} Weekly Report
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Run {ABBR} Publisher
        id: run_publisher
        env:
          REPO_ROOT: ${{{{ github.workspace }}}}
          MONITOR_SLUG: {slug}
          # LINEAGE_WRITE_TOKEN: used by pipeline/shared/lineage.py to write provenance
          # envelopes to asym-intel-internal/archive/lineage/. Non-blocking if absent.
          LINEAGE_WRITE_TOKEN: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}
        run: |
          python3 pipeline/publishers/publisher.py
          ISSUE=$(python3 -c 'import json; print(json.load(open("static/monitors/{slug}/data/report-latest.json"))["meta"]["issue"])')
          echo "issue_number=$ISSUE" >> $GITHUB_OUTPUT

      - name: Pre-publication integrity gate
        uses: ./.github/actions/integrity-gate
        with:
          monitor-slug: {slug}
          gh-token: ${{{{ secrets.ASYM_INTEL_PIPELINE }}}}

      - name: Commit published report
        run: |
          git config user.name "{ABBR} Publisher Bot"
          git config user.email "{abbr}-publisher@asym-intel.info"
          git add static/monitors/{slug}/data/
          git add docs/monitors/{slug}/data/
          git add content/monitors/{slug}/
          git diff --staged --quiet && echo "No changes to commit" && exit 0
          git commit -m "data({abbr}): Issue ${{{{ steps.run_publisher.outputs.issue_number }}}} published by {ABBR} Publisher Bot"
          for attempt in 1 2 3; do
            git pull --rebase --autostash origin main
            git push && break
            echo "Push attempt $attempt/3 failed — retrying in ${{attempt}}0s..."
            sleep $((attempt * 10))
          done

      - name: Purge Cloudflare cache
        if: success()
        env:
          CF_TOKEN: ${{{{ secrets.PPLX_COMPUTER_ASYM_ENGINE }}}}
          CF_ZONE: cc419b7519eba04ef0dc6a7b851930c7
        run: |
          curl -s -X POST \\
            "https://api.cloudflare.com/client/v4/zones/${{CF_ZONE}}/purge_cache" \\
            -H "Authorization: Bearer ${{CF_TOKEN}}" \\
            -H "Content-Type: application/json" \\
            -d '{{
              "files": [
                "https://asym-intel.info/monitors/{slug}/data/report-latest.json",
                "https://asym-intel.info/monitors/{slug}/data/report-latest.md"
              ]
            }}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('CF purge:', 'ok' if d.get('success') else d.get('errors'))"
"""

# ---------------------------------------------------------------------------
# File map: (output_filename_template, template_string)
# ---------------------------------------------------------------------------
FILES = [
    ("{abbr}-collector.yml",       T1_COLLECTOR),
    ("{abbr}-chatter.yml",         T2_CHATTER),
    ("{abbr}-weekly-research.yml", T3_WEEKLY_RESEARCH),
    ("{abbr}-reasoner.yml",        T4_REASONER),
    ("{abbr}-synthesiser.yml",     T5_SYNTHESISER),
    ("{abbr}-interpreter.yml",     T6_INTERPRETER),
    ("{abbr}-reviewer.yml",        T7_REVIEWER),
    ("{abbr}-composer.yml",        T8_COMPOSER),
    ("{abbr}-applier.yml",         T9_APPLIER),
    ("{abbr}-curator.yml",         T10_CURATOR),
    ("{slug}-publisher.yml",       T11_PUBLISHER),
]


def build_ctx(args) -> dict:
    """Build the substitution variable dict from parsed args."""
    ABBR = args.abbr.upper()
    day_full = expand_day(args.day)
    reasoner_name  = args.reasoner_name  or f"{ABBR} Reasoner"
    interpreter_name = args.interpreter_name or f"{ABBR} Interpreter"
    reviewer_name  = args.reviewer_name  or f"{ABBR} Reviewer"
    applier_name   = args.applier_name   or f"{ABBR} Applier"
    return {
        "abbr":             args.abbr,
        "ABBR":             ABBR,
        "slug":             args.slug,
        "display_name":     args.display_name,
        "day":              day_full,
        "reasoner_name":    reasoner_name,
        "interpreter_name": interpreter_name,
        "reviewer_name":    reviewer_name,
        "applier_name":     applier_name,
    }


def render_files(ctx: dict, output_dir: pathlib.Path, dry_run: bool = False) -> list:
    """Render all 11 workflow files. Returns list of output Path objects."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for filename_tpl, template in FILES:
        filename = filename_tpl.format(**ctx)
        content = template.format(**ctx)
        out_path = output_dir / filename
        if dry_run:
            print(f"would write: {out_path}")
        else:
            out_path.write_text(content, encoding="utf-8")
            print(f"wrote: {out_path}")
        written.append(out_path)
    return written


def run_parity_check(generated_files: list, reference_dir: pathlib.Path) -> bool:
    """
    Diff each generated file against the live reference file in reference_dir.
    Returns True if all match (or reference missing), False if any diff found.
    """
    mismatches = []
    for f in generated_files:
        live = reference_dir / f.name
        if not live.exists():
            print(f"  skip (no reference): {live}")
            continue
        generated_text = f.read_text(encoding="utf-8")
        live_text = live.read_text(encoding="utf-8")
        diff = list(difflib.unified_diff(
            live_text.splitlines(keepends=True),
            generated_text.splitlines(keepends=True),
            fromfile=str(live),
            tofile=str(f),
        ))
        if diff:
            mismatches.append((live, diff))

    if mismatches:
        for path, diff in mismatches:
            print(f"\n=== PARITY FAIL: {path} ===")
            print("".join(diff))
        return False

    print("Parity check: all files match live WDM workflows.")
    return True


def self_test(reference_dir: pathlib.Path) -> int:
    """
    Run the parity check by generating WDM-parameterised files to a temp dir
    and diffing them against the reference_dir (default: .github/workflows/).
    Returns 0 on pass, 1 on failure.
    """
    import argparse as _ap

    # Build WDM args
    wdm_args = _ap.Namespace(
        abbr="wdm",
        slug="democratic-integrity",
        display_name="World Democracy Monitor",
        day="MON",
        reasoner_name="WDM Reasoner — Deterioration Pattern Analysis",
        interpreter_name="WDM Interpreter",
        reviewer_name="WDM Reviewer",
        applier_name="WDM Applier",
    )
    ctx = build_ctx(wdm_args)

    with tempfile.TemporaryDirectory(prefix="scaffold-parity-") as tmpdir:
        out_dir = pathlib.Path(tmpdir)
        generated = render_files(ctx, out_dir, dry_run=False)
        # Suppress per-file "wrote:" output for self-test (redirect stdout)
        ok = run_parity_check(generated, reference_dir)

    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold GitHub Actions workflows for a new monitor."
    )
    parser.add_argument("--abbr",             required=False, help="Short monitor abbreviation, lower-case (e.g. wdm, fim)")
    parser.add_argument("--slug",             required=False, help="Kebab-case monitor slug (e.g. democratic-integrity)")
    parser.add_argument("--display-name",     required=False, dest="display_name", help="Human display name (e.g. 'World Democracy Monitor')")
    parser.add_argument("--day",              default="MON",  help="Publish-day comment (e.g. MON, WED, FRI). Default: MON")
    parser.add_argument("--reasoner-name",    default=None,   dest="reasoner_name",    help="Exact Reasoner workflow name")
    parser.add_argument("--interpreter-name", default=None,   dest="interpreter_name", help="Exact Interpreter workflow name")
    parser.add_argument("--reviewer-name",    default=None,   dest="reviewer_name",    help="Exact Reviewer workflow name")
    parser.add_argument("--applier-name",     default=None,   dest="applier_name",     help="Exact Applier workflow name")
    parser.add_argument("--output-dir",       default=".github/workflows", dest="output_dir",
                        help="Output directory. Default: .github/workflows")
    parser.add_argument("--dry-run",          action="store_true", dest="dry_run",
                        help="Print filenames that would be written; do not write.")
    parser.add_argument("--self-test",        action="store_true", dest="self_test",
                        help="Run parity check against WDM reference workflows.")
    parser.add_argument("--wdm-reference-dir", default=None, dest="wdm_reference_dir",
                        help="Directory containing live WDM reference workflows for self-test. "
                             "Default: .github/workflows/")

    args = parser.parse_args()

    if args.self_test:
        if args.wdm_reference_dir:
            ref_dir = pathlib.Path(args.wdm_reference_dir)
        else:
            ref_dir = pathlib.Path(".github/workflows")
        if not ref_dir.exists():
            print(f"ERROR: reference directory not found: {ref_dir}", file=sys.stderr)
            sys.exit(1)
        sys.exit(self_test(ref_dir))

    # Normal invocation — require --abbr, --slug, --display-name
    errors = []
    if not args.abbr:
        errors.append("--abbr is required")
    if not args.slug:
        errors.append("--slug is required")
    if not args.display_name:
        errors.append("--display-name is required")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        parser.print_usage(sys.stderr)
        sys.exit(1)

    ctx = build_ctx(args)
    output_dir = pathlib.Path(args.output_dir)
    render_files(ctx, output_dir, dry_run=args.dry_run)
    sys.exit(0)


if __name__ == "__main__":
    main()
