#!/usr/bin/env python3
"""
build_site.py — Static site generator for asym-intel.info
=========================================================
Replaces Hugo. Reads the same content/, layouts/-equivalent logic (ported
in this file), assets/, and writes to docs/. Authority: AD-2026-05-01-BN.

Usage:
    python3 tools/build_site.py [--source PATH] [--output PATH]

Defaults source to repo root (cwd) and output to ./docs.

Files this generator owns (writes/overwrites):
    docs/index.html, docs/index.xml, docs/404.html, docs/sitemap.xml
    docs/css/main.css
    docs/about/index.html, docs/mission/index.html, docs/commercial/index.html
    docs/search/index.html, docs/subscribe/index.html
    docs/monitors/index.html
    docs/monitors/{slug}/index.html, docs/monitors/{slug}/index.xml
    docs/monitors/{slug}/page/N/index.html              (paginated)
    docs/monitors/{slug}/methodology/index.html         (when methodology.md)
    docs/monitors/{slug}/{date}-weekly-brief/index.html (per brief md)
    docs/topics/index.html, docs/topics/index.xml
    docs/topics/page/N/index.html
    docs/topics/{slug}/index.html
    docs/tags/index.html, docs/tags/index.xml, docs/tags/{tag}/index.html

Files this generator NEVER touches (publisher / static / pass-through):
    docs/monitors/{slug}/dashboard.html, report.html, chatter.html,
    archive.html, data/**, anything else under docs/ that is not in the
    write list above.
"""

from __future__ import annotations

import argparse
import json
import html
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

import frontmatter  # python-frontmatter
import markdown as md_lib

# ─────────────────────────────────────────────────────────────────────────────
# Constants — site-wide
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://asym-intel.info"
SITE_TITLE = "Asymmetric Intelligence"
SITE_DESCRIPTION = "A public intelligence commons. Eight monitors. One weekly briefing each."
LANGUAGE_CODE = "en-GB"
NETWORK_MAIN = "https://asym-intel.info"
NETWORK_SUB = "/network/"
PAGER_SIZE = 10
SITEMAP_PRIORITY = "0.5"
SITEMAP_CHANGEFREQ = "weekly"

# Homepage triage order — port of layouts/index.html $triageOrder (7 slugs).
HOME_TRIAGE_ORDER = [
    "macro-monitor",
    "conflict-escalation",
    "fimi-cognitive-warfare",
    "ai-governance",
    "democratic-integrity",
    "european-strategic-autonomy",
    "environmental-risks",
]

# Homepage colour/label/full-name dicts — exact port of layouts/index.html.
MONITOR_COLOURS = {
    "european-strategic-autonomy": "#5b8db0",
    "democratic-integrity":        "#61a5d2",
    "macro-monitor":               "#22a0aa",
    "ai-governance":               "#3a7d5a",
    "fimi-cognitive-warfare":      "#38bdf8",
    "environmental-risks":         "#4caf7d",
    "conflict-escalation":         "#dc2626",
}
MONITOR_LABELS = {
    "european-strategic-autonomy": "ESA",
    "democratic-integrity":        "WDM",
    "macro-monitor":               "GMM",
    "ai-governance":               "AGM",
    "fimi-cognitive-warfare":      "FCW",
    "environmental-risks":         "ERM",
    "conflict-escalation":         "SCEM",
}
MONITOR_FULL_NAMES = {
    "european-strategic-autonomy": "European Strategic Autonomy",
    "democratic-integrity":        "World Democracy Monitor",
    "macro-monitor":               "Global Macro Monitor",
    "ai-governance":               "AI Governance Monitor",
    "fimi-cognitive-warfare":      "FIMI & Cognitive Warfare",
    "environmental-risks":         "Environmental Risks Monitor",
    "conflict-escalation":         "Strategic Conflict & Escalation",
}

# ─────────────────────────────────────────────────────────────────────────────
# Markdown rendering
# ─────────────────────────────────────────────────────────────────────────────

# Hugo Goldmark with `unsafe: true` allows raw HTML. Python-Markdown allows raw
# HTML by default. Extensions roughly match Goldmark's table/footnote/extra set.
_MD_EXTENSIONS = ["extra", "tables", "footnotes", "sane_lists", "smarty"]


def render_markdown(body: str) -> str:
    return md_lib.markdown(
        body,
        extensions=_MD_EXTENSIONS,
        output_format="html5",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def parse_date(value: Any) -> datetime:
    """Hugo accepts strings, datetimes, dates. Normalise to aware UTC datetime."""
    if value is None:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    # date object
    if hasattr(value, "year") and hasattr(value, "month") and not hasattr(value, "hour"):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, str):
        s = value.strip()
        # Try ISO formats
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(s.replace("Z", "+0000") if fmt == "%Y-%m-%dT%H:%M:%S%z" else s, fmt)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        # fallback
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return datetime(1970, 1, 1, tzinfo=timezone.utc)
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def fmt_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z").replace("+0000", "Z") or "1970-01-01T00:00:00Z"


def fmt_date_long(dt: datetime) -> str:
    """e.g. '29 April 2026' — Hugo `2 January 2006`."""
    return f"{dt.day} {dt.strftime('%B %Y')}"


def fmt_date_short(dt: datetime) -> str:
    """e.g. '29 Apr 2026' — Hugo `2 Jan 2006`."""
    return f"{dt.day} {dt.strftime('%b %Y')}"


def slugify_anchor(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def truncate_words(s: str, n_chars: int = 120) -> str:
    if len(s) <= n_chars:
        return s
    cut = s[:n_chars].rsplit(" ", 1)[0]
    return cut + "…"


def jsonify_safe(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def get_git_short_sha(source_root: Path) -> str:
    sha = os.environ.get("GIT_SHA") or os.environ.get("GITHUB_SHA")
    if sha:
        return sha[:8]
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=8", "HEAD"],
            cwd=source_root, stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return "dev"


def write_file(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Page model
# ─────────────────────────────────────────────────────────────────────────────


class Page:
    """A renderable content unit."""

    def __init__(
        self,
        *,
        kind: str,                  # 'home','section','single','page','taxonomy','term','virtual'
        source_path: Path | None,
        permalink: str,             # e.g. '/monitors/macro-monitor/'
        title: str,
        description: str = "",
        params: dict | None = None,
        body_md: str = "",
        body_html: str = "",
        date: datetime | None = None,
        lastmod: datetime | None = None,
        section: str = "",
        parent_permalink: str | None = None,
        tags: list[str] | None = None,
        sitemap_disabled: bool = False,
        no_index: bool = False,
    ):
        self.kind = kind
        self.source_path = source_path
        self.permalink = permalink
        self.title = title
        self.description = description
        self.params = params or {}
        self.body_md = body_md
        self.body_html = body_html or (render_markdown(body_md) if body_md else "")
        self.date = date or datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.lastmod = lastmod or self.date
        self.section = section
        self.parent_permalink = parent_permalink
        self.tags = tags or []
        self.sitemap_disabled = sitemap_disabled
        self.no_index = no_index

    @property
    def absolute_url(self) -> str:
        return BASE_URL.rstrip("/") + self.permalink

    @property
    def is_home(self) -> bool:
        return self.kind == "home"

    @property
    def is_section(self) -> bool:
        return self.kind == "section"

    @property
    def is_page(self) -> bool:
        return self.kind in ("single", "page")


# ─────────────────────────────────────────────────────────────────────────────
# Loader
# ─────────────────────────────────────────────────────────────────────────────


def load_content(source_root: Path) -> dict:
    """
    Read content/ and assets/, return a dict:
      - briefs:   dict[slug -> list[Page]]
      - sections: dict[slug -> Page]   (monitor section index pages)
      - methodology: dict[slug -> Page | None]
      - topics:   list[Page]
      - topics_index: Page
      - static_pages: dict[name -> Page] (about, mission, commercial, search, subscribe)
      - home_index: Page
      - monitors_index: Page
      - registry: dict (parsed monitor-registry.json)
      - faqs:     dict (parsed monitor_faqs.json)
    """
    content_dir = source_root / "content"
    assets_dir = source_root / "assets"

    # ── Registry ─────────────────────────────────────────────────────────────
    registry_path = assets_dir / "monitors" / "monitor-registry.json"
    with registry_path.open() as f:
        registry = json.load(f)

    # ── FAQ data ─────────────────────────────────────────────────────────────
    faqs_path = source_root / "data" / "monitor_faqs.json"
    if faqs_path.exists():
        with faqs_path.open() as f:
            faqs = json.load(f)
    else:
        faqs = {}

    # ── Static pages (about/mission/commercial/search/subscribe) ─────────────
    static_pages = {}
    for name in ("about", "mission", "commercial", "search", "subscribe"):
        path = content_dir / f"{name}.md"
        if not path.exists():
            continue
        post = frontmatter.load(path)
        meta = post.metadata or {}
        sitemap_meta = meta.get("sitemap") or {}
        sitemap_disabled = bool(
            (isinstance(sitemap_meta, dict) and sitemap_meta.get("disable"))
        )
        static_pages[name] = Page(
            kind="page",
            source_path=path,
            permalink=f"/{name}/",
            title=meta.get("title", name.title()),
            description=meta.get("description", ""),
            params=meta,
            body_md=post.content or "",
            date=parse_date(meta.get("date") or meta.get("lastmod")),
            lastmod=parse_date(meta.get("lastmod") or meta.get("date")),
            sitemap_disabled=sitemap_disabled,
            no_index=bool(meta.get("robotsNoIndex")),
        )

    # ── Home _index.md ───────────────────────────────────────────────────────
    home_index_path = content_dir / "_index.md"
    if home_index_path.exists():
        post = frontmatter.load(home_index_path)
        meta = post.metadata or {}
    else:
        meta = {}
    home_index = Page(
        kind="home",
        source_path=home_index_path if home_index_path.exists() else None,
        permalink="/",
        title=meta.get("title", SITE_TITLE),
        description=meta.get("description", SITE_DESCRIPTION),
        params=meta,
        body_md="",
        date=datetime.now(timezone.utc),
        lastmod=datetime.now(timezone.utc),
    )

    # ── Monitors index (content/monitors/_index.md) ──────────────────────────
    mon_index_path = content_dir / "monitors" / "_index.md"
    if mon_index_path.exists():
        post = frontmatter.load(mon_index_path)
        meta = post.metadata or {}
    else:
        meta = {"title": "Monitors", "description": "Eight domains. One structured briefing each, published weekly."}
    monitors_index = Page(
        kind="section",
        source_path=mon_index_path if mon_index_path.exists() else None,
        permalink="/monitors/",
        title=meta.get("title", "Monitors"),
        description=meta.get("description", ""),
        params=meta,
        body_md=post.content if mon_index_path.exists() else "",
        date=parse_date(meta.get("date")),
        lastmod=parse_date(meta.get("lastmod") or meta.get("date")),
        section="monitors",
    )

    # ── Per-monitor sections + briefs + methodology ──────────────────────────
    sections: dict[str, Page] = {}
    briefs: dict[str, list[Page]] = defaultdict(list)
    methodology: dict[str, Page | None] = {}

    monitors_dir = content_dir / "monitors"
    if monitors_dir.is_dir():
        for monitor_dir in sorted(p for p in monitors_dir.iterdir() if p.is_dir()):
            slug = monitor_dir.name
            # Section _index.md
            idx_path = monitor_dir / "_index.md"
            if idx_path.exists():
                post = frontmatter.load(idx_path)
                meta = post.metadata or {}
                section_page = Page(
                    kind="section",
                    source_path=idx_path,
                    permalink=f"/monitors/{slug}/",
                    title=meta.get("title", slug),
                    description=meta.get("description", ""),
                    params=meta,
                    body_md=post.content or "",
                    date=parse_date(meta.get("date")),
                    lastmod=parse_date(meta.get("lastmod") or meta.get("date")),
                    section="monitors",
                    parent_permalink="/monitors/",
                )
                sections[slug] = section_page

            # Briefs (any .md not _index.md, methodology.md)
            for md_path in sorted(monitor_dir.glob("*.md")):
                name = md_path.name
                if name in ("_index.md",):
                    continue
                if name == "methodology.md":
                    post = frontmatter.load(md_path)
                    meta = post.metadata or {}
                    methodology[slug] = Page(
                        kind="single",
                        source_path=md_path,
                        permalink=f"/monitors/{slug}/methodology/",
                        title=meta.get("title", "Methodology"),
                        description=meta.get("description", ""),
                        params=meta,
                        body_md=post.content or "",
                        date=parse_date(meta.get("date") or meta.get("lastmod")),
                        lastmod=parse_date(meta.get("lastmod") or meta.get("date")),
                        section="monitors",
                        parent_permalink=f"/monitors/{slug}/",
                    )
                    continue

                post = frontmatter.load(md_path)
                meta = post.metadata or {}
                # Skip drafts
                if meta.get("draft") is True:
                    continue
                stem = md_path.stem  # e.g. 2026-04-29-weekly-brief
                page = Page(
                    kind="single",
                    source_path=md_path,
                    permalink=f"/monitors/{slug}/{stem}/",
                    title=meta.get("title", stem),
                    description=meta.get("description", "") or meta.get("summary", ""),
                    params=meta,
                    body_md=post.content or "",
                    date=parse_date(meta.get("date")),
                    lastmod=parse_date(meta.get("lastmod") or meta.get("date")),
                    section="monitors",
                    parent_permalink=f"/monitors/{slug}/",
                    tags=list(meta.get("tags") or []),
                )
                briefs[slug].append(page)
            briefs[slug].sort(key=lambda p: p.date, reverse=True)
            methodology.setdefault(slug, None)

    # ── Topics ───────────────────────────────────────────────────────────────
    topics_dir = content_dir / "topics"
    topics: list[Page] = []
    topics_idx_path = topics_dir / "_index.md"
    if topics_idx_path.exists():
        post = frontmatter.load(topics_idx_path)
        meta = post.metadata or {}
        topics_index = Page(
            kind="section",
            source_path=topics_idx_path,
            permalink="/topics/",
            title=meta.get("title", "Topics"),
            description=meta.get("description", ""),
            params=meta,
            body_md=post.content or "",
            date=parse_date(meta.get("date")),
            lastmod=parse_date(meta.get("lastmod") or meta.get("date")),
            section="topics",
        )
    else:
        topics_index = Page(
            kind="section",
            source_path=None,
            permalink="/topics/",
            title="Topics",
            description="",
        )

    if topics_dir.is_dir():
        for md_path in sorted(topics_dir.glob("*.md")):
            if md_path.name == "_index.md":
                continue
            stem = md_path.stem
            post = frontmatter.load(md_path)
            meta = post.metadata or {}
            if meta.get("draft") is True:
                continue
            topics.append(Page(
                kind="single",
                source_path=md_path,
                permalink=f"/topics/{stem}/",
                title=meta.get("title", stem),
                description=meta.get("description", ""),
                params=meta,
                body_md=post.content or "",
                date=parse_date(meta.get("date")),
                lastmod=parse_date(meta.get("lastmod") or meta.get("date")),
                section="topics",
                parent_permalink="/topics/",
                tags=list(meta.get("tags") or []),
            ))
    topics.sort(key=lambda p: p.date, reverse=True)

    # ── Report published dates (from report-latest.json meta.published) ────────
    # Used by Dataset JSON-LD to set dateModified accurately for monitor sections.
    report_published: dict[str, str] = {}
    _monitor_slugs = [
        "democratic-integrity", "macro-monitor", "european-strategic-autonomy",
        "fimi-cognitive-warfare", "ai-governance", "environmental-risks",
        "conflict-escalation",
    ]
    for _slug in _monitor_slugs:
        _report_path = source_root / "static" / "monitors" / _slug / "data" / "report-latest.json"
        if _report_path.exists():
            try:
                with _report_path.open() as _f:
                    _report = json.load(_f)
                _pub = (_report.get("meta") or {}).get("published", "")
                if _pub:
                    report_published[_slug] = _pub
            except Exception:
                pass

    return {
        "registry": registry,
        "faqs": faqs,
        "static_pages": static_pages,
        "home_index": home_index,
        "monitors_index": monitors_index,
        "sections": sections,
        "briefs": briefs,
        "methodology": methodology,
        "topics_index": topics_index,
        "topics": topics,
        "report_published": report_published,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Shell — port of baseof.html + partials
# ─────────────────────────────────────────────────────────────────────────────


def render_head(page: Page, *, ctx: dict, css_cache_buster: str, alt_outputs: list[tuple[str, str, str, str]] | None = None) -> str:
    """alt_outputs: list of (rel, type, href, title) for <link rel="alternate">."""
    alt_outputs = alt_outputs or []
    site = ctx["site"]
    is_home = page.is_home
    title_tag = SITE_TITLE if is_home else f"{html.escape(page.title)} · {SITE_TITLE}"
    description = page.description or SITE_DESCRIPTION
    canonical = page.absolute_url

    # Choose summary for OG/Twitter
    og_desc = page.description or page.params.get("summary") or SITE_DESCRIPTION
    og_type = "article" if page.is_page else "website"

    # OG image: explicit > monitor-specific > fallback
    og_image_param = page.params.get("image")
    monitor_param = page.params.get("monitor")
    if og_image_param:
        og_image = og_image_param if og_image_param.startswith("http") else BASE_URL + "/" + og_image_param.lstrip("/")
    elif monitor_param:
        og_image = f"{BASE_URL}/images/og/{monitor_param}-og.png"
    else:
        og_image = f"{BASE_URL}/images/og-fallback.png"

    head_lines = [
        '<meta charset="utf-8">',
        '<!-- Favicons -->',
        '<link rel="icon" type="image/x-icon" href="/favicon.ico">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">',
        '<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">',
        '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<!-- Nav: single source of truth across all pages (theme toggle + network bar) -->',
        '<script src="/monitors/shared/js/theme.js"></script>',
        '<script src="/monitors/shared/js/nav.js" defer></script>',
        f'<meta name="description" content="{html.escape(description, quote=True)}">',
        f'<title>{title_tag}</title>',
        f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">',
        '<!-- Fonts: Satoshi (Fontshare) + Instrument Serif (Google Fonts) — async load (P-003) -->',
        '<link rel="preconnect" href="https://api.fontshare.com">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://api.fontshare.com/v2/css?f[]=satoshi@300,400,500,700&display=swap" rel="stylesheet" media="print" onload="this.media=\'all\'">',
        '<noscript><link href="https://api.fontshare.com/v2/css?f[]=satoshi@300,400,500,700&display=swap" rel="stylesheet"></noscript>',
        '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet" media="print" onload="this.media=\'all\'">',
        '<noscript><link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet"></noscript>',
        '<!-- Main stylesheet -->',
        f'<link rel="stylesheet" href="/css/main.css?v={css_cache_buster}">',
    ]
    if page.no_index:
        head_lines.append('<meta name="robots" content="noindex, nofollow">')

    # Alternate output formats (RSS, etc)
    if alt_outputs:
        head_lines.append('<!-- Alternate outputs -->')
        for rel, mtype, href, atitle in alt_outputs:
            head_lines.append(
                f'<link rel="{rel}" type="{mtype}" href="{html.escape(href, quote=True)}" title="{html.escape(atitle, quote=True)}">'
            )

    # AI-readable discovery tag for monitor sections
    if page.is_section and page.permalink.startswith("/monitors/") and page.permalink != "/monitors/":
        slug = page.permalink.rstrip("/").rsplit("/", 1)[-1]
        head_lines.append(
            f'<link rel="alternate" type="text/markdown" title="AI-Readable Version" href="/monitors/{slug}/data/report-latest.md">'
        )

    head_lines.append('<link rel="alternate" type="text/plain" title="LLM Site Index" href="/llms.txt">')

    # Open Graph
    og_title = SITE_TITLE if is_home else page.title
    twitter_title = SITE_TITLE if is_home else page.title
    head_lines += [
        '<!-- Open Graph -->',
        f'<meta property="og:title" content="{html.escape(og_title if is_home else f"{og_title} · {SITE_TITLE}", quote=True)}">',
        f'<meta property="og:description" content="{html.escape(og_desc, quote=True)}">',
        f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">',
        f'<meta property="og:type" content="{og_type}">',
        '<meta property="og:site_name" content="Asymmetric Intelligence">',
        f'<meta property="og:image" content="{html.escape(og_image, quote=True)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<!-- Twitter / X card -->',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html.escape(twitter_title, quote=True)}">',
        f'<meta name="twitter:description" content="{html.escape(og_desc, quote=True)}">',
        f'<meta name="twitter:image" content="{html.escape(og_image, quote=True)}">',
    ]

    # JSON-LD
    head_lines.append("<!-- JSON-LD -->")
    if is_home:
        org = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Asymmetric Intelligence",
            "url": "https://asym-intel.info",
            "logo": {"@type": "ImageObject", "url": "https://asym-intel.info/favicon-32x32.png"},
            "description": "Open-source geopolitical intelligence platform publishing weekly early-warning monitors across democracy, macro, FIMI, AI governance, environment, conflict, and European strategic autonomy.",
            "sameAs": [],
        }
        head_lines.append(f'<script type="application/ld+json">{jsonify_safe(org)}</script>')
    else:
        # BreadcrumbList
        crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"}]
        if page.parent_permalink and page.parent_permalink != "/":
            parent = ctx["pages_by_url"].get(page.parent_permalink)
            crumbs.append({
                "@type": "ListItem", "position": 2,
                "name": parent.title if parent else page.parent_permalink.strip("/").split("/")[-1].replace("-", " ").title(),
                "item": BASE_URL + page.parent_permalink,
            })
            crumbs.append({"@type": "ListItem", "position": 3, "name": page.title, "item": page.absolute_url})
        else:
            crumbs.append({"@type": "ListItem", "position": 2, "name": page.title, "item": page.absolute_url})
        bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs}
        head_lines.append(f'<script type="application/ld+json">{jsonify_safe(bc)}</script>')

    # Dataset for monitor sections
    if page.is_section and page.description and page.permalink.startswith("/monitors/") and page.permalink != "/monitors/":
        slug = page.permalink.rstrip("/").rsplit("/", 1)[-1]
        dataset = {
            "@context": "https://schema.org",
            "@type": ["WebPage", "Dataset"],
            "name": f"{page.title} — Asymmetric Intelligence",
            "description": page.description,
            "url": page.absolute_url,
            "publisher": {"@type": "Organization", "name": "Asymmetric Intelligence", "url": "https://asym-intel.info"},
            "creator": {"@type": "Person", "name": "Peter Howitt"},
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "isAccessibleForFree": True,
            "inLanguage": "en",
            "temporalCoverage": "2026/..",
            "updateFrequency": "P7D",
        }
        monitor_param = page.params.get("monitor") or slug
        dataset["distribution"] = [{
            "@type": "DataDownload",
            "encodingFormat": "application/json",
            "contentUrl": f"https://asym-intel.info/monitors/{monitor_param}/data/report-latest.json",
        }]
        # Use report-latest.json meta.published as authoritative dateModified for monitor sections
        report_published = (ctx.get("data", {}).get("report_published") or {}).get(slug)
        if report_published:
            # report_published is ISO 8601 string e.g. "2026-04-27T06:00:00Z" — take date part
            dataset["dateModified"] = report_published[:10]
        elif page.lastmod:
            dataset["dateModified"] = page.lastmod.strftime("%Y-%m-%d")
        if report_published and "datePublished" not in dataset:
            dataset["datePublished"] = report_published[:10]
        head_lines.append(f'<script type="application/ld+json">{jsonify_safe(dataset)}</script>')

        # FAQPage if FAQs exist
        faqs_for_slug = ctx["data"]["faqs"].get(slug)
        if faqs_for_slug:
            entities = [
                {"@type": "Question", "name": q["question"],
                 "acceptedAnswer": {"@type": "Answer", "text": q["answer"]}}
                for q in faqs_for_slug
            ]
            faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
            head_lines.append(f'<script type="application/ld+json">{jsonify_safe(faq_ld)}</script>')

    return "\n  ".join(head_lines)


def render_network_bar(page: Page) -> str:
    is_home_active = page.is_home
    active_class = " network-bar__link--active" if is_home_active else ""
    return f"""<header class="network-bar" role="banner" aria-label="Asymmetric Intelligence network">
  <div class="network-bar__inner">
    <a class="network-bar__brand" href="{NETWORK_MAIN}" aria-label="Asymmetric Intelligence home">
      <svg class="network-bar__svg" width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <rect x="2"  y="4"  width="10" height="2.5" rx="1.25" fill="currentColor"/>
        <rect x="6"  y="9"  width="12" height="2.5" rx="1.25" fill="currentColor" opacity="0.65"/>
        <rect x="2"  y="14" width="7"  height="2.5" rx="1.25" fill="currentColor" opacity="0.35"/>
      </svg>
      <span class="network-bar__name">Asymmetric Intelligence</span>
    </a>
    <div class="network-bar__spacer"></div>
    <nav class="network-bar__nav" aria-label="Platform sections">
      <a class="network-bar__link{active_class}" href="{NETWORK_MAIN}/monitors/">Monitors</a>
      <a class="network-bar__link" href="{NETWORK_SUB}">Network</a>
      <a class="network-bar__link" href="/map/">World Map</a>
      <a class="network-bar__link" href="/commercial/">Commercial</a>
    </nav>
    <button class="network-bar__hamburger" aria-label="Toggle network links" aria-expanded="false"
            onclick="this.setAttribute('aria-expanded', this.nextElementSibling.classList.toggle('network-bar__nav--open') ? 'true' : 'false')">
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#a8a7a4" stroke-width="1.5">
        <line x1="2" y1="4.5" x2="16" y2="4.5"/><line x1="2" y1="9" x2="16" y2="9"/>
        <line x1="2" y1="13.5" x2="16" y2="13.5"/>
      </svg>
    </button>
    <nav class="network-bar__dropdown" aria-label="Network links mobile">
      <a href="{NETWORK_MAIN}/monitors/">Monitors</a>
      <a href="{NETWORK_SUB}">Network</a>
      <a href="/map/">World Map</a>
      <a href="/commercial/">Commercial</a>
    </nav>
  </div>
</header>"""


def render_site_header(page: Page) -> str:
    rp = page.permalink
    about_active = ' class="active"' if rp == "/about/" else ""
    search_active = ' class="active"' if rp.startswith("/search") else ""
    return f"""<nav class="site-nav" aria-label="Site navigation">
  <div class="site-nav__spacer"></div>
  <ul class="site-nav__links" role="list">
    <li><a href="/about/"{about_active}>About</a></li>
    <li><a href="/search/"{search_active}>Search</a></li>
  </ul>
  <div class="site-nav__actions">
    <a class="site-nav__subscribe" href="/subscribe/">Subscribe</a>
  </div>
</nav>"""


# Triage order for monitor strip — from monitor-strip.html template.
# (Hugo template uses a hardcoded slice; if registry abbr matches, render.)
_STRIP_TRIAGE = ["GMM", "SCEM", "FCW", "AIM", "WDM", "ESA", "ERM"]


def render_monitor_strip(page: Page, registry: dict) -> str:
    monitors = {m["abbr"]: m for m in registry["monitors"]}
    # Treat 'AGM' (registry) as 'AIM' (template name) to match Hugo behaviour:
    # the engine's strip uses 'AIM' but the registry stores 'AIM' — verify.
    # In current registry the abbr is 'AIM' for ai-governance, so direct match.
    pills = []
    for abbr in _STRIP_TRIAGE:
        m = monitors.get(abbr)
        if not m:
            continue
        pills.append(
            f'  <a class="monitor-strip__pill" data-monitor="{html.escape(m["abbr"])}" '
            f'href="{html.escape(m["url"], quote=True)}" style="--pill-accent: {html.escape(m["accent"])}">\n'
            f'    <img class="monitor-strip__icon" src="{html.escape(m["svg_url"], quote=True)}" '
            f'alt="" width="16" height="16" aria-hidden="true">\n'
            f'    <span>{html.escape(m["short_name"])}</span>\n'
            f'  </a>'
        )
    return ('<nav class="monitor-strip" role="navigation" aria-label="Monitor navigation">\n'
            '  <span class="monitor-strip__label">Monitors</span>\n'
            + "\n".join(pills) + "\n</nav>")


def render_footer(now_year: int) -> str:
    return f"""<footer class="site-footer">
  <div class="site-footer__inner">
    <div class="site-footer__brand">
      <a href="https://a-i.gi/" style="display:inline-flex;align-items:center;gap:0.4rem;text-decoration:none;color:inherit">
        <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <rect x="2" y="4" width="10" height="2.5" rx="1.25" fill="#4f98a3"/>
          <rect x="6" y="9" width="12" height="2.5" rx="1.25" fill="#4f98a3" opacity=".65"/>
          <rect x="2" y="14" width="7" height="2.5" rx="1.25" fill="#4f98a3" opacity=".35"/>
        </svg>
        <span>Asymmetric Intelligence</span>
      </a>
    </div>
    <p class="site-footer__copy">
      &copy; {now_year} Asymmetric Intelligence.
      Commons and commercial: <a href="https://a-i.gi/">a-i.gi</a>.
      Published by <a href="https://ramparts.gi/people/peter-howitt/">Peter Howitt</a>.
      Content is published under <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>.
      <a href="https://www.perplexity.ai/computer" target="_blank" rel="noopener">Produced with Perplexity Computer</a>.
    </p>
  </div>
</footer>"""


_SITE_NAV_INLINE_SCRIPT = r"""<script>
/* Site-nav hamburger — inline since Hugo pages don't load nav.js */
(function() {
  function initSiteNav() {
    var btn   = document.querySelector('.site-nav__hamburger');
    var links = document.querySelector('.site-nav__links');
    if (!btn || !links) return;
    btn.addEventListener('click', function () {
      var open = links.classList.toggle('site-nav__links--open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('site-nav__links--open');
        btn.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('click', function (e) {
      if (links.classList.contains('site-nav__links--open') &&
          !links.contains(e.target) && !btn.contains(e.target)) {
        links.classList.remove('site-nav__links--open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSiteNav);
  } else {
    initSiteNav();
  }
})();
</script>"""


def render_shell(
    page: Page,
    *,
    main_html: str,
    ctx: dict,
    css_cache_buster: str,
    alt_outputs: list[tuple[str, str, str, str]] | None = None,
) -> str:
    head_html = render_head(page, ctx=ctx, css_cache_buster=css_cache_buster, alt_outputs=alt_outputs)
    network_bar = render_network_bar(page)
    site_header = render_site_header(page)
    monitor_strip = render_monitor_strip(page, ctx["data"]["registry"])
    footer = render_footer(ctx["now_year"])
    return f"""<!DOCTYPE html>
<html lang="{LANGUAGE_CODE}">
<head>
  {head_html}
</head>
<body>
  {network_bar}
  {site_header}
  {monitor_strip}
  <main id="main-content">
{main_html}
  </main>
  {footer}
  {_SITE_NAV_INLINE_SCRIPT}
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Page renderers
# ─────────────────────────────────────────────────────────────────────────────


def render_homepage_main(ctx: dict) -> str:
    """Port of layouts/index.html — OMITS home-synthesis widget per AD-2026-04-30 carry-forward."""
    briefs = ctx["data"]["briefs"]
    # Collect latest brief from each triage-order monitor
    all_latest = []
    for slug in HOME_TRIAGE_ORDER:
        monitor_briefs = briefs.get(slug, [])
        if monitor_briefs:
            all_latest.append({"post": monitor_briefs[0], "slug": slug})
    all_latest.sort(key=lambda x: x["post"].date, reverse=True)
    lead = all_latest[0] if all_latest else None
    secondary = all_latest[1:7] if len(all_latest) > 1 else []

    parts = []
    parts.append('<div class="home-layout">')
    parts.append('  <div class="container container--wide">')
    parts.append('    <div class="home-grid">')

    # LEFT panel
    parts.append("""      <aside class="home-panel">
        <p class="home-panel__tagline">Seven monitors tracking geopolitics, democracy, AI governance, and systemic risk.</p>
        <nav class="home-panel__nav" aria-label="Platform tools">
          <a class="home-featured-card" href="/network/">
            <img class="home-featured-card__thumb" src="/images/thumbs/network-graph.svg" alt="" loading="lazy">
            <div class="home-featured-card__body">
              <span class="home-featured-card__title">Network Graph</span>
              <span class="home-featured-card__desc">Cross-monitor entity and theme relationships.</span>
            </div>
          </a>
          <a class="home-featured-card" href="/map/">
            <img class="home-featured-card__thumb" src="/images/thumbs/world-map.svg" alt="" loading="lazy">
            <div class="home-featured-card__body">
              <span class="home-featured-card__title">World Map</span>
              <span class="home-featured-card__desc">Geographic view of monitored risks and events.</span>
            </div>
          </a>
          <a class="home-featured-card" href="/ops/pipeline.html">
            <img class="home-featured-card__thumb" src="/images/thumbs/pipeline-health.svg" alt="" loading="lazy">
            <div class="home-featured-card__body">
              <span class="home-featured-card__title">Pipeline Health</span>
              <span class="home-featured-card__desc">Live status of data collection, synthesis, and publishing.</span>
            </div>
          </a>
        </nav>
      </aside>""")

    parts.append('      <div class="home-feed">')
    # Synthesis widget OMITTED (carry-forward note: fetches non-existent JSON).

    # Value statement HP-02
    parts.append("""        <div class="home-value-statement">
          <p class="home-value-statement__text">Asymmetric Intelligence is a public, methodology-transparent intelligence platform that surfaces pre-consensus structural risks and weekly signals across democracy, conflict, information operations, macroeconomy, AI governance, European strategy, and planetary boundaries.</p>
          <div class="home-routing-cues">
            <div class="home-routing-cue">
              <span class="home-routing-cue__label">Triage</span>
              <span class="home-routing-cue__body">This week's assessed signals, risk levels, and cross-monitor flags.</span>
              <a class="home-routing-cue__link" href="/monitors/">Monitor dashboards →</a>
            </div>
            <div class="home-routing-cue">
              <span class="home-routing-cue__label">This week's analysis</span>
              <span class="home-routing-cue__body">Weekly briefs and reports for in-depth analytical coverage.</span>
            </div>
            <div class="home-routing-cue">
              <span class="home-routing-cue__label">Structural pipelines</span>
              <span class="home-routing-cue__body">Living Knowledge — slower-moving structures, indices, and scenarios behind the weekly data.</span>
            </div>
            <div class="home-routing-cue">
              <span class="home-routing-cue__label">Raw signal</span>
              <span class="home-routing-cue__body">Chatter feeds — pre-synthesis, high-volume signal, clearly labelled and separate from assessed intelligence.</span>
            </div>
          </div>
        </div>""")

    # Lead
    if lead:
        post = lead["post"]
        slug = lead["slug"]
        colour = MONITOR_COLOURS[slug]
        abbr = MONITOR_LABELS[slug]
        summary = post.params.get("summary") or ""
        summary_html = f'\n            <p class="tn-lead__summary">{html.escape(summary)}</p>' if summary else ""
        parts.append(f"""        <article class="tn-lead" style="--lead-accent: {colour}">
          <div class="tn-lead__stripe"></div>
          <div class="tn-lead__inner">
            <div class="tn-lead__meta">
              <span class="monitor-pill" style="--monitor-accent: {colour}; --monitor-accent-bg: {colour}1a">
                <span class="monitor-dot" style="background: {colour}"></span>{abbr}
              </span>
              <time class="tn-lead__date" datetime="{post.date.strftime('%Y-%m-%d')}">{fmt_date_long(post.date)}</time>
            </div>
            <h1 class="tn-lead__title">
              <a href="{post.permalink}">{html.escape(post.title)}</a>
            </h1>{summary_html}
            <div class="tn-lead__actions">
              <a class="btn btn--primary btn--sm" href="{post.permalink}">Read brief</a>
              <a class="btn btn--outline btn--sm" href="/monitors/{slug}/dashboard.html">Dashboard →</a>
            </div>
          </div>
        </article>""")

    # Secondary grid
    if secondary:
        parts.append('        <section class="home-report-grid" aria-label="Latest from all monitors">')
        parts.append('          <h2 class="home-section-label">Latest issues</h2>')
        parts.append('          <div class="card-grid">')
        for entry in secondary:
            post = entry["post"]
            slug = entry["slug"]
            colour = MONITOR_COLOURS[slug]
            abbr = MONITOR_LABELS[slug]
            summary = post.params.get("summary") or ""
            summary_html = f'\n                <div class="report-card__summary">{html.escape(truncate_words(summary, 120))}</div>' if summary else ""
            parts.append(f"""            <a class="report-card" href="{post.permalink}"
               style="--card-accent: {colour}; --monitor-accent: {colour}; --monitor-accent-bg: {colour}1a">
              <div class="report-card__accent"></div>
              <div class="report-card__body">
                <div class="report-card__monitor">
                  <span class="monitor-dot"></span> {abbr}
                </div>
                <div class="report-card__title">{html.escape(post.title)}</div>{summary_html}
              </div>
              <div class="report-card__footer">
                <time datetime="{post.date.strftime('%Y-%m-%d')}">{fmt_date_short(post.date)}</time>
                <span>Read →</span>
              </div>
            </a>""")
        parts.append('          </div>')
        parts.append('        </section>')

    parts.append('      </div>')  # /home-feed

    # RIGHT chatter aside
    parts.append("""      <aside class="home-chatter" id="home-chatter-col">
        <div class="home-chatter__header">
          <h2 class="home-chatter__title">Signal Chatter</h2>
          <span class="home-chatter__label">Pre-synthesis</span>
        </div>
        <p class="home-chatter__desc">Raw signal streamed daily before weekly synthesis. Unvalidated.</p>
        <ul class="home-chatter__list" id="chatter-col-list">
          <li class="home-chatter__item" style="color:var(--color-text-faint);font-size:0.75rem;padding:1rem">Loading…</li>
        </ul>
      </aside>""")

    parts.append('    </div>')  # /home-grid
    parts.append('  </div>')
    parts.append('</div>')

    # Chatter loader script (verbatim from index.html)
    parts.append(r"""<script>
(function() {
  var monitors = [
    { slug: 'democratic-integrity',        accent: '#61a5d2', label: 'WDM' },
    { slug: 'macro-monitor',               accent: '#22a0aa', label: 'GMM' },
    { slug: 'fimi-cognitive-warfare',      accent: '#38bdf8', label: 'FCW' },
    { slug: 'european-strategic-autonomy', accent: '#5b8db0', label: 'ESA' },
    { slug: 'ai-governance',               accent: '#3a7d5a', label: 'AGM' },
    { slug: 'environmental-risks',         accent: '#4caf7d', label: 'ERM' },
    { slug: 'conflict-escalation',         accent: '#dc2626', label: 'SCEM' },
  ];
  function escHtml(s) {
    return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  var listEl = document.getElementById('chatter-col-list');
  if (!listEl) return;
  var allItems = [];
  var pending = monitors.length;
  monitors.forEach(function(m) {
    fetch('/monitors/' + m.slug + '/data/chatter-latest.json')
      .then(function(r) { return r.ok ? r.json() : Promise.reject(); })
      .then(function(d) {
        (d.items || []).forEach(function(item) {
          allItems.push({ item: item, accent: m.accent, label: m.label });
        });
      })
      .catch(function() {})
      .finally(function() {
        pending--;
        if (pending === 0) renderChatter();
      });
  });
  function renderChatter() {
    if (!allItems.length) {
      listEl.innerHTML = '<li class="home-chatter__item" style="font-size:0.75rem;color:var(--color-text-faint)">No chatter available yet. Check back after 08:00 UTC.</li>';
      return;
    }
    allItems.sort(function() { return Math.random() - 0.5; });
    var top = allItems.slice(0, 10);
    var html = '';
    top.forEach(function(entry) {
      var item = entry.item;
      html += '<li class="home-chatter__item">';
      html += '<span class="home-chatter__chip" style="color:' + entry.accent + ';border-color:' + entry.accent + '">' + escHtml(entry.label) + '</span>';
      html += '<a class="home-chatter__link" href="' + escHtml(item.source_url || '#') + '" target="_blank" rel="noopener">' + escHtml(item.title || '') + '</a>';
      html += '<span class="home-chatter__source">' + escHtml(item.source_name || '') + '</span>';
      html += '</li>';
    });
    listEl.innerHTML = html;
  }
})();
</script>""")
    return "\n".join(parts)


def render_monitors_index_main(ctx: dict) -> str:
    registry = ctx["data"]["registry"]
    parts = []
    parts.append('<div class="page-container">')
    parts.append('  <header class="page-header">')
    parts.append('    <h1>Monitors</h1>')
    parts.append(f'    <p>Weekly intelligence across {len(registry["monitors"])} thematic domains. Each monitor runs an autonomous collector / reasoner / synthesiser / publisher pipeline and publishes a dated brief on its scheduled day.</p>')
    parts.append('  </header>')
    parts.append('  <div class="monitor-directory">')
    for m in registry["monitors"]:
        parts.append(f"""    <article class="monitor-card-v2" data-monitor="{html.escape(m['abbr'])}" style="--card-accent: {html.escape(m['accent'])}">
      <div class="monitor-card-v2__top">
        <div class="monitor-card-v2__logo">
          <img src="{html.escape(m['svg_url'], quote=True)}" alt="" width="28" height="28" aria-hidden="true">
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:var(--space-1)">
          <span class="monitor-card-v2__abbr" style="color:{html.escape(m['accent'])}">{html.escape(m['abbr'])}</span>
          <span class="monitor-card-v2__day">{html.escape(m['publish_day'])}</span>
        </div>
      </div>
      <div>
        <h2 class="monitor-card-v2__title"><a href="{html.escape(m['url'], quote=True)}">{html.escape(m['short_name'])}</a></h2>
        <p class="monitor-card-v2__description">{html.escape(m['description'])}</p>
      </div>
      <div class="monitor-card-v2__actions">
        <a class="monitor-card-v2__btn monitor-card-v2__btn--primary" href="{html.escape(m['url'], quote=True)}">Latest issue</a>
        <a class="monitor-card-v2__btn monitor-card-v2__btn--secondary" href="{html.escape(m['url'], quote=True)}dashboard.html">Dashboard</a>
      </div>
    </article>""")
    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_section_main(section_page: Page, posts: list[Page], *, page_num: int = 1, total_pages: int = 1, base_url: str | None = None) -> str:
    """Used for monitor section pages — feed-card list with optional pagination."""
    base_url = base_url or section_page.permalink
    title = html.escape(section_page.title)
    desc = section_page.description
    publish_day = section_page.params.get("publishDay") if section_page.params else None
    # Slice for pagination
    total = len(posts)
    start = (page_num - 1) * PAGER_SIZE
    end = start + PAGER_SIZE
    page_posts = posts[start:end]

    parts = ['<main class="list">', '  <div class="container">']
    parts.append('    <header class="list__header">')
    parts.append('      <div class="topic__meta" style="margin-bottom:var(--space-4)">')
    parts.append('        <a class="topic__back" href="/monitors/">← All monitors</a>')
    if publish_day:
        parts.append(f'        <span class="topic__cadence">Publishes every {html.escape(publish_day)}</span>')
    parts.append('      </div>')
    parts.append(f'      <h1>{title}</h1>')
    if desc:
        parts.append(f'      <p class="list__description">{html.escape(desc)}</p>')
    parts.append('    </header>')

    # Dashboard redirect script (matches Hugo behaviour: section root redirects to dashboard.html
    # only on the FIRST page, since paginated sub-pages should not auto-redirect).
    if page_num == 1 and section_page.permalink.startswith("/monitors/"):
        parts.append('    <script>')
        parts.append("      window.location.replace(window.location.pathname.replace(/\\/$/, '') + '/dashboard.html');")
        parts.append('    </script>')
        parts.append('    <noscript>')
        parts.append('      <meta http-equiv="refresh" content="0; url=dashboard.html">')
        parts.append('    </noscript>')

    if page_posts:
        for post in page_posts:
            summary = post.params.get("summary") or ""
            summary_html = f'\n          <p class="feed-card__summary">{html.escape(summary)}</p>' if summary else ""
            parts.append(f"""    <article class="feed-card">
      <div class="feed-card__meta">
        <time class="feed-card__date" datetime="{post.date.strftime('%Y-%m-%d')}">{fmt_date_long(post.date)}</time>
      </div>
      <h2 class="feed-card__title">
        <a href="{post.permalink}">{html.escape(post.title)}</a>
      </h2>{summary_html}
      <a class="feed-card__read-more" href="{post.permalink}">Read briefing →</a>
    </article>""")
    else:
        parts.append('    <p style="color:var(--color-text-muted);padding-block:var(--space-8)">No briefings published yet. Check back soon.</p>')

    # Pagination links
    if total_pages > 1:
        parts.append('    <nav class="pagination" aria-label="Pagination">')
        if page_num > 1:
            prev_url = base_url if page_num == 2 else f"{base_url}page/{page_num - 1}/"
            parts.append(f'      <a class="pagination__prev" href="{prev_url}">← Newer</a>')
        parts.append(f'      <span class="pagination__current">Page {page_num} of {total_pages}</span>')
        if page_num < total_pages:
            parts.append(f'      <a class="pagination__next" href="{base_url}page/{page_num + 1}/">Older →</a>')
        parts.append('    </nav>')

    parts.append('  </div>')
    parts.append('</main>')
    return "\n".join(parts)


def render_brief_main(post: Page, ctx: dict) -> str:
    """Single brief — port of layouts/_default/single.html."""
    parent_permalink = post.parent_permalink or "/"
    parent = ctx["pages_by_url"].get(parent_permalink)
    parent_title = parent.title if parent else post.section.title()

    # NewsArticle JSON-LD
    summary = post.params.get("summary") or post.description or ""
    ld = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": post.title,
        "description": summary,
        "datePublished": fmt_iso(post.date),
        "dateModified": fmt_iso(post.lastmod),
        "url": post.absolute_url,
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "author": {"@type": "Organization", "name": "Asymmetric Intelligence", "url": "https://asym-intel.info"},
        "publisher": {
            "@type": "Organization", "name": "Asymmetric Intelligence", "url": "https://asym-intel.info",
            "logo": {"@type": "ImageObject", "url": "https://asym-intel.info/favicon-32x32.png"},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": post.absolute_url},
    }
    if parent:
        ld["isPartOf"] = {
            "@type": "Dataset",
            "name": f"{parent.title} — Asymmetric Intelligence",
            "url": parent.absolute_url,
            "description": parent.description,
            "creator": {"@type": "Person", "name": "Peter Howitt"},
            "license": "https://creativecommons.org/licenses/by/4.0/",
        }

    # Sources block
    sources = post.params.get("brief_sources") or []
    sources_html = ""
    if sources:
        rows = []
        for src in sources:
            url = src.get("url", "")
            label = src.get("label")
            if not label and url:
                m = re.match(r"https?://(?:www\.)?([^/]+)", url)
                label = m.group(1) if m else url
            tier = src.get("tier")
            tier_html = f' <span style="opacity:0.6">{html.escape(tier)}</span>' if tier else ""
            rows.append(
                f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer" '
                'style="display:inline-block;margin:2px 4px 2px 0;padding:2px 8px;border:1px solid var(--color-border-subtle,#e2e0dc);border-radius:3px;font-size:0.7rem;color:var(--color-text-secondary,#6b6459);text-decoration:none;background:var(--color-surface-raised,#f5f3f0)">'
                f'{html.escape(label or "source")} →{tier_html}</a>'
            )
        sources_html = (
            '\n      <div class="post__sources" style="margin-top:2rem;padding-top:1rem;border-top:1px solid var(--color-border-subtle,#e2e0dc)">\n'
            '        <span style="font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:var(--color-text-muted,#9e9690);margin-right:0.5rem">Sources</span>\n'
            "        " + "\n        ".join(rows) + "\n      </div>"
        )

    monitor_param = post.params.get("monitor")
    monitor_links_html = ""
    if monitor_param:
        monitor_links_html = (
            '\n      <nav class="post__monitor-links">\n'
            f'        <a href="/monitors/{html.escape(monitor_param)}/dashboard.html">View live dashboard →</a>\n'
            '      </nav>'
        )

    summary_html = f'\n      <p class="post__summary">{html.escape(summary)}</p>' if summary else ""

    parent_link_label = f"← All {parent_title} briefings"

    return f"""<script type="application/ld+json">{jsonify_safe(ld)}</script>
<main class="single">
  <article class="post">
    <header class="post__header">
      <div class="post__meta">
        <span class="post__monitor">{html.escape(parent_title)}</span>
        <time class="post__date" datetime="{post.date.strftime('%Y-%m-%d')}">{fmt_date_long(post.date)}</time>
      </div>
      <h1 class="post__title">{html.escape(post.title)}</h1>{summary_html}{monitor_links_html}
    </header>

    <div class="post__body">
{post.body_html}
    </div>{sources_html}

    <footer class="post__footer">
      <div class="post__footer-links">
        <a class="post__back" href="{parent_permalink}">{html.escape(parent_link_label)}</a>
      </div>
    </footer>
  </article>
</main>"""


def render_methodology_main(page: Page, ctx: dict) -> str:
    monitor_param = page.params.get("monitor")
    parent = None
    if monitor_param:
        parent = ctx["pages_by_url"].get(f"/monitors/{monitor_param}/")
    breadcrumb_extra = ""
    footer_back = ""
    if parent:
        breadcrumb_extra = f'<span aria-hidden="true">·</span>\n        <a href="{parent.permalink}">{html.escape(parent.title)}</a>\n        '
        footer_back = f'<a class="post__back" href="{parent.permalink}">← Back to {html.escape(parent.title)} briefings</a>'

    desc_html = f'\n        <p class="methodology-page__description">{html.escape(page.description)}</p>' if page.description else ""

    # Auto-TOC from h2
    h2s = re.findall(r"(?m)^## (.+)$", page.body_md)
    toc_html = ""
    if len(h2s) > 3:
        items = []
        for h in h2s:
            anchor = slugify_anchor(h)
            items.append(f'          <li><a href="#{anchor}">{html.escape(h)}</a></li>')
        toc_html = (
            '\n      <nav class="methodology-toc" aria-label="Table of contents">\n'
            '        <h2 class="methodology-toc__heading">Contents</h2>\n'
            '        <ol class="methodology-toc__list">\n'
            + "\n".join(items) + "\n"
            "        </ol>\n"
            "      </nav>"
        )

    dash_link = ""
    if monitor_param:
        dash_link = f'\n        <a class="methodology-page__dashboard-link" href="/monitors/{monitor_param}/dashboard.html">View live dashboard →</a>'

    ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": page.title,
        "description": page.description or "",
        "datePublished": fmt_iso(page.date),
        "dateModified": fmt_iso(page.lastmod),
        "url": page.absolute_url,
        "publisher": {"@type": "Organization", "name": "Asymmetric Intelligence", "url": "https://asym-intel.info"},
    }

    return f"""<script type="application/ld+json">{jsonify_safe(ld)}</script>

<main class="methodology-page">
  <div class="methodology-page__header">
    <div class="container">
      <div class="methodology-page__breadcrumb">
        <a href="/monitors/">Monitors</a>
        {breadcrumb_extra}<span aria-hidden="true">·</span>
        <span>Methodology</span>
      </div>
      <h1 class="methodology-page__title">{html.escape(page.title)}</h1>{desc_html}
      <div class="methodology-page__meta">
        <span>Last updated: <time datetime="{page.lastmod.strftime('%Y-%m-%d')}">{fmt_date_long(page.lastmod)}</time></span>{dash_link}
      </div>
    </div>
  </div>

  <div class="methodology-page__body">
    <div class="methodology-page__inner">{toc_html}

      <div class="methodology-body">
{page.body_html}
      </div>

      <footer class="methodology-page__footer">
        {footer_back}
      </footer>

    </div>
  </div>
</main>"""


def render_topic_main(topic: Page, ctx: dict) -> str:
    related_slug = topic.params.get("relatedMonitor")
    related_section = ctx["pages_by_url"].get(f"/monitors/{related_slug}/") if related_slug else None
    related_briefs = ctx["data"]["briefs"].get(related_slug, []) if related_slug else []
    publish_day = topic.params.get("publishDay")

    ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": topic.title,
        "description": topic.description or "",
        "dateModified": fmt_iso(topic.lastmod),
        "url": topic.absolute_url,
        "publisher": {"@type": "Organization", "name": "Asymmetric Intelligence", "url": "https://asym-intel.info"},
    }

    parts = [f'<script type="application/ld+json">{jsonify_safe(ld)}</script>',
             '<main class="topic">',
             '  <header class="topic__header">',
             '    <div class="container container--wide">',
             '      <div class="topic__meta">',
             '        <a class="topic__back" href="/topics/">← All domains</a>']
    if publish_day:
        parts.append(f'        <span class="topic__cadence">Monitor publishes every {html.escape(publish_day)}</span>')
    parts.append('      </div>')
    parts.append(f'      <h1 class="topic__title">{html.escape(topic.title)}</h1>')
    if topic.description:
        parts.append(f'      <p class="topic__description">{html.escape(topic.description)}</p>')
    parts.append('    </div>')
    parts.append('  </header>')

    parts.append('  <div class="topic__content-wrap">')
    parts.append('    <div class="container container--wide">')
    parts.append('      <div class="topic__content-grid">')

    if related_section:
        rs_desc = f'\n            <p class="topic__monitor-card-desc">{html.escape(related_section.description)}</p>' if related_section.description else ""
        parts.append(f"""        <aside class="topic__sidebar">
          <div class="topic__monitor-card">
            <div class="topic__monitor-card-label">Weekly monitor</div>
            <h2 class="topic__monitor-card-title">{html.escape(related_section.title)}</h2>{rs_desc}
            <div class="topic__monitor-card-links">
              <a class="topic__monitor-card-link" href="{related_section.permalink}">All briefings →</a>
              <a class="topic__monitor-card-link topic__monitor-card-link--secondary" href="/monitors/{related_slug}/dashboard.html">Live dashboard →</a>
            </div>
          </div>
        </aside>""")

    if topic.body_html:
        parts.append(f"""        <section class="topic__body">
          <div class="topic__prose">
{topic.body_html}
          </div>
        </section>""")

    parts.append('      </div>')
    parts.append('    </div>')
    parts.append('  </div>')

    if related_briefs:
        parts.append('  <section class="topic__feed">')
        parts.append('    <div class="container container--wide">')
        parts.append('      <h2 class="topic__feed-heading">Recent briefings</h2>')
        parts.append('      <div class="topic__feed-grid">')
        for post in related_briefs[:4]:
            summary = post.params.get("summary") or ""
            summary_html = f'\n          <p class="topic__feed-card__summary">{html.escape(summary)}</p>' if summary else ""
            parts.append(f"""        <article class="topic__feed-card">
          <time class="topic__feed-card__date" datetime="{post.date.strftime('%Y-%m-%d')}">{fmt_date_short(post.date)}</time>
          <h3 class="topic__feed-card__title">
            <a href="{post.permalink}">{html.escape(post.title)}</a>
          </h3>{summary_html}
          <a class="topic__feed-card__read" href="{post.permalink}">Read briefing →</a>
        </article>""")
        parts.append('      </div>')
        if len(related_briefs) > 4:
            parts.append(f'      <a class="topic__feed-all" href="{related_section.permalink if related_section else "#"}">All {html.escape(related_section.title) if related_section else ""} briefings →</a>')
        parts.append('    </div>')
        parts.append('  </section>')

    parts.append('</main>')
    return "\n".join(parts)


def render_topics_index_main(ctx: dict) -> str:
    """Topics index — port of layouts/topics/list.html which redirects to /."""
    return """<script>window.location.replace('/');</script>
<noscript><meta http-equiv="refresh" content="0; url=/"></noscript>
<main class="list">
  <div class="container">
    <p>Redirecting to homepage…</p>
  </div>
</main>"""


def render_static_page_main(page: Page) -> str:
    """Used for about, mission — _default/single.html behaviour for type:page."""
    ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page.title,
        "description": page.description or "",
        "url": page.absolute_url,
        "publisher": {"@type": "Organization", "name": "Asymmetric Intelligence", "url": "https://asym-intel.info"},
    }
    desc_html = f'\n      <p class="static-page__desc">{html.escape(page.description)}</p>' if page.description else ""
    body_html = f'\n    <div class="static-page__body post__body">\n{page.body_html}\n    </div>' if page.body_html else ""
    return f"""<script type="application/ld+json">{jsonify_safe(ld)}</script>
<main class="static-page">
  <div class="container">
    <header class="static-page__header">
      <h1 class="static-page__title">{html.escape(page.title)}</h1>{desc_html}
    </header>{body_html}
  </div>
</main>"""


def render_404_main() -> str:
    return """<section class="error-404">
  <div class="container">
    <p class="error-404__code">404</p>
    <h1 class="error-404__title">This page has moved or no longer exists.</h1>
    <p class="error-404__body">
      The monitor or briefing you were looking for may have been restructured.
      Use the links below to find what you need.
    </p>
    <nav class="error-404__nav">
      <a class="error-404__link" href="/monitors/">All monitors →</a>
      <a class="error-404__link" href="/topics/">Topics →</a>
      <a class="error-404__link" href="/">Home →</a>
    </nav>
  </div>
</section>"""


def render_search_main() -> str:
    """Verbatim port of layouts/search/single.html main content (the page is mostly client-side JS)."""
    return r"""<style>
.search-page{max-width:720px;margin:0 auto;padding:3rem 1.5rem 6rem}
.search-page__eyebrow{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--color-text-muted,#6b7280);margin-bottom:.5rem}
.search-page__title{font-size:1.75rem;font-weight:700;letter-spacing:-.025em;font-family:var(--font-body,'Satoshi',sans-serif);color:var(--color-text,#111827);margin-bottom:.375rem;line-height:1.2}
.search-page__desc{font-size:1rem;color:var(--color-text-secondary,#4b5563);margin-bottom:2rem}
.search-input-el{width:100%;padding:.75rem 1rem;font-family:inherit;font-size:1rem;background:var(--color-surface,#fff);border:1.5px solid var(--color-border,#e5e7eb);border-radius:8px;color:var(--color-text,#111827);outline:none;transition:border-color .15s,box-shadow .15s;box-sizing:border-box;margin-bottom:1rem}
.search-input-el:focus{border-color:var(--color-primary,#2563eb);box-shadow:0 0 0 3px rgba(37,99,235,.08)}
.search-input-el::placeholder{color:var(--color-text-faint,#9ca3af)}
.search-filter-bar{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1.5rem}
.search-filter-btn{padding:.3rem .85rem;font-size:.8rem;font-weight:600;border-radius:999px;border:1.5px solid var(--color-border,#e5e7eb);background:transparent;color:var(--color-text-secondary,#4b5563);cursor:pointer;transition:background .12s,color .12s,border-color .12s;white-space:nowrap;font-family:var(--font-body,'Satoshi',sans-serif)}
.search-filter-btn:hover{background:var(--color-surface-raised,#f9fafb)}
.search-filter-btn.active{background:var(--color-text,#111827);color:#fff;border-color:var(--color-text,#111827)}
.search-filter-btn[data-monitor=democratic-integrity].active{background:#61a5d2;border-color:#61a5d2}
.search-filter-btn[data-monitor=macro-monitor].active{background:#22a0aa;border-color:#22a0aa}
.search-filter-btn[data-monitor=fimi-cognitive-warfare].active{background:#38bdf8;border-color:#38bdf8}
.search-filter-btn[data-monitor=european-strategic-autonomy].active{background:#5b8db0;border-color:#5b8db0}
.search-filter-btn[data-monitor=ai-governance].active{background:#3a7d5a;border-color:#3a7d5a}
.search-filter-btn[data-monitor=environmental-risks].active{background:#4caf7d;border-color:#4caf7d}
.search-filter-btn[data-monitor=conflict-escalation].active{background:#dc2626;border-color:#dc2626}
.search-status{font-size:.8125rem;color:var(--color-text-muted,#6b7280);margin-bottom:1.5rem;min-height:1.25rem}
.search-result{padding:1.25rem 0;border-bottom:1px solid var(--color-border,#e5e7eb)}
.search-result:last-child{border-bottom:none}
.search-result__header{display:flex;align-items:center;gap:.5rem;margin-bottom:.35rem;flex-wrap:wrap}
.search-result__monitor-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.search-result__monitor-label{font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.search-result__issue{font-size:.75rem;color:var(--color-text-faint,#9ca3af)}
.search-result__body{font-size:.9375rem;color:var(--color-text-secondary,#4b5563);line-height:1.6;margin-bottom:.5rem}
.search-result__body mark{background:rgba(37,99,235,.12);color:inherit;border-radius:2px;padding:0 2px}
.search-result__link{font-size:.8125rem;font-weight:600;color:var(--color-primary,#2563eb);text-decoration:none}
.search-result__link:hover{text-decoration:underline}
.search-empty{padding:3rem 0;font-size:.9375rem;color:var(--color-text-muted,#6b7280);text-align:center}
</style>

<div class="search-page">
  <div class="search-page__eyebrow">Asymmetric Intelligence</div>
  <h1 class="search-page__title">Search all monitors</h1>
  <p class="search-page__desc">Full-text search across all published briefs from all seven monitors.</p>

  <input type="search" class="search-input-el" id="search-input"
    placeholder="Search across all monitors and issues…" autocomplete="off" spellcheck="false">

  <div class="search-filter-bar" id="filter-bar">
    <button class="search-filter-btn active" data-monitor="all">All monitors</button>
    <button class="search-filter-btn" data-monitor="democratic-integrity">WDM</button>
    <button class="search-filter-btn" data-monitor="macro-monitor">GMM</button>
    <button class="search-filter-btn" data-monitor="fimi-cognitive-warfare">FCW</button>
    <button class="search-filter-btn" data-monitor="european-strategic-autonomy">ESA</button>
    <button class="search-filter-btn" data-monitor="ai-governance">AGM</button>
    <button class="search-filter-btn" data-monitor="environmental-risks">ERM</button>
    <button class="search-filter-btn" data-monitor="conflict-escalation">SCEM</button>
  </div>

  <div class="search-status" id="search-status">Loading corpus…</div>
  <div id="search-results"></div>
</div>

<script>
(function(){
  var MONITORS=[
    {slug:'democratic-integrity',abbr:'WDM',label:'World Democracy Monitor',accent:'#61a5d2'},
    {slug:'macro-monitor',abbr:'GMM',label:'Global Macro Monitor',accent:'#22a0aa'},
    {slug:'fimi-cognitive-warfare',abbr:'FCW',label:'FIMI & Cognitive Warfare Monitor',accent:'#38bdf8'},
    {slug:'european-strategic-autonomy',abbr:'ESA',label:'European Strategic Autonomy Monitor',accent:'#5b8db0'},
    {slug:'ai-governance',abbr:'AGM',label:'Artificial Intelligence Monitor',accent:'#3a7d5a'},
    {slug:'environmental-risks',abbr:'ERM',label:'Environmental Risks Monitor',accent:'#4caf7d'},
    {slug:'conflict-escalation',abbr:'SCEM',label:'Strategic Conflict & Escalation',accent:'#dc2626'}
  ];
  var BASE='https://asym-intel.info/monitors/';
  var corpus=[],loaded=false,activeFilter='all';
  function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function highlight(t,q){return esc(t).replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi'),'<mark>$1</mark>');}
  function flatten(obj,meta,items){
    if(!obj||typeof obj!=='object')return;
    if(Array.isArray(obj)){obj.forEach(function(i){flatten(i,meta,items);});return;}
    var t='';
    ['title','headline','summary','body','detail','note','signal','significance','description','asymmetric','linkage','one_line','analysis'].forEach(function(k){if(obj[k]&&typeof obj[k]==='string')t+=' '+obj[k];});
    if(t.trim())items.push({text:t.trim(),meta:meta});
    Object.keys(obj).forEach(function(k){if(typeof obj[k]==='object')flatten(obj[k],meta,items);});
  }
  var statusEl=document.getElementById('search-status'),done=0;
  function chatterDates(){
    var dates=[],d=new Date();
    for(var i=0;i<182;i++){dates.push(d.toISOString().slice(0,10));d.setDate(d.getDate()-1);}
    return dates;
  }
  var reportPromise=Promise.all(MONITORS.map(function(mon){
    return fetch(BASE+mon.slug+'/data/archive.json').then(function(r){return r.ok?r.json():[];})
    .then(function(issues){
      issues=Array.isArray(issues)?issues:[];
      return Promise.all(issues.map(function(issue){
        var sl=issue.slug||issue.published||'';
        var meta={monitorSlug:mon.slug,monitorAbbr:mon.abbr,monitorLabel:mon.label,monitorAccent:mon.accent,
                  type:'report',issue:sl,published:issue.published||'',
                  url:BASE+mon.slug+'/'+sl+'-weekly-brief/'};
        return fetch(BASE+mon.slug+'/data/report-'+sl+'.json').then(function(r){return r.ok?r.json():null;})
        .then(function(d){if(d)flatten(d,meta,corpus);}).catch(function(){});
      }));
    }).then(function(){done++;if(statusEl)statusEl.textContent='Loading '+done+'/'+MONITORS.length+' monitors…';}).catch(function(){done++;});
  }));
  var chatterPromise=Promise.all(MONITORS.map(function(mon){
    return fetch(BASE+mon.slug+'/data/chatter-index.json').then(function(r){return r.ok?r.json():null;})
    .then(function(idx){
      var dates=idx?idx.dates:chatterDates();
      var seen={};
      return Promise.all(dates.map(function(date){
        var url=BASE+mon.slug+'/data/chatter-'+date+'.json';
        if(seen[url])return Promise.resolve();
        seen[url]=true;
        var meta={monitorSlug:mon.slug,monitorAbbr:mon.abbr,monitorLabel:mon.label,monitorAccent:mon.accent,
                  type:'chatter',issue:date,published:date,
                  url:BASE+mon.slug+'/chatter.html'};
        return fetch(url).then(function(r){return r.ok?r.json():null;})
        .then(function(d){if(d)flatten(d,meta,corpus);}).catch(function(){});
      }));
    }).catch(function(){});
  }));
  Promise.all([reportPromise,chatterPromise]).then(function(){
    loaded=true;
    if(statusEl)statusEl.textContent=corpus.length+' searchable items loaded across all monitors and chatter.';
    var q=document.getElementById('search-input').value;
    if(q.trim())doSearch(q);
  });
  function doSearch(q){
    var el=document.getElementById('search-results');
    q=q.trim();
    if(!q){el.innerHTML='';if(statusEl&&loaded)statusEl.textContent=corpus.length+' searchable items loaded across all monitors.';return;}
    if(!loaded){if(statusEl)statusEl.textContent='Loading corpus…';return;}
    var lower=q.toLowerCase();
    var matches=corpus.filter(function(item){
      if(activeFilter!=='all'&&item.meta.monitorSlug!==activeFilter)return false;
      return item.text.toLowerCase().indexOf(lower)>-1;
    });
    var seen={},deduped=[];
    matches.forEach(function(m){var k=m.meta.monitorSlug+'|'+m.meta.issue+'|'+m.text.slice(0,100);if(!seen[k]){seen[k]=true;deduped.push(m);}});
    if(statusEl)statusEl.textContent=deduped.length?deduped.length+' result'+(deduped.length!==1?'s':'')+' for "'+esc(q)+'"':'No results for "'+esc(q)+'"';
    if(!deduped.length){el.innerHTML='<div class="search-empty">No results found.</div>';return;}
    el.innerHTML=deduped.slice(0,50).map(function(item){
      var m=item.meta,preview=item.text.length>220?item.text.slice(0,220)+'…':item.text;
      var typeTag=m.type==='chatter'?'<span style="font-size:.7rem;background:var(--color-surface-raised,#f3f4f6);color:var(--color-text-muted,#6b7280);padding:1px 5px;border-radius:3px;margin-left:4px">Chatter</span>':'';
      var linkLabel=m.type==='chatter'?'View chatter →':'View brief →';
      return '<div class="search-result"><div class="search-result__header"><span class="search-result__monitor-dot" style="background:'+esc(m.monitorAccent)+'"></span><span class="search-result__monitor-label" style="color:'+esc(m.monitorAccent)+'">'+esc(m.monitorAbbr)+'</span><span class="search-result__issue">'+esc(m.monitorLabel)+(m.published?' · '+esc(m.published):'')+typeTag+'</span></div><div class="search-result__body">'+highlight(preview,q)+'</div><a class="search-result__link" href="'+esc(m.url)+'">'+linkLabel+'</a></div>';
    }).join('');
  }
  document.getElementById('filter-bar').addEventListener('click',function(e){
    var btn=e.target.closest('.search-filter-btn');if(!btn)return;
    document.querySelectorAll('.search-filter-btn').forEach(function(b){b.classList.remove('active');});
    btn.classList.add('active');activeFilter=btn.getAttribute('data-monitor');
    doSearch(document.getElementById('search-input').value);
  });
  var timer;
  document.getElementById('search-input').addEventListener('input',function(){clearTimeout(timer);var val=this.value;timer=setTimeout(function(){doSearch(val);},200);});
  document.getElementById('search-input').focus();
})();
</script>"""


def render_subscribe_main() -> str:
    """Verbatim port of layouts/subscribe/single.html main content."""
    # The subscribe page is a static form with hardcoded SVG glyphs per monitor.
    # We reproduce the form verbatim from the layout.
    return r"""<main class="subscribe-page">
  <div class="container">
    <header class="subscribe-page__header">
      <h1 class="subscribe-page__title">Subscribe</h1>
      <p class="subscribe-page__desc">
        Choose the monitors you want to follow. One briefing per monitor, per week.
        All free. Unsubscribe from any at any time.
      </p>
    </header>

    <form
      action="https://buttondown.com/api/emails/embed-subscribe/asym-intel"
      method="post"
      class="subscribe-form"
      target="popupwindow"
      onsubmit="window.open('https://buttondown.com/asym-intel','popupwindow')"
    >

      <div class="subscribe-form__monitors">

        <label class="subscribe-monitor-card" for="monitor-esa">
          <div class="subscribe-monitor-card__check">
            <input type="checkbox" id="monitor-esa" name="tag" value="monitor:european-strategic-autonomy">
            <span class="subscribe-monitor-card__checkmark"></span>
          </div>
          <div class="subscribe-monitor-card__logo" aria-hidden="true" style="background:#0f172a">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 36 36" fill="none"><polygon points="18,2 32,10 32,26 18,34 4,26 4,10" stroke="#5b8db0" stroke-width="1.5" fill="none"/><polygon points="18,7 27,12 27,24 18,29 9,24 9,12" stroke="#4a7fa0" stroke-width="1" fill="none"/><polygon points="18,11 24,14.5 24,21.5 18,25 12,21.5 12,14.5" stroke="#3d6f8e" stroke-width="1" fill="none"/><line x1="18" y1="2" x2="18" y2="34" stroke="#4a7fa0" stroke-width="0.7"/><line x1="4" y1="10" x2="32" y2="26" stroke="#4a7fa0" stroke-width="0.7"/><line x1="4" y1="26" x2="32" y2="10" stroke="#4a7fa0" stroke-width="0.7"/><circle cx="18" cy="18" r="2.5" fill="#6488ac"/></svg>
          </div>
          <div class="subscribe-monitor-card__body">
            <span class="subscribe-monitor-card__name">European Strategic Autonomy</span>
            <span class="subscribe-monitor-card__meta">Wednesday · Hybrid threats, European defence, strategic independence</span>
          </div>
        </label>

        <label class="subscribe-monitor-card" for="monitor-wdm">
          <div class="subscribe-monitor-card__check">
            <input type="checkbox" id="monitor-wdm" name="tag" value="monitor:democratic-integrity">
            <span class="subscribe-monitor-card__checkmark"></span>
          </div>
          <div class="subscribe-monitor-card__logo" aria-hidden="true" style="background:#0f172a">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="13" stroke="#61a5d2" stroke-width="1.5" fill="none"/><ellipse cx="16" cy="16" rx="13" ry="5" stroke="#61a5d2" stroke-width="1" fill="none"/><ellipse cx="16" cy="16" rx="13" ry="9" stroke="#61a5d2" stroke-width="1" fill="none"/><ellipse cx="16" cy="16" rx="5" ry="13" stroke="#61a5d2" stroke-width="1" fill="none"/><line x1="3" y1="16" x2="29" y2="16" stroke="#61a5d2" stroke-width="1"/><line x1="16" y1="3" x2="16" y2="29" stroke="#61a5d2" stroke-width="1"/></svg>
          </div>
          <div class="subscribe-monitor-card__body">
            <span class="subscribe-monitor-card__name">Democratic Integrity</span>
            <span class="subscribe-monitor-card__meta">Tuesday · Democratic erosion, resilience, and state capture</span>
          </div>
        </label>

        <label class="subscribe-monitor-card" for="monitor-macro">
          <div class="subscribe-monitor-card__check">
            <input type="checkbox" id="monitor-macro" name="tag" value="monitor:macro-monitor">
            <span class="subscribe-monitor-card__checkmark"></span>
          </div>
          <div class="subscribe-monitor-card__logo" aria-hidden="true" style="background:#0f172a">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 38 38" fill="none"><rect x="2" y="2" width="34" height="34" rx="6" stroke="#22a0aa" stroke-width="2" fill="none"/><circle cx="12" cy="10" r="2.5" fill="#e87040"/><line x1="12" y1="12.5" x2="12" y2="18" stroke="#e87040" stroke-width="1.5"/><line x1="8" y1="15" x2="16" y2="15" stroke="#e87040" stroke-width="1.5"/><line x1="12" y1="18" x2="9" y2="22" stroke="#e87040" stroke-width="1.5"/><line x1="12" y1="18" x2="15" y2="22" stroke="#e87040" stroke-width="1.5"/><polyline points="5,30 10,30 13,24 17,33 21,26 25,33 29,22 33,30" stroke="#e87040" stroke-width="2" fill="none" stroke-linejoin="round"/></svg>
          </div>
          <div class="subscribe-monitor-card__body">
            <span class="subscribe-monitor-card__name">Global Macro</span>
            <span class="subscribe-monitor-card__meta">Monday · Financial crisis early-warning, debt, credit, systemic risk</span>
          </div>
        </label>

        <label class="subscribe-monitor-card" for="monitor-ai">
          <div class="subscribe-monitor-card__check">
            <input type="checkbox" id="monitor-ai" name="tag" value="monitor:ai-governance">
            <span class="subscribe-monitor-card__checkmark"></span>
          </div>
          <div class="subscribe-monitor-card__logo" aria-hidden="true" style="background:#0f172a">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 36 36" fill="none"><rect x="3" y="3" width="30" height="30" rx="3" stroke="#3a7d5a" stroke-width="1.5" fill="none"/><rect x="8" y="8" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.9"/><rect x="20" y="8" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.6"/><rect x="8" y="20" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.6"/><rect x="20" y="20" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.3"/><line x1="12" y1="16" x2="12" y2="20" stroke="#3a7d5a" stroke-width="1.5"/><line x1="24" y1="16" x2="24" y2="20" stroke="#3a7d5a" stroke-width="1.5"/><line x1="16" y1="12" x2="20" y2="12" stroke="#3a7d5a" stroke-width="1.5"/></svg>
          </div>
          <div class="subscribe-monitor-card__body">
            <span class="subscribe-monitor-card__name">AI Governance</span>
            <span class="subscribe-monitor-card__meta">Friday · AI capability, regulatory frameworks, governance contest</span>
          </div>
        </label>

        <label class="subscribe-monitor-card" for="monitor-fimi">
          <div class="subscribe-monitor-card__check">
            <input type="checkbox" id="monitor-fimi" name="tag" value="monitor:fimi-cognitive-warfare">
            <span class="subscribe-monitor-card__checkmark"></span>
          </div>
          <div class="subscribe-monitor-card__logo" aria-hidden="true" style="background:#0f172a">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 36 36" fill="none"><circle cx="18" cy="18" r="14" stroke="#38bdf8" stroke-width="1.5" fill="none"/><circle cx="18" cy="18" r="9" stroke="#38bdf8" stroke-width="1" fill="none" opacity="0.6"/><circle cx="18" cy="18" r="4" stroke="#38bdf8" stroke-width="1" fill="none" opacity="0.35"/><line x1="18" y1="4" x2="18" y2="32" stroke="#38bdf8" stroke-width="0.75" opacity="0.4"/><line x1="4" y1="18" x2="32" y2="18" stroke="#38bdf8" stroke-width="0.75" opacity="0.4"/><circle cx="18" cy="18" r="2" fill="#dc2626"/><circle cx="26" cy="10" r="1.5" fill="#dc2626" opacity="0.8"/><circle cx="10" cy="24" r="1" fill="#38bdf8" opacity="0.9"/></svg>
          </div>
          <div class="subscribe-monitor-card__body">
            <span class="subscribe-monitor-card__name">FIMI & Cognitive Warfare</span>
            <span class="subscribe-monitor-card__meta">Thursday · Foreign information manipulation, influence operations</span>
          </div>
        </label>

        <label class="subscribe-monitor-card" for="monitor-gerp">
          <div class="subscribe-monitor-card__check">
            <input type="checkbox" id="monitor-gerp" name="tag" value="monitor:environmental-risks">
            <span class="subscribe-monitor-card__checkmark"></span>
          </div>
          <div class="subscribe-monitor-card__logo" aria-hidden="true" style="background:#0f172a">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 36 36" fill="none"><circle cx="18" cy="18" r="14" stroke="#4caf7d" stroke-width="1.5" fill="none"/><circle cx="18" cy="18" r="9" stroke="#4caf7d" stroke-width="1" fill="none" opacity="0.5"/><path d="M18 4 Q22 10 18 18 Q14 26 18 32" stroke="#4caf7d" stroke-width="1" fill="none" opacity="0.6"/><path d="M4 18 Q10 14 18 18 Q26 22 32 18" stroke="#4caf7d" stroke-width="1" fill="none" opacity="0.6"/><circle cx="18" cy="18" r="2.5" fill="#4caf7d" opacity="0.9"/><circle cx="12" cy="11" r="1.2" fill="#4caf7d" opacity="0.6"/><circle cx="25" cy="13" r="1" fill="#4caf7d" opacity="0.4"/><circle cx="11" cy="24" r="0.9" fill="#4caf7d" opacity="0.5"/></svg>
          </div>
          <div class="subscribe-monitor-card__body">
            <span class="subscribe-monitor-card__name">Environmental Risks & Planetary Boundaries</span>
            <span class="subscribe-monitor-card__meta">Saturday · Earth system risk, tipping points, geopolitical cascades</span>
          </div>
        </label>

        <label class="subscribe-monitor-card" for="monitor-conflict">
          <div class="subscribe-monitor-card__check">
            <input type="checkbox" id="monitor-conflict" name="tag" value="monitor:conflict-escalation">
            <span class="subscribe-monitor-card__checkmark"></span>
          </div>
          <div class="subscribe-monitor-card__logo" aria-hidden="true" style="background:#0f172a">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 36 36" fill="none"><line x1="6" y1="30" x2="30" y2="6" stroke="#dc2626" stroke-width="1.8" stroke-linecap="round"/><line x1="6" y1="6" x2="30" y2="30" stroke="#dc2626" stroke-width="1.8" stroke-linecap="round"/><circle cx="18" cy="18" r="3" fill="#dc2626" opacity="0.9"/><polyline points="22,6 30,6 30,14" stroke="#dc2626" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><polyline points="6,22 6,30 14,30" stroke="#dc2626" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <div class="subscribe-monitor-card__body">
            <span class="subscribe-monitor-card__name">Strategic Conflict & Escalation</span>
            <span class="subscribe-monitor-card__meta">Sunday · Armed conflict trajectories, military escalation risks</span>
          </div>
        </label>

      </div>

      <div class="subscribe-form__footer">
        <div class="subscribe-form__email-row">
          <label class="subscribe-form__email-label" for="subscribe-email">Email address</label>
          <div class="subscribe-form__email-wrap">
            <input
              type="email"
              id="subscribe-email"
              name="email"
              placeholder="you@example.com"
              required
              class="subscribe-form__email-input"
            >
            <input type="hidden" value="1" name="embed">
            <button type="submit" class="subscribe-form__submit">Subscribe</button>
          </div>
        </div>
        <p class="subscribe-form__note">
          You will receive a confirmation email. Select at least one monitor above before subscribing.
          Published by <a href="/about/">Asymmetric Intelligence</a> via Buttondown.
        </p>
      </div>

    </form>

  </div>
</main>"""


# ─────────────────────────────────────────────────────────────────────────────
# RSS / Sitemap
# ─────────────────────────────────────────────────────────────────────────────


def render_rss(*, title: str, link: str, description: str, items: list[Page]) -> str:
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    item_xml = []
    for p in items[:50]:
        pub_date = p.date.strftime("%a, %d %b %Y %H:%M:%S +0000")
        summary = p.params.get("summary") or p.description or ""
        item_xml.append(f"""    <item>
      <title>{xml_escape(p.title)}</title>
      <link>{xml_escape(p.absolute_url)}</link>
      <pubDate>{pub_date}</pubDate>
      <guid>{xml_escape(p.absolute_url)}</guid>
      <description>{xml_escape(summary)}</description>
    </item>""")
    items_str = "\n".join(item_xml)
    return f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{xml_escape(title)}</title>
    <link>{xml_escape(link)}</link>
    <description>{xml_escape(description)}</description>
    <language>en-gb</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{xml_escape(link.rstrip('/') + '/index.xml')}" rel="self" type="application/rss+xml" />
{items_str}
  </channel>
</rss>
"""


def render_sitemap(pages: list[Page]) -> str:
    rows = []
    seen = set()
    for p in pages:
        if p.sitemap_disabled:
            continue
        if p.permalink in seen:
            continue
        seen.add(p.permalink)
        lastmod = fmt_iso(p.lastmod) if p.lastmod else None
        lm_line = f"\n    <lastmod>{lastmod}</lastmod>" if lastmod else ""
        rows.append(f"""  <url>
    <loc>{xml_escape(p.absolute_url)}</loc>{lm_line}
    <changefreq>{SITEMAP_CHANGEFREQ}</changefreq>
    <priority>{SITEMAP_PRIORITY}</priority>
  </url>""")
    return f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(rows)}
</urlset>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Main build
# ─────────────────────────────────────────────────────────────────────────────


def build(source_root: Path, output_root: Path) -> None:
    print(f"build_site.py — source={source_root} output={output_root}")
    data = load_content(source_root)
    css_cache_buster = get_git_short_sha(source_root)
    now_year = datetime.now(timezone.utc).year

    # ── pages_by_url for cross-references (parent lookups) ────────────────────
    pages_by_url: dict[str, Page] = {}
    pages_by_url["/"] = data["home_index"]
    pages_by_url["/monitors/"] = data["monitors_index"]
    for slug, sec in data["sections"].items():
        pages_by_url[sec.permalink] = sec
    for sp in data["static_pages"].values():
        pages_by_url[sp.permalink] = sp
    pages_by_url["/topics/"] = data["topics_index"]

    ctx = {
        "site": {"title": SITE_TITLE, "description": SITE_DESCRIPTION},
        "data": data,
        "pages_by_url": pages_by_url,
        "now_year": now_year,
    }

    output_root.mkdir(parents=True, exist_ok=True)

    # ── CSS copy with cache-buster source name preserved ──────────────────────
    css_src = source_root / "assets" / "css" / "main.css"
    css_dst = output_root / "css" / "main.css"
    if css_src.exists():
        css_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(css_src, css_dst)
        print(f"  copied {css_src} -> {css_dst}")

    # ── Static assets pass-through (assets/monitors/ etc) ─────────────────────
    # Only the registry JSON is consumed at build; the SVG icons/logos are
    # already published via static/ → docs/ from other pipeline tooling. We
    # do NOT copy assets/monitors/ because Hugo did not either.

    # ── Track sitemap-eligible pages ──────────────────────────────────────────
    sitemap_pages: list[Page] = []
    sitemap_pages.append(data["home_index"])

    # ── Homepage ──────────────────────────────────────────────────────────────
    home_main = render_homepage_main(ctx)
    home_html = render_shell(
        data["home_index"], main_html=home_main, ctx=ctx,
        css_cache_buster=css_cache_buster,
        alt_outputs=[("alternate", "application/rss+xml", "/index.xml", SITE_TITLE)],
    )
    write_file(output_root / "index.html", home_html)
    print("  wrote /index.html")

    # ── Static pages (about / mission / commercial / search / subscribe) ─────
    for name, p in data["static_pages"].items():
        if name == "search":
            main_html = render_search_main()
        elif name == "subscribe":
            main_html = render_subscribe_main()
        else:
            main_html = render_static_page_main(p)
        out = output_root / name / "index.html"
        write_file(out, render_shell(p, main_html=main_html, ctx=ctx, css_cache_buster=css_cache_buster))
        print(f"  wrote /{name}/index.html")
        sitemap_pages.append(p)

    # ── Monitors index ────────────────────────────────────────────────────────
    mon_idx = data["monitors_index"]
    write_file(
        output_root / "monitors" / "index.html",
        render_shell(mon_idx, main_html=render_monitors_index_main(ctx), ctx=ctx, css_cache_buster=css_cache_buster),
    )
    print("  wrote /monitors/index.html")
    sitemap_pages.append(mon_idx)

    # ── Per-monitor sections + briefs + methodology + RSS + pagination ───────
    all_briefs_flat: list[Page] = []
    for slug, briefs_list in data["briefs"].items():
        section = data["sections"].get(slug)
        if not section:
            # Skip if no _index.md was provided
            continue

        sitemap_pages.append(section)
        all_briefs_flat.extend(briefs_list)

        # Section index — page 1 (with dashboard.html redirect)
        total = len(briefs_list)
        total_pages = max(1, (total + PAGER_SIZE - 1) // PAGER_SIZE)

        # Section needs RSS link in head
        rss_alt = [("alternate", "application/rss+xml", f"/monitors/{slug}/index.xml", section.title)]

        section_main = render_section_main(section, briefs_list, page_num=1, total_pages=total_pages,
                                           base_url=section.permalink)
        write_file(
            output_root / "monitors" / slug / "index.html",
            render_shell(section, main_html=section_main, ctx=ctx, css_cache_buster=css_cache_buster, alt_outputs=rss_alt),
        )
        print(f"  wrote /monitors/{slug}/index.html ({total} briefs, {total_pages} page(s))")

        # Paginated subpages
        for n in range(2, total_pages + 1):
            sub_main = render_section_main(section, briefs_list, page_num=n, total_pages=total_pages,
                                           base_url=section.permalink)
            sub_page = Page(
                kind="section",
                source_path=section.source_path,
                permalink=f"/monitors/{slug}/page/{n}/",
                title=section.title,
                description=section.description,
                params=section.params,
                section="monitors",
                parent_permalink="/monitors/",
                date=section.date,
                lastmod=section.lastmod,
            )
            write_file(
                output_root / "monitors" / slug / "page" / str(n) / "index.html",
                render_shell(sub_page, main_html=sub_main, ctx=ctx, css_cache_buster=css_cache_buster, alt_outputs=rss_alt),
            )

        # Section RSS
        rss_xml = render_rss(
            title=f"{section.title} on {SITE_TITLE}",
            link=f"{BASE_URL}/monitors/{slug}/",
            description=section.description or "",
            items=briefs_list,
        )
        write_file(output_root / "monitors" / slug / "index.xml", rss_xml)

        # Briefs
        for post in briefs_list:
            out_path = output_root / "monitors" / slug / post.permalink.strip("/").split("/")[-1] / "index.html"
            write_file(
                out_path,
                render_shell(post, main_html=render_brief_main(post, ctx), ctx=ctx, css_cache_buster=css_cache_buster),
            )
            sitemap_pages.append(post)

        # Methodology
        method = data["methodology"].get(slug)
        if method:
            write_file(
                output_root / "monitors" / slug / "methodology" / "index.html",
                render_shell(method, main_html=render_methodology_main(method, ctx), ctx=ctx, css_cache_buster=css_cache_buster),
            )
            sitemap_pages.append(method)

    # ── Topics ────────────────────────────────────────────────────────────────
    topics = data["topics"]
    topics_index = data["topics_index"]
    sitemap_pages.append(topics_index)
    # Topics index uses redirect-to-home behaviour (matches Hugo).
    topics_idx_main = render_topics_index_main(ctx)
    write_file(
        output_root / "topics" / "index.html",
        render_shell(topics_index, main_html=topics_idx_main, ctx=ctx, css_cache_buster=css_cache_buster,
                     alt_outputs=[("alternate", "application/rss+xml", "/topics/index.xml", "Topics on " + SITE_TITLE)]),
    )

    # Topic singles
    for topic in topics:
        write_file(
            output_root / "topics" / topic.permalink.strip("/").split("/")[-1] / "index.html",
            render_shell(topic, main_html=render_topic_main(topic, ctx), ctx=ctx, css_cache_buster=css_cache_buster),
        )
        sitemap_pages.append(topic)

    # Topics RSS
    topics_rss = render_rss(
        title=f"Topics on {SITE_TITLE}",
        link=f"{BASE_URL}/topics/",
        description=topics_index.description or "",
        items=topics,
    )
    write_file(output_root / "topics" / "index.xml", topics_rss)

    # ── Tags taxonomy (auto from `tag` front matter) ──────────────────────────
    tagged_pages = [p for p in all_briefs_flat + topics if p.tags]
    tag_to_pages: dict[str, list[Page]] = defaultdict(list)
    for p in tagged_pages:
        for tag in p.tags:
            tag_to_pages[tag].append(p)
    if tag_to_pages:
        # Tags index
        tag_index_page = Page(
            kind="taxonomy", source_path=None, permalink="/tags/",
            title="Tags", description="All tags",
            section="tags", lastmod=datetime.now(timezone.utc),
        )
        rows = ['<main class="list">', '  <div class="container">', '    <h1>Tags</h1>', '    <ul class="tag-list">']
        for tag in sorted(tag_to_pages.keys()):
            rows.append(f'      <li><a href="/tags/{slugify_anchor(tag)}/">{html.escape(tag)}</a> ({len(tag_to_pages[tag])})</li>')
        rows += ['    </ul>', '  </div>', '</main>']
        write_file(
            output_root / "tags" / "index.html",
            render_shell(tag_index_page, main_html="\n".join(rows), ctx=ctx, css_cache_buster=css_cache_buster),
        )
        sitemap_pages.append(tag_index_page)

        # Per-tag pages
        for tag, plist in tag_to_pages.items():
            tag_slug = slugify_anchor(tag)
            tp = Page(
                kind="term", source_path=None, permalink=f"/tags/{tag_slug}/",
                title=tag, description=f"Pages tagged '{tag}'",
                section="tags", parent_permalink="/tags/",
                lastmod=datetime.now(timezone.utc),
            )
            posts_sorted = sorted(plist, key=lambda x: x.date, reverse=True)
            section_html = render_section_main(tp, posts_sorted, page_num=1, total_pages=1)
            write_file(
                output_root / "tags" / tag_slug / "index.html",
                render_shell(tp, main_html=section_html, ctx=ctx, css_cache_buster=css_cache_buster),
            )
            sitemap_pages.append(tp)

        # Tags RSS
        all_tagged_sorted = sorted(tagged_pages, key=lambda x: x.date, reverse=True)
        write_file(
            output_root / "tags" / "index.xml",
            render_rss(title=f"Tags on {SITE_TITLE}", link=f"{BASE_URL}/tags/",
                       description="All tagged content", items=all_tagged_sorted),
        )

    # ── Home RSS feed (all briefs across monitors) ────────────────────────────
    home_rss_items = sorted(all_briefs_flat, key=lambda x: x.date, reverse=True)
    write_file(
        output_root / "index.xml",
        render_rss(title=SITE_TITLE, link=BASE_URL + "/", description=SITE_DESCRIPTION, items=home_rss_items),
    )
    print("  wrote /index.xml")

    # ── 404 ───────────────────────────────────────────────────────────────────
    page_404 = Page(
        kind="single", source_path=None, permalink="/404.html",
        title="Not Found", description="Page not found",
        no_index=True,
    )
    write_file(
        output_root / "404.html",
        render_shell(page_404, main_html=render_404_main(), ctx=ctx, css_cache_buster=css_cache_buster),
    )
    print("  wrote /404.html")

    # ── Sitemap ───────────────────────────────────────────────────────────────
    write_file(output_root / "sitemap.xml", render_sitemap(sitemap_pages))
    print(f"  wrote /sitemap.xml ({len(sitemap_pages)} URLs)")

    print("done.")


def main() -> int:
    parser = argparse.ArgumentParser(description="asym-intel.info static site generator")
    parser.add_argument("--source", type=Path, default=Path.cwd(),
                        help="Source repo root (default: cwd)")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output directory (default: <source>/docs)")
    args = parser.parse_args()
    source_root = args.source.resolve()
    output_root = (args.output or (source_root / "docs")).resolve()
    if not (source_root / "content").is_dir():
        print(f"error: no content/ dir at {source_root}", file=sys.stderr)
        return 2
    build(source_root, output_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())

