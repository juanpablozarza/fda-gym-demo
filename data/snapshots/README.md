# Snapshots

This public demo does **not** ship gzip openFDA bodies. Clone size stays small, and the published sheet is still in [`data/tasks/public/`](../tasks/public/).

`drugs.txt` and `pilot.txt` list the 150-name `2026-10-15` exam universe (public freeze, not a private holdout).

Offline pytest uses JSON fixtures under `tests/env/fixtures/`. Tests that need a DiskSnapshot freeze skip when `data/snapshots/2026-10-15/` is absent.

If you already have that freeze from your own recording, point the env at it:

```bash
export FDAGYM_SNAPSHOT_DIR=/path/to/snapshots   # directory that contains 2026-10-15/
uv run python -m fdagym.openfda verify
```

`python -m fdagym.openfda` does not download anything. It only locates or verifies a freeze you already have.
