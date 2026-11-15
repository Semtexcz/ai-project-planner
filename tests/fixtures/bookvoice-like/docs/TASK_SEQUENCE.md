# Task sequence

Adopted order and dependency authority for this fixture. A card's folder does
not override this file or its own explicit prerequisites.

1. TASK-019 - access model foundation
2. TASK-037 - storage interface
3. TASK-073 - local sync engine
4. TASK-074 - conflict detection
5. TASK-075 - cloud sync adapter (requires 073, 074, 019, 037)
6. TASK-076 - offline backfill (backlog; related to 075, not a prerequisite)

`Related` is not a blocking dependency. `docs/contracts/sync-contract.md` is an
artifact gate for TASK-075, not a task identity.
