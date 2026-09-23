# 02 — Protocol Kernel

## Responsibility

The kernel is the smallest stable layer. It provides generic state and proof mechanics without domain semantics.

## Required capabilities

- create/issue protocol objects;
- validate object structure and authorization;
- create state transitions;
- commit canonical objects;
- anchor commitments through supported adapters;
- export/import proof packages;
- verify proof-package integrity;
- preserve historical validation across controller rotation.

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

## Adapter boundary

Bitcoin/RGB implementation details live behind adapters. Entity, Claim, Attestation, and Policy semantics must not depend on a particular explorer, database, or web API.

## Initial deployment path

```text
local dev → Bitcoin regtest → public test network → mainnet
```

The same protocol test vectors must pass in every environment.
