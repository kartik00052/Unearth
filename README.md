# Unearth

**Unearth undocumented databases and turn them into secure, tested tools for AI agents.**

Unearth is a semantic discovery and governance platform that profiles data sources,
infers business meaning with supporting evidence, generates controlled business tools,
and monitors changes that may affect their correctness.

## Applications

- `backend/` — FastAPI application and domain services.
- `frontend/` — React and TypeScript dashboard.
- `backend/ml/` — model training and evaluation.
- `backend/mcp_runtime/` — MCP tool runtime.
- `docs/` — architecture and engineering decisions.
- `demo/` — demonstration datasets and scripts.

## Development status

Early development. Features are added incrementally.

## Local development

Prerequisites: [uv](https://docs.astral.sh/uv/) and Node.js 22 or newer.

The `Makefile` wraps the common backend tasks (`make test`, `make lint`,
`make typecheck`, `make openapi`). `make` is optional; on Windows run the
equivalent commands directly:

```powershell
# Backend (run from backend/)
uv sync
uv run pytest -q
uv run ruff check .
uv run mypy app
uv run alembic heads
uv run python -m scripts.export_openapi
uv run uvicorn app.main:app --reload

# Frontend (run from frontend/)
npm install
npm run build
```

Configuration is read from environment variables. Copy `.env.example` to `.env`
in the repository root and adjust the values before starting the API.
