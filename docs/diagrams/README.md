# O2A Protocol Diagrams

This folder contains the architecture and flow diagrams proposed during the initial O2A protocol design thread.

All diagrams use Mermaid so they render directly in GitHub and remain editable/version-controlled.

## Contents

1. [Modular layered architecture](./01-modular-layered-architecture.md)
2. [End-to-end protocol flow](./02-end-to-end-protocol-flow.md)
3. [Identity and attestation evidence graph](./03-identity-attestation-evidence-graph.md)
4. [Bootstrap and scale roadmap](./04-bootstrap-and-scale.md)
5. [Software stack architecture](./05-software-stack-architecture.md)
6. [Development-to-public-release pipeline](./06-deployment-pipeline.md)
7. [Hello-World pilot](./07-hello-world-pilot.md)
8. [O2A ecosystem and namespace map](./08-o2a-ecosystem-map.md)
9. [Protocol framework and authority boundaries](./09-protocol-framework.md)

## Design rules reflected in these diagrams

- lower layers never depend on upper layers;
- every EntityID is rooted in a dedicated BIP340 key and an RGB lifecycle
  anchored to Bitcoin;
- artist, venue, promoter, label/organization, event, and album identities
  each have their own public key;
- owner wallets retain seeds, keys, consignments, attestations, and proof
  packages, with a full Bitcoin node or an explicitly labeled light mode;
- human-readable names are non-exclusive evidence-backed claims;
- signed claims and attestations are evidence, not truth by themselves;
- every signature uses a purpose-specific domain and an authorized key purpose;
- public proof packages are immutable, content-addressed, and independently
  retrievable; transport and hosting never become identity authority;
- verification is a deterministic policy result over evidence;
- registries are rebuildable projections, not the source of truth;
- GatePass and SplitNight remain downstream application modules;
- scale comes from adding evidence, registries, and applications without rewriting identity.
