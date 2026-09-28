# ADR-0008 regression suite (genesis-bound EntityID)

CC0-1.0. Test-only until [ADR-0008](../../../adr/0008-genesis-bound-entity-id.md)
is accepted.

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

`entity_id_of`, `genesis_valid` and `identity_state` currently call the
candidate implementation (`RULE = "candidate:ADR-0008"`). When the normative
specification adopts ADR-0008:

1. Replace those three bodies with calls into the normative implementation in
   `check_protocol_objects.py`.
2. Set `RULE` to the normative source.
3. Do not edit any expectation. A needed edit means the spec diverged from
   ADR-0008.

Known candidate limitation: only the genesis seal is classified as
`PENDING_CONFIRMATION`. The normative implementation must apply the rule to
every seal-creating transaction named by a valid history.

```bash
docker compose --file dev/compose.yaml --profile tools run --rm toolchain \
  bash -lc 'python3 tests/vectors/entity-id-regression/check_entity_id_regression.py'
```
