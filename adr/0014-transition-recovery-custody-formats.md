# ADR-0014 — Transition, Recovery, and Custody-Transfer Formats

**Status:** Proposed, 2026-10-22. Not accepted. Closes Phase 0 open item 3
only after the acceptance checklist below is complete and the maintainer
accepts it. Decision 2 was chosen by the maintainer on 2026-10-22 (see
"Maintainer decisions").

## Context

[O2A-CANON-1](../specs/canonical-encoding.md) already gives byte layouts for
the identity-transition payload (operations 1, 2, 4, 5) and the recovery
authorization (operation 3), and the
[identity contract](../specs/rgb-identity-contract.md) gives their
authorization rules. Phase 0 item 3 remains open because:

- per-operation state-change rules are partly implicit (what each operation
  may and may not change);
- operation 4 names a custody-acceptance claim but not its object bytes or ID;
- operation 3 has several signers, each signing its own header over one body,
  yet the contract's anchor is `TaggedHash("O2A/v0.1/recovery", recovery
  payload)`, which is ambiguous when there is more than one payload — the
  "recovery-signer" ambiguity flagged in `.grok/skills/o2a-spec-change`; and
- there are no regression vectors that would detect a change to these bytes.

## Decision

If accepted, the following are frozen for v0.1 alongside
[ADR-0009](0009-scoped-genesis-freeze.md), and
[`tests/vectors/transition-freeze-v0.1.json`](../tests/vectors/transition-freeze-v0.1.json)
pins them.

### 1. Layouts

The O2A-CANON-1 transition and recovery layouts are frozen unchanged:
`common_header || operation || resulting_state` (object type 2, capability 2,
controller role, domain `O2A/v0.1/identity-transition`, operation 1, 2, 4, or
5) and `common_header || operation || policy_hash || not_before_height ||
resulting_state` (object type 3, capability 3, recovery role, domain
`O2A/v0.1/recovery`, operation 3).

### 2. Recovery anchor digest (maintainer choice: selected 2026-10-22)

The anchor for operation 3 commits to the signer-independent recovery body:

```text
recovery_body   = operation || policy_hash || not_before_height || resulting_state
recovery_anchor = TaggedHash("O2A/v0.1/recovery-anchor", entity_id || recovery_body)
```

Every recovery authorization MUST carry byte-identical `recovery_body` after
its own common header; each signer still signs its full payload under
`O2A/v0.1/recovery`. `O2A/v0.1/recovery-anchor` is an identifier tag, not a
signature domain. This is the value carried in ADR-0012's `transitionDigest`
for transition type `8102`. The contract's current sentence for operation 3
is amended accordingly.

Alternatives: (a) the digest of the lowest-`signing_key_id` signer's payload —
rejected because the anchor would depend on which signers took part; (b) the
resulting state ID — rejected because it does not commit to
`policy_hash` or `not_before_height`.

### 3. Rules common to every transition

Against the prior valid state: `signer_entity` is the history EntityID;
`authorizing_state` and `previous_state` equal the prior state ID;
`sequence` is prior plus one; `previous_seal` equals the prior `next_seal`;
`next_seal` differs from it; the prior state is ACTIVE; the resulting state
passes the existing seal-binding and cross-role x-only checks; and the
committed anchor digest is present and equals the recomputed one. A state
after REVOKED is invalid.

### 4. Per-operation rules

| Op | Controllers | Recovery policy | Custodian | `custody_acceptance` | Status |
| --- | --- | --- | --- | --- | --- |
| 1 rotation | MUST change | unchanged | unchanged | absent | ACTIVE |
| 2 policy change | unchanged | MUST change, `policy_sequence` = prior + 1 | unchanged | absent | ACTIVE |
| 3 recovery | may change | unchanged, or `policy_sequence` = prior + 1 | unchanged | absent | ACTIVE |
| 4 custody transfer | unchanged | unchanged | MUST change to the accepting entity | REQUIRED | ACTIVE |
| 5 revocation | unchanged | unchanged | unchanged | absent | REVOKED |

Operation 3 additionally requires `policy_hash` = the prior policy hash,
`not_before_height` = seal-creating height + `delay_blocks`, an anchor at or
above that height, sorted unique signers all named by the prior policy, and at
least `threshold` of them. Revocation still names a `next_seal` (ADR-0012
rule 4).

### 5. Custody-acceptance claim (operation 4)

A claim (object type 4, capability 4, domain `O2A/v0.1/claim`) signed by a
controller of the incoming custodian with capability 4 in that custodian's
current state:

```text
subject   = EntityID being transferred
predicate = "o2a/custody-acceptance/v1"
object    = prior_state_id (32) || next_custodian (32) || next_seal (36)
context, supersedes, checkpoint = absent
```

`next_custodian` MUST equal the claim's `signer_entity` and the resulting
state's `custodian`; it MUST differ from the transferred EntityID and from the
prior custodian. `next_seal` MUST equal the resulting state's `next_seal`.
`custody_acceptance` in the resulting state is the claim ID
`TaggedHash("O2A/v0.1/claim", claim payload)`. Binding the prior state and
next seal prevents replay of one acceptance into another transfer.

## Evidence

`tests/vectors/check_transition_freeze.py` builds one regtest lineage —
genesis, 1, 2, 4, 3 (2-of-2 after the policy change), 5 — evaluates it from
decoded bytes, and checks 27 single-rule adversarial cases (ADR-0014 §3–5 and
ADR-0012 rules 2–3). Signatures are produced in Python and verified by the
independent Rust `crypto-checker`. These are protocol-only vectors; no RGB or
Bitcoin execution is involved.

## Required evidence before acceptance

1. ~~Maintainer choice on decision 2.~~ Done 2026-10-22.
2. The ADR-0012 regtest lineage exercises operations 1–5 with these exact
   rules, including one custody transfer and one rejected acceptance replay.
3. The Rust `crypto-checker` gains independent encoders for the vector
   payloads (today it verifies signatures, EntityIDs, and state IDs only).

## Consequences

- Phase 0 item 3 closes on acceptance. Changing any frozen byte requires a new
  versioned tag, as for ADR-0009.
- `specs/rgb-identity-contract.md`, `specs/canonical-encoding.md`, and
  `specs/cryptographic-profile.md` take the amendments above on acceptance;
  until then they carry a pointer to this proposal.

## Maintainer decisions — 2026-10-22

- Decision 2: the maintainer selected the signer-independent
  `O2A/v0.1/recovery-anchor` digest over
  `entity_id || recovery_body`. Alternatives (a) and (b) are rejected. The
  vector file already uses this rule. The ADR stays Proposed until checklist
  items 2 and 3 are met.
