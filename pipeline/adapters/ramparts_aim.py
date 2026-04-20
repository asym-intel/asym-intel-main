"""
Commons AIM (ai-governance) → Ramparts WP shape adapter.

Target renderer: Ramparts/scripts/generate-static.js (Node, 65KB).
Target field shape: the Ramparts "report-latest.json" format as observed
in Ramparts/data/report-latest.json at commit dated 2026-04-10.

MAPPING SPEC (source of truth — update this comment when mapping changes)
-------------------------------------------------------------------------
meta.*                     ← canonical.meta.* (passthrough + site/pipeline fields)
source_url (top-level)     → meta.source_url (moved under meta)

delta_strip[*]
  .text                    ← canonical .title
  .label                   ← canonical .module
  (rank, module, delta_type, one_line pass through)
  .source_url              ← "" (commons doesn't carry per-delta source URLs)

country_grid[*]
  .jurisdiction            ← canonical .country
  .binding_law             ← canonical .signal
  .status_icon             ← "" (commons dropped this field; renderer copes)
  .key_guidance            ← ""
  .standards               ← ""
  .last_updated            ← canonical.meta.published
  .change_flag             ← "—"

country_grid_watch[*]      ← similar to country_grid (thin)

module_0                   passthrough {title, body}
module_1                   {title, subtitle, mainstream, underweighted}
                             - mainstream/underweighted arrays: passthrough
                               (commons items already use headline/body/asymmetric/source_*)
module_2                   EMPTY SHELL {title, models: [], no_releases: [], benchmarks_table: {}}
                             - commons "module_2" in AIM now holds framework-status data,
                               not model-release data. Ramparts module_2 (Model Frontier)
                               has no upstream data in the new canonical; emit a safe shell
                               so generate-static.js does not crash.
module_3                   passthrough {title, funding_rounds, strategic_deals, secondary_markets, energy_wall}
                             - commons lacks secondary_markets; adapter adds `secondary_markets: []`.
                             - energy_wall: commons sends list; Ramparts expects
                               {signal_confirmed, context, rounds}. If commons sends a list,
                               wrap it as {..., rounds: <list>}.
module_4, module_5         passthrough
module_6                   passthrough (+ drill_down_results default [])
module_7                   passthrough
module_8                   {title, subtitle, items}  (items: passthrough)
module_9                   REMAP  commons {law_highlights, standards_highlights, litigation_highlights}
                             → ramparts {new_developments, no_change, friction_analysis, eu_ai_act_layered}
                             Since commons doesn't carry the exact Ramparts partition,
                             we CONCATENATE commons highlights into `new_developments` and leave
                             `no_change: []`, `friction_analysis: {title, note, items: []}`,
                             `eu_ai_act_layered: {title, note, layers: []}` as safe shells.
module_10                  passthrough (field names already aligned)
module_11                  {title, subtitle, items}  (items: passthrough)
module_12                  REMAP commons {items, capability_watch, asymmetric_flags}
                             → ramparts {title, subtitle, bodies, asymmetric_flags}
                             bodies: from commons.items if present (thin pass-through);
                             asymmetric_flags: passthrough.
module_13                  REMAP commons {items, structural_trends, asymmetric_flags}
                             → ramparts {title, subtitle, description, cases, no_change, methodology}
                             cases: from commons.items; description/methodology: "" if absent.
module_14                  MERGE  commons.module_14 + commons.module_15
                             → ramparts.module_14 {title, subtitle, description, lab_movements,
                                                   government_ai_bodies, revolving_door,
                                                   asymmetric_flags, methodology, aisi_pipeline_result}
                             lab_movements/government_ai_bodies/revolving_door: from commons.module_15
                             asymmetric_flags: merge of both modules' flags.

Dropped (commons-only, not rendered by Ramparts):
  weekly_brief, key_judgments, jurisdiction_risk_matrix, lab_posture_scorecard,
  governance_health_composite, weekly_brief_sources
"""

from __future__ import annotations

from typing import Any

from .base import Adapter
from .registry import register


# Default module titles/subtitles, used when the canonical report omits them.
RAMPARTS_MODULE_DEFAULTS: dict[str, dict[str, str]] = {
    "module_0": {"title": "The Signal"},
    "module_1": {
        "title": "Executive Insight",
        "subtitle": "Items 1–10 · mainstream + underweighted signals",
    },
    "module_2": {"title": "Model Frontier"},
    "module_3": {"title": "Investment & M&A"},
    "module_4": {"title": "Sector Penetration"},
    "module_5": {"title": "European & China Watch"},
    "module_6": {"title": "AI in Science"},
    "module_7": {"title": "Risk Indicators: 2028"},
    "module_8": {"title": "Military AI Watch", "subtitle": ""},
    "module_9": {"title": "Law & Guidance"},
    "module_10": {"title": "AI Governance"},
    "module_11": {"title": "Ethics & Accountability", "subtitle": ""},
    "module_12": {"title": "Technical Standards", "subtitle": ""},
    "module_13": {"title": "Litigation Tracker", "subtitle": ""},
    "module_14": {"title": "Personnel & Org Watch", "subtitle": ""},
}


@register
class RampartsAimAdapter(Adapter):
    monitor = "ai-governance"
    target = "ramparts-wp"
    accepts_schema_versions = ("2.0",)
    emits_schema_version = "ramparts-v2"

    def transform(self, canonical: dict) -> dict:
        self._assert_canonical_schema(canonical)

        out: dict[str, Any] = {}

        # ---- meta ----
        c_meta = canonical.get("meta", {}) or {}
        out["meta"] = {
            "published": c_meta.get("published", ""),
            "publish_time_utc": c_meta.get("publish_time_utc", ""),
            "week_label": c_meta.get("week_label", ""),
            "volume": c_meta.get("volume"),
            "issue": c_meta.get("issue"),
            "schema_version": self.emits_schema_version,
            "pipeline_version": "ramparts-aim-adapter/v1",
            "source_url": canonical.get("source_url", "") or c_meta.get("source_url", ""),
            "site_url": c_meta.get("site_url", "https://ramparts.gi"),
            "slug": c_meta.get("slug", ""),
        }

        # ---- modules 0–14 ----
        published = c_meta.get("published", "") or ""
        out["module_0"] = self._module_0(canonical.get("module_0", {}))
        out["module_1"] = self._module_1(canonical.get("module_1", {}), published)
        out["module_2"] = self._module_2(canonical.get("module_2"))
        out["module_3"] = self._module_3(canonical.get("module_3", {}))
        out["module_4"] = self._module_4(canonical.get("module_4", {}))
        out["module_5"] = self._module_5(canonical.get("module_5", {}))
        out["module_6"] = self._module_6(canonical.get("module_6", {}))
        out["module_7"] = self._module_7(canonical.get("module_7", {}))
        out["module_8"] = self._module_8(canonical.get("module_8", {}))
        out["module_9"] = self._module_9(canonical.get("module_9", {}))
        out["module_10"] = self._module_10(canonical.get("module_10", {}))
        out["module_11"] = self._module_11(canonical.get("module_11", {}))
        out["module_12"] = self._module_12(canonical.get("module_12", {}))
        out["module_13"] = self._module_13(canonical.get("module_13", {}))
        out["module_14"] = self._module_14(
            canonical.get("module_14", {}),
            canonical.get("module_15", {}) or {},
        )

        # ---- delta strip, country grids ----
        out["delta_strip"] = self._delta_strip(canonical.get("delta_strip", []))
        out["country_grid"] = self._country_grid(
            canonical.get("country_grid", []),
            c_meta.get("published", ""),
        )
        out["country_grid_watch"] = self._country_grid_watch(
            canonical.get("country_grid_watch", []),
            c_meta.get("published", ""),
        )

        # ---- cross monitor flags (passthrough if present) ----
        if canonical.get("cross_monitor_flags") is not None:
            out["cross_monitor_flags"] = canonical["cross_monitor_flags"]

        return out

    # ------------------------------------------------------------------
    # Per-module transforms. Each handles the missing/empty canonical case.
    # ------------------------------------------------------------------

    def _titled(self, module_key: str, extras: dict | None = None) -> dict:
        base = dict(RAMPARTS_MODULE_DEFAULTS.get(module_key, {}))
        if extras:
            base.update(extras)
        return base

    def _module_0(self, m: dict) -> dict:
        if not isinstance(m, dict):
            m = {}
        return self._titled(
            "module_0",
            {
                "title": m.get("title") or RAMPARTS_MODULE_DEFAULTS["module_0"]["title"],
                "body": m.get("body") or m.get("text") or m.get("summary") or "",
            },
        )

    def _module_1(self, m: dict, published: str = "") -> dict:
        """Module 1 — Executive Insight (mainstream + underweighted items).

        Commons items: {headline, why_it_matters}
        Ramparts items: {rank, headline, date, body, asymmetric, source_label, source_url}

        Mapping:
        - headline passes through.
        - why_it_matters -> body.
        - rank synthesised from array index (mainstream: 1..N; underweighted: N+1..).
        - date defaults to the report's published date.
        - asymmetric / source_label / source_url default to empty strings so
          the renderer does not print 'undefined'.
        """
        if not isinstance(m, dict):
            m = {}

        def _shape(item: Any, rank: int) -> dict:
            if not isinstance(item, dict):
                return {
                    "rank": rank,
                    "headline": "",
                    "date": published,
                    "body": "",
                    "asymmetric": "",
                    "source_label": "",
                    "source_url": "",
                }
            return {
                "rank": item.get("rank") if isinstance(item.get("rank"), int) else rank,
                "headline": item.get("headline") or item.get("title") or "",
                "date": item.get("date") or published,
                "body": item.get("body") or item.get("why_it_matters") or item.get("summary") or "",
                "asymmetric": item.get("asymmetric") or "",
                "source_label": item.get("source_label") or "",
                "source_url": item.get("source_url") or "",
            }

        mainstream_in = m.get("mainstream") or []
        underweighted_in = m.get("underweighted") or []
        if not isinstance(mainstream_in, list):
            mainstream_in = []
        if not isinstance(underweighted_in, list):
            underweighted_in = []

        n = len(mainstream_in)
        mainstream = [_shape(it, i + 1) for i, it in enumerate(mainstream_in)]
        underweighted = [_shape(it, n + i + 1) for i, it in enumerate(underweighted_in)]

        return self._titled(
            "module_1",
            {
                "mainstream": mainstream,
                "underweighted": underweighted,
            },
        )

    def _module_2(self, m: Any) -> dict:
        # Commons AIM module_2 now holds framework-status data (not model releases).
        # Ramparts module_2 expects model-release data. Emit a safe empty shell.
        # Note: if models[] ever gets populated, each item must carry benchmarks: []
        # because the renderer does mod.benchmarks.length / .map().
        return self._titled(
            "module_2",
            {
                "models": [],
                "no_releases": [],
                "benchmarks_table": {
                    "arc_agi_2": [],
                    "arc_agi_3": [],
                    "gpqa_diamond": [],
                },
            },
        )

    def _module_3(self, m: dict) -> dict:
        """Module 3 — Investment & M&A.

        Commons funding_rounds item:
            {company, amount, stage, sector, valuation, announced, investors,
             asymmetric, source_url}
        Ramparts funding_rounds item expected by renderer:
            {company, amount, valuation, date, lead, focus, asymmetric,
             source_label, source_url, cursor_curve, cursor_note, persistence,
             confidence}

        Commons strategic_deals item:
            {type, parties, amount, announced, asymmetric, source_url}
        Ramparts strategic_deals item:
            {name, type, date, detail, source_label, source_url}

        Commons energy_wall is list of rounds; Ramparts is dict
            {signal_confirmed, context, rounds}.
        """
        if not isinstance(m, dict):
            m = {}

        def _round(r: Any) -> dict:
            if not isinstance(r, dict):
                return {
                    "company": "", "amount": "", "valuation": "", "date": "",
                    "lead": "", "focus": "", "asymmetric": "",
                    "source_label": "", "source_url": "",
                    "cursor_curve": False, "cursor_note": "",
                    "persistence": "", "confidence": "",
                }
            investors = r.get("investors") or []
            if isinstance(investors, list):
                lead = investors[0] if investors else ""
            else:
                lead = str(investors)
            return {
                "company": r.get("company") or "",
                "amount": r.get("amount") or "",
                "valuation": r.get("valuation") or "",
                "date": r.get("date") or r.get("announced") or "",
                "lead": r.get("lead") or lead or "",
                "focus": r.get("focus") or r.get("sector") or r.get("stage") or "",
                "asymmetric": r.get("asymmetric") or "",
                "source_label": r.get("source_label") or ("Source" if r.get("source_url") else ""),
                "source_url": r.get("source_url") or "",
                "cursor_curve": bool(r.get("cursor_curve", False)),
                "cursor_note": r.get("cursor_note") or "",
                "persistence": r.get("persistence") or "",
                "confidence": r.get("confidence") or "",
            }

        def _deal(d: Any) -> dict:
            if not isinstance(d, dict):
                return {"name": "", "type": "", "date": "", "detail": "",
                        "source_label": "", "source_url": ""}
            parties = d.get("parties") or []
            if isinstance(parties, list):
                name = " × ".join(str(p) for p in parties) if parties else ""
            else:
                name = str(parties)
            detail_bits = []
            if d.get("amount"):
                detail_bits.append(str(d["amount"]))
            if d.get("asymmetric"):
                detail_bits.append(str(d["asymmetric"]))
            return {
                "name": d.get("name") or name or d.get("title") or "",
                "type": d.get("type") or "",
                "date": d.get("date") or d.get("announced") or "",
                "detail": d.get("detail") or " — ".join(detail_bits),
                "source_label": d.get("source_label") or ("Source" if d.get("source_url") else ""),
                "source_url": d.get("source_url") or "",
            }

        energy_wall = m.get("energy_wall")
        if isinstance(energy_wall, list):
            energy_wall = {"signal_confirmed": False, "context": "", "rounds": energy_wall}
        elif not isinstance(energy_wall, dict):
            energy_wall = {"signal_confirmed": False, "context": "", "rounds": []}
        else:
            energy_wall = dict(energy_wall)
            energy_wall.setdefault("signal_confirmed", False)
            energy_wall.setdefault("context", "")
            energy_wall.setdefault("rounds", [])

        return self._titled(
            "module_3",
            {
                "funding_rounds": [_round(r) for r in (m.get("funding_rounds") or [])],
                "strategic_deals": [_deal(d) for d in (m.get("strategic_deals") or [])],
                "secondary_markets": m.get("secondary_markets", []) or [],
                "energy_wall": energy_wall,
            },
        )

    def _module_4(self, m: dict) -> dict:
        """Module 4 — Sector Penetration.

        Commons sector item:
            {sector, status, headline_developments, capability_to_deployment_gap,
             stealth_flag, asymmetric, sources}
        Ramparts sector item:
            {name, status, headline, detail, asymmetric, source_label, source_url}
        """
        if not isinstance(m, dict):
            m = {}

        def _sector(s: Any) -> dict:
            if not isinstance(s, dict):
                return {"name": "", "status": "", "headline": "", "detail": "",
                        "asymmetric": "", "source_label": "", "source_url": ""}
            srcs = s.get("sources") or []
            source_url = s.get("source_url") or (srcs[0] if isinstance(srcs, list) and srcs else "")
            headline_dev = s.get("headline_developments")
            if isinstance(headline_dev, list):
                headline = headline_dev[0] if headline_dev else ""
                detail = " ".join(str(x) for x in headline_dev[1:])
            else:
                headline = s.get("headline") or (str(headline_dev) if headline_dev else "")
                detail = s.get("detail") or s.get("capability_to_deployment_gap") or ""
            return {
                "name": s.get("name") or s.get("sector") or "",
                "status": s.get("status") or "",
                "headline": headline,
                "detail": detail,
                "asymmetric": s.get("asymmetric") or "",
                "source_label": s.get("source_label") or ("Source" if source_url else ""),
                "source_url": source_url or "",
            }

        sectors_in = m.get("sectors") or []
        if not isinstance(sectors_in, list):
            sectors_in = []
        return self._titled("module_4", {"sectors": [_sector(s) for s in sectors_in]})

    def _module_5(self, m: dict) -> dict:
        # Commons and Ramparts use incompatible shapes here:
        #   commons.module_5.european/china are LISTS of news items
        #   ramparts.module_5.european/china are DICTS with keyed sub-sections
        # Adapter emits renderer-safe dicts with empty sub-sections plus an `items`
        # list carrying the commons data through for any future renderer consumption.
        #
        # The Ramparts renderer reads these keys on `european`:
        #   headline, digital_omnibus, standards_vacuum
        # and on `china`:
        #   headline, deepseek, alibaba, export_controls, ciyuan_signal
        # plus `funding[]` and `displacement[]` on `european`.
        # We default missing strings to '' so nothing renders as 'undefined'.
        if not isinstance(m, dict):
            m = {}

        def _coerce_eu(raw: Any) -> dict:
            if isinstance(raw, dict):
                out = dict(raw)
            elif isinstance(raw, list):
                out = {"items": raw}
            else:
                out = {}
            out.setdefault("headline", "")
            out.setdefault("digital_omnibus", "")
            # standards_vacuum is falsy-checked by the renderer, so a missing
            # key is fine; only coerce to a dict if something partial exists.
            if "standards_vacuum" in out and not isinstance(out["standards_vacuum"], dict):
                out["standards_vacuum"] = {"summary": str(out["standards_vacuum"] or "")}
            out.setdefault("funding", [])
            out.setdefault("displacement", [])
            return out

        def _coerce_cn(raw: Any) -> dict:
            if isinstance(raw, dict):
                out = dict(raw)
            elif isinstance(raw, list):
                out = {"items": raw}
            else:
                out = {}
            out.setdefault("headline", "")
            out.setdefault("deepseek", "")
            out.setdefault("alibaba", "")
            out.setdefault("export_controls", "")
            # ciyuan_signal is falsy-checked; only coerce if partial.
            if "ciyuan_signal" in out and not isinstance(out["ciyuan_signal"], dict):
                out["ciyuan_signal"] = {
                    "flag": "",
                    "summary": str(out["ciyuan_signal"] or ""),
                    "asymmetric": "",
                }
            # Renderer doesn't read these but keep for downstream consumers.
            out.setdefault("funding", [])
            out.setdefault("displacement", [])
            return out

        return self._titled(
            "module_5",
            {
                "european": _coerce_eu(m.get("european")),
                "china": _coerce_cn(m.get("china")),
            },
        )

    def _module_6(self, m: dict) -> dict:
        """Module 6 — AI in Science.

        Commons threshold_event:
            {title, date, domain, lab, summary, reliability_flags, asymmetric, source_url}
        Ramparts threshold_event:
            {flag, title, date, domain, lab, model, capability, reliability,
             partnerships, programme, asymmetric, source_label, source_url}

        Commons programme_update: {programme, lab, update, source_url}
        Ramparts programme_update: {title, date, domain, lab, detail, source_label, source_url}

        Commons arxiv_highlight: {title, authors, published, venue, significance, tier, url}
        Ramparts arxiv_highlight: {id, title, domain, note, url}
        """
        if not isinstance(m, dict):
            m = {}

        def _threshold(t: Any) -> dict:
            if not isinstance(t, dict):
                t = {}
            reliability = t.get("reliability")
            if not reliability:
                rf = t.get("reliability_flags")
                if isinstance(rf, list):
                    reliability = ", ".join(str(x) for x in rf)
                elif rf:
                    reliability = str(rf)
                else:
                    reliability = ""
            return {
                "flag": t.get("flag") or "",
                "title": t.get("title") or "",
                "date": t.get("date") or "",
                "domain": t.get("domain") or "",
                "lab": t.get("lab") or "",
                "model": t.get("model") or "",
                "capability": t.get("capability") or t.get("summary") or "",
                "reliability": reliability,
                "partnerships": t.get("partnerships") or "",
                "programme": t.get("programme") or "",
                "asymmetric": t.get("asymmetric") or "",
                "source_label": t.get("source_label") or ("Source" if t.get("source_url") else ""),
                "source_url": t.get("source_url") or "",
            }

        def _programme(p: Any) -> dict:
            if not isinstance(p, dict):
                p = {}
            return {
                "title": p.get("title") or p.get("programme") or "",
                "date": p.get("date") or "",
                "domain": p.get("domain") or "",
                "lab": p.get("lab") or "",
                "detail": p.get("detail") or p.get("update") or "",
                "source_label": p.get("source_label") or ("Source" if p.get("source_url") else ""),
                "source_url": p.get("source_url") or "",
            }

        def _arxiv(a: Any) -> dict:
            if not isinstance(a, dict):
                a = {}
            url = a.get("url") or a.get("source_url") or ""
            # Derive arxiv id from URL if not explicit.
            arxiv_id = a.get("id") or ""
            if not arxiv_id and "arxiv.org" in url:
                # crude: last path segment
                arxiv_id = url.rstrip("/").split("/")[-1]
            return {
                "id": arxiv_id or "paper",
                "title": a.get("title") or "",
                "domain": a.get("domain") or a.get("venue") or "",
                "note": a.get("note") or a.get("significance") or "",
                "url": url,
            }

        return self._titled(
            "module_6",
            {
                "threshold_events": [_threshold(t) for t in (m.get("threshold_events") or [])],
                "programme_updates": [_programme(p) for p in (m.get("programme_updates") or [])],
                "arxiv_highlights": [_arxiv(a) for a in (m.get("arxiv_highlights") or [])],
                "drill_down_results": m.get("drill_down_results", []) or [],
            },
        )

    def _module_7(self, m: dict) -> dict:
        """Module 7 — Risk Indicators: 2028.

        Commons vector item:
            {vector, rating, summary, asymmetric, confidence, changed,
             unchanged_since, sources, last_updated, version_history}
        Ramparts vector item expected by the renderer:
            {name, color, level, headline, detail, asymmetric,
             source_label, source_url, additional_items[]}

        Mapping:
        - vector -> name
        - rating (HIGH / ELEVATED / VACUUM / ...) -> color + level label
        - summary -> headline (detail left blank unless commons provides one)
        - sources[0] -> source_url with default source_label 'Source'
        - additional_items defaults to []
        """
        if not isinstance(m, dict):
            m = {}

        # Rating → (color, level_label) mapping. Renderer's colorMap keys are
        # 'red'/'amber'/'yellow'; the levelMap it uses is derived from color,
        # but we keep an explicit `level` so we degrade gracefully.
        rating_map = {
            "HIGH": ("red", "HIGH"),
            "CRITICAL": ("red", "CRITICAL"),
            "ELEVATED": ("amber", "ELEVATED"),
            "MEDIUM": ("amber", "ELEVATED"),
            "VACUUM": ("yellow", "VACUUM"),
            "LOW": ("yellow", "LOW"),
        }

        def _shape(v: Any) -> dict:
            if not isinstance(v, dict):
                return {
                    "name": "",
                    "color": "amber",
                    "level": "",
                    "headline": "",
                    "detail": "",
                    "asymmetric": "",
                    "source_label": "",
                    "source_url": "",
                    "additional_items": [],
                }
            rating = (v.get("rating") or v.get("level") or "").upper()
            color, level_label = rating_map.get(rating, ("amber", rating or ""))
            sources = v.get("sources") or []
            source_url = v.get("source_url") or (sources[0] if isinstance(sources, list) and sources else "")
            return {
                "name": v.get("name") or v.get("vector") or "",
                "color": v.get("color") or color,
                "level": v.get("level") or level_label,
                "headline": v.get("headline") or v.get("summary") or "",
                "detail": v.get("detail") or "",
                "asymmetric": v.get("asymmetric") or "",
                "source_label": v.get("source_label") or ("Source" if source_url else ""),
                "source_url": source_url or "",
                "additional_items": v.get("additional_items") or [],
            }

        vectors_in = m.get("vectors") or []
        if not isinstance(vectors_in, list):
            vectors_in = []
        vectors = [_shape(v) for v in vectors_in]
        return self._titled("module_7", {"vectors": vectors})

    def _module_8(self, m: dict) -> dict:
        """Module 8 — Military AI Watch.

        Commons item: {title, category, jurisdiction, summary, ihl_friction,
                       asymmetric, source_url}
        Ramparts item (renderer): {title, date, jurisdiction, category, body,
                                    ihl_friction, asymmetric, source_label,
                                    source_url}
        """
        if not isinstance(m, dict):
            m = {}

        def _item(it: Any) -> dict:
            if not isinstance(it, dict):
                it = {}
            return {
                "title": it.get("title") or "",
                "date": it.get("date") or "",
                "jurisdiction": it.get("jurisdiction") or "",
                "category": it.get("category") or "doctrine",
                "body": it.get("body") or it.get("summary") or "",
                "ihl_friction": it.get("ihl_friction") or "",
                "asymmetric": it.get("asymmetric") or "",
                "source_label": it.get("source_label") or ("Source" if it.get("source_url") else ""),
                "source_url": it.get("source_url") or "",
            }

        items_in = m.get("items") or []
        if not isinstance(items_in, list):
            items_in = []
        return self._titled(
            "module_8",
            {
                "subtitle": m.get("subtitle", "") or "",
                "items": [_item(it) for it in items_in],
            },
        )

    def _module_9(self, m: dict) -> dict:
        """Module 9 — Law & Guidance.

        Commons partitions into law_highlights / standards_highlights /
        litigation_highlights. Each item is shaped like:
            {title, date, jurisdiction, summary, source_url}
          (standards_highlights additionally has standards_vacuum_active, days_to_deadline)

        Ramparts expects new_developments items shaped like:
            {jurisdiction, flag, instrument, date, issuer, domain, obligations,
             friction_analysis, source_label, source_url, enforcement, asymmetric}
        """
        if not isinstance(m, dict):
            m = {}

        def _dev(it: Any, domain: str) -> dict:
            if not isinstance(it, dict):
                it = {}
            return {
                "jurisdiction": it.get("jurisdiction") or "",
                "flag": it.get("flag") or "new",
                "instrument": it.get("instrument") or it.get("title") or "",
                "date": it.get("date") or "",
                "issuer": it.get("issuer") or "",
                "domain": it.get("domain") or domain,
                "obligations": it.get("obligations") or it.get("summary") or "",
                "enforcement": it.get("enforcement") or "",
                "asymmetric": it.get("asymmetric") or "",
                "source_label": it.get("source_label") or ("Source" if it.get("source_url") else ""),
                "source_url": it.get("source_url") or "",
            }

        new_developments: list = []
        for key, domain in (
            ("law_highlights", "Law"),
            ("standards_highlights", "Standards"),
            ("litigation_highlights", "Litigation"),
        ):
            items = m.get(key) or []
            if isinstance(items, list):
                new_developments.extend(_dev(it, domain) for it in items)
        return self._titled(
            "module_9",
            {
                "new_developments": new_developments,
                "no_change": [],
                "friction_analysis": {"title": "", "note": None, "items": []},
                "eu_ai_act_layered": {"title": "", "note": "", "layers": []},
            },
        )

    def _module_10(self, m: dict) -> dict:
        if not isinstance(m, dict):
            m = {}
        return self._titled(
            "module_10",
            {
                "international_soft_law": m.get("international_soft_law", []) or [],
                "corporate_governance": m.get("corporate_governance", []) or [],
                "product_liability": m.get("product_liability", []) or [],
                "algorithmic_accountability": m.get("algorithmic_accountability", []) or [],
                "governance_gaps": m.get("governance_gaps", []) or [],
            },
        )

    def _module_11(self, m: dict) -> dict:
        """Module 11 — Ethics & Accountability.

        Commons item: {title, category, jurisdiction, accountability_friction,
                       source_url}
        Ramparts item (renderer): {title, date, jurisdiction, category, body,
                                    accountability_friction, source_label,
                                    source_url, asymmetric}
        """
        if not isinstance(m, dict):
            m = {}

        def _item(it: Any) -> dict:
            if not isinstance(it, dict):
                it = {}
            return {
                "title": it.get("title") or "",
                "date": it.get("date") or "",
                "jurisdiction": it.get("jurisdiction") or "",
                "category": it.get("category") or "standards",
                "body": it.get("body") or it.get("summary") or "",
                "accountability_friction": it.get("accountability_friction") or "",
                "asymmetric": it.get("asymmetric") or "",
                "source_label": it.get("source_label") or ("Source" if it.get("source_url") else ""),
                "source_url": it.get("source_url") or "",
            }

        items_in = m.get("items") or []
        if not isinstance(items_in, list):
            items_in = []
        return self._titled(
            "module_11",
            {
                "subtitle": m.get("subtitle", "") or "",
                "items": [_item(it) for it in items_in],
            },
        )

    def _module_12(self, m: dict) -> dict:
        """Module 12 — Technical Standards.

        Commons shape and Ramparts shape are fundamentally different:

        - Commons publishes FIMI-style items (this monitor's AIM module_12 is
          used for FIMI/capability watch items) shaped like
            {title, category, actor_type, region, platform_response,
             detection_method, summary, asymmetric, source_url}
          plus `capability_watch` and `asymmetric_flags`.

        - Ramparts expects `bodies[]` grouped by standards body, each with
          `standards[]` each shaped like {standard, status, status_class,
           scope, week_update, source_label, source_url}.

        The two shapes don't map cleanly. Rather than force-fit, we group
        commons items by `actor_type` (or `region`) as a pseudo-body and
        emit minimal standards entries. If no items, return an empty bodies
        list — the renderer guards with `|| !module_12.bodies` and shows
        'No material developments this week.'.
        """
        if not isinstance(m, dict):
            m = {}

        items_in = m.get("items") or []
        if not isinstance(items_in, list):
            items_in = []

        pass_through_bodies = m.get("bodies")
        if isinstance(pass_through_bodies, list) and pass_through_bodies:
            # If a future commons version provides Ramparts-shape bodies,
            # normalise each body's standards list.
            bodies = []
            for b in pass_through_bodies:
                if not isinstance(b, dict):
                    continue
                bb = {
                    "body": b.get("body") or "",
                    "jurisdiction": b.get("jurisdiction") or "",
                    "standards": [],
                }
                for s in (b.get("standards") or []):
                    if not isinstance(s, dict):
                        continue
                    bb["standards"].append({
                        "standard": s.get("standard") or "",
                        "status": s.get("status") or "",
                        "status_class": s.get("status_class") or "active",
                        "scope": s.get("scope") or "",
                        "week_update": s.get("week_update") or "No material update this week.",
                        "source_label": s.get("source_label") or "",
                        "source_url": s.get("source_url") or "",
                    })
                bodies.append(bb)
            return self._titled(
                "module_12",
                {
                    "subtitle": m.get("subtitle", "") or "",
                    "bodies": bodies,
                    "asymmetric_flags": m.get("asymmetric_flags", []) or [],
                },
            )

        # Else, group commons items by actor_type (or region) as pseudo-body.
        grouped: dict[str, dict] = {}
        for it in items_in:
            if not isinstance(it, dict):
                continue
            body_label = it.get("actor_type") or it.get("region") or "Standards Watch"
            if body_label not in grouped:
                grouped[body_label] = {
                    "body": body_label,
                    "jurisdiction": it.get("region") or "",
                    "standards": [],
                }
            grouped[body_label]["standards"].append({
                "standard": it.get("title") or "",
                "status": it.get("status") or "Active",
                "status_class": "active",
                "scope": it.get("summary") or "",
                "week_update": it.get("asymmetric") or "No material update this week.",
                "source_label": ("Source" if it.get("source_url") else ""),
                "source_url": it.get("source_url") or "",
            })

        return self._titled(
            "module_12",
            {
                "subtitle": m.get("subtitle", "") or "",
                "bodies": list(grouped.values()),
                "asymmetric_flags": m.get("asymmetric_flags", []) or [],
            },
        )

    def _module_13(self, m: dict) -> dict:
        if not isinstance(m, dict):
            m = {}
        # Ramparts renderer reads l.week_update.startsWith(…) on litigation cases.
        # Ensure week_update is always a string.
        cases = []
        for l in (m.get("items", []) or m.get("cases", []) or []):
            if isinstance(l, dict):
                ll = dict(l)
                ll.setdefault("week_update", "")
                cases.append(ll)
        return self._titled(
            "module_13",
            {
                "subtitle": m.get("subtitle", "") or "",
                "description": m.get("description", "") or "",
                "cases": cases,
                "no_change": [],
                "methodology": m.get("methodology", "") or "",
            },
        )

    def _module_14(self, m14: dict, m15: dict) -> dict:
        # Merge commons module_14 (+ module_15 for people moves) into Ramparts module_14.
        if not isinstance(m14, dict):
            m14 = {}
        if not isinstance(m15, dict):
            m15 = {}
        return self._titled(
            "module_14",
            {
                "subtitle": m14.get("subtitle", "") or m15.get("subtitle", "") or "",
                "description": m14.get("description", "") or m15.get("description", "") or "",
                "lab_movements": m15.get("lab_movements", []) or [],
                "government_ai_bodies": m15.get("government_ai_bodies", []) or [],
                "revolving_door": m15.get("revolving_door", []) or [],
                "asymmetric_flags": (m14.get("asymmetric_flags", []) or [])
                + (m15.get("asymmetric_flags", []) or []),
                "methodology": m15.get("methodology", "") or "",
                "aisi_pipeline_result": m15.get("aisi_pipeline_result", "") or "",
            },
        )

    # ------------------------------------------------------------------
    # Delta strip + country grids
    # ------------------------------------------------------------------

    def _delta_strip(self, items: list) -> list:
        if not isinstance(items, list):
            return []
        out = []
        for d in items:
            if not isinstance(d, dict):
                continue
            title = d.get("title", "") or d.get("text", "")
            module = d.get("module", "") or d.get("label", "")
            out.append(
                {
                    "rank": d.get("rank"),
                    "text": title,
                    "label": module,
                    "module": module,
                    "delta_type": d.get("delta_type", ""),
                    "one_line": d.get("one_line", ""),
                    "source_url": d.get("source_url", ""),
                }
            )
        return out

    def _country_grid(self, items: list, last_updated: str) -> list:
        if not isinstance(items, list):
            return []
        out = []
        for c in items:
            if not isinstance(c, dict):
                continue
            out.append(
                {
                    "jurisdiction": c.get("country", "") or c.get("jurisdiction", ""),
                    "status_icon": c.get("status_icon", ""),
                    "binding_law": c.get("signal", "") or c.get("binding_law", ""),
                    "key_guidance": c.get("key_guidance", ""),
                    "standards": c.get("standards", ""),
                    "last_updated": c.get("last_updated", "") or last_updated,
                    "change_flag": c.get("change_flag", "—"),
                }
            )
        return out

    def _country_grid_watch(self, items: list, last_updated: str) -> list:
        if not isinstance(items, list):
            return []
        out = []
        for c in items:
            if not isinstance(c, dict):
                continue
            out.append(
                {
                    "jurisdiction": c.get("country", "") or c.get("jurisdiction", ""),
                    "status_icon": c.get("status_icon", ""),
                    "threshold_status": c.get("threshold_status", "")
                    or c.get("signal", ""),
                    "threshold_trigger": c.get("threshold_trigger", ""),
                    "current_framework": c.get("current_framework", ""),
                    "source_url": c.get("source_url", ""),
                }
            )
        return out
