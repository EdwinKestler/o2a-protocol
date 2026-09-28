# ADR-0008 regression suite (genesis-bound EntityID)

CC0-1.0. Normative regression coverage for accepted
[ADR-0008](../../../adr/0008-genesis-bound-entity-id.md).

Every expectation is behavior ADR-0008 **requires**:

| Group | Requirement |
|---|---|
| R1 | Derivation: EntityID = `TaggedHash("O2A/v0.1/entity-id", genesis payload)`; genesis `signer_entity` is zero; deterministic; any payload change gives a new ID |
| R2 | A genesis naming a non-zero `signer_entity` is invalid |
| R3 | A stolen root, on the same or a different seal, even with the seal key, never obtains the legitimate EntityID |
| R4 | Rotation keeps the EntityID; a same-seal parallel history is closed by the first legitimate transition |
| R5 | `PENDING_CONFIRMATION` below depth, `INCOMPLETE` when the seal-creating tx is absent, no payout until `CURRENT` |
| N | Negative controls: the previous root-only rule and Option B must still admit the attacks |

## Rule seam

`entity_id_of`, `genesis_valid` and `identity_state` call the normative
implementation in `check_protocol_objects.py`; `RULE` names that source. The
negative controls use `legacy_evaluator.py`, a clearly labelled, frozen
c7b0871 seam for the previous root-only rule and Option B. It is not imported
by the standard vector suite. Existing expectations remain unchanged; the
successor-seal confirmation row is additive.

```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain \
  bash -lc 'python3 tests/vectors/entity-id-regression/check_entity_id_regression.py'
```
