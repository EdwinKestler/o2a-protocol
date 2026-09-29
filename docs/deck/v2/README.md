# O2A pitch deck, v2 (September 2026)

`O2A-pitch-deck-2026-09-v2.pptx` is the **editable source** of the pitch deck
(17 slides, 16:9). It opens in PowerPoint, Keynote and Google Slides. Export
PDFs from it; do not edit the PDF.

It supersedes `../v1/O2A-pitch-deck-2026-09.pdf` (kept as history). Changes
from v1:

| Slide | Change | Source |
|---|---|---|
| 6 | EntityID is rooted in the root key **and** the signed genesis (the ID is the genesis fingerprint) | ADR-0008 |
| 7 | RGB row names the production line (v0.11.1) | ADR-0010 |
| 8 | Attestations produce "one signed record" (no Bitcoin transaction per claim) | specs |
| 9 | Signing keys never spend bitcoin; a dedicated seal key guards the seal. RGB: built on the production line (v0.11.1); genesis format works with any RGB line | seal policy, ADR-0010 |
| 11 | Current metrics: 4 accepted ADRs, 3 signet rehearsals, 63 frozen outputs, 27 regression checks, 2 validators, 3 derivation implementations | docs/25, docs/26 |
| 12 | **New:** "Block 0" hand-over slide to the live mainnet mint (speaker notes included) | ADR-0009, ADR-0011 |
| 13 | Roadmap: Oct 2026 Block 0 on mainnet; pilot gate is the RGB program for transitions (no RGB 0.12 gate) | ADR-0010 |
| 15 | "RGB is live on mainnet" replaces "RGB reached 0.12" | ADR-0010 |

Fonts: Arial and Consolas (present in Office on Windows and macOS). Palette:
background `0E1230`, cards `141A40`, text `EEF0FA`, amber `F2B33D`, violet
`9A8CFF`, cyan `3FD3F0`.

Supporting document; it introduces no protocol rule. Figures and statements
must stay consistent with the accepted ADRs and `docs/25-scenario-matrix.md`.
