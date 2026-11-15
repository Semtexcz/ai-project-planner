# Bookvoice-like synthetic fixture

This fixture imitates the observed Bookvoice planning conventions without
copying private source. It is used only in disposable test repositories.

- Task cards exist in state folders, but a folder is not authoritative state.
- `docs/TASK_SEQUENCE.md` is the adopted order/dependency authority.
- `TASK-075` deliberately appears twice with conflicting folder/body/frontmatter
  state.
- A backlog card is not automatically ready.
