# Monitor SVG Icons

Each monitor has an identity SVG stored at:
`static/monitors/{slug}/assets/icon.svg`

## SCEM — Strategic Conflict & Escalation Monitor
- File: `static/monitors/conflict-escalation/assets/icon.svg`
- Design: Dark navy rounded square (#0f172a), red arrows (#dc2626) pointing outward from centre
- Motif: Expand/escalation — 4 arrows radiating from a centre point
- Two primary arrows (full opacity) + two secondary arrows (60% opacity) for depth
- Source: User-provided screenshot (Screenshot-2026-04-01-at-00.24.43.jpg)
- Recreated: 31 March 2026

## Standard usage
- In overview.html sidebar identity panel: 40×40px
- In monitor-nav__brand (future): 18×18px inline, monitor accent colour
- SVG uses hardcoded #0f172a background + #dc2626 arrows
- For nav brand use: remove background rect, set fill to currentColor on arrows
