# ADR-0015 — Restore and Discovery of Entity and Role Indexes

**Status:** Proposed, 2026-10-22. Not accepted. Closes Phase 0 open item 4
only after the acceptance checklist below is complete and the maintainer
accepts it.

## Context

Route B derives every identity key from `xprv_o2a` at
`m/coin'/entity'/role'/index'`, and allocated indexes MUST NOT be reused
([key-derivation profile](../specs/key-derivation-profile.md)). A mnemonic
alone does not say which `entity'` and per-role indexes were allocated, and it
cannot reproduce EntityIDs without retained genesis payloads or consignments
([ADR-0008](0008-genesis-bound-entity-id.md)). The profile leaves this
restore/discovery rule unspecified.

The real risk is **index reuse after restore**: a wallet that forgets an
allocated but unpublished index derives the same key again for a different
identity or role. Losing a manifest must cost unused indexes, never reuse.

## Decision

If accepted, wallets restore indexes with an authenticated **index manifest**
as the primary source and a **bounded gap-limit scan** as fallback and
cross-check, followed by a mandatory **skip-ahead**.
[`tests/vectors/index-manifest-v0.1.json`](../tests/vectors/index-manifest-v0.1.json)
pins the bytes and outcomes.

### 1. Index manifest

O2A-CANON-1 primitives:

```text
index_manifest = u16(1) || network || wallet_tag || u64(manifest_sequence)
               || list<entity_entry>
entity_entry   = u32(entity_index) || u8(entry_state) || option<entity_id>
               || u32(next_controller) || u32(next_recovery)
               || u32(next_nostr) || u32(next_seal)
wallet_tag     = TaggedHash("O2A/v0.1/index-manifest-wallet", ser_P(xprv_o2a))
mac_key        = TaggedHash("O2A/v0.1/index-manifest-key",
                            ser_256(k_o2a) || chain_code_o2a)
stored         = index_manifest
              || HMAC-SHA256(mac_key, TaggedHash("O2A/v0.1/index-manifest", index_manifest))
```

`entry_state` is 1 RESERVED, 2 PUBLISHED, or 3 ABANDONED; `entity_id` is
present exactly when PUBLISHED. Entries are strictly increasing by
`entity_index`. Each `next_*` value is the smallest index of that role not yet
allocated for that entity. All indexes are below 2^31. The new tags are
identifier tags, not signature domains.

Rules:

1. **Write-ahead.** A wallet MUST durably store a manifest with an increased
   `manifest_sequence` that already covers an index before deriving any key
   at that index for persistent use.
2. **Off-site cap.** A wallet MUST NOT allocate an index more than 20 beyond
   its *restorable high-water mark* — the highest index covered by an
   off-site manifest copy or by an off-site published history. If an
   allocation would exceed it, the wallet first copies the current manifest
   off-site. A wallet SHOULD keep at least two independent off-site manifest
   copies.
3. A manifest is valid only if its HMAC verifies, its network and
   `wallet_tag` match the restoring wallet, and it parses exactly. A failing
   manifest is ignored, not repaired.
4. Among valid manifests the highest `manifest_sequence` wins; equal
   sequences with different contents are merged by taking each maximum and
   reported as `CONFLICT_MERGED`.
5. The manifest is private backup data: it links EntityIDs to one wallet and
   SHOULD be stored encrypted beside the consignment backups. Its HMAC gives
   integrity, not confidentiality, and it is never a protocol object.

### 2. Gap-limit scan

For `entity' = 0, 1, …` the wallet derives the root key
`m/coin'/entity'/0'/0'` and searches the supplied sources — retained
consignments, genesis payloads, and proof packages — for a genesis whose
`root_xonly` matches and which verifies (root signature, EntityID recompute,
ADR-0009 shape). Registry or discovery hits only locate payloads; validity
comes from verification. The scan stops after `100` consecutive misses
above the highest index known from the manifest or the scan. For each found
identity, each role's next index is one past the highest index whose key
appears in any valid state of its history, scanning each role up to 100
beyond the highest hit.

### 3. Skip-ahead after every restore

```text
S           = 20   if a valid manifest was found, otherwise 100
next_entity = max(manifest next, scan high + 1) + S
next_role   = max(manifest next_role, scan next_role) + S   (per known entity)
```

A restored wallet cannot prove its newest manifest was the last one written,
so it always skips. With rule 2, a manifest restore needs only 20; a
scan-only restore cannot see unpublished drafts and skips 100. Unused
indexes are free; reuse is not.

### 4. Missing history

If a manifest lists a PUBLISHED entity whose genesis or consignment is not
found, the wallet reports `HISTORY_MISSING` for that index: keys are restored,
the identity is not presented as current, and that index is never allocated
again. A new root and EntityID is the only continuity path if the history is
truly lost (ADR-0005).

## Evidence

`tests/vectors/check_index_manifest.py` (Python, unsafe test seed) checks:
latest-manifest selection; rollback to an older manifest; scan-only restore;
a scan with a history gap; a manifest whose published history is missing; and
rejection of a flipped byte, a dropped entry under the old MAC, a wrong
network, unsorted entries, a PUBLISHED entry without an EntityID, and a
foreign `wallet_tag`.

## Required evidence before acceptance

1. An independent Rust implementation of `wallet_tag`, `mac_key`, the HMAC,
   and the restore arithmetic agrees with the vector file.
2. The demo wallet writes a manifest before each derivation in one disposable
   regtest lineage and restores it from the mnemonic plus the consignment
   backup on a clean machine.
3. ~~Maintainer review of the skip values and the always-skip rule.~~ Done
   2026-10-22 on the simulation below.

## Consequences

- Phase 0 item 4 closes on acceptance; the key-derivation profile's
  "Out of scope: restore and discovery" section is replaced by a pointer here.
- ADR-0009's frozen entity-allocation rule is unchanged; this ADR only
  constrains how a restored wallet resumes it.

## Maintainer decisions — 2026-10-22

The maintainer chose a 20-index skip after every restore and asked for it to
be simulated. Evidence:
[`evidence/phase0/restore-skip-simulation-2026-10-22/`](../evidence/phase0/restore-skip-simulation-2026-10-22/RUN.md),
from `scripts/simulate_restore_skip.py` (fixed seed, 20 000 trials per cell,
six scenarios).

- A fixed 20-index skip alone reused an index in 0.07 % of typical restores
  but 31.6 % with poor off-site backups.
- Adding the off-site cap (rule 2) reduced that to 0–1 %, and to zero whenever
  a manifest was restored.
- The remainder came from scan-only restores with many unpublished drafts.
  A 100-index skip and a 100-miss scan gap in that case removed it: zero
  reuses in 120 000 trials, at a mean cost of 19–36 skipped indexes (about 97
  without a manifest) out of 2^31.

**Decision:** keep the 20-index skip after a manifest restore, add the
off-site cap of 20 (rule 2) and the two-copy recommendation, and use a
100-miss scan gap with a 100-index skip after a scan-only restore. The
vector file implements these values. The ADR stays Proposed until checklist
items 1 and 2 are met.
