# Sync contract (artifact gate)

The synchronization boundary must be explicit. A task may depend on this
artifact instead of inventing a task ID for it.

- Local content is authoritative until a sync transaction commits.
- Conflict resolution is visible to the user.
- No background upload without explicit user action.
