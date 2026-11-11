"""Export the FastAPI OpenAPI schema to ``contracts/openapi.json``.

Run from the ``backend`` directory:

    uv run python -m scripts.export_openapi

The output is generated; never edit ``contracts/openapi.json`` by hand.
"""

import json
from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "contracts" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
