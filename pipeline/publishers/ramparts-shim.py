#!/usr/bin/env python3
"""
ramparts-shim.py
================
Converts an AIM report-latest.json (asym-intel.info schema) into a
Ramparts-compatible report JSON (ramparts.gi schema).

Usage:
    python3 ramparts-shim.py <input_aim_json> <output_ramparts_json>

Called by ramparts-publisher.yml after freshness check.
Updated: 2026-04-12
"""

import json
import sys
import re
from datetime import datetime


def shim(aim_path, out_path):
    data = json.load(open(aim_path))

    # ── Meta ────────────────────────────────────────────────────────────────
    aim_meta = data.get("meta", data.get("_meta", {}))
    published = aim_meta.get("published", aim_meta.get("synthesised_at", ""))
    pub_date = published.split("T")[0] if published else ""
    week_label_raw = aim_meta.get("week_label", aim_meta.get("week_ending", pub_date))
    # Strip redundant "W/E " prefix if present
    week_label = re.sub(r"^W/E\s+", "", week_label_raw).strip()

    out = {
        "meta": {
            "issue":           aim_meta.get("issue", aim_meta.get("issue_number")),
            "volume":          aim_meta.get("volume", 1),
            "week_label":      week_label,
            "published":       pub_date,
            "slug":            pub_date,
            "schema_version":  "2.0",
            "editor":          "ramparts-publisher-bot",
            "publish_time_utc": "T09:00:00Z",
        }
    }

    # ── module_0 — The Signal ───────────────────────────────────────────────
    m0 = data.get("module_0", {})
    out["module_0"] = {
        "title": m0.get("title", ""),
        "body":  m0.get("body", ""),
    }

    # ── delta_strip — add text/label aliases ────────────────────────────────
    raw_delta = data.get("delta_strip", [])
    out["delta_strip"] = []
    for d in raw_delta:
        entry = dict(d)
        entry["text"]  = d.get("text",  d.get("title", ""))
        entry["label"] = d.get("label", d.get("module_tag", ""))
        out["delta_strip"].append(entry)

    # ── country_grid — expand to full Ramparts schema ───────────────────────
    raw_grid = data.get("country_grid", data.get("jurisdiction_risk_matrix", []))
    out["country_grid"] = []
    for row in raw_grid:
        out["country_grid"].append({
            "jurisdiction":       row.get("jurisdiction", ""),
            "status_icon":        _risk_to_icon(row.get("overall_risk", "")),
            "binding_law":        row.get("binding_law", row.get("key_development", "")),
            "key_guidance":       row.get("key_guidance", ""),
            "standards":          row.get("standards", ""),
            "last_updated":       row.get("last_updated", pub_date),
            "change_flag":        row.get("change_flag", False),
            "regulatory_readiness": row.get("regulatory_readiness", ""),
            "enforcement_capacity": row.get("enforcement_capacity", ""),
            "overall_risk":       row.get("overall_risk", ""),
            "key_development":    row.get("key_development", ""),
            "trajectory":         row.get("trajectory", "Stable"),
        })

    # ── module_1 — Executive Insight ────────────────────────────────────────
    m1 = data.get("module_1", {})
    out["module_1"] = {
        "mainstream":    _shim_m1_items(m1.get("mainstream", []), pub_date),
        "underweighted": _shim_m1_items(m1.get("underweighted", []), pub_date),
    }

    # ── module_2 — Model Frontier (pass-through, add benchmarks stub if missing) ──
    m2_raw = data.get("module_2", {})
    m2 = m2_raw if isinstance(m2_raw, dict) else {}
    out["module_2"] = {
        "models":      m2.get("models", []),
        "papers":      m2.get("papers", m2.get("arxiv_highlights", [])),
        "benchmarks_table": m2.get("benchmarks_table", {
            "arc_agi_2":     [],
            "arc_agi_3":     [],
            "gpqa_diamond":  [],
        }),
        "lmarena_update": m2.get("lmarena_update", {"week_note": "", "source_url": ""}),
        "no_releases": m2.get("no_releases", False),
    }

    # ── module_3 — Investment & M&A ─────────────────────────────────────────
    m3 = data.get("module_3", {})
    out["module_3"] = {
        "funding_rounds":  _shim_m3_funding(m3.get("funding_rounds", []), pub_date),
        "strategic_deals": m3.get("strategic_deals", []),
        "secondary_markets": m3.get("secondary_markets", []),
        "energy_wall":     m3.get("energy_wall", {"signal": "", "items": []}),
    }

    # ── module_4 — Sector Penetration (pass-through) ─────────────────────────
    out["module_4"] = data.get("module_4", {})

    # ── module_5 — European & China Watch ───────────────────────────────────
    m5 = data.get("module_5", {})
    euro_raw = m5.get("european", {})
    china_raw = m5.get("china", {})

    # If european is a list (old AIM schema), convert to object
    if isinstance(euro_raw, list):
        euro_obj = {
            "headline":              next((i.get("item","") for i in euro_raw[:1]), ""),
            "funding":               euro_raw,
            "displacement":          [],
            "sovereign_infrastructure": "",
            "digital_omnibus":       "",
            "standards_vacuum":      "",
        }
    else:
        euro_obj = euro_raw

    if isinstance(china_raw, list):
        china_obj = {
            "headline":        next((i.get("item","") for i in china_raw[:1]), ""),
            "deepseek":        "",
            "alibaba":         "",
            "uscc_report":     "",
            "export_controls": "",
            "state_deployment":"",
            "ciyuan_signal":   "",
        }
        for item in china_raw:
            text = item.get("summary", item.get("item", ""))
            cat  = item.get("category", "").lower()
            if "deepseek" in cat or "deepseek" in text.lower():
                china_obj["deepseek"] = text
            elif "alibaba" in cat or "alibaba" in text.lower():
                china_obj["alibaba"] = text
            elif "uscc" in cat or "export" in cat:
                china_obj["export_controls"] = text
            elif "ciyuan" in text.lower():
                china_obj["ciyuan_signal"] = text
    else:
        china_obj = china_raw

    out["module_5"] = {"european": euro_obj, "china": china_obj}

    # ── module_6 — AI in Science (pass-through) ──────────────────────────────
    out["module_6"] = data.get("module_6", {})

    # ── module_7 — Risk Indicators ───────────────────────────────────────────
    m7 = data.get("module_7", {})
    out["module_7"] = {
        "vectors": [
            dict(v, **{
                "name":     v.get("name",    v.get("vector", "")),
                "level":    v.get("level",   v.get("rating", "")),
                "color":    v.get("color",   _rating_to_color(v.get("rating", v.get("level","")))),
                "headline": v.get("headline",v.get("summary", "")[:80]),
                "detail":   v.get("detail",  v.get("summary", "")),
            })
            for v in m7.get("vectors", [])
        ]
    }

    # ── module_8 — Military AI Watch ─────────────────────────────────────────
    m8 = data.get("module_8", {})
    out["module_8"] = {
        "new_developments": [
            dict(item, **{
                "enforcement": item.get("enforcement", item.get("friction_analysis", "Not yet specified.")),
                "asymmetric":  item.get("asymmetric",  item.get("accountability_implication", "")),
            })
            for item in m8.get("new_developments", m8.get("items", []))
        ]
    }

    # ── module_9 — Law & Guidance ────────────────────────────────────────────
    m9 = data.get("module_9", {})
    # Merge law/standards/litigation into new_developments if not already present
    new_devs = list(m9.get("new_developments", []))
    if not new_devs:
        for item in m9.get("law_highlights", []):
            new_devs.append(dict(item, category="Legislation",
                enforcement=item.get("enforcement","Not yet specified.")))
        for item in m9.get("standards_highlights", []):
            new_devs.append(dict(item, category="Standards",
                enforcement=item.get("enforcement","Not yet specified.")))
        for item in m9.get("litigation_highlights", []):
            new_devs.append(dict(item, category="Litigation",
                enforcement=item.get("enforcement","Not yet specified.")))
    # Ensure enforcement field on all items
    for item in new_devs:
        if "enforcement" not in item:
            item["enforcement"] = item.get("friction_analysis", "Not yet specified.")

    out["module_9"] = {
        "new_developments":   new_devs,
        "no_change":          m9.get("no_change", []),
        "friction_analysis":  m9.get("friction_analysis", ""),
        "eu_ai_act_layered":  m9.get("eu_ai_act_layered", ""),
        "law_highlights":     m9.get("law_highlights", []),
        "standards_highlights": m9.get("standards_highlights", []),
        "litigation_highlights": m9.get("litigation_highlights", []),
    }

    # ── module_10 — AI Governance (pass-through) ─────────────────────────────
    out["module_10"] = data.get("module_10", {})

    # ── module_11 — Ethics & Accountability ──────────────────────────────────
    m11 = data.get("module_11", {})
    out["module_11"] = {
        "items": [
            dict(item, **{
                "asymmetric": item.get("asymmetric", item.get("accountability_implication", "")),
                "body":       item.get("body", item.get("summary", item.get("why_it_matters", ""))),
            })
            for item in m11.get("items", [])
        ]
    }

    # ── module_12 — Technical Standards (replaces AIM Info Ops) ──────────────
    m12_aim = data.get("module_12", {})
    # If AIM has Info Ops content, create a stub Technical Standards structure
    if "items" in m12_aim or "capability_watch" in m12_aim:
        out["module_12"] = {
            "bodies": [
                {
                    "body": "CEN-CENELEC JTC21",
                    "standards": [
                        {
                            "standard":     "Harmonised AI Standards — Status Overview",
                            "status_class": "in-development",
                            "status":       "In development — no harmonised standard in OJ",
                            "scope":        "No harmonised AI standard has reached Published/Operational status under the EU AI Act. Arithmetically impossible to close the vacuum before the August 2026 deadline.",
                            "week_update":  "No material update this week. Standards vacuum remains active.",
                            "source_url":   "https://www.cencenelec.eu/areas-of-work/cen-cenelec-topics/artificial-intelligence/",
                            "source_label": "CEN-CENELEC JTC21",
                        }
                    ]
                }
            ],
            "asymmetric_flags": m12_aim.get("asymmetric_flags", []),
        }
    else:
        out["module_12"] = m12_aim

    # ── modules 13–14 — pass-through ─────────────────────────────────────────
    out["module_13"] = data.get("module_13", {})
    # AIM module_15 (Personnel) → Ramparts module_14
    out["module_14"] = data.get("module_14", data.get("module_15", {}))

    # ── Scorecard / composite fields (pass-through) ───────────────────────────
    for key in ("jurisdiction_risk_matrix", "lab_posture_scorecard",
                "governance_health_composite", "weekly_brief_draft"):
        if key in data:
            out[key] = data[key]

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"✅ Shim complete: {out_path}")
    print(f"   Modules: {[k for k in out.keys() if k.startswith('module_')]}")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _shim_m1_items(items, pub_date):
    out = []
    for i, item in enumerate(items):
        out.append({
            "rank":         item.get("rank", i + 1),
            "headline":     item.get("headline", ""),
            "why_it_matters": item.get("why_it_matters", item.get("body", "")),
            "date":         item.get("date", pub_date),
            "body":         item.get("body", item.get("why_it_matters", "")),
            "asymmetric":   item.get("asymmetric", ""),
            "source_label": item.get("source_label", ""),
            "source_url":   item.get("source_url", ""),
        })
    return out


def _shim_m3_funding(items, pub_date):
    out = []
    for item in items:
        out.append(dict(item, **{
            "date":         item.get("date", item.get("announced", pub_date)),
            "lead":         item.get("lead", item.get("investors", "").split(",")[0].strip()),
            "focus":        item.get("focus", item.get("sector", "")),
            "cursor_curve": item.get("cursor_curve", False),
            "cursor_note":  item.get("cursor_note", item.get("asymmetric", "")),
        }))
    return out


def _risk_to_icon(rating):
    r = (rating or "").upper()
    if r in ("HIGH",):         return "🔴"
    if r in ("ELEVATED",):     return "🟡"
    if r in ("MODERATE",):     return "🟡"
    if r in ("LOW",):          return "🟢"
    return "🟡"


def _rating_to_color(rating):
    r = (rating or "").upper()
    if r == "HIGH":      return "red"
    if r == "ELEVATED":  return "amber"
    if r == "MODERATE":  return "yellow"
    if r == "LOW":       return "green"
    return "amber"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ramparts-shim.py <aim_input.json> <ramparts_output.json>")
        sys.exit(1)
    shim(sys.argv[1], sys.argv[2])
