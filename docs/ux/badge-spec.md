# Confidence Badge Spec
**Status:** ✅ Signed off by Peter — 7 April 2026
**Used in:** SL-03 (confidence badge system distinct from severity)

---

## Design decision

Confidence badges must be visually distinct from severity badges at a glance.

| Property | Severity badge | Confidence badge |
|---|---|---|
| Style | Filled, coloured background | Outline only, transparent fill |
| Border | None | 1px solid, neutral grey |
| Text colour | White | Neutral (--color-text-muted) |
| Background | --critical / --high / --moderate / --positive / --contested | Transparent |
| Weight | Medium — draws attention | Light — supporting information |

---

## Confidence levels and labels

| Level | Badge label | Notes |
|---|---|---|
| Confirmed | Confirmed | Direct evidence + corroboration |
| High | High | Strong indirect evidence |
| Assessed | Assessed | Credible, not independently verified |
| Possible | Possible | Emerging signal, unconfirmed |

---

## CSS implementation (for SL-03)

```css
/* Base confidence badge — outline, neutral */
.badge-confidence {
  display: inline-flex;
  align-items: center;
  gap: 0.25em;
  padding: 0.15em 0.55em;
  border: 1px solid oklch(from var(--color-text) l c h / 0.25);
  border-radius: 99px;          /* pill shape */
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-muted);
  background: transparent;
  white-space: nowrap;
}

/* Modifier variants — border tint only, no fill */
.badge-confidence--confirmed  { border-color: oklch(from var(--color-success)  l c h / 0.5); color: var(--color-success-text,  var(--color-text)); }
.badge-confidence--high        { border-color: oklch(from var(--color-warning)  l c h / 0.4); }
.badge-confidence--assessed    { border-color: oklch(from var(--color-text)     l c h / 0.25); }
.badge-confidence--possible    { border-color: oklch(from var(--color-text)     l c h / 0.15); color: var(--color-text-faint); }
```

---

## Usage rules

- Confidence badges appear **after** the finding headline or in a card footer — never as the lead element.
- Never use severity colours (--critical, --high, --moderate, --positive) on confidence badges.
- Never use confidence badge styles on severity indicators.
- On mobile: badge remains visible — do not hide or collapse to icon-only.
- Minimum size: text must remain at `--text-xs` (never smaller).
- A finding may show both a severity badge AND a confidence badge — they are complementary, not interchangeable.

---

## Validator rule (for SL-08)

Add CI check: any element with class `badge-confidence` must not also carry
`--critical`, `--high`, `--moderate`, `--positive`, or `--contested` as a CSS variable reference.
