---
name: o2a-site-publishing
description: Update the public protocol site within its curated allowlist and publishing rules.
when-to-use: Only when explicitly asked to change site copy or figures.
disable-model-invocation: true
paths: site/**, docs/WEBSITE.md, docs/diagrams/**
---

# Site publishing

- Follow docs/WEBSITE.md: an eleven-file allowlist, no new pages, generic participants only.
- Never mention artist names, event names or dates, a live or stage genesis ceremony, wallet addresses, or private paths.
- Status copy stays honest: Draft v0.1, ADR-0009 Proposed, no mainnet identity network running, and each test proves only its named case.
- Figures follow their Mermaid sources: update docs/diagrams/*.md first, then the matching site/assets/*.svg, keeping the visual style. Validate Mermaid by rendering.
- Validate with `python3 scripts/build_site.py`.
- Merging changes under site/** to main redeploys GitHub Pages (pages.yml). The OpenAI Sites route is a separate publication and requires explicit authorization every time.
