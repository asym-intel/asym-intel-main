# Shared Monitor Design System — Component Inventory

Canonical list of shared-layer primitives that live under
`static/monitors/shared/`. Each row points at its source files and the
BRIEF that authorised it. Primitives in this inventory are the only
files that define a given visual contract; per-consumer variation is
expressed through descriptor data and `data-*` hooks, never by
redefining the primitive's classes downstream.

| Primitive       | CSS                                  | JS                                   | Demo / Template                                 | Authored by                                     |
|-----------------|--------------------------------------|--------------------------------------|-------------------------------------------------|-------------------------------------------------|
| freshness-badge | `css/freshness-badge.css`            | `js/freshness-badge.js`              | `demos/freshness-badge.html`                    | BRIEF-FE-FRESHNESS-BADGE-PRIMITIVE              |
| chip-filter     | `css/chip-filter.css`                | `js/chip-filter.js`                  | `demos/chip-filter.html`                        | BRIEF-FE-DEMO-SUBSTANCE-UNIFICATION             |
| typography-floor| (tokens in `css/base.css` v1.8+)     | —                                    | `demos/typography-floor.html`                   | BRIEF-FE-TYPOGRAPHY-FLOOR                       |
| entity-card     | `css/entity-card.css`                | `js/entity-card.js`                  | `demos/entity-card.html`                        | BRIEF-L2-FE-ENTITY-CARD-PRIMITIVE               |
| sub-nav         | (tokens in `css/base.css` §monitor-nav) + `css/sub-nav.css` (generic host) | `js/sub-nav.js` (auto-init; `window.AsymSubNav`) | `templates/sub-nav.html` | BRIEF-L1-FE-SUB-NAV-PRIMITIVE |

## Composition contract

- `entity-card` hosts `freshness-badge` and consumes typography-floor
  tokens from `base.css`. It is the single visual contract for card
  surfaces across the fleet (commons monitor cards, commons archive
  items, Advennt `/jurisdictions/`, Advennt `/signals/`).
- Consumers wire entity-card by passing a JSON descriptor to
  `AsymEntityCard.renderInto(mount, items)` — they do **not** author
  per-page card HTML.
- `sub-nav` reads its 9-item link list from
  `static/monitors/monitor-registry.json` → `sub_nav` array (inlined
  at build by `tools/inline_registry_into_navjs.py`). The canonical
  host is the existing `<ul class="monitor-nav__links">` inside
  `<nav class="monitor-nav">`; a generic `<div data-sub-nav>` host is
  also supported for non-chrome pages. Consumers do **not** author
  per-monitor nav HTML. PI-1 graceful-fallback: if the inlined list
  is missing/malformed, the host stays empty.

## Authority

P1 (cluster-4) — schema-driven projection. P5 (cluster-4) — reusable
composition primitives. P12 — product not library. P13 — no per-page
edits; new cards are data renders, not HTML touches; new nav items
are JSON edits, not HTML touches.
