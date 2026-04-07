# asym-intel — Homepage v4 IA Note
## Editorial Front Page Direction

**Date:** 7 April 2026  
**Status:** Updated working IA and implementation note for the preferred homepage direction  
**Basis:** homepage visual spec, site rebuild roadmap, and thread decisions through 7 April 2026

---

## 1. What this note is

This note captures the preferred information architecture for the asym-intel homepage after the later homepage experiments and corrections.

It is not a replacement for the earlier CSS-oriented homepage visual spec. Instead, it sits above that document and answers a different question:

> **What should the homepage do, in what order, and why?**

The homepage should be treated as an **editorial front page for a network of monitors**, not as a dashboard and not as a simple routing directory.

---

## 2. Core homepage job

The homepage has four jobs:

1. **Orient** the reader to the platform and its purpose.  
2. **Generate curiosity** about the system as a whole, not just a single monitor.  
3. **Route** readers cleanly into the right monitor, issue, or depth layer.  
4. **Signal immediacy** by showing a light, clearly labelled raw-signal layer without collapsing into a live dashboard.

This means the homepage should answer:
- What kind of platform is this?
- Why does the system matter this week?
- Where do I go next depending on how I want to read?
- What is moving now across the monitor network?

---

## 3. What the homepage is not

The homepage is **not**:

- a monitor dashboard,
- a giant feed,
- a dense OSINT surface,
- or a world map-first interface that replaces editorial judgement.

The world-map concept is useful, but only as a **module within the homepage** or as a secondary discovery layer. It should not become the homepage’s sole organising principle.

---

## 4. Preferred structural model

The preferred homepage structure is the stronger **editorial v4** direction.

That means the page should feel closer to a front page that says:

> “Here is the shape of the week across the system.”

rather than:

> “Here are seven monitor links.”

This direction emerged because the homepage needs to frame the platform as a coherent analytical system, not just a collection of standalone products.

---

## 5. Page order

The preferred homepage order is:

1. **Top nav**  
2. **Monitor strip**  
3. **Hero / featured editorial frame**  
4. **System-level framing module** (“Shape of the Week” or equivalent)  
5. **Explore by mode**  
6. **Latest from the monitors**  
7. **Cross-monitor collisions**  
8. **Today’s Raw Signal / Chatter**  
9. **Footer / secondary links**

This order matters because it moves from orientation, to framing, to routing, to cross-monitor discovery, to immediacy.

---

## 6. Section purposes

### 6.1 Top nav

The top nav is stable platform navigation.

It should remain minimal and not compete with the monitor strip or the homepage editorial modules.

### 6.2 Monitor strip

The monitor strip is the first monitor-level routing layer.

It should sit directly below the top nav, use small coloured monitor dots, and remain visually restrained. Its purpose is orientation and quick access, not to act as the dominant visual object on the page. The strip background should remain the same as the page background, not a contrasting container.

### 6.3 Hero / featured editorial frame

The hero should introduce asym-intel as a system-reading platform.

Its job is not simply branding. It should provide one concise framing line and one explanatory paragraph that tell the user why this platform exists and why the current moment matters. Visually, it should retain the approved stripe-only treatment: left accent stripe, no background tint, no gradient wash.

### 6.4 Shape of the Week

This is the key addition that differentiates the stronger editorial homepage from the earlier routing-first versions.

Its function is to offer one **system-level reading of the current week**: not a list of stories, but a synthesis of how multiple pressures are beginning to align or collide. This module should make readers feel they are looking at a structured analytical system rather than unrelated feeds.

This label can change. “Shape of the Week” is a working name, not a locked one.

### 6.5 Explore by mode

This section should route users by **reading mode**, not only by topic.

The expected route types are:
- Dashboard / triage,
- Latest Issue / synthesis,
- Living Knowledge / structural depth,
- Chatter / pre-synthesis signals.

This is important because users will often know how they want to read before they know which monitor they need.

### 6.6 Latest from the monitors

This section should make the monitors feel distinct in object and tone while preserving a common platform language.

The cards should not all sound interchangeable. Each should clearly signal the kind of pressure or domain it covers, while using the shared monitor accent system and card grammar.

### 6.7 Cross-monitor collisions

This section is where the homepage demonstrates that the monitors are not isolated silos.

It should show a small number of **meaningful cross-domain links** — for example, democracy and cognitive warfare, strategic conflict and European autonomy, or environmental stress and macro repricing. The goal is to encourage lateral movement through the platform.

### 6.8 Today’s Raw Signal / Chatter

This is the homepage’s immediacy layer.

It should stay visibly subordinate to the editorial modules above it and be clearly labelled as **pre-synthesis** or raw signal. It should never be allowed to redefine the homepage as a live intelligence dashboard.

---

## 7. Left-rail visual discovery modules

The homepage left rail can carry a compact stack of **visual discovery modules** rather than a purely textual navigation list.

These modules should act as alternate entry points into the system. They should remain compact and secondary to the central editorial framing, but they are useful because they let users enter the platform by **mode of seeing** rather than only by monitor.

Recommended left-rail modules:

1. **Network**  
2. **Map**  
3. **Timeline**  
4. **Signals**  
5. **Connections**

The important rule is that these should not route into arbitrary monitor pages. Because they sit in the homepage’s cross-monitor discovery layer, they should lead to **cross-monitor destinations**.

### 7.1 Network

**Network** should route to the existing or planned cross-domain network view.

This is the page that lets users trace how actors, themes, and pressures connect across domains. It is already legible as a platform-level view and does not need redefinition here.

### 7.2 Map

**Map** should route to a dedicated **Coverage Map** page.

This page should be a full-page world map that shows which countries are covered by the platform and allows filtering by monitor. It should be a discovery surface, not a dashboard, and should help users understand how different monitor lenses reorganise geographic attention.

Suggested route:
- `/map/`
- or `/coverage-map/`

### 7.3 Timeline

**Timeline** should route to a dedicated **Platform Timeline** page.

This should be a **cross-monitor chronology**, not a single-monitor timeline. If individual monitor timelines already exist, this page should act as the higher-order version of that logic: a place where users can see what is happening across the system in sequence.

Default behaviour:
- all monitors visible,
- chronological ordering,
- filters for monitor, geography, theme, and date range.

Primary question answered:
> What is happening across the system in sequence?

Suggested route:
- `/timeline/`
- or `/platform-timeline/`

### 7.4 Signals

**Signals** should route to a dedicated **Signals** page that sits between chatter and synthesis.

This page should be **cross-monitor and monitor-agnostic**, presenting emerging items in a cleaner and more structured way than the homepage raw-signal rail. It should not read like a dashboard, but like a pre-synthesis analytical surface.

Default behaviour:
- all monitors visible,
- sortable by recency, salience, geography, monitor, or type,
- each item routes onward to a monitor, issue, or network explanation.

Primary question answered:
> What is surfacing now before full synthesis?

Suggested route:
- `/signals/`
- or `/cross-monitor-signals/`

### 7.5 Connections

**Connections** should route to a dedicated **Cross-Monitor Connections** page.

This page should be the clearest expression of the homepage’s cross-domain logic. It should organise content around **meaningful relationships** between domains rather than around time or recency.

Examples:
- democracy + cognitive warfare,
- strategic conflict + European autonomy,
- environmental stress + macro repricing.

Default behaviour:
- show curated relationships,
- explain why each connection matters,
- route users onward into the relevant issue, monitor, or network view.

Primary question answered:
> Where are domains interacting or destabilising one another?

Suggested route:
- `/connections/`
- or `/cross-monitor-connections/`
- or `/cross-monitor-collisions/`

### 7.6 Distinction between the three cross-monitor pages

To avoid overlap, the three pages should be differentiated clearly:

- **Timeline** = organised by time.  
- **Signals** = organised by emergence / salience.  
- **Connections** = organised by relationship / overlap.

This creates genuinely different reading modes and makes the homepage left rail a set of alternate ways into the same system.

---

## 8. Visual and layout rules that remain fixed

The following visual decisions are stable and should be treated as constraints, not open questions:

- The monitor strip sits below the top nav.
- The homepage uses a **three-zone surface split**: left sidebar, main content area, right signal/chatter sidebar.
- The main reading area stays on the lightest background; the sidebars sit on `--color-surface`.
- The featured article / hero uses a **left accent stripe only** and must not receive a background tint or gradient.
- The card grid uses 1px gaps with divider-colour bleed and subtle top accent strips keyed to monitor identity.
- Monitor colours are identity markers, not full-surface fills.

These rules are already documented in the visual spec and should survive homepage content refinements.

---

## 9. Copy and register rules

### 9.1 Overall homepage register

The homepage should read as:
- analytical,
- editorial,
- restrained,
- and cross-domain.

It should not read like a product landing page full of generic SaaS claims, and it should not read like a chaotic live feed.

### 9.2 GMM-specific rule

Any homepage reference to the **Global Macro Monitor** must remain within the public GMM register:
- signals,
- contextual analysis,
- macro regime,
- liquidity,
- sovereign and credit stress,
- policy transmission,
- thresholds,
- and blind spots.

Homepage GMM wording must **not** drift into:
- investment advice framing,
- portfolio suggestions,
- imperative trading language,
- or gambling-monitor language accidentally inherited from external prototypes.

This is an explicit acceptance criterion for future homepage polish and implementation work.

---

## 10. Relationship to the map idea

The world-map / monitor-switching concept remains valuable.

However, the agreed role for it is:
- a discovery module,
- a visual interpretation layer,
- or a later homepage enhancement,
not the sole homepage IA.

If integrated, it should sit **below** the core editorial framing and monitor strip, and should help readers explore how different monitor lenses reorganise the world.

---

## 11. Recommended implementation interpretation

For implementation purposes, the homepage should be built as an editorial front page with **layered entry points**:

- **Layer 1:** immediate orientation (top nav + monitor strip + hero)  
- **Layer 2:** system meaning (Shape of the Week / system frame)  
- **Layer 3:** reading-mode routing (Explore by mode)  
- **Layer 4:** monitor-specific discovery (Latest from the monitors)  
- **Layer 5:** cross-domain interpretation (Cross-monitor collisions)  
- **Layer 6:** live movement, clearly badged (Today’s Raw Signal / Chatter)

The left-rail visual modules are best understood as **parallel cross-monitor discovery routes** sitting beside these layers rather than replacing them.

This creates a homepage that is readable for first-time visitors, useful for returning readers, and extensible as the platform grows.

---

## 12. Non-goals and cautions

The following should be treated as explicit non-goals:

- Do not turn the homepage into a dashboard.
- Do not let the chatter rail dominate the editorial modules.
- Do not let the world map become the page’s only organising logic.
- Do not use monitor colours as large decorative fills.
- Do not add a tinted hero background; keep the left stripe only.
- Do not reintroduce contaminated GMM wording from the Advennt gambling-monitor example.
- Do not route left-rail visual modules into arbitrary single-monitor pages when a cross-monitor page is intended.

---

## 13. Working labels

The following labels are currently acceptable but still open to refinement:

- **Shape of the Week**
- **Explore by mode**
- **Latest from the monitors**
- **Cross-monitor collisions**
- **Today’s Raw Signal**
- **Platform Timeline**
- **Signals**
- **Cross-Monitor Connections**

These are strong enough for mockup work, but can be tightened later during final homepage polish.

---

## 14. Deliverables this note supports

This note should be used to guide:

1. final polish of the preferred homepage v4 artefact,  
2. a future homepage implementation brief for Hugo / Computer,  
3. integration of a map module into the v4 homepage,  
4. homepage copy review for consistency with platform and GMM boundaries,  
5. future mockups for the cross-monitor **Map**, **Timeline**, **Signals**, and **Connections** pages.

---

## 15. Short implementation summary

If the homepage visual spec defines **how the homepage should look**, this note defines **how the homepage should think**.

The preferred homepage is an editorial front page for a monitor network: restrained, structured, cross-domain, and alive to the current week without becoming a dashboard.

The left-rail visual modules should reinforce that logic by opening distinct, monitor-agnostic ways of reading the same system:
- **Map** for geography,
- **Timeline** for sequence,
- **Signals** for emergence,
- **Connections** for overlap.
