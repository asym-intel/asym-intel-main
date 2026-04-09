# ⚠️ DO NOT RECREATE — RETIRED

This analyst cron prompt has been retired. The analyst cron was replaced by
the generic publisher (`pipeline/publishers/publisher.py`) on 9 April 2026.

**Current pipeline:**
- Synthesiser prompt: `pipeline/synthesisers/{abbr}/{slug}-synthesiser-api-prompt.txt`
- Collector prompt: `pipeline/monitors/{slug}/{abbr}-collector-api-prompt.txt`
- Weekly research prompt: `pipeline/monitors/{slug}/{abbr}-weekly-research-api-prompt.txt`
- Chatter prompt: `pipeline/monitors/{slug}/{abbr}-chatter-api-prompt.txt`
- Publisher: `pipeline/publishers/publisher.py` (config-driven, no per-monitor prompt)

All prompts are in `asym-intel-main`. Methodology files stay in `asym-intel-internal`.

*Retired: 9 April 2026*

