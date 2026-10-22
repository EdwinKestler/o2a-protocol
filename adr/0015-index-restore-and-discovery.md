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
2. A manifest is valid only if its HMAC verifies, its network and
   `wallet_tag` match the restoring wallet, and it parses exactly. A failing
   manifest is ignored, not repaired.
3. Among valid manifests the highest `manifest_sequence` wins; equal
   sequences with different contents are merged by taking each maximum and
   reported as `CONFLICT_MERGED`.
4. The manifest is private backup data: it links EntityIDs to one wallet and
   SHOULD be stored encrypted beside the consignment backups. Its HMAC gives
   integrity, not confidentiality, and it is never a protocol object.

### 2. Gap-limit scan

For `entity' = 0, 1, …` the wallet derives the root key
`m/coin'/entity'/0'/0'` and searches the supplied sources — retained
consignments, genesis payloads, and proof packages — for a genesis whose
`root_xonly` matches and which verifies (root signature, EntityID recompute,
ADR-0009 shape). Registry or discovery hits only locate payloads; validity
comes from verification. The scan stops after `G = 20` consecutive misses
above the highest index known from the manifest or the scan. For each found
identity, each role's next index is one past the highest index whose key
appears in any valid state of its history, scanning each role up to `G`
beyond the highest hit.

### 3. Skip-ahead after every restore

```text
next_entity = max(manifest next, scan high + 1) + G
next_role   = max(manifest next_role, scan next_role) + G   (per known entity)
```

A restored wallet cannot prove its newest manifest was the last one written,
so it always skips `G` indexes. Unused indexes are free; reuse is not.

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
3. Maintainer review of `G = 20` and of the always-skip rule.

## Consequences

- Phase 0 item 4 closes on acceptance; the key-derivation profile's
  "Out of scope: restore and discovery" section is replaced by a pointer here.
- ADR-0009's frozen entity-allocation rule is unchanged; this ADR only
  constrains how a restored wallet resumes it.
