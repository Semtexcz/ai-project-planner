# ADR-001: Semantic core independence

## Status

Accepted historical design decision.

## Context

Presentation and storage formats evolve faster than the process semantics.

## Decision

The semantic core owns definitions, invariants and units. Presentation,
serialization and reporting adapt to the core and may not introduce normative
meaning.

## Consequences

- A diagram is a view, not an authority.
- Storage choices are replaceable.
- Semantic review is required before a presentation feature can claim meaning.
