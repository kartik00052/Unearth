#!/usr/bin/env python3
"""Usage: python scripts/check_structure.py --phase 2   (checks phases 0..2)
          python scripts/check_structure.py --all"""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def pkg(base, modules):
    """A Python package: __init__.py plus each module."""
    return [f"{base}/__init__.py"] + [f"{base}/{m}.py" for m in modules]

PHASES = {
0: [
    "README.md", "Makefile", "docker-compose.yml", ".env.example", ".gitignore",
    ".github/workflows/ci-backend.yml", ".github/workflows/ci-frontend.yml",
    "backend/pyproject.toml", "backend/Dockerfile", "backend/alembic.ini",
    "backend/alembic/env.py", "backend/alembic/versions/",
    "backend/app/main.py",
    *pkg("backend/app/core", ["config", "logging", "errors", "deps", "security"]),
    *pkg("backend/app/db", ["base", "session"]),
    *pkg("backend/app/api", ["router"]),
    *pkg("backend/app/api/v1", ["health"]),
    "backend/tests/conftest.py", "backend/tests/unit/", "backend/tests/integration/",
    "frontend/package.json", "frontend/vite.config.ts", "frontend/tsconfig.json",
    "frontend/index.html", "frontend/src/main.tsx",
],
1: [
    *pkg("backend/app/connectors", ["base", "registry", "introspection", "sql_connector", "csv_duckdb_connector"]),
    *pkg("backend/app/ingestion", ["storage", "file_sniffer", "type_inference", "sanitizers", "loader"]),
    *pkg("backend/app/profiling", ["profile_runner", "sampler", "column_stats", "distributions",
                                   "key_detection", "relationship_discovery", "pii_detector"]),
    *pkg("backend/app/models", ["source", "upload", "profile"]),
    *pkg("backend/app/schemas", ["common", "source", "upload", "profile", "job"]),
    *pkg("backend/app/services", ["source_service", "upload_service", "profiling_service"]),
    *pkg("backend/app/api/v1", ["sources", "uploads", "profiles", "jobs"]),
    *pkg("backend/app/workers", ["arq_worker"]),
    "backend/app/workers/jobs/profile_job.py",
    "backend/tests/fixtures/messy.csv",
],
2: [
    "frontend/src/app/App.tsx", "frontend/src/app/router.tsx", "frontend/src/app/providers.tsx",
    "frontend/src/api/client.ts", "frontend/src/api/generated/",
    "frontend/src/features/sources/pages/SourcesPage.tsx",
    "frontend/src/features/upload/pages/UploadPage.tsx",
    "frontend/src/features/profile/pages/ProfilePage.tsx",
    "frontend/src/components/ui/", "frontend/src/components/common/",
    "contracts/openapi.json",
],
3: [
    *pkg("backend/app/inference", ["embeddings", "vector_store"]),
    *pkg("backend/app/inference/classifier", ["model", "features", "predictor", "calibration"]),
    *pkg("backend/app/inference/graphs", ["state", "column_meaning_graph"]),
    *pkg("backend/app/inference/nodes", ["gather_evidence", "propose_meaning", "verify_meaning"]),
    "backend/app/api/v1/semantics.py", "backend/ml/training/train_classifier.py",
    "frontend/src/features/review/pages/ReviewQueuePage.tsx",
],
4: [
    *pkg("backend/app/compiler", ["tool_spec", "sql_validator", "tool_generator", "mcp_generator"]),
    *pkg("backend/app/policy", ["fga_client", "rules", "masking", "permission_tester"]),
    "backend/mcp_runtime/server.py", "backend/app/api/v1/tools.py", "backend/app/api/v1/policies.py",
    "frontend/src/features/tools/pages/ToolsPage.tsx",
    "frontend/src/features/policies/pages/PoliciesPage.tsx",
],
5: [
    *pkg("backend/app/evals", ["runner", "golden_builder", "metrics"]),
    *pkg("backend/app/drift", ["snapshot", "schema_diff", "data_drift", "impact"]),
    *pkg("backend/app/lineage", ["graph_builder", "impact_analysis", "exporter"]),
    "frontend/src/features/drift/pages/DriftPage.tsx",
    "frontend/src/features/lineage/pages/LineagePage.tsx",
    ".github/workflows/evals-gate.yml",
],
6: [
    *pkg("backend/app/reports", ["discovery_report", "pdf_renderer"]),
    "infra/k8s/", "infra/helm/archaeologist/Chart.yaml", "infra/otel/otel-collector.yaml",
    "docs/architecture.md", "docs/runbook.md",
    "backend/tests/e2e/",
],
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    upto = max(PHASES) if a.all else a.phase

    missing = 0
    for ph in range(upto + 1):
        print(f"\n== Phase {ph} ==")
        for item in PHASES[ph]:
            p = ROOT / item
            ok = p.is_dir() if item.endswith("/") else p.is_file()
            if not ok:
                missing += 1
                print(f"  MISSING  {item}")
        if missing == 0:
            print("  all present")

    # Rule: every folder under backend/app/ that holds .py files needs __init__.py
    print("\n== Package check ==")
    bad = 0
    for d in (ROOT / "backend/app").rglob("*"):
        if d.is_dir() and d.name != "__pycache__" and list(d.glob("*.py")) and not (d / "__init__.py").exists():
            bad += 1
            print(f"  NO __init__.py  {d.relative_to(ROOT)}")
    if not bad:
        print("  ok")

    # Rule: files in the wrong place
    print("\n== Misplaced file check ==")
    wrong = [p for p in (ROOT / "backend").rglob("*.tsx")] + [p for p in (ROOT / "frontend/src").rglob("*.py")]
    for p in wrong:
        print(f"  WRONG PLACE  {p.relative_to(ROOT)}")
    if not wrong:
        print("  ok")

    print(f"\nSummary: {missing} missing, {bad} packages without __init__.py, {len(wrong)} misplaced")
    sys.exit(1 if (missing or bad or wrong) else 0)

if __name__ == "__main__":
    main()