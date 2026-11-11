.PHONY: help test lint typecheck openapi

help:
	@echo "Available targets:"
	@echo "  test       Run the backend test suite"
	@echo "  lint       Run ruff on the backend"
	@echo "  typecheck  Run mypy on the backend app package"
	@echo "  openapi    Regenerate contracts/openapi.json"

test:
	cd backend && uv run pytest -q

lint:
	cd backend && uv run ruff check .

typecheck:
	cd backend && uv run mypy app

openapi:
	cd backend && uv run python -m scripts.export_openapi
