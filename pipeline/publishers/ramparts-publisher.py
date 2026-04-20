#!/usr/bin/env python3
"""
Ramparts Publisher — AI Frontier Monitor
Publishes weekly AIM report to ramparts.gi (WordPress).

Pipeline position: fires Friday 10:00 UTC via dispatcher (1h after AIM commons publisher at 09:00 UTC)
Input:  static/monitors/ai-governance/data/report-latest.json (commons AIM report)
Output:
  - WordPress issue page + homepage/archive updates on ramparts.gi
  - New entry appended to asym-intel/Ramparts:data/archive.json (cross-repo PUT via gh_put)

Idempotency:
  - Step 0 dup-check reads asym-intel/Ramparts:data/archive.json over HTTPS — the
    Ramparts repo is the source of truth for what has shipped to ramparts.gi.
    DO NOT change this to read static/monitors/ai-governance/data/archive.json —
    that's the AIM commons archive (different surface). Reading the commons
    archive caused a silent-skip bug on 2026-04-17 (Issue 4 missed). See
    pipeline/incidents/incidents.jsonl 2026-04-20 entry.
"""

import json
import os
import sys
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

import re as _re
import requests

# Vendored race-safe GitHub Contents API writer (see pipeline/lib/gh_put.py).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from gh_put import gh_put  # noqa: E402

# ---------------------------------------------------------------------------
# Cross-repo archive constants — Ramparts archive is the source of truth
# ---------------------------------------------------------------------------

RAMPARTS_REPO = "asym-intel/Ramparts"
RAMPARTS_ARCHIVE_PATH = "data/archive.json"
RAMPARTS_ARCHIVE_RAW_URL = (
    f"https://raw.githubusercontent.com/{RAMPARTS_REPO}/main/{RAMPARTS_ARCHIVE_PATH}"
)
RAMPARTS_ARCHIVE_API_URL = (
    f"https://api.github.com/repos/{RAMPARTS_REPO}/contents/{RAMPARTS_ARCHIVE_PATH}"
)

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


def _fetch_ramparts_archive() -> list:
    """Fetch asym-intel/Ramparts:data/archive.json over HTTPS.

    The Ramparts repo is the source of truth for what has shipped to ramparts.gi.
    Authenticated GitHub API call (Ramparts is a private repo) using GH_TOKEN.
    Returns [] if the file does not exist on the remote (first-ever publish).
    Raises RuntimeError on any other failure — never silently swallow.
    """
    gh_token = os.environ.get("GH_TOKEN", "")
    if not gh_token:
        raise RuntimeError(
            "GH_TOKEN not set — cannot fetch Ramparts archive for dup-check. "
            "Refusing to proceed (would risk publishing duplicates)."
        )
    try:
        resp = requests.get(
            RAMPARTS_ARCHIVE_API_URL,
            headers={
                "Authorization": f"token {gh_token}",
                "Accept": "application/vnd.github.v3.raw",
            },
            timeout=20,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Network error fetching Ramparts archive: {exc}") from exc

    if resp.status_code == 404:
        log(f"Ramparts archive not found at {RAMPARTS_REPO}:{RAMPARTS_ARCHIVE_PATH} — treating as empty (first publish).")
        return []
    if resp.status_code != 200:
        raise RuntimeError(
            f"Ramparts archive fetch returned {resp.status_code}: {resp.text[:200]}"
        )
    try:
        return resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Ramparts archive is not valid JSON: {exc}") from exc


def step0_load_and_validate():
    log("Step 0: Loading and validating report JSON …")

    repo_root = Path(os.environ.get("REPO_ROOT", os.getcwd()))
    report_path = repo_root / "static/monitors/ai-governance/data/report-latest.json"

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

    backfill_mode = os.environ.get("BACKFILL", "").lower() in ("1", "true", "yes")
    if pub_date < yesterday_utc:
        if backfill_mode:
            log(
                f"BACKFILL=1 — freshness check overridden. Publishing report dated {pub_date} on {today_utc}."
            )
        else:
            log(
                f"ERROR: Report is stale. Published {pub_date}, today is {today_utc}. "
                "Expected today or yesterday. Set BACKFILL=1 (workflow_dispatch input) to override."
            )
            sys.exit(1)

    log(f"Report date: {report_date_str}, week_label: {week_label}")

    # Duplication guard — read Ramparts repo's own archive.json (source of truth).
    # NOTE: previously read static/monitors/ai-governance/data/archive.json (the AIM
    # commons archive). That caused a silent-skip on 2026-04-17 because the commons
    # publisher had already written the date to the commons archive at 09:00 UTC,
    # and this publisher exited cleanly at 10:00 UTC without doing anything.
    log(f"Fetching Ramparts archive for dup-check: {RAMPARTS_REPO}:{RAMPARTS_ARCHIVE_PATH}")
    archive = _fetch_ramparts_archive()
    log(f"Ramparts archive: {len(archive)} existing entries.")

    existing_slugs = {entry.get("slug", "") for entry in archive}
    if report_date_str in existing_slugs:
        log(
            f"Already published: {report_date_str} found in {RAMPARTS_REPO}:{RAMPARTS_ARCHIVE_PATH}"
            " — exiting cleanly."
        )
        sys.exit(0)

    log("Validation passed — proceeding with publication.")
    return report, meta, report_date_str, week_label, volume, issue, repo_root, archive


# ---------------------------------------------------------------------------
# Step 1 — Read credentials
# ---------------------------------------------------------------------------


def step1_credentials():
    log("Step 1: Reading credentials from environment …")

    # WP basic-auth pair: (WP_USER, WP_APP_PASS) where WP_USER is the WordPress
    # user that owns the application password (asym-intel-engine since
    # 2026-04-20). Both are loaded from asym-intel-internal:platform-config.md
    # by the workflow — no defaults; fail loud if either is missing.
    wp_user = os.environ.get("WP_USER", "")
    wp_app_pass = os.environ.get("WP_APP_PASS", "")

    if not wp_user:
        log("ERROR: WP_USER environment variable is required but not set.")
        sys.exit(1)
    if not wp_app_pass:
        log("ERROR: WP_APP_PASS environment variable is required but not set.")
        sys.exit(1)

    log(f"Credentials loaded for WP user {wp_user!r}.")
    return wp_user, wp_app_pass


# ---------------------------------------------------------------------------
# Step 2 — Adapter-driven thin-frontend render.
#
# New architecture (AD-2026-04-20, thin-frontend pattern):
#   commons canonical JSON (report-latest.json)
#     → RampartsAimAdapter.transform()         (pipeline/adapters/)
#     → shaped JSON committed to
#         asym-intel/Ramparts:ramparts-v2/data/report-{date}.json
#     → node scripts/generate-static.js {date}  (run inside Ramparts checkout)
#     → static-report-{date}.html (≈150 KB rich monitor HTML)
#     → wrapped in <!-- wp:html --> and posted to WordPress by Step 3.
#
# The Ramparts repo is the single source of HTML/CSS/JS truth for ramparts.gi.
# This publisher never writes front-end bytes — only data, then delegates.
# ---------------------------------------------------------------------------


# Add repo root to sys.path so `from pipeline.adapters import …` resolves.
# publishers/ → pipeline/ → repo root = parents[2].
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Ramparts repo writes: shaped JSON and Node renderer invocation.
RAMPARTS_SHAPED_PATH_TMPL = "scripts/ramparts-v2/data/report-{date}.json"
RAMPARTS_REPO_CHECKOUT_ENV = "RAMPARTS_REPO_CHECKOUT"  # set by workflow
RAMPARTS_RENDERER_REL = "scripts/generate-static.js"
RAMPARTS_RENDERED_HTML_REL_TMPL = "scripts/ramparts-v2/data/static-report-{date}.html"


def _run_node_renderer(ramparts_checkout: Path, report_date_str: str) -> Path:
    """Invoke the Ramparts Node renderer; return path to the rendered HTML."""
    renderer = ramparts_checkout / RAMPARTS_RENDERER_REL
    if not renderer.exists():
        raise RuntimeError(
            f"Ramparts renderer not found at {renderer}. "
            f"Workflow must checkout asym-intel/Ramparts into {ramparts_checkout}."
        )
    # The renderer reads {cwd}/ramparts-v2/data/report-{date}.json so we run it
    # from the Ramparts repo root.
    log(f"Running Node renderer: node {renderer} {report_date_str}")
    result = subprocess.run(
        ["node", str(renderer), report_date_str],
        cwd=str(ramparts_checkout),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.stdout:
        for line in result.stdout.splitlines():
            log(f"  [renderer] {line}")
    if result.returncode != 0:
        log(f"Renderer stderr:\n{result.stderr}")
        raise RuntimeError(
            f"Node renderer exited with code {result.returncode} for {report_date_str}"
        )
    rendered = ramparts_checkout / RAMPARTS_RENDERED_HTML_REL_TMPL.format(
        date=report_date_str
    )
    if not rendered.exists():
        raise RuntimeError(f"Renderer did not produce expected output: {rendered}")
    return rendered


def step2_build_html(report: dict, report_date_str: str, week_label: str, volume, issue) -> str:
    """
    Build the WordPress issue HTML by:
      1. Transforming commons canonical → Ramparts-shape via adapter registry.
      2. Committing shaped JSON to asym-intel/Ramparts:ramparts-v2/data/.
      3. Invoking the Ramparts Node renderer in the Ramparts checkout.
      4. Wrapping the rendered HTML in a WordPress Custom HTML block.
    """
    log("Step 2: Adapter-driven render …")

    # --- 2.1 Adapter transform ---
    # Imports happen inside the function so top-level imports stay minimal and
    # the adapter package isn't required for unrelated unit tests.
    from pipeline.adapters import get, ramparts_aim  # noqa: F401  (registers)

    adapter = get("ai-governance", "ramparts-wp")
    try:
        shaped = adapter.transform(report)
    except Exception as exc:
        log(f"ERROR: adapter.transform failed: {exc}")
        raise

    log(
        f"Adapter OK — monitor={adapter.monitor} target={adapter.target} "
        f"accepts={adapter.accepts_schema_versions} emits={adapter.emits_schema_version}"
    )

    # --- 2.2 PUT shaped JSON to Ramparts repo ---
    shaped_path = RAMPARTS_SHAPED_PATH_TMPL.format(date=report_date_str)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(shaped, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        tmp_path = tmp.name
    try:
        commit_sha = gh_put(
            repo=RAMPARTS_REPO,
            path=shaped_path,
            content_path=tmp_path,
            message=(
                f"data(ramparts-v2): shaped report {report_date_str} "
                f"— Issue {issue} ({week_label}) [skip ci]"
            ),
            branch="main",
        )
        log(f"Shaped JSON PUT → {RAMPARTS_REPO}:{shaped_path}@{commit_sha[:7]}")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # --- 2.3 Invoke Node renderer ---
    checkout_env = os.environ.get(RAMPARTS_REPO_CHECKOUT_ENV)
    if not checkout_env:
        raise RuntimeError(
            f"Environment variable {RAMPARTS_REPO_CHECKOUT_ENV} not set — "
            "workflow must checkout asym-intel/Ramparts and export this path."
        )
    ramparts_checkout = Path(checkout_env).resolve()
    # Copy the just-shaped JSON into the checkout so the renderer sees it
    # (avoids a git pull race after our PUT).
    checkout_shaped = ramparts_checkout / shaped_path
    checkout_shaped.parent.mkdir(parents=True, exist_ok=True)
    with open(checkout_shaped, "w", encoding="utf-8") as fh:
        json.dump(shaped, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    rendered_path = _run_node_renderer(ramparts_checkout, report_date_str)
    rendered_html = rendered_path.read_text(encoding="utf-8")
    log(f"Rendered HTML: {len(rendered_html):,} chars from {rendered_path.name}")

    # --- 2.4 Wrap in WordPress Custom HTML block ---
    # The renderer emits a full <html>…</html> document; we only need the
    # body content for embedding inside a WP page. We extract the <body>
    # inner HTML and wrap it in wp:html so WordPress doesn't sanitise it.
    body_inner = _extract_body_inner(rendered_html)
    wp_html = (
        "<!-- wp:html -->\n"
        f"{body_inner}\n"
        "<!-- /wp:html -->\n"
    )
    log(f"WP Custom HTML block assembled: {len(wp_html):,} chars.")
    return wp_html


def _extract_body_inner(full_html: str) -> str:
    """Return HTML suitable for embedding in a WordPress wp:html block.

    Slices <body>…</body> content AND prepends any <style> blocks from
    <head>. This is required to preserve the WORDPRESS-BACK-ENGINE.md
    §5 canonical CSS override block — generate-static.js emits it inside
    <head>, and without it Elementor/Hello-theme defaults win (content
    clamped to 1140px, .entry-title visible, links underlined,
    .ramparts-btn loses white text, floating right nav chrome breaks,
    body fonts and background revert to theme defaults).

    See: asym-intel-main:docs/architecture/thin-frontend-pattern.md
    Regression introduced: PR #69 (20 Apr 2026). Fixed: 20 Apr 2026.
    """
    head_styles = _extract_head_styles(full_html)
    lower = full_html.lower()
    start = lower.find("<body")
    if start == -1:
        # degrade: embed the whole thing (styles included)
        return full_html
    body_open_end = lower.find(">", start)
    if body_open_end == -1:
        return full_html
    end = lower.rfind("</body>")
    if end == -1 or end < body_open_end:
        body_inner = full_html[body_open_end + 1 :]
    else:
        body_inner = full_html[body_open_end + 1 : end]
    if head_styles:
        return head_styles + "\n" + body_inner
    return body_inner


def _extract_head_styles(full_html: str) -> str:
    """Return every <style>…</style> block found inside <head>…</head>.

    Preserves order. Returns empty string if there is no <head> or no
    <style> blocks inside it. Case-insensitive; DOTALL so blocks may
    span newlines.
    """
    head_match = _re.search(
        r"<head[^>]*>(.*?)</head>", full_html, _re.DOTALL | _re.IGNORECASE
    )
    if not head_match:
        return ""
    head_inner = head_match.group(1)
    blocks = _re.findall(
        r"<style[^>]*>.*?</style>", head_inner, _re.DOTALL | _re.IGNORECASE
    )
    return "\n".join(blocks)


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
    volume="",
    issue="",
):
    log("Step 4: Updating standing WordPress pages (homepage + archive) …")
    wp_auth = (wp_user, wp_app_pass)

    # --- Homepage (read-then-patch: only the latest-banner div) ---
    # Rich landing page (hero + module grid + audience cards) is authored manually.
    # The publisher only swaps the inner <span class="text-sm"> of the latest-banner
    # div — never replaces full content. See WORDPRESS-BACK-ENGINE.md §5 (Rule 2).
    try:
        # 1. Read current homepage content
        get_resp = requests.get(
            f"{WP_SITE}/wp-json/wp/v2/pages/{WP_HOMEPAGE_ID}?context=edit",
            auth=wp_auth,
            timeout=60,
        )
        get_resp.raise_for_status()
        current = get_resp.json().get("content", {}).get("raw", "")

        # 2. Build new banner inner HTML
        vol_iss_parts = []
        if volume:
            vol_iss_parts.append(f"Vol. {html_escape(str(volume))}")
        if issue:
            vol_iss_parts.append(f"Issue {html_escape(str(issue))}")
        vol_iss = " · ".join(vol_iss_parts)
        banner_suffix = f" · {vol_iss}" if vol_iss else ""
        new_span = (
            f'<span class="text-sm">Latest Issue: {html_escape(week_label)}'
            f"{banner_suffix} &nbsp;\n"
            f'      <a href="{html_escape(page_url)}">Read now →</a>\n'
            f"    </span>"
        )

        # 3. Read-then-patch: replace ONLY the <span class="text-sm">...</span>
        #    inside <div class="latest-banner">.
        pattern = _re.compile(
            r'(<div class="latest-banner">.*?<div class="container">\s*)'
            r'<span class="text-sm">.*?</span>'
            r'(\s*</div>\s*</div>)',
            _re.DOTALL,
        )
        if not pattern.search(current):
            log(
                "WARN: latest-banner slot not found on homepage — skipping update. "
                "Check page 22643 still has <div class='latest-banner'> structure."
            )
        else:
            patched = pattern.sub(r"\1" + new_span + r"\2", current, count=1)
            resp = requests.post(
                f"{WP_SITE}/wp-json/wp/v2/pages/{WP_HOMEPAGE_ID}",
                auth=wp_auth,
                json={"content": patched, "status": "publish"},
                timeout=60,
            )
            resp.raise_for_status()
            log(f"Homepage (ID {WP_HOMEPAGE_ID}) latest-banner updated.")
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

    # --- Search page (all issues, base64-encoded script to prevent WP mangling) ---
    try:
        import base64

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
                vol_issue_str += f"Vol. {vol} \u00b7 "
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

        # Serialise search data as JSON for the data-items attribute
        search_json = json.dumps(search_items, ensure_ascii=False)
        # HTML-escape for safe embedding in a data attribute
        search_json_attr = html_escape(search_json)

        # Build the search script — uses DOM methods (no innerHTML assignment
        # with HTML-like strings that WP wpautop would mangle)
        search_script = (
            'var c=document.getElementById("aim-search");'
            'var items=JSON.parse(c.getAttribute("data-items"));'
            'var inp=document.getElementById("aim-search-input");'
            'var res=document.getElementById("aim-search-results");'
            'inp.addEventListener("input",function(){'
            'var q=this.value.toLowerCase().trim();'
            'if(q.length<3){while(res.firstChild)res.removeChild(res.firstChild);return;}'
            'var hits=items.filter(function(d){return d.text.toLowerCase().indexOf(q)!==-1;});'
            'while(res.firstChild)res.removeChild(res.firstChild);'
            'hits.slice(0,20).forEach(function(h){'
            'var idx=h.text.toLowerCase().indexOf(q);'
            'var start=Math.max(0,idx-80);'
            'var snippet=(start>0?"\u2026":"")+h.text.substring(start,idx+q.length+120)+"\u2026";'
            'var row=document.createElement("div");'
            'row.style.cssText="padding:12px 0;border-bottom:1px solid #eee";'
            'var a=document.createElement("a");'
            'a.href=h.url;a.style.cssText="font-weight:600;color:#006b6f;text-decoration:none";'
            'a.textContent=h.module+" \u2014 "+h.week;'
            'var sp=document.createElement("span");'
            'sp.style.cssText="font-size:13px;color:#888;margin-left:8px";'
            'sp.textContent=h.issue;'
            'var p=document.createElement("p");'
            'p.style.cssText="font-size:14px;color:#555;margin-top:4px;line-height:1.5";'
            'p.textContent=snippet;'
            'row.appendChild(a);row.appendChild(sp);row.appendChild(p);res.appendChild(row);});'
            'if(hits.length===0){var np=document.createElement("p");'
            'np.style.color="#888";np.textContent="No results found.";res.appendChild(np);}'
            'if(hits.length>20){var mp=document.createElement("p");'
            'mp.style.cssText="color:#888;margin-top:12px";'
            'mp.textContent="Showing 20 of "+hits.length+" results.";res.appendChild(mp);}'
            '});'
        )
        # Base64-encode the script to prevent WordPress wpautop from mangling it
        search_script_b64 = base64.b64encode(search_script.encode("utf-8")).decode("ascii")

        search_block = (
            f'<div class="aim-search" id="aim-search" data-items="{search_json_attr}">\n'
            '  <h2>Search All Issues</h2>\n'
            '  <input type="text" id="aim-search-input" placeholder="Search across all modules and issues\u2026" '
            'style="width:100%;padding:12px 16px;border:1px solid #ccc;border-radius:8px;font-size:16px;margin-bottom:16px">\n'
            '  <div id="aim-search-results"></div>\n'
            '</div>\n'
            f'<script>eval(atob("{search_script_b64}"))</script>'
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
        search_pattern = r'<div class="aim-search" id="aim-search"[^>]*>.*?</script>'
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
        log(f"Search page (ID {WP_SEARCH_ID}) updated with {len(search_items)} items from {len(archive)} issues (base64 script, styling preserved).")
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
):
    """Update Ramparts-side data files.

    Two write surfaces:
      1. asym-intel/Ramparts:data/archive.json — cross-repo PUT via gh_put (race-safe).
         Source of truth for what has shipped to ramparts.gi. Drives next week's
         dup-check.
      2. Local report-latest.json + report-{DATE}.json + persistent-state.json under
         static/monitors/ai-governance/data/ in the asym-intel-main checkout. These
         are committed back to asym-intel-main by the workflow's "Commit data updates"
         step (see ramparts-publisher.yml). They are the cached AIM-shaped Ramparts
         report, kept in asym-intel-main so the publisher has a deterministic input
         on the next run; they are NOT the same surface as the AIM commons report.
    """
    log("Step 6: Updating data files …")

    data_dir = repo_root / "static/monitors/ai-governance/data"

    # --- Update meta with ramparts fields ---
    report.setdefault("meta", {})
    report["meta"]["source_url"] = page_url
    report["meta"]["site_url"] = WP_SITE
    report["meta"]["pipeline_version"] = PIPELINE_VERSION

    # Write report-{DATE}.json (asym-intel-main checkout — committed by workflow)
    dated_path = data_dir / f"report-{report_date_str}.json"
    try:
        with open(dated_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        log(f"Written: {dated_path}")
    except Exception as exc:
        log(f"ERROR writing dated report: {exc}")

    # Write report-latest.json (asym-intel-main checkout — committed by workflow)
    latest_path = data_dir / "report-latest.json"
    try:
        with open(latest_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        log(f"Written: {latest_path}")
    except Exception as exc:
        log(f"ERROR writing report-latest.json: {exc}")

    # --- Prepend new entry to Ramparts:data/archive.json via cross-repo PUT ---
    existing_slugs = {entry.get("slug", "") for entry in archive}
    if report_date_str in existing_slugs:
        log(
            f"Ramparts archive already contains {report_date_str} — skipping cross-repo PUT."
        )
    else:
        new_entry = {
            "slug": report_date_str,
            "week_label": week_label,
            "volume": volume,
            "issue": issue,
            "source_url": page_url,
            "site_url": WP_SITE,
            "pipeline_version": PIPELINE_VERSION,
        }
        archive_with_new = [new_entry] + archive
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as tmp:
                json.dump(archive_with_new, tmp, ensure_ascii=False, indent=2)
                # Trailing newline keeps gitdiffs clean and matches existing file shape.
                tmp.write("\n")
                tmp_path = tmp.name
            commit_sha = gh_put(
                repo=RAMPARTS_REPO,
                path=RAMPARTS_ARCHIVE_PATH,
                content_path=tmp_path,
                message=f"data: archive entry for {report_date_str} — Issue {issue} ({week_label}) [skip ci]",
                branch="main",
            )
            log(
                f"Ramparts archive PUT successful → {RAMPARTS_REPO}@{commit_sha[:7]}"
                f" (now {len(archive_with_new)} entries)."
            )
        except RuntimeError as exc:
            # Hard fail — a successful WP publish without an archive write would
            # cause the next week's run to re-publish the same issue (the dup-check
            # would not see this slug). Better to fail loud here so Peter notices.
            log(f"ERROR: cross-repo archive PUT failed: {exc}")
            sys.exit(1)
        finally:
            try:
                os.unlink(tmp_path)
            except (OSError, NameError):
                pass

    # --- Update persistent-state.json (asym-intel-main checkout) ---
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

    return dated_path, latest_path, state_path


# ---------------------------------------------------------------------------
# Step 7 — REMOVED.
# ---------------------------------------------------------------------------
# Previously this step did `git push` to https://github.com/asym-intel/asym-intel.git
# (the wrong remote — neither the asym-intel-main checkout nor the Ramparts repo).
# The push silently failed or no-op'd in production.
#
# Cross-repo writes are now handled in Step 6 via the GitHub Contents API
# (gh_put) — race-safe and targets the correct repo.
#
# Local writes to the asym-intel-main checkout (report-latest.json, report-{DATE}.json,
# persistent-state.json) are committed back to asym-intel-main by the workflow's
# "Commit data updates" step in .github/workflows/ramparts-publisher.yml — that
# is the only push surface this publisher relies on.
# ---------------------------------------------------------------------------


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
        wp_user, wp_app_pass, week_label, report_date_str, page_url, archive, report,
        volume=volume, issue=issue,
    )


    # Step 6 — local writes (committed by workflow) + cross-repo Ramparts archive PUT
    dated_path, latest_path, state_path = step6_update_data_pipeline(
        report,
        meta,
        report_date_str,
        week_label,
        volume,
        issue,
        page_url,
        repo_root,
        archive,
    )

    # Summary
    log("")
    log("=" * 60)
    log("RAMPARTS PUBLISHER COMPLETE")
    log("=" * 60)
    log(f"WordPress issue URL : {page_url}")
    log(f"Homepage URL        : {WP_SITE}/")
    log(f"Ramparts archive    : {RAMPARTS_REPO}:{RAMPARTS_ARCHIVE_PATH}")
    log(f"Local data files    : {dated_path.name}, {latest_path.name}, {state_path.name}")
    log("=" * 60)


if __name__ == "__main__":
    main()
