# Monitor SVG Icon Registry

All SVG icons are stored inline in `layouts/topics/list.html` and `layouts/subscribe/single.html`.
Each monitor's icon is also stored individually at `static/monitors/{slug}/assets/icon.svg`.

Use these canonical SVGs for all overview.html identity panels and future monitor-nav brand areas.

---

## ESA — European Strategic Autonomy Monitor
Accent: #5b8db0 | Motif: Nested hexagons (strategic layers/containment)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 36 36" fill="none">
  <polygon points="18,2 32,10 32,26 18,34 4,26 4,10" stroke="#5b8db0" stroke-width="1.5" fill="none"/>
  <polygon points="18,7 27,12 27,24 18,29 9,24 9,12" stroke="#4a7fa0" stroke-width="1" fill="none"/>
  <polygon points="18,11 24,14.5 24,21.5 18,25 12,21.5 12,14.5" stroke="#3d6f8e" stroke-width="1" fill="none"/>
  <line x1="18" y1="2" x2="18" y2="34" stroke="#4a7fa0" stroke-width="0.7"/>
  <line x1="4" y1="10" x2="32" y2="26" stroke="#4a7fa0" stroke-width="0.7"/>
  <line x1="4" y1="26" x2="32" y2="10" stroke="#4a7fa0" stroke-width="0.7"/>
  <circle cx="18" cy="18" r="2.5" fill="#6488ac"/>
</svg>
```

## WDM — World Democracy Monitor
Accent: #61a5d2 | Motif: Globe with latitude/longitude lines
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 32 32" fill="none">
  <circle cx="16" cy="16" r="13" stroke="#61a5d2" stroke-width="1.5" fill="none"/>
  <ellipse cx="16" cy="16" rx="13" ry="5" stroke="#61a5d2" stroke-width="1" fill="none"/>
  <ellipse cx="16" cy="16" rx="13" ry="9" stroke="#61a5d2" stroke-width="1" fill="none"/>
  <ellipse cx="16" cy="16" rx="5" ry="13" stroke="#61a5d2" stroke-width="1" fill="none"/>
  <line x1="3" y1="16" x2="29" y2="16" stroke="#61a5d2" stroke-width="1"/>
  <line x1="16" y1="3" x2="16" y2="29" stroke="#61a5d2" stroke-width="1"/>
</svg>
```

## GMM — Global Macro Monitor
Accent: #22a0aa | Motif: Rounded square with figure + volatility line
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 38 38" fill="none">
  <rect x="2" y="2" width="34" height="34" rx="6" stroke="#22a0aa" stroke-width="2" fill="none"/>
  <circle cx="12" cy="10" r="2.5" fill="#e87040"/>
  <line x1="12" y1="12.5" x2="12" y2="18" stroke="#e87040" stroke-width="1.5"/>
  <line x1="8" y1="15" x2="16" y2="15" stroke="#e87040" stroke-width="1.5"/>
  <line x1="12" y1="18" x2="9" y2="22" stroke="#e87040" stroke-width="1.5"/>
  <line x1="12" y1="18" x2="15" y2="22" stroke="#e87040" stroke-width="1.5"/>
  <polyline points="5,30 10,30 13,24 17,33 21,26 25,33 29,22 33,30" stroke="#e87040" stroke-width="2" fill="none" stroke-linejoin="round"/>
</svg>
```

## AGM — AI Governance Monitor
Accent: #3a7d5a | Motif: Grid of connected squares (neural network / governance nodes)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 36 36" fill="none">
  <rect x="3" y="3" width="30" height="30" rx="3" stroke="#3a7d5a" stroke-width="1.5" fill="none"/>
  <rect x="8" y="8" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.9"/>
  <rect x="20" y="8" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.6"/>
  <rect x="8" y="20" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.6"/>
  <rect x="20" y="20" width="8" height="8" rx="1" fill="#3a7d5a" opacity="0.3"/>
  <line x1="12" y1="16" x2="12" y2="20" stroke="#3a7d5a" stroke-width="1.5"/>
  <line x1="24" y1="16" x2="24" y2="20" stroke="#3a7d5a" stroke-width="1.5"/>
  <line x1="16" y1="12" x2="20" y2="12" stroke="#3a7d5a" stroke-width="1.5"/>
</svg>
```

## FCW — FIMI & Cognitive Warfare Monitor
Accent: #38bdf8 | Motif: Concentric circles (radar/signal) with red target dot
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 36 36" fill="none">
  <circle cx="18" cy="18" r="14" stroke="#38bdf8" stroke-width="1.5" fill="none"/>
  <circle cx="18" cy="18" r="9" stroke="#38bdf8" stroke-width="1" fill="none" opacity="0.6"/>
  <circle cx="18" cy="18" r="4" stroke="#38bdf8" stroke-width="1" fill="none" opacity="0.35"/>
  <line x1="18" y1="4" x2="18" y2="32" stroke="#38bdf8" stroke-width="0.75" opacity="0.4"/>
  <line x1="4" y1="18" x2="32" y2="18" stroke="#38bdf8" stroke-width="0.75" opacity="0.4"/>
  <circle cx="18" cy="18" r="2" fill="#dc2626"/>
  <circle cx="26" cy="10" r="1.5" fill="#dc2626" opacity="0.8"/>
  <circle cx="10" cy="24" r="1" fill="#38bdf8" opacity="0.9"/>
</svg>
```

## ERM — Environmental Risks Monitor
Accent: #4caf7d | Motif: Globe with curved latitude/longitude lines + orbital dots
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 36 36" fill="none">
  <circle cx="18" cy="18" r="14" stroke="#4caf7d" stroke-width="1.5" fill="none"/>
  <circle cx="18" cy="18" r="9" stroke="#4caf7d" stroke-width="1" fill="none" opacity="0.5"/>
  <path d="M18 4 Q22 10 18 18 Q14 26 18 32" stroke="#4caf7d" stroke-width="1" fill="none" opacity="0.6"/>
  <path d="M4 18 Q10 14 18 18 Q26 22 32 18" stroke="#4caf7d" stroke-width="1" fill="none" opacity="0.6"/>
  <circle cx="18" cy="18" r="2.5" fill="#4caf7d" opacity="0.9"/>
  <circle cx="12" cy="11" r="1.2" fill="#4caf7d" opacity="0.6"/>
  <circle cx="25" cy="13" r="1" fill="#4caf7d" opacity="0.4"/>
  <circle cx="11" cy="24" r="0.9" fill="#4caf7d" opacity="0.5"/>
</svg>
```

## SCEM — Strategic Conflict & Escalation Monitor
Accent: #dc2626 | Motif: Crossed arrows expanding outward from centre (escalation/expansion)
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 36 36" fill="none">
  <line x1="6" y1="30" x2="30" y2="6" stroke="#dc2626" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="6" y1="6" x2="30" y2="30" stroke="#dc2626" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="18" cy="18" r="3" fill="#dc2626" opacity="0.9"/>
  <polyline points="22,6 30,6 30,14" stroke="#dc2626" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="6,22 6,30 14,30" stroke="#dc2626" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

---

## Usage notes
- All icons render on dark navy background (#0f172a) in the subscribe page
- For overview.html sidebar: use at 40×40px, no background rect needed
- For monitor-nav brand (future): strip to 18×18px, use currentColor
- Source: `layouts/topics/list.html` and `layouts/subscribe/single.html`
