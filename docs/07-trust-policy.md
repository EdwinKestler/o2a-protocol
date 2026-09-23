# 07 — Trust Policy

## Principle

O2A does not introduce a new blockchain consensus layer for questions such as "is this really Artist X?"

Instead, signed evidence is evaluated under a deterministic, versioned policy.

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

## Result

A verification result should contain:

- subject;
- status;
- policy identifier/hash;
- protocol version;
- evidence references;
- evaluation explanation;
- evaluation time/context where relevant.

Graph-derived reputation should not be introduced until sufficient real evidence exists to validate its behavior.
