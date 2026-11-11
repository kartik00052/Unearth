# Unearth — Status

**Current phase:** 0
**Last updated:** 2026-11-12 by opencode (feat/phase-0-foundations)

## Done
- Phase 0 foundations implemented on `feat/phase-0-foundations`:
  - `docs/STATUS.md` and ADR `0005-sync-db-in-routes`.
  - Dev dependencies moved to `[dependency-groups].dev`; `mypy` (strict, pydantic plugin) and
    ruff isort config added; `uv.lock` committed.
  - Minimal router-based API: `GET /api/v1/health` returns `{"status": "ok"}`.
  - Settings via `pydantic-settings` v2 with a cached `get_settings()`; `.env.example` documents
    the nine variables and the root `.env` is resolved from the config file location.
  - Database foundation: `DeclarativeBase`, session factory, `get_db` dependency, and Alembic
    reading the URL from settings (not the ini file).
  - OpenAPI export script (`backend/scripts/export_openapi.py`), generated `contracts/openapi.json`,
    a `Makefile`, and README local-development commands.
  - uv-based backend CI (lint, types, tests) and Node 22 frontend CI; empty `ci.yml` removed.
  - `.pre-commit-config.yaml` (ruff-check, ruff-format, gitleaks) and normalized formatting.
- Not done: `docker-compose.yml` is still an empty placeholder (Task 0.6 deferred at the human's request).

## In progress (claimed by)
- [ ] None.

## Next up (ordered)
1. Author `docker-compose.yml` (Postgres 16, Redis 7, MinIO) with healthchecks, named volumes,
   and loopback-bound ports; verify `docker compose config -q` (Task 0.6, deferred).
2. Human review of the Phase 0 diff and acceptance evidence.
3. Mark Phase 0 complete in this file.
4. Begin Phase 1 — data in (models, connectors, ingestion, profiling, workers, APIs).

## Blockers / questions for the human
- MinIO community images were removed from Docker Hub (~Sep 2026) and `quay.io` now requires
  auth. Compose uses `cgr.dev/chainguard/minio:latest` (Chainguard's fork) as agreed; this image
  only publishes a `latest` tag, so it is not version-pinned. Revisit if a pinned, maintained
  S3-compatible image is preferred.

## Known issues (found, not fixed)
- The tracked agent-instructions file is named `Agents.md` (not `AGENTS.md`) and its full
  content is uncommitted in the working tree. Case-sensitive filesystems (Linux CI) would treat
  `AGENTS.md` and `Agents.md` as different paths.
- `scripts/check_structure.py` is present but untracked in git.
- An empty `docs/` ADR set (`0001-modular-monolith.md`, `0002-postgresql-as-metadata-store.md`)
  differs from the ADR names referenced in AGENTS.md Section 19; both files are 0 bytes.
- `frontend/src` still contains the Vite template (`App.tsx`, `App.css`, unused assets); cleanup
  is planned for Phase 2.
- `frontend/tsconfig.app.json` does not enable `"strict": true`.
- `pre-commit` is not in `[dependency-groups].dev`, so `.pre-commit-config.yaml` cannot be run
  yet without installing it separately (adding it is a dependency change pending approval).

## Decisions pending
- Object-storage image pinning strategy (see blockers).
- Whether to rename `Agents.md` → `AGENTS.md` and commit its content.
