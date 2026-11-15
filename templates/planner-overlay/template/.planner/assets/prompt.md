# Derived execution prompt asset

NEXT fills this structure from an approved task contract. Values in angle
brackets are replacements, never instructions to invent content. A saved prompt
must also carry a derived-artifact header and source manifest; this blank asset
is not authority and must not be executed.

```text
DERIVED EXECUTION PROMPT - <TASK-ID>, not project authority
Sources: <repository>, <commit/working-tree state>, <task authority + scope digest>
Recommended model: DeepSeek V4.1 Flash; reasoning HIGH.
Escalation: DeepSeek V4 Pro HIGH only under the recorded escalation policy.

Read existing project/agent instructions first, then these sources:
<authoritative task, requirement clauses, parent milestone outcome, relevant ADRs>
<distinguish normative context from historical/background references>

Objective and rationale: <verbatim or faithful approved contract>
Trace: VIS -> OBJ/OUT -> REQ -> MS -> [WP] -> TASK
Deliver: <exact deliverables and intended files/components>
Scope includes: <approved list>
Scope excludes: <approved list>
Constraints: <approved domain/architecture/tool/project constraints>
Prerequisites: <refs, satisfaction evidence, unresolved limits>
Acceptance and verification: <criterion IDs, method, expected evidence, reviewer>

Work only within this contract. Do not infer additional product requirements.
Reread current sources before work; stop if normative scope or approval changed.
Stop before <specific consequential action requiring approval>.
If a dependency fails, authority conflicts, or requirements are ambiguous,
report evidence and propose a planning change; do not approve it yourself.

Return: changed artifacts; each acceptance criterion's result and evidence;
verification actually performed and subject revision; unrun checks/limitations;
remaining risks; requested review and any human acceptance needed.
Do not claim done/accepted solely because work was produced or checks were planned.
```

For a non-software task, replace code-test expectations with the verification
method the approved task actually requires: diagram inspection, semantic
counterexample, engineering analysis, experiment, package build, API test or
human-only review. A model recommendation does not change the deliverable or
authorize escalation expense.
