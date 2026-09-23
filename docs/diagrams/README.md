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

## Design rules reflected in these diagrams

- lower layers never depend on upper layers;
- EntityID is the generic protocol primitive;
- signed claims and attestations are evidence, not truth by themselves;
- verification is a deterministic policy result over evidence;
- registries are rebuildable projections, not the source of truth;
- GatePass and SplitNight remain downstream application modules;
- scale comes from adding evidence, registries, and applications without rewriting identity.
