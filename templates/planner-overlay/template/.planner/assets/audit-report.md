# Audit report template

Derived artifact. It is not authority and may not be edited to add scope.

```markdown
# Planning audit - <date>

- Source revision: <commit or working-tree fingerprint>
- Approved baseline: <decision/commit reference>
- Review scope: <paths/IDs reviewed>
- Unverified coverage: <external or unreadable sources; or "none">

## Deterministic results

Command:

    uv run --script .planner/scripts/check_planning.py --project . --format json --source-revision <revision>

Result: <errors/warnings/manual-review counts; checker exit code>

## Findings

### <ID> - <severity: blocking|warning|information> - <short title>

- Evidence: <ID/path/lines and observed fact>
- Affected chain: <VIS/OBJ/OUT/REQ/MS/TASK/evidence>
- Confidence: <high|medium|low>
- Owner: <role>
- Proposed repair: <bounded action>
- Required human decision: <decision or "none">
- Recommended operation: <CHANGE|PLAN|NEXT|none>

## Reverse-coverage summary

- Delivered work without an approved trace: <IDs or none>
- Approved requirements without milestones: <IDs or none>
- Outcomes without outcome evidence: <IDs or none>
- Tasks done without accepted evidence: <IDs or none>

## Strategic review limitations

<What structural checks cannot establish; suspected semantic conflicts that need adjudication.>

## Recommendation

<One bounded next planning/review action. No automatic repair was performed.>
```
