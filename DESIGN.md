---
name: PCW architectural alternative
description: A complete content-preserving contractor prospectus.
colors:
  ink: "#0a192f"
  navy: "#0f274a"
  blue: "#2563eb"
  amber: "#fbbf24"
  paper: "#ffffff"
  ground: "#f3f6fa"
  muted: "#526174"
  line: "#dbe2eb"
  field-border: "#718096"
typography:
  display:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(3rem,5vw,4.75rem)"
    fontWeight: 600
    lineHeight: 1.02
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "16px"
    lineHeight: 1.6
rounded:
  control: "2px"
spacing:
  gutter: "24px"
  chapter: "72px"
components:
  button-primary:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
  search:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
---

# PCW architectural alternative — design system

## Product and scope
Static 45-route alternative to the production website. Product truth is in PRODUCT.md and the read-only approved source. The public artifact contains only routes/assets, not audit records or design contracts.

## Visual system
- Ink: `--c-ink: #0a192f`; deep navy: `--c-navy: #0f274a`.
- Action blue: `--c-blue: #2563eb`; restrained construction-detail amber: `--c-amber: #fbbf24`.
- White: `--c-paper: #ffffff`; cool quiet surface: `--c-ground: #f3f6fa`; text secondary: `--c-muted: #526174`; rules: `--c-line: #dbe2eb`.
- Display face: locally served Archivo 400/600. Existing DM Sans body and original header/fonts stay. No custom cursor.
- Main container: 1240px including 24px gutters. Editorial text measure, square photo plates, restrained 2px controls, 1px rules. No round-card wall and no colored glows.

## Composition
The homepage is a prospectus: oversized masthead above a panoramic construction photo, a navy photo caption with a restrained amber rule, and a quiet proof ledger. Project services occupy an asymmetric white photo spread; property services use an opposing navy chapter. Each opens a searchable native-details service directory, keeping all 36 source cards and complete quote dialogs accessible. The company introduction is typographic, with full differentiators behind disclosure. A signed large-format testimonial leads all seven complete reviews. Resources use one dark feature and a quieter linked list. The complete contact introduction remains visible; the home form opens on demand and the separate Contact route is complete.

Services use a consistent light editorial title and right photo plate, full technical scope, facts/estimate sidebar and related links. All 45 routes share the same header and base system rather than becoming homepage-only stubs.

## Interaction and responsive behavior
Native details work without JavaScript. Search progressively filters source entries and announces result counts. Fragment dialog IDs are retained, with Escape, backdrop dismissal, focus containment and focus restoration. Direct Learn More links always go to real matching pages. On phones, the masthead, photo, chapters, directories and service content stack; every touch action retains a visible focus state. CDP device emulation, not window.resizeTo, is used for testing.

## Research and explicit exceptions
UI/UX Pro Max research query: `construction architecture contractor --design-system --density 2 --motion 1`. Applicable findings: hero-led photography, spacious Swiss grid, clear type hierarchy, restrained hover, explicit focus and reduced-motion support. The tool's gray/orange palette and Cinzel pairing were not adopted: the brief pins navy/blue/amber and an architectural rather than ornamental voice. `keyboard focus modal --domain ux` informs focus containment and non-obscured controls.

Impeccable and Hallmark guide composition and mechanical craft, not content rewriting. Approved source wording, all existing source claims/testimonials, header/nav copy, literal // separators and labels are preserved even when stylistic detectors object. White is explicitly requested. Original header chrome and its style literals are exempt from redesign lint. No automated removal or copy-shortening pass was run.

## Integration boundary
The original form fields, IDs, onsubmit handler and public webhook remain. The original six-key payload does not separately serialize all additional displayed fields; this pre-existing issue is documented, not silently rewritten during a presentation alternative. No real leads are submitted.
