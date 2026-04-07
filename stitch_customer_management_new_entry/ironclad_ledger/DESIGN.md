```markdown
# Design System Specification: High-End Financial Intelligence

## 1. Overview & Creative North Star
### The Creative North Star: "The Sovereign Analyst"
This design system moves away from the cluttered, "dashboard-lite" aesthetic of legacy fintech. Instead, it adopts the persona of a high-end editorial publication for global risk management. The visual language is defined by **The Sovereign Analyst**: a style that is authoritative, whisper-quiet, and immaculately structured.

We achieve this by breaking the traditional "box-and-border" layout. Instead of rigid grids, we use **Intentional Asymmetry** and **Tonal Depth**. Data isn't just displayed; it is curated. By utilizing generous white space (negative space) and a sophisticated layering of dark surfaces, the UI feels like a bespoke terminal rather than a standard web application.

---

## 2. Colors & Surface Architecture
The palette is rooted in deep obsidian and charcoal tones, designed to reduce eye strain during long analytical sessions while projecting a sense of "bank-grade" security.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1x solid borders to define sections or cards. Layout boundaries must be established solely through background color shifts. Use `surface_container_low` for the base and `surface_container` for nested elements. 

### Surface Hierarchy & Layering
Treat the UI as a series of physical layers. Each layer deeper into the information hierarchy should move toward a slightly lighter or darker tier to create natural separation:
- **Base Layer:** `surface` (#080e1a) - The primary canvas.
- **Structural Layouts:** `surface_container_low` (#0a1323) - Used for the fixed left navigation and sidebar panels.
- **Content Cards:** `surface_container` (#0d192f) - The primary container for data visualizations and tables.
- **Interactive Overlays:** `surface_container_high` (#0f1f3a) - Used for modals or active states.

### The "Glass & Gradient" Rule
To inject a "premium" feel, use **Glassmorphism** for floating elements (like tooltips or dropdowns). 
- **Recipe:** Use `surface_variant` at 60% opacity with a `20px` backdrop blur.
- **Signature Textures:** For primary CTAs and critical risk indicators, use a subtle linear gradient from `primary` (#76d6d5) to `primary_container` (#004f4f) at a 135-degree angle. This adds "soul" and depth to otherwise flat interactive elements.

---

## 3. Typography
The typography system uses a pairing of **Manrope** (Display/Headline) for a modern, geometric authority and **Inter** (Body/Labels) for maximum legibility in high-density data environments.

- **Display & Headlines (Manrope):** Large, low-contrast scales. `display-lg` (3.5rem) should be used sparingly for high-level portfolio totals. It conveys a "Big Picture" editorial feel.
- **Titles & Body (Inter):** These are the workhorses. Use `title-md` (1.125rem) for section headers.
- **Hierarchy through Weight:** Use `on_surface_variant` (#98abd4) for secondary metadata. This silver-blue tone ensures that while the data is present, it doesn't compete with the primary "On-Surface" white text for the user’s attention.

---

## 4. Elevation & Depth
In this system, depth is a function of light and tone, not shadows.

- **The Layering Principle:** Instead of a drop shadow, place a `surface_container_lowest` (#000000) card on a `surface_container` background to create a "recessed" look, or a `surface_container_highest` on a `surface` background to create "lift."
- **Ambient Shadows:** If an element must float (e.g., a context menu), use a shadow with a blur of `32px`, an opacity of `8%`, and a color derived from `on_secondary_container` to ensure the shadow feels like a natural part of the environment.
- **The "Ghost Border" Fallback:** If accessibility requires a stroke (e.g., in high-contrast modes), use `outline_variant` (#35486b) at **15% opacity**. Never use 100% opaque lines.

---

## 5. Components

### Navigation & Layout
- **Fixed Left Menu:** Width is set to `12` (4rem) collapsed or `24` (8.5rem) expanded. Use `surface_container_low` for the background. Active states are indicated by a `3.5` (1.2rem) vertical "pill" of `primary` (#76d6d5) on the far left edge.

### Buttons & Interaction
- **Primary:** `primary` background with `on_primary` text. Use `roundedness-md` (0.375rem). Use the signature gradient for a "High-End" feel.
- **Secondary:** Transparent background with an `outline` (#63769b) ghost border.
- **Tertiary/Ghost:** No container. Use `primary` text color for actions that should not distract from the data.

### Input Fields
- **Design:** Use `surface_container_highest` for the input background. No bottom border. Instead, use a 2px `primary` underline only during the `:focus` state.
- **Error States:** Use `error` (#ee7d77) text for helper messages and `error_container` for the input background to clearly signal risk without breaking the dark-mode aesthetic.

### Cards & Data Lists
- **The Divider Rule:** Strictly forbid 1px horizontal dividers. Use the Spacing Scale (e.g., `4` or `1.4rem`) to separate list items. If separation is visually required, use a subtle background toggle between `surface_container` and `surface_container_low`.
- **Data Densities:** For risk tables, use `body-sm` for values to maximize the "terminal" feel.

---

## 6. Do’s and Don’ts

### Do
- **Do** use `2.5` (0.85rem) to `4` (1.4rem) padding as your default "breathing room" within containers.
- **Do** use `tertiary` (#f4f6ff) for non-interactive decorative elements to provide a stark, high-contrast accent.
- **Do** utilize `backdrop-blur` on all sticky headers to maintain a sense of depth as the user scrolls.

### Don’t
- **Don’t** use pure #000000 for text or backgrounds (except for `surface_container_lowest`). It creates "smearing" on OLED screens and feels unpolished.
- **Don’t** use "Alert Red" for everything. Reserve `error` colors specifically for critical financial risk thresholds.
- **Don’t** use standard 1px borders. If you feel the need for a line, try a background color shift first.
- **Don't** use "Floating Action Buttons" (FABs). This system is structured and serious; actions should be docked or contextual.

---

## 7. Signature Financial Components
- **The Risk Heatmap:** Use tonal shifts from `surface_container` to `primary` rather than a standard green-to-red scale to maintain the brand’s sophisticated palette.
- **The "Pulse" Indicator:** Use a subtle animation on a `primary` dot to indicate real-time data streaming—a tiny, 2px glow with 40% opacity.