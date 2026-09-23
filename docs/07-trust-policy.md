# 07 — Trust Policy

## Principle

O2A uses Bitcoin consensus for RGB identity ordering and single-use seals. It
does not introduce a validator set or blockchain vote for questions such as
"is this really Artist X?"

Each wallet first validates the supplied Bitcoin/RGB identity history, then
evaluates signed evidence under a deterministic, versioned policy.

## Basic form

For subject x:

[
V(x)=1 quad 	ext{if} quad sum_i w_i A_i(x) geq 	heta
]

otherwise:

[
V(x)=0
]

This equation is illustrative. v0.1 should begin with explicit logical rules rather than opaque learned weights.

## Example policy

An artist could satisfy an initial verification policy using one of:

- two independently verified venues;
- one verified venue plus one verified promoter;
- three independently verified artists.

This is an example only, not a frozen production policy.

## Required properties

A policy MUST be:

- versioned;
- content-addressable or hash-identifiable;
- deterministic;
- explainable;
- side-effect free during evaluation;
- explicit about acceptable evidence types;
- explicit about conflicts and revocations.
- explicit about required Bitcoin network, confirmations, reorg context, and
  RGB identity profile;
- explicit about DNS/social observation freshness and source independence;
- able to compare competing name claims without silently creating a global
  first-claim namespace.

## Result

A verification result should contain:

- subject;
- status;
- policy identifier/hash;
- protocol version;
- evidence references;
- identity-state and Bitcoin-anchor references;
- evaluation explanation;
- evaluation time/context where relevant.

Graph-derived reputation should not be introduced until sufficient real evidence exists to validate its behavior.

Consensus in O2A therefore has two precise meanings: Bitcoin nodes agree on the
chain history used by the anchors, and conforming O2A wallets given the same
bounded inputs agree on the deterministic result. No special O2A nodes vote on
the real-world truth of a name claim.
