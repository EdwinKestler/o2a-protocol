# 02 — Protocol Kernel

## Responsibility

The kernel is the smallest stable layer. It provides generic state and proof
mechanics without music-application semantics. The v0.1 conformance profile
requires Bitcoin anchoring and RGB client-side validation for identity state.

## Required capabilities

- create/issue protocol objects;
- validate object structure and authorization;
- create state transitions;
- commit canonical objects;
- anchor identity transitions through the versioned Bitcoin commitment method;
- export/import proof packages;
- verify proof-package content integrity, publisher authorization, tagged-hash
  domain, and BIP340 package signature;
- preserve historical validation across controller rotation;
- validate the BIP340 root/genesis binding;
- validate the RGB identity schema, consignment history, seals, anchors, and
  current controller/recovery state;
- distinguish root, controller, recovery, Nostr-publication, and seal key roles
  from payment and Pubky keys;
- recompute each named seal's deterministic P2TR script from committed state
  and validate the seal-creating transaction and proof;
- require an explicit Bitcoin-view observation before reporting a current seal
  unspent, and validate any closing spend at anchor depth under the same reorg
  rule;
- validate key role and authorization capability as separate signed fields;
- validate object-specific BIP340 tagged-hash domains and reject cross-domain
  signature reuse;
- import, hash-check, and export public identity proof packages;
- expose explicit Bitcoin confirmation and reorg context; and
- validate EVENT and ALBUM identity lifecycles like other entities.

## Conceptual API

```text
issue()
transition()
validate()
prove()
consume_seal()
anchor()
export_consignment()
import_consignment()
```

Names are provisional until implementation.

## Canonicalization

Any object that is signed, hashed, or committed MUST first be serialized using one explicitly versioned canonical encoding.

Never hash ordinary application JSON directly.

[
id(x)=H(version || type || canonical(x))
]

## Bitcoin/RGB boundary

Bitcoin and RGB implementation details live behind versioned interfaces so the
kernel does not depend on a particular explorer, indexer, database, or web API.
They are nevertheless required inputs for identity lifecycle validation.

The kernel consumes authenticated Bitcoin headers/proofs and complete RGB
client-side data. It MUST fail closed when the expected network, contract,
schema, outpoint, witness, commitment, confirmations, or consignment is missing
or mismatched. A transaction ID or public key alone is insufficient.

## Initial deployment path

```text
local deterministic vectors → Bitcoin regtest + RGB → public test network → mainnet
```

The same protocol test vectors must pass in every environment. Mainnet remains
held until version-pinned regtest and public-test evidence cover reorgs,
consignment loss, controller recovery, revocation, and independent verifier
agreement.
