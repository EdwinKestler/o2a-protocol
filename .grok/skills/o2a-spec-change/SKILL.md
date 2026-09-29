---
name: o2a-spec-change
description: Rules for changing normative O2A material (ADRs, specs, canonical encoding, vectors) without breaking the authority chain, the frozen genesis set, or regression expectations.
when-to-use: When editing anything under specs/ or adr/, or regenerating vectors under tests/vectors/.
paths: specs/**, adr/**, tests/vectors/**
---

# Changing normative material

## Authority and edits
- Order: accepted ADRs > specs/ > docs/ explanations > supporting docs > diagrams/site/examples (docs/DOCUMENT-AUTHORITY.md).
- Never edit the decision text of an accepted ADR. Amend with a new ADR; you may add one status line (e.g. "Amended by ADR-0008").
- A new rule lands in an ADR or spec first, then is copied downward: README, docs 01/03/13/14, phase0closure, diagrams, site. Find restatements with Palimnex search plus grep.

## Frozen set (ADR-0009, Accepted)
- `tests/vectors/genesis-freeze-v0.1.json` pins 63 outputs: genesis payload, resulting state, seal policy, EntityID = TaggedHash("O2A/v0.1/entity-id", genesis_payload) with a zero genesis signer_entity, state_id = TaggedHash("O2A/v0.1/state-id", entity_id || resulting_state), seal script, official_name claim, Route B roles 0/1/2/4.
- If `check_genesis_freeze.py` changes, STOP: you are changing frozen bytes. That requires a new versioned tag and a maintainer decision, never an in-place edit.

## Vectors
- Python (check_protocol_objects.py, check_vectors.py) and Rust (crypto-checker) must implement every rule independently and agree.
- Regenerate deterministically and report EVERY regenerated field and why.
- Never edit an expectation in tests/vectors/entity-id-regression/. Adding rows is allowed. Its negative controls use the vendored LEGACY evaluator and must keep admitting the old attacks.
- Seal scripts must keep matching the Bitcoin Core oracle (check_seal_core.py).

## Stop and ask when
- a change conflicts with an accepted ADR;
- a freeze output or a regression expectation would change;
- you find an ambiguity (for example the recovery-signer state-ID case). Report the options; do not pick silently.
