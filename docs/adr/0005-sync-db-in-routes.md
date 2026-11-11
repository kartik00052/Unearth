# 0005 — Synchronous SQLAlchemy sessions in FastAPI routes

Status: accepted
Date: 2026-11-12

## Context

Unearth's API is built on FastAPI. FastAPI supports both `async def` endpoints with async
database drivers and plain `def` endpoints with synchronous drivers. The stack (SQLAlchemy 2.x,
`psycopg` 3) can be used either way, but mixing styles across a large codebase causes confusion
and subtle bugs (blocking the event loop, duplicate session handling patterns).

Heavy work in Unearth — profiling, inference, compilation, evals, drift, reports — is long
running and must not run inside request handlers regardless of the sync/async choice. That work
belongs in background workers (ARQ).

## Decision

FastAPI endpoints are plain `def` functions that use **synchronous** SQLAlchemy sessions. A
request handler does only: validate input → call a service → return a response. Any long or
heavy work is dispatched to an ARQ worker and tracked as a job.

Concretely:
- `backend/app/db/session.py` builds a synchronous engine and `sessionmaker` from settings.
- `backend/app/core/deps.py` provides a `get_db` dependency that yields a `Session` and closes it.
- Services own transaction boundaries; routers contain no SQL.

## Alternatives considered

- **Async SQLAlchemy + `asyncpg`/`psycopg` async everywhere:** rejected for now. It complicates
  the codebase, requires async-aware services/repositories throughout, and provides little
  benefit given that heavy work already moves to workers. Would require its own ADR to adopt.
- **Mixed sync/async per endpoint:** rejected. Two patterns for the same concern invite mistakes
  (accidentally blocking the event loop) and make review harder.

## Consequences

- Simpler, uniform data-access code; easier onboarding and review.
- Scale comes from ARQ workers and horizontally replicated API replicas, not from async I/O in
  handlers.
- Every request handler must stay thin; heavy work must be offloaded to a job, or the API will
  block.
- If a future feature genuinely needs async I/O in a handler, it requires a new ADR rather than
  an ad-hoc exception.
