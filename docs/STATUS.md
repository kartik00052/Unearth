# Unearth — Status

**Current phase:** 0
**Last updated:** 2026-11-12 by opencode (feat/phase-0-foundations)

## Done
- Repository skeleton, Docker Compose placeholder, config placeholders, Alembic scaffolding,
  first test slot, CI workflow placeholders, and an empty Vite app already exist.
- Phase 0 foundations implemented on `feat/phase-0-foundations`:
  - `docs/STATUS.md` and ADR `0005-sync-db-in-routes`.
  - Runtime/dev dependencies pinned via `uv`; `[dependency-groups].dev` added; `mypy` configured.
  - Minimal router-based API: `GET /api/v1/health` returns `{"status": "ok"}`.
  - Settings via `pydantic-settings` v2 with a cached `get_settings()`.
  - Database foundation: `DeclarativeBase`, session factory, `get_db` dependency, Alembic wired to settings.
  - `docker-compose.yml` for Postgres, Redis, and object storage.
  - OpenAPI export script, `contracts/openapi.json`, and a `Makefile`.
  - uv-based backend CI and frontend CI.

## In progress (claimed by)
- [ ] None.

## Next up (ordered)
1. Human review of the Phase 0 diff and acceptance evidence.
2. Mark Phase 0 complete in this file.
3. Begin Phase 1 — data in (models, connectors, ingestion, profiling, workers, APIs).

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

## Decisions pending
- Object-storage image pinning strategy (see blockers).
- Whether to rename `Agents.md` → `AGENTS.md` and commit its content.
