# PCW alternative — project notes

## Scope and state
- Existing separate repository only: `callmat3ai-cloud/pcw-services-concept`.
- Intended URL: https://callmat3ai-cloud.github.io/pcw-services-concept/
- Rollback point before this rebuild: `9058042`.
- Read-only source: `/root/pcw-services-preview`, HEAD `3f77b56e6c786fc7046c818f8e2fff3e990734f1`, baseline `998bfaf`.
- Production repo, domain, CNAME, Vercel and live CRM untouched. No test leads sent.

## Delivered implementation
All 45 HTML routes copied from approved source and redesigned with one shared architectural system. Original header, logo and mobile navigation are preserved exactly except the home URL is made project-subpath safe. Full source text is retained on each route. Source home remains complete with native progressive disclosure for the service indexes, company differentiators, complete testimonials and estimate form.

The final art direction replaces the rejected small concept and the first local split-hero draft: prospectus masthead above a panoramic photo plate; asymmetric white project chapter; opposing navy property chapter; searchable service disclosures; typographic company section; signed oversized client quotation; dark featured resource plus quieter supporting resources. All service entries keep separate Request Quote modal and direct Learn More page actions. There is no custom cursor, autoplay or decorative Three.js runtime.

## Acceptance evidence
- `audit/source-inventory.json`: initial source inventory, full per-route text, IDs, services, modals and form markup.
- `audit/acceptance.json`: 45/45 route source-copy coverage, 36 service routes, 36 home service entries, 7 home testimonials, 72 preserved modal instances, 6,023 local link/asset/fragment checks, no missing source text/IDs, no broken local targets, no CSS parse errors/cycles/undefined variables, original form markup and handler preserved.
- `audit/baseline-coverage.json`: baseline 998bfaf has no lost substantive text. Only the explicitly superseded old action labels `Details & Quote →` and `Discover More` differ from restored source/new Request Quote/Learn More buttons.
- `audit/responsive-routes.json`: 135 real Chromium renders across all 45 routes at 1440, 768 and 390px using CDP device metrics. No overflow, broken loaded images, JavaScript page errors or empty CSS tokens after the final lazy-image readback.
- `audit/interaction-tests.json`: service search, modal display/focus trapping/Escape, mobile menu/accordion, Contact service preselection and all 16 form controls. Exact original handler also exercised with mocked fetch and a stubbed DOM; zero real network submissions.
- `audit/screenshots/`: correctly dimensioned full-frame desktop/mobile captures, representative inner pages, full homepage captures and desktop chapter captures. Pixel dimensions were checked with Pillow.
- `audit/visual-*-final.txt`: fresh-context visual reviews of actual captures. Follow-up fixes cover project-directory contrast, resource spacing/feature styling, mobile hero image alignment and contact-info separation.

## Tool and lint limits
The configured `vision_analyze` auxiliary failed with an upstream authentication/account-ban error. A second configured auxiliary also rejected its key. Visual review was completed instead through the live OpenAI Codex multimodal backend in isolated fresh-context image requests; no global Hermes configuration was changed. Initial Puppeteer screenshots revealed a stale 800px screenshot clip despite CDP viewport emulation; those captures were replaced with raw CDP full-frame captures and verified dimensions.

Impeccable detector result is in `audit/impeccable-final.json`. Hallmark renders successfully using a local root-only Chrome wrapper. Mechanical transition-all, bare image-grid tracks and scripting-off reveal issues were repaired without rewriting content. Raw Hallmark style findings remain for retained source color literals/header and approved verbatim labels/separators/caps, the required pure white, and retained original font declarations. These are explicit brief-over-style exceptions; no destructive automated copy sweep was run.

## Pre-existing integration limitation
The preserved handler sends only `name`, `email`, `phone`, `service`, `message`, `source_url`. The approved markup includes 16 controls, including Gate Code and Due Date, but the original handler does not separately serialize the additional controls. This rebuild preserves the exact handler/schema as instructed rather than silently altering live integration behavior. Real CRM delivery was not tested. This limitation needs a separate approved integration fix; do not claim all form fields are delivered.

## Reproduction
`/usr/bin/python3 tools/build_concept.py` reads source and rebuilds concept HTML/legacy CSS; it does not overwrite the design layer or write to source. It requires system `beautifulsoup4` and `tinycss2`.
`/usr/bin/python3 tools/audit_concept.py` performs the offline content/route/CSS checks.
Browser QA tools use locally installed Puppeteer Core in the profile scratch folder and `/usr/bin/google-chrome`; their paths are local QA dependencies, not deployed dependencies.
`python3 tools/stage_site.py` produces `_site` with only public HTML/assets/robots; audit records, design notes, tools and Git metadata never reach Pages.
