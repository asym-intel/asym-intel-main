#!/usr/bin/env python3
"""
Ramparts Publisher — AI Frontier Monitor
Publishes weekly AIM report to ramparts.gi (WordPress).

Pipeline position: fires Friday 16:00 UTC (2h after AIM publisher at 14:00 UTC)
Input:  static/monitors/ai-governance/data/report-latest.json
Output: WordPress issue page + homepage/archive updates
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

import re as _re
import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WP_SITE = "https://ramparts.gi"
PIPELINE_VERSION = "ramparts-1.0"

MODULE_NAMES = {
    "module_0": "The Signal",
    "module_1": "Executive Insight",
    "module_2": "Model Frontier",
    "module_3": "Investment & M&A",
    "module_4": "Sector Penetration",
    "module_5": "European & China Watch",
    "module_6": "AI in Science",
    "module_7": "Risk Indicators: 2028",
    "module_8": "Military AI Watch",
    "module_9": "Law & Guidance",
    "module_10": "AI Governance",
    "module_11": "Ethics & Accountability",
    "module_12": "Technical Standards",
    "module_13": "Litigation Tracker",
    "module_14": "Personnel & Org Watch",
}

# WordPress standing page IDs
WP_HOMEPAGE_ID = 22643
WP_ARCHIVE_ID = 22648
WP_ABOUT_ID = 22647
WP_DIGEST_ID = 22649
WP_SEARCH_ID = 22651

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}", flush=True)


def normalise_module_key(raw_key: str) -> str:
    """Accept both 'module_0' and 'module-0' forms."""
    return raw_key.replace("-", "_")


def get_module_items(module_data) -> list:
    """
    Return the list of items from a module value, regardless of
    whether they live under .items, .entries, or are the value itself.
    """
    if isinstance(module_data, list):
        return module_data
    if isinstance(module_data, dict):
        for key in ("items", "entries"):
            if key in module_data and isinstance(module_data[key], list):
                return module_data[key]
    return []


def get_item_field(item: dict, *fields, default="") -> str:
    """Return the first non-empty value among the given field names."""
    for f in fields:
        v = item.get(f, "")
        if v:
            return str(v)
    return default


def html_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Step 0 — Load and validate
# ---------------------------------------------------------------------------


def step0_load_and_validate():
    log("Step 0: Loading and validating report JSON …")

    repo_root = Path(os.environ.get("REPO_ROOT", os.getcwd()))
    report_path = repo_root / "static/monitors/ai-governance/data/report-latest.json"
    archive_path = repo_root / "static/monitors/ai-governance/data/archive.json"

    if not report_path.exists():
        log(f"ERROR: report-latest.json not found at {report_path}")
        sys.exit(1)

    with open(report_path, "r", encoding="utf-8") as fh:
        report = json.load(fh)

    meta = report.get("meta", {})

    # Extract key meta fields
    report_date = meta.get("published") or meta.get("slug", "")
    if not report_date:
        log("ERROR: meta.published and meta.slug are both missing from report JSON")
        sys.exit(1)

    # Normalise to YYYY-MM-DD
    report_date_str = str(report_date)[:10]

    week_label = meta.get("week_label") or meta.get("label") or report_date_str
    volume = meta.get("volume", "")
    issue = meta.get("issue", "")

    # Freshness check — must be today or yesterday (UTC)
    today_utc = datetime.now(timezone.utc).date()
    yesterday_utc = today_utc - timedelta(days=1)
    try:
        pub_date = datetime.fromisoformat(report_date_str).date()
    except ValueError:
        log(f"ERROR: Cannot parse report date '{report_date_str}'")
        sys.exit(1)

    if pub_date < yesterday_utc:
        log(
            f"ERROR: Report is stale. Published {pub_date}, today is {today_utc}. "
            "Expected today or yesterday."
        )
        sys.exit(1)

    log(f"Report date: {report_date_str}, week_label: {week_label}")

    # Duplication guard — check archive.json
    archive = []
    if archive_path.exists():
        with open(archive_path, "r", encoding="utf-8") as fh:
            archive = json.load(fh)

    existing_slugs = {entry.get("slug", "") for entry in archive}
    if report_date_str in existing_slugs:
        log(f"Already published: {report_date_str} found in archive.json — exiting cleanly.")
        sys.exit(0)

    log("Validation passed — proceeding with publication.")
    return report, meta, report_date_str, week_label, volume, issue, repo_root, archive, archive_path


# ---------------------------------------------------------------------------
# Step 1 — Read credentials
# ---------------------------------------------------------------------------


def step1_credentials():
    log("Step 1: Reading credentials from environment …")

    wp_user = os.environ.get("WP_USER", "peterhowitt@gmail.com")
    wp_app_pass = os.environ.get("WP_APP_PASS", "")


    if not wp_app_pass:
        log("ERROR: WP_APP_PASS environment variable is required but not set.")
        sys.exit(1)


    log("Credentials loaded.")
    return wp_user, wp_app_pass


# ---------------------------------------------------------------------------
# Step 2 — Build WordPress HTML
# ---------------------------------------------------------------------------


def _build_item_html(item: dict) -> str:
    title = get_item_field(item, "title", "headline")
    body = get_item_field(item, "body", "text", "summary")
    asymmetric = item.get("asymmetric", "")
    friction = item.get("friction_analysis", "")
    source_url = item.get("source_url", "")
    source_name = item.get("source_name", "Source")

    parts = ['<div class="item">']
    if title:
        parts.append(f"  <h3>{html_escape(title)}</h3>")
    if body:
        parts.append(f'  <div class="item-body">{html_escape(body)}</div>')
    if asymmetric:
        parts.append(
            f'  <div class="asymmetric"><strong>Asymmetric Signal:</strong> {html_escape(asymmetric)}</div>'
        )
    if friction:
        parts.append(
            f'  <div class="friction"><strong>&#9881;&#65039; Technical Friction:</strong> {html_escape(friction)}</div>'
        )
    if source_url:
        parts.append(
            f'  <p class="source"><a href="{html_escape(source_url)}" target="_blank">{html_escape(source_name)}</a></p>'
        )
    parts.append("</div>")
    return "\n".join(parts)


def step2_build_html(report: dict, report_date_str: str, week_label: str, volume, issue) -> str:
    log("Step 2: Building WordPress HTML …")

    # Normalise module keys in report
    normalised = {}
    for k, v in report.items():
        normalised[normalise_module_key(k)] = v

    lines = []
    lines.append("<!-- wp:html -->")
    lines.append('<div class="aim-report">')
    lines.append('  <div class="report-meta">')
    lines.append(f"    <h1>AI Frontier Monitor &#8212; {html_escape(week_label)}</h1>")

    vol_issue = ""
    if volume:
        vol_issue += f"Vol. {html_escape(str(volume))} &middot; "
    if issue:
        vol_issue += f"Issue {html_escape(str(issue))} &middot; "
    vol_issue += f"Published {html_escape(report_date_str)}"
    lines.append(f'    <p class="issue-info">{vol_issue}</p>')
    lines.append("  </div>")
    lines.append("")

    # module_0 (The Signal) — body is directly on the module dict
    m0 = normalised.get("module_0", {})
    if m0:
        m0_body = ""
        if isinstance(m0, dict):
            m0_body = m0.get("body") or m0.get("text") or m0.get("summary") or ""
        lines.append('  <div class="module" id="m0">')
        lines.append("    <h2>The Signal</h2>")
        lines.append(f'    <div class="module-body">{html_escape(m0_body)}</div>')
        lines.append("  </div>")
        lines.append("")

    # modules 1–14
    for i in range(1, 15):
        key = f"module_{i}"
        module_data = normalised.get(key)
        if module_data is None:
            continue

        display_name = MODULE_NAMES.get(key, key.replace("_", " ").title())
        items = get_module_items(module_data)

        lines.append(f'  <div class="module" id="m{i}">')
        lines.append(f"    <h2>{html_escape(display_name)}</h2>")

        for item in items:
            if isinstance(item, dict):
                item_html = _build_item_html(item)
                # Indent each line of item HTML
                for line in item_html.splitlines():
                    lines.append(f"    {line}")

        lines.append("  </div>")
        lines.append("")

    # Delta strip
    delta_strip = normalised.get("delta_strip") or report.get("delta_strip", [])
    if delta_strip and isinstance(delta_strip, list):
        lines.append('  <div class="delta-strip">')
        lines.append("    <h2>Key Changes This Week</h2>")
        lines.append("    <ol>")
        for d in delta_strip[:10]:
            if isinstance(d, dict):
                label = html_escape(d.get("label") or d.get("module_tag") or "")
                text = html_escape(d.get("text") or "")
                lines.append(f"      <li><strong>{label}:</strong> {text}</li>")
        lines.append("    </ol>")
        lines.append("  </div>")
        lines.append("")

    # Country grid
    country_grid = normalised.get("country_grid") or report.get("country_grid", [])
    if country_grid and isinstance(country_grid, list):
        lines.append('  <div class="country-grid">')
        lines.append("    <h2>Country Grid</h2>")
        lines.append("    <table>")
        lines.append("      <tr><th>Jurisdiction</th><th>Status</th><th>Binding Law</th></tr>")
        for c in country_grid:
            if isinstance(c, dict):
                jurisdiction = html_escape(c.get("jurisdiction", ""))
                status_icon = html_escape(c.get("status_icon", ""))
                binding_law = html_escape(c.get("binding_law", ""))
                lines.append(
                    f"      <tr><td>{jurisdiction}</td><td>{status_icon}</td><td>{binding_law}</td></tr>"
                )
        lines.append("    </table>")
        lines.append("  </div>")
        lines.append("")

    lines.append("</div>")
    lines.append("<!-- /wp:html -->")

    html_content = "\n".join(lines)
    log(f"HTML built: {len(html_content)} characters.")
    return html_content


# ---------------------------------------------------------------------------
# Step 3 — Create / update WordPress issue page
# ---------------------------------------------------------------------------


def step3_wordpress_issue_page(
    wp_user: str,
    wp_app_pass: str,
    week_label: str,
    report_date_str: str,
    html_content: str,
) -> str:
    log("Step 3: Creating/updating WordPress issue page …")

    page_slug = f"ai-frontier-monitor-issue-{report_date_str}"
    page_title = f"AI Frontier Monitor — {week_label}"
    wp_auth = (wp_user, wp_app_pass)
    page_url = f"{WP_SITE}/{page_slug}/"

    try:
        # Check if page already exists
        check_url = f"{WP_SITE}/wp-json/wp/v2/pages?slug={page_slug}"
        resp = requests.get(check_url, auth=wp_auth, timeout=30)
        resp.raise_for_status()
        existing = resp.json()

        if existing:
            page_id = existing[0]["id"]
            page_url = existing[0].get("link", page_url)
            log(f"Page exists (ID {page_id}) — updating …")
            update_resp = requests.post(
                f"{WP_SITE}/wp-json/wp/v2/pages/{page_id}",
                auth=wp_auth,
                json={"content": html_content, "status": "publish"},
                timeout=60,
            )
            update_resp.raise_for_status()
            page_url = update_resp.json().get("link", page_url)
            log(f"Page updated: {page_url}")
        else:
            log("Page does not exist — creating …")
            create_resp = requests.post(
                f"{WP_SITE}/wp-json/wp/v2/pages",
                auth=wp_auth,
                json={
                    "title": page_title,
                    "slug": page_slug,
                    "content": html_content,
                    "status": "publish",
                },
                timeout=60,
            )
            create_resp.raise_for_status()
            page_url = create_resp.json().get("link", page_url)
            log(f"Page created: {page_url}")

    except Exception as exc:
        log(f"ERROR in step 3 (WordPress issue page): {exc}")
        # Return a best-guess URL so downstream steps can use it
        page_url = f"{WP_SITE}/{page_slug}/"

    return page_url


# ---------------------------------------------------------------------------
# Step 4 — Update standing WordPress pages
# ---------------------------------------------------------------------------


def step4_update_standing_pages(
    wp_user: str,
    wp_app_pass: str,
    week_label: str,
    report_date_str: str,
    page_url: str,
    archive: list,
    report: dict,
):
    log("Step 4: Updating standing WordPress pages (homepage + archive) …")
    wp_auth = (wp_user, wp_app_pass)

    # --- Homepage ---
    try:
        # Pull signal text
        m0 = report.get("module_0") or report.get("module-0") or {}
        signal_text = ""
        if isinstance(m0, dict):
            signal_text = m0.get("body") or m0.get("text") or m0.get("summary") or ""

        homepage_html = (
            "<!-- wp:html -->\n"
            '<div class="aim-latest">\n'
            f"  <h2>AI Frontier Monitor &#8212; {html_escape(week_label)}</h2>\n"
            f"  <p class=\"signal-preview\">{html_escape(signal_text[:600])}{'&hellip;' if len(signal_text) > 600 else ''}</p>\n"
            f'  <p><a href="{html_escape(page_url)}" class="read-more">Read this week\'s issue &rarr;</a></p>\n'
            f'  <p class="pub-date">Published {html_escape(report_date_str)}</p>\n'
            "</div>\n"
            "<!-- /wp:html -->"
        )

        resp = requests.post(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_HOMEPAGE_ID}",
            auth=wp_auth,
            json={"content": homepage_html, "status": "publish"},
            timeout=60,
        )
        resp.raise_for_status()
        log(f"Homepage (ID {WP_HOMEPAGE_ID}) updated.")
    except Exception as exc:
        log(f"ERROR updating homepage: {exc}")

    # --- Archive page (read-then-patch to preserve styling) ---
    try:
        archive_rows = []
        for entry in archive:
            slug = entry.get("slug", "")
            label = entry.get("week_label") or entry.get("label") or slug
            vol = entry.get("volume", "")
            iss = entry.get("issue", "")
            entry_url = entry.get("source_url") or f"{WP_SITE}/ai-frontier-monitor-issue-{slug}/"
            vol_iss = ""
            if vol:
                vol_iss += f"Vol. {html_escape(str(vol))} &middot; "
            if iss:
                vol_iss += f"Issue {html_escape(str(iss))} &middot; "
            vol_iss += html_escape(slug)
            archive_rows.append(
                f'  <li><a href="{html_escape(entry_url)}">{html_escape(label)}</a>'
                f" <span class=\"issue-meta\">({vol_iss})</span></li>"
            )

        archive_list_html = "\n".join(archive_rows)
        archive_block = (
            '<div class="aim-archive">\n'
            "  <h2>Issue Archive</h2>\n"
            "  <ul>\n"
            f"{archive_list_html}\n"
            "  </ul>\n"
            "</div>"
        )

        # Fetch existing page to preserve styling
        resp = requests.get(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_ARCHIVE_ID}",
            auth=wp_auth,
            timeout=30,
        )
        resp.raise_for_status()
        _cdata = resp.json().get("content", {})
        current_archive = _cdata.get("raw", "") or _cdata.get("rendered", "")

        # Replace the aim-archive div if it exists, otherwise append
        archive_pattern = r'<div class="aim-archive">.*?</div>'
        if _re.search(archive_pattern, current_archive, _re.DOTALL):
            new_archive = _re.sub(archive_pattern, archive_block, current_archive, flags=_re.DOTALL)
        else:
            new_archive = current_archive + "\n<!-- wp:html -->\n" + archive_block + "\n<!-- /wp:html -->"

        resp = requests.post(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_ARCHIVE_ID}",
            auth=wp_auth,
            json={"content": new_archive, "status": "publish"},
            timeout=60,
        )
        resp.raise_for_status()
        log(f"Archive page (ID {WP_ARCHIVE_ID}) updated (styling preserved).")
    except Exception as exc:
        log(f"ERROR updating archive page: {exc}")

    # --- About page CTA ---
    try:
        about_cta_html = (
            "<!-- wp:html -->\n"
            '<div class="aim-about-cta" style="background:#006b6f;color:#fff;padding:3rem;text-align:center;border-radius:12px;margin-top:2rem">\n'
            f"  <h2 style=\"color:#fff;margin-bottom:0.5rem\">Read the Latest Issue</h2>\n"
            f"  <p style=\"color:rgba(255,255,255,0.8);margin-bottom:1.5rem\">Week of {html_escape(week_label)} &middot; Published {html_escape(report_date_str)}. All primary sources linked. All asymmetric signals flagged.</p>\n"
            f'  <a href="{html_escape(page_url)}" style="background:#fff;color:#006b6f;padding:0.6rem 1.5rem;border-radius:6px;text-decoration:none;font-weight:600">Open Report &rarr;</a>\n'
            "</div>\n"
            "<!-- /wp:html -->"
        )
        # Fetch current About page content
        resp = requests.get(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_ABOUT_ID}",
            auth=wp_auth,
            timeout=30,
        )
        resp.raise_for_status()
        _cdata = resp.json().get("content", {})
        current_about = _cdata.get("raw", "") or _cdata.get("rendered", "")

        # Replace the CTA block if it exists, otherwise append
        cta_pattern = r'<!-- wp:html -->\s*<div class="aim-about-cta".*?<!-- /wp:html -->'
        if _re.search(cta_pattern, current_about, _re.DOTALL):
            new_about = _re.sub(cta_pattern, about_cta_html, current_about, flags=_re.DOTALL)
        else:
            new_about = current_about + "\n" + about_cta_html

        resp = requests.post(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_ABOUT_ID}",
            auth=wp_auth,
            json={"content": new_about, "status": "publish"},
            timeout=60,
        )
        resp.raise_for_status()
        log(f"About page CTA (ID {WP_ABOUT_ID}) updated.")
    except Exception as exc:
        log(f"ERROR updating About page CTA: {exc}")

    # --- Digest page (latest issue preview) ---
    try:
        m0 = report.get("module_0") or report.get("module-0") or {}
        signal_text = ""
        if isinstance(m0, dict):
            signal_text = m0.get("body") or m0.get("text") or m0.get("summary") or ""
        words = signal_text.split()
        signal_truncated = " ".join(words[:80]) + ("\u2026" if len(words) > 80 else "")

        delta_strip = report.get("delta_strip", [])
        delta_items = ""
        for d in delta_strip[:5]:
            if isinstance(d, dict):
                delta_items += f"<li>{html_escape(d.get('text', ''))}</li>\n"

        digest_preview_html = (
            "<!-- wp:html -->\n"
            '<div class="aim-digest-preview" style="max-width:620px;margin:2rem auto;border:1px solid #ddd;border-radius:12px;overflow:hidden">\n'
            f'  <div style="background:#006b6f;padding:1.5rem;color:#fff">\n'
            f'    <div style="font-weight:700;font-size:0.9rem;letter-spacing:0.08em;text-transform:uppercase">Ramparts AI Frontier Monitor</div>\n'
            f'    <div style="font-size:1.1rem;font-weight:700;margin-top:0.5rem">The Signal &mdash; Week of {html_escape(week_label)}</div>\n'
            f'    <div style="font-size:0.8rem;color:rgba(255,255,255,0.7);margin-top:0.25rem">Asymmetric Intelligence &middot; ramparts.gi</div>\n'
            f"  </div>\n"
            f'  <div style="padding:1.5rem;background:#f8f7f4">\n'
            f'    <div style="font-weight:700;font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:#006b6f;border-bottom:2px solid #006b6f;padding-bottom:0.5rem;margin-bottom:1rem">&#9889; The Signal</div>\n'
            f'    <p style="font-size:0.9rem;line-height:1.75;margin-bottom:1.5rem">{html_escape(signal_truncated)}</p>\n'
            f'    <div style="font-weight:700;font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:#888;margin-bottom:0.75rem">&darr; Five Key Changes This Week</div>\n'
            f'    <ul style="list-style:none;padding:0;margin-bottom:1.5rem">{delta_items}</ul>\n'
            f'    <a href="{html_escape(page_url)}" style="display:block;text-align:center;background:#006b6f;color:#fff;padding:0.6rem;border-radius:6px;text-decoration:none;font-weight:600">Read the full report &rarr;</a>\n'
            f"  </div>\n"
            "</div>\n"
            "<!-- /wp:html -->"
        )
        # Fetch current Digest page
        resp = requests.get(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_DIGEST_ID}",
            auth=wp_auth,
            timeout=30,
        )
        resp.raise_for_status()
        _cdata = resp.json().get("content", {})
        current_digest = _cdata.get("raw", "") or _cdata.get("rendered", "")

        # Replace digest preview if it exists, otherwise append
        preview_pattern = r'<!-- wp:html -->\s*<div class="aim-digest-preview".*?<!-- /wp:html -->'
        if _re.search(preview_pattern, current_digest, _re.DOTALL):
            new_digest = _re.sub(preview_pattern, digest_preview_html, current_digest, flags=_re.DOTALL)
        else:
            new_digest = current_digest + "\n" + digest_preview_html

        resp = requests.post(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_DIGEST_ID}",
            auth=wp_auth,
            json={"content": new_digest, "status": "publish"},
            timeout=60,
        )
        resp.raise_for_status()
        log(f"Digest page (ID {WP_DIGEST_ID}) updated.")
    except Exception as exc:
        log(f"ERROR updating Digest page: {exc}")

    # --- Search page (all issues) ---
    try:
        search_items = []
        data_dir = Path(os.environ.get("REPO_ROOT", os.getcwd())) / "static/monitors/ai-governance/data"

        # Build search index from all report JSON files
        for entry in archive:
            slug = entry.get("slug", "")
            entry_url = entry.get("source_url") or f"{WP_SITE}/ai-frontier-monitor-issue-{slug}/"
            entry_label = entry.get("week_label") or slug
            vol = entry.get("volume", "")
            iss = entry.get("issue", "")
            vol_issue_str = ""
            if vol:
                vol_issue_str += f"Vol. {vol} · "
            if iss:
                vol_issue_str += f"Issue {iss}"

            # Try to load full report for this issue
            report_file = data_dir / f"report-{slug}.json"
            if not report_file.exists():
                report_file = data_dir / "report-latest.json" if slug == report_date_str else None

            if report_file and report_file.exists():
                try:
                    with open(report_file, "r", encoding="utf-8") as fh:
                        issue_report = json.load(fh)
                    for mod_key, mod_name in MODULE_NAMES.items():
                        mod_data = issue_report.get(mod_key) or issue_report.get(mod_key.replace("_", "-"))
                        if not mod_data:
                            continue
                        text_parts = []
                        items = get_module_items(mod_data)
                        for item in items:
                            if isinstance(item, dict):
                                for field in ("title", "headline", "body", "text", "summary", "asymmetric"):
                                    v = item.get(field, "")
                                    if v:
                                        text_parts.append(str(v))
                        if isinstance(mod_data, dict) and mod_data.get("body"):
                            text_parts.insert(0, str(mod_data["body"]))
                        if text_parts:
                            search_items.append({
                                "module": mod_name,
                                "week": entry_label,
                                "issue": vol_issue_str,
                                "text": " ".join(text_parts)[:2000],
                                "url": entry_url,
                            })
                except Exception:
                    pass

        search_json = json.dumps(search_items, ensure_ascii=False)
        search_block = (
            '<div class="aim-search" id="aim-search">\n'
            '  <h2>Search All Issues</h2>\n'
            '  <input type="text" id="aim-search-input" placeholder="Search across all modules and issues\u2026" '
            'style="width:100%;padding:12px 16px;border:1px solid #ccc;border-radius:8px;font-size:16px;margin-bottom:16px">\n'
            '  <div id="aim-search-results"></div>\n'
            '</div>\n'
            '<script>\n'
            f'var AIM_SEARCH_DATA = {search_json};\n'
            'var input = document.getElementById("aim-search-input");\n'
            'var results = document.getElementById("aim-search-results");\n'
            'input.addEventListener("input", function() {\n'
            '  var q = this.value.toLowerCase().trim();\n'
            '  if (q.length < 3) { results.innerHTML = ""; return; }\n'
            '  var hits = AIM_SEARCH_DATA.filter(function(d) { return d.text.toLowerCase().indexOf(q) !== -1; });\n'
            '  results.innerHTML = hits.slice(0, 20).map(function(h) {\n'
            '    var idx = h.text.toLowerCase().indexOf(q);\n'
            '    var start = Math.max(0, idx - 80);\n'
            '    var snippet = (start > 0 ? "\u2026" : "") + h.text.substring(start, idx + q.length + 120) + "\u2026";\n'
            '    return \'<div style="padding:12px 0;border-bottom:1px solid #eee">\' +\n'
            '      \'<a href="\' + h.url + \'" style="font-weight:600;color:#006b6f;text-decoration:none">\' + h.module + \' &mdash; \' + h.week + \'</a>\' +\n'
            '      \'<span style="font-size:13px;color:#888;margin-left:8px">\' + h.issue + \'</span>\' +\n'
            '      \'<p style="font-size:14px;color:#555;margin-top:4px;line-height:1.5">\' + snippet + \'</p></div>\';\n'
            '  }).join("");\n'
            '  if (hits.length === 0) results.innerHTML = \'<p style="color:#888">No results found.</p>\';\n'
            '  if (hits.length > 20) results.innerHTML += \'<p style="color:#888;margin-top:12px">Showing 20 of \' + hits.length + \' results.</p>\';\n'
            '});\n'
            '</script>'
        )

        # Fetch existing page to preserve styling
        resp = requests.get(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_SEARCH_ID}",
            auth=wp_auth,
            timeout=30,
        )
        resp.raise_for_status()
        _cdata = resp.json().get("content", {})
        current_search = _cdata.get("raw", "") or _cdata.get("rendered", "")

        # Replace the aim-search div + script if it exists, otherwise append
        search_pattern = r'<div class="aim-search" id="aim-search">.*?</script>'
        if _re.search(search_pattern, current_search, _re.DOTALL):
            new_search = _re.sub(search_pattern, search_block, current_search, flags=_re.DOTALL)
        else:
            new_search = current_search + "\n<!-- wp:html -->\n" + search_block + "\n<!-- /wp:html -->"

        resp = requests.post(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_SEARCH_ID}",
            auth=wp_auth,
            json={"content": new_search, "status": "publish"},
            timeout=120,
        )
        resp.raise_for_status()
        log(f"Search page (ID {WP_SEARCH_ID}) updated with {len(search_items)} items from {len(archive)} issues (styling preserved).")
    except Exception as exc:
        log(f"ERROR updating Search page: {exc}")


# ---------------------------------------------------------------------------
# Step 6 — Update JSON data pipeline
# ---------------------------------------------------------------------------


def step6_update_data_pipeline(
    report: dict,
    meta: dict,
    report_date_str: str,
    week_label: str,
    volume,
    issue,
    page_url: str,
    repo_root: Path,
    archive: list,
    archive_path: Path,
):
    log("Step 6: Updating JSON data pipeline files …")

    data_dir = repo_root / "static/monitors/ai-governance/data"

    # --- Update meta with ramparts fields ---
    report.setdefault("meta", {})
    report["meta"]["source_url"] = page_url
    report["meta"]["site_url"] = WP_SITE
    report["meta"]["pipeline_version"] = PIPELINE_VERSION

    # Write report-{DATE}.json
    dated_path = data_dir / f"report-{report_date_str}.json"
    try:
        with open(dated_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        log(f"Written: {dated_path}")
    except Exception as exc:
        log(f"ERROR writing dated report: {exc}")

    # Write report-latest.json (updated meta)
    latest_path = data_dir / "report-latest.json"
    try:
        with open(latest_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        log(f"Written: {latest_path}")
    except Exception as exc:
        log(f"ERROR writing report-latest.json: {exc}")

    # --- Prepend to archive.json (idempotent) ---
    try:
        existing_slugs = {entry.get("slug", "") for entry in archive}
        if report_date_str not in existing_slugs:
            new_entry = {
                "slug": report_date_str,
                "week_label": week_label,
                "volume": volume,
                "issue": issue,
                "source_url": page_url,
                "site_url": WP_SITE,
                "pipeline_version": PIPELINE_VERSION,
            }
            archive.insert(0, new_entry)
            with open(archive_path, "w", encoding="utf-8") as fh:
                json.dump(archive, fh, ensure_ascii=False, indent=2)
            log(f"archive.json prepended with {report_date_str}")
        else:
            log("archive.json already contains this slug — skipping prepend.")
    except Exception as exc:
        log(f"ERROR updating archive.json: {exc}")

    # --- Update persistent-state.json ---
    state_path = data_dir / "persistent-state.json"
    try:
        state = {}
        if state_path.exists():
            with open(state_path, "r", encoding="utf-8") as fh:
                state = json.load(fh)
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        state["last_issue"] = {
            "slug": report_date_str,
            "week_label": week_label,
            "volume": volume,
            "issue": issue,
            "source_url": page_url,
        }
        with open(state_path, "w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
        log(f"persistent-state.json updated.")
    except Exception as exc:
        log(f"ERROR updating persistent-state.json: {exc}")

    return dated_path, latest_path, archive_path, state_path


# ---------------------------------------------------------------------------
# Step 7 — Sync to Ramparts repo
# ---------------------------------------------------------------------------


def step7_sync_repo(
    report_date_str: str,
    repo_root: Path,
    dated_path: Path,
    latest_path: Path,
    archive_path: Path,
    state_path: Path,
):
    log("Step 7: Syncing data files to repository …")

    gh_token = os.environ.get("GH_TOKEN", "")
    if not gh_token:
        log("WARNING: GH_TOKEN not set — skipping repo sync.")
        return []

    synced_files = []
    data_dir = repo_root / "static/monitors/ai-governance/data"

    try:
        # Configure git identity
        subprocess.run(
            ["git", "config", "user.name", "Ramparts Build"],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "build@ramparts.gi"],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
        )

        # Stage data files
        files_to_add = [
            str(dated_path.relative_to(repo_root)),
            str(latest_path.relative_to(repo_root)),
            str(archive_path.relative_to(repo_root)),
            str(state_path.relative_to(repo_root)),
        ]
        for f in files_to_add:
            if (repo_root / f).exists():
                subprocess.run(
                    ["git", "add", f],
                    cwd=str(repo_root),
                    check=True,
                    capture_output=True,
                )
                synced_files.append(f)

        # Check if there are staged changes
        diff_result = subprocess.run(
            ["git", "diff", "--staged", "--quiet"],
            cwd=str(repo_root),
            capture_output=True,
        )

        if diff_result.returncode == 0:
            log("No staged changes — nothing to commit.")
            return synced_files

        # Commit
        commit_msg = f"data(ramparts): published {report_date_str} to ramparts.gi [skip ci]"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
        )
        log(f"Committed: {commit_msg}")

        # Push with retry
        remote_url = (
            f"https://x-access-token:{gh_token}@github.com/asym-intel/asym-intel.git"
        )
        subprocess.run(
            ["git", "remote", "set-url", "origin", remote_url],
            cwd=str(repo_root),
            check=True,
            capture_output=True,
        )

        for attempt in range(1, 4):
            pull_result = subprocess.run(
                ["git", "pull", "--rebase", "origin", "main"],
                cwd=str(repo_root),
                capture_output=True,
            )
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=str(repo_root),
                capture_output=True,
            )
            if push_result.returncode == 0:
                log("Push successful.")
                break
            else:
                log(
                    f"Push attempt {attempt}/3 failed: "
                    f"{push_result.stderr.decode(errors='replace').strip()}"
                )
                if attempt < 3:
                    import time
                    time.sleep(attempt * 10)
        else:
            log("ERROR: All push attempts failed.")

    except Exception as exc:
        log(f"ERROR in step 7 (repo sync): {exc}")

    return synced_files


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    log("=" * 60)
    log("Ramparts Publisher — starting")
    log("=" * 60)

    # Step 0
    (
        report,
        meta,
        report_date_str,
        week_label,
        volume,
        issue,
        repo_root,
        archive,
        archive_path,
    ) = step0_load_and_validate()

    # Step 1
    wp_user, wp_app_pass = step1_credentials()

    # Step 2
    html_content = step2_build_html(report, report_date_str, week_label, volume, issue)

    # Step 3
    page_url = step3_wordpress_issue_page(
        wp_user, wp_app_pass, week_label, report_date_str, html_content
    )

    # Step 4
    step4_update_standing_pages(
        wp_user, wp_app_pass, week_label, report_date_str, page_url, archive, report
    )


    # Step 6
    dated_path, latest_path, updated_archive_path, state_path = step6_update_data_pipeline(
        report,
        meta,
        report_date_str,
        week_label,
        volume,
        issue,
        page_url,
        repo_root,
        archive,
        archive_path,
    )

    # Step 7
    synced_files = step7_sync_repo(
        report_date_str,
        repo_root,
        dated_path,
        latest_path,
        updated_archive_path,
        state_path,
    )

    # Summary
    log("")
    log("=" * 60)
    log("RAMPARTS PUBLISHER COMPLETE")
    log("=" * 60)
    log(f"WordPress issue URL : {page_url}")
    log(f"Homepage URL        : {WP_SITE}/")
    log(f"Files synced        : {', '.join(synced_files) if synced_files else 'none'}")
    log("=" * 60)


if __name__ == "__main__":
    main()
