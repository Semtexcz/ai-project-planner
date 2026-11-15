---
schema_version: 1
kind: decision
id: DEC-000
owner: product_owner
scope:
  topic: State the decision topic.
  rationale: Explain why a decision is needed and the reasoning.
  options:
    - Describe a considered option and its consequence.
  choice: State the chosen option.
  targets: []
  authority: Replace with the accountable authority for this decision.
  supersedes: []
execution:
  state: proposed
  actor: ""
  decided_at: ""
  approval_source: ""
  applied_revision: null
---

# Decision

A decision records a human disposition. The agent may author a `proposed`
record; only an explicit human decision makes it `accepted`. Record the human
actor, date, and the original approval source (for example a reviewed pull
request URL or a retained session instruction).

`targets` binds approval to exact record content: each entry names a record and
the SHA-256 digest of its `scope`. Changing a normative field invalidates that
approval. `delegation` is optional and bounded; a delegated decomposition must
still record its conformance rationale and the authorizing decision.

The checker verifies bindings and fields. It cannot prove human identity or
consent; Git review and human process supply that trust boundary.
