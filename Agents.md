# AGENTS.md — Unearth: Rules + Workflow for Coding Agents

> **Read this whole file once at the start of every session.** Then re-read the sections named in the Task Protocol (Section 12) before each task.
> Applies to every coding agent (Antigravity, Claude Code, Codex, Cursor, or any other) working in this repo.
> If your tool expects a different filename (for example `GEMINI.md` or `CLAUDE.md`), copy this file to that name. Keep this file as the single source of truth.

---

## 0. How to use this file

**Priority order when instructions conflict:**
1. The human's latest explicit instruction in chat
2. This file
3. `docs/` (STATUS.md, data-model.md, ADRs, security-model.md)
4. Code already in the repo
5. Your own assumptions (lowest, and you must label them as assumptions)

**Reading protocol (to save context and avoid ignoring rules):**
- Always apply: Sections 1, 2, 3, 12, 13.
- Read when relevant: backend work → 5, 6, 7, 8, **21**; frontend work → 9, **22, 23**; a feature touching both → **24**; ML or LangGraph → 10, 11, 21.7; bugs or breakage → **25**; planning or phases → 4; reviewing someone's work → **26**.
- If you are unsure which section applies, read Section 12 first.

**If this file is wrong or outdated:** do not silently work around it. Tell the human which rule is wrong, propose a fix, and wait.

---

## 1. Project snapshot

**Name:** Unearth

**One-line pitch:** Unearth turns an undocumented legacy database (or a folder of CSV exports) into a versioned, tested, permissioned **semantic contract** for AI agents, and re-validates that contract whenever the data changes.

**Problems it solves**
1. Discovering what cryptic legacy columns (like `CUST_ST_CD`) mean takes weeks of manual work.
2. Free-form text-to-SQL is unsafe and inaccurate; agents guess joins and meanings.
3. Silent schema and data drift makes agents answer from wrong data.
4. Customer security reviews block deployment unless access control is provable.

**Inputs:** read-only database connection (PostgreSQL, MySQL, SQL Server), uploaded CSV/Excel files, optional manuals (PDF), optional business questions, optional role/permission matrix, optional glossary.

**Outputs delivered to the customer**
1. Data dictionary: plain-English meanings, evidence, confidence
2. Generated MCP server and REST API with typed, read-only, tested tools
3. Permission policy files and a permission tester
4. Eval suite with pass rates
5. Discovery and security-review reports (PDF/HTML)
6. Drift dashboard with alerts and tool status
7. Lineage graph and impact analysis

**Core pipeline:** Connect/Upload → Profile → Infer meaning (rules → PyTorch classifier → LLM → human review) → Approve → Compile typed tools → Enforce policy → Evaluate → Watch for drift → Re-validate.

**Non-goals (do NOT build these)**
- A general chatbot or generic "chat with your data" UI
- Write access to customer databases (everything is read-only)
- Free-form, unvalidated SQL execution by agents
- Features beyond the current phase (see Section 4)

---

## 2. GOLDEN RULES (non-negotiable)

These exist to stop hallucination and quiet damage. Breaking one is a failure even if the code "works".

### 2.1 Never invent
1. **Never invent** libraries, functions, class names, method signatures, CLI flags, config keys, environment variables, file paths, API endpoints, database columns, or package versions.
2. **Verify before use.** For any third-party API you are not 100% sure about, check it in this order:
   1. The installed package itself: `pip show <pkg>`, `python -c "import x; help(x.y)"`, read the source in the virtualenv, or `npm ls <pkg>` and its `.d.ts` types.
   2. The repo's own usage of it (`grep` the codebase).
   3. Official documentation via web search, matching the **installed version**.
   4. If still unsure, write `UNVERIFIED:` in your plan or report and ask the human. Do not guess.
3. **Libraries in this stack change fast** (LangGraph, MCP SDK, Docling, OpenFGA SDK, Pydantic, SQLAlchemy, TanStack Query, React Router, Tailwind). Your memory of their APIs may be outdated. Always check the installed version first (Section 13 lists known hotspots).
4. **If you cannot find it, say so.** "I could not verify X" is a good answer. A confident wrong answer is the worst answer.

### 2.2 Read before you write
5. Open and read every file you will edit. Read its neighbours and its tests.
6. `grep` for an existing implementation before creating a new one. No duplicate helpers.
7. Never edit from memory of how a file "probably" looks.
8. When you claim something about code behaviour, cite `path:line`.

### 2.3 Stay in scope
9. **One task = one small, reviewable diff.** No drive-by refactors, renames, or formatting sweeps.
10. **Only create files that exist in the planned structure** (Section 5). Do not invent new top-level folders or move or rename existing ones without an approved ADR.
11. **Do not work ahead of the current phase** (Section 4). Read `docs/STATUS.md` to find it.
12. **Do not add dependencies** without asking. When asked to add one, state: why, the alternative in the standard library or existing stack, license, and maintenance health.
13. **Do not touch**: `.env` (real secrets), `contracts/openapi.json` and `frontend/src/api/generated/` (generated only), already-applied Alembic migrations, `node_modules`, `.git`.

### 2.4 No fake success
14. **Never claim tests pass, a build works, or a feature is done unless you ran the command and saw the real output.** Paste the actual result (or the key lines of it). If you cannot run it, say "NOT RUN" and why.
15. **No fake implementations.** Unfinished functions must `raise NotImplementedError("reason")`. Never return hardcoded or made-up data from a real code path.
16. **No fake tests.** Every test must assert real behaviour. Never write tests that assert nothing, always pass, or only check that a mock was called with itself.
17. **Never weaken, skip, or delete a failing test or check to make CI pass.** Fix the cause. If the test is wrong, explain why and get approval.
18. **No silent failure.** No bare `except:`, no `except Exception: pass`, no swallowed errors. Catch specific errors, log with context, and re-raise or return a typed error.
19. **No invented numbers.** Never state accuracy, latency, cost, or coverage figures that were not produced by a command in this repo. Cite the file or run that produced them.

### 2.5 Safety
20. **No secrets in code, logs, tests, commits, or chat output.** Use environment variables. `.env.example` lists variable names only.
21. **Customer data never leaves the system unmasked.** Only masked samples or statistics may reach any LLM. See Section 7.4.
22. **All source-database access is read-only**, through a dedicated read-only role, and every SQL string is validated (Section 7.3).
23. **Every endpoint that returns customer-derived data must enforce authentication and authorization** and write an audit record.

### 2.6 Quality
- **UI must be visually checked, not just compiled.** A passing build does not mean a good screen. Follow Section 23.2 or write `NOT RUN`.
- **Do not ship generic-looking UI.** Check every screen against the "What to avoid" list (Section 22.2).
- **Backend work is not done at "it runs".** It is done when errors, limits, timeouts, idempotency, authorization, and observability are handled (Section 21).

### 2.7 Honesty
24. When blocked, uncertain, or when the task is ambiguous: **stop and ask** (Section 14). Do not silently choose.
25. When you make an assumption, list it explicitly in your plan and in your final report.
26. When you find a bug or inconsistency outside your task, **report it; do not fix it silently.**
27. If you made a mistake, say so plainly, state what is affected, and propose the fix.

---

## 3. Source of truth and where facts live

| Question | Authoritative source | Never use |
|---|---|---|
| What does the API look like? | Running FastAPI app → `contracts/openapi.json` (generated) | Hand-written guesses |
| What are the DB tables and columns? | `backend/app/models/` and Alembic migrations, summarised in `docs/data-model.md` | Memory of earlier tasks |
| What phase are we in? | `docs/STATUS.md` | Assumption |
| Why was a design decision made? | `docs/adr/` | Guessing intent |
| Which versions of libraries are installed? | `backend/pyproject.toml`, `frontend/package.json`, lock files | Training-data memory |
| What env vars exist? | `.env.example` and `backend/app/core/config.py` | Inventing names |
| Domain terms | Section 6 of this file | Synonyms you invent |
| Security rules | Section 7 and `docs/security-model.md` | Convenience |

**If two sources conflict, stop and report the conflict. Do not pick one silently.**

---

## 4. Phases and the work to do

Work strictly in order. Each phase has **deliverables** and **acceptance criteria**. A phase is done only when every acceptance item is demonstrated with real command output.

### Phase 0 — Foundations
**Deliverables:** repo skeleton, Docker Compose (Postgres, Redis, MinIO), config via environment, health endpoint, Alembic set up with one head, first test, CI workflows (`ci-backend.yml`, `ci-frontend.yml`), pre-commit, empty Vite app building.
**Acceptance:**
- `python scripts/check_structure.py --phase 0` reports nothing missing
- `pytest -q` passes (at least the health test)
- `ruff check .` clean; `alembic heads` shows exactly one head
- `npm run build` succeeds in `frontend/`
- `docker compose config -q` is valid
- CI is green on the first commit

### Phase 1 — Data in (backend only)
**Deliverables:**
- Models + migrations: `users`, `sources`, `uploads`, `jobs`, `profiles` (tables, columns, relationships)
- `connectors/`: `SourceConnector` interface; SQL connector (read-only, introspection of tables/columns/keys); CSV/Excel connector via DuckDB
- `ingestion/`: file sniffing (encoding, delimiter, header), type inference, sanitizers (size/type limits, CSV-injection), storage in MinIO, streaming loader
- `profiling/`: column stats, distributions, null rates, key candidates, relationship (candidate foreign key) discovery via value overlap, PII detection
- ARQ worker running profiling jobs; job status API
- API: `POST /sources`, `POST /sources/{id}/test`, `POST /uploads`, `GET /profiles/{id}`, `GET /jobs/{id}`
**Acceptance:**
- Fixture `tests/fixtures/messy.csv` profiles to exactly the expected stats (assert real values)
- Relationship discovery finds the known foreign keys in the demo dataset and reports no more than the expected false positives (set the threshold in the test, not by tuning the test)
- A file larger than memory-safe limits is streamed, not loaded whole (test with a generated large file)
- Wrong encoding, mixed date formats, quoted newlines and formula-injection cells (`=`, `+`, `-`, `@`) each have a test
- All queries to a source run as a read-only role (test that a write attempt fails)

### Phase 2 — First screens
**Deliverables:** design tokens in `src/index.css` (Section 22.3) and an approved design plan for the app shell, generated API client, app shell with context bar and command palette, `sources`/`upload` (the "Add data" surface with chunked upload and progress), `profile` screens, job polling hook.
**Acceptance:**
- `make openapi && make client` regenerates cleanly with no manual edits
- Playwright e2e: upload CSV → see profile results
- Every data view has loading, empty, error, and large-data states
- Screenshots at 1440/1024/390 widths reviewed against Section 22.2; keyboard-only pass and axe check done (Section 23.2)
- `tsc` strict and ESLint clean

### Phase 3 — Meaning inference + review
**Deliverables:** demo ground truth (`demo/ground_truth.yaml`), PyTorch column semantic-type classifier (`backend/ml/`), calibration, LLM gateway with structured output, LangGraph column/table meaning graphs with human-in-the-loop pause, semantics API, review UI.
**Acceptance:**
- Classifier trained with a **schema-level split** (no schema appears in both train and test) and evaluated by a script that writes metrics to `docs/results/`
- Calibration measured (e.g., reliability and expected calibration error) and reported by script output
- Every proposed meaning carries evidence and a confidence derived from classifier + verifier agreement (never from the LLM's self-reported confidence)
- "Unknown" is returned when evidence is insufficient
- Human approvals/corrections persist and are used as training signal later

### Phase 4 — Tools, policy, MCP
**Deliverables:** tool spec + compiler, typed parameterised query templates, `sqlglot` validator, generated REST + MCP server, OpenFGA authorization model, row/column filters, masking, permission tester (automated leak tests), tools + policies screens.
**Acceptance:**
- Generated tools never execute unvalidated SQL
- Adversarial permission tests (prompt-injection-style inputs, cross-tenant requests, column smuggling) produce **zero leaks** in the test suite
- An MCP client can connect to the generated server and list and call tools (integration test)
- Tool versions are immutable once approved

### Phase 5 — Evals, drift, lineage
**Deliverables:** eval generation + runner (Promptfoo export), drift snapshots, schema diff, data-drift stats (PSI, KS), embedding drift, impact analysis, scheduler, alerts, lineage graph (Postgres tables + NetworkX + React Flow), `evals-gate.yml`.
**Acceptance:**
- `demo/inject_drift.py` changes are detected with measured precision and recall (script output)
- Impact analysis lists exactly the affected tools/evals for an injected change (assert the set)
- Drifted tools are marked **unsafe** until re-approved
- Eval gate fails CI when a regression is introduced (demonstrate with a deliberate regression, then revert)

### Phase 6 — Production readiness
**Deliverables:** discovery and security reports, OpenTelemetry + Langfuse + Grafana, Kubernetes + Helm, load tests (k6 or Locust), runbook, e2e suite, demo script.
**Acceptance:** documented p95 latency and throughput from real load-test runs; runbook tested by following it from scratch; full e2e onboarding passes.

> **Do not start Phase N+1 until the human marks Phase N complete in `docs/STATUS.md`.**

---

## 5. Repository structure and placement rules

The structure is fixed. **Do not move, rename, or add top-level folders without an ADR.**

```
Unearth/
├── AGENTS.md  README.md  Makefile  docker-compose.yml  .env.example
├── .github/workflows/        # ci-backend.yml  ci-frontend.yml  evals-gate.yml  release.yml
├── contracts/                # GENERATED openapi.json, semantic-contract.schema.json
├── docs/                     # STATUS.md  architecture.md  data-model.md  security-model.md  runbook.md  adr/  results/
├── demo/                     # uglify_schema.py  inject_drift.py  ground_truth.yaml  sample_questions.yaml  csv/
├── infra/                    # docker/ postgres/ otel/ prometheus/ grafana/ openfga/ k8s/ helm/unearth/
├── scripts/                  # check_structure.py (repo-level helper scripts)
├── backend/
│   ├── app/
│   │   ├── core/ db/ models/ schemas/ api/v1/ services/
│   │   ├── connectors/ ingestion/ profiling/
│   │   ├── inference/ (llm/ prompts/ classifier/ nodes/ graphs/)
│   │   ├── compiler/ policy/ evals/ drift/ lineage/ reports/ workers/
│   ├── ml/                   # training code, NOT imported by the API
│   ├── mcp_runtime/          # the server customers run
│   ├── scripts/              # export_openapi.py, seed_demo.py, ...
│   ├── alembic/  tests/ (unit, integration, e2e, fixtures)
└── frontend/
    └── src/ app/ api/ (generated/) features/ components/ (ui/, common/) hooks/ lib/ types/
```

### Where does new code go?

| You are adding… | Put it in | Notes |
|---|---|---|
| HTTP route | `api/v1/<resource>.py` | **Thin**: validate → call service → return |
| Business logic that coordinates things | `services/<name>_service.py` | No HTTP types here |
| Request/response shape | `schemas/<name>.py` | Pydantic only |
| Database table | `models/<name>.py` + new Alembic migration | Never edit applied migrations |
| DB queries | `db/repositories/<name>_repo.py` | Services call repos, not raw sessions in routers |
| New data source type | `connectors/` implementing `SourceConnector` | Register in `registry.py` |
| File upload handling | `ingestion/` | |
| Statistics about columns | `profiling/` | |
| LLM prompt | `inference/prompts/*.yaml` | **Never inline prompts in code** |
| LLM call | through `inference/llm/gateway.py` only | |
| LangGraph node / graph | `inference/nodes/`, `inference/graphs/` | |
| Model training code | `backend/ml/` | Not in the API image |
| Model inference code | `inference/classifier/` | Loads artifacts, never trains |
| Tool generation | `compiler/` | |
| Permission logic | `policy/` | |
| Background job | `workers/jobs/<name>_job.py` | Must be idempotent |
| React screen | `frontend/src/features/<feature>/pages/` | |
| React reusable UI | `frontend/src/components/` | Feature-specific UI stays in the feature |
| Server data hook | `features/<feature>/hooks/` | TanStack Query |

### Stub policy
- A planned-but-unbuilt file may exist as a placeholder with a module docstring explaining its purpose and a marker line: `# STATUS: not implemented (Phase N)`.
- Placeholder functions `raise NotImplementedError`.
- Do not fill placeholder files with fake behaviour to make the structure "look" finished.

---

## 6. Domain glossary (use these exact terms)

| Term | Meaning |
|---|---|
| **Source** | A connected database or an uploaded file set |
| **Upload** | A single uploaded file (CSV/Excel/PDF) |
| **Profile** | Measured facts about a source: stats, distributions, keys, relationships (no meaning yet) |
| **Evidence** | A concrete fact supporting a meaning (sample values, join overlap, doc excerpt, name pattern) |
| **Concept** | A business meaning (e.g., "customer credit hold flag") |
| **Semantic map** | Approved mapping from tables/columns to concepts, with versions |
| **Confidence** | Calibrated score from classifier + verifier agreement |
| **Review** | Human approval/correction of a proposed meaning |
| **Tool** | A typed, parameterised, read-only operation generated from the semantic map |
| **Contract** | The versioned bundle: semantic map + tools + policies + evals |
| **Policy** | Rules for who may see which rows/columns (OpenFGA + masking) |
| **Eval** | An automated test (question + expected result/behaviour) for tools |
| **Drift** | A change in schema or data that may invalidate meaning/tools |
| **Impact** | The set of tools/policies/evals affected by a change (from lineage) |
| **Lineage** | Directed graph: source → column → concept → tool → policy/eval → consumer |
| **Tenant** | An isolated customer workspace |
| **Job** | A background task with status (`queued`, `running`, `succeeded`, `failed`, `cancelled`) |

Do not introduce synonyms (for example "schema map", "rule", "check") for these terms.

---

## 7. Backend rules (Python, FastAPI)

### 7.1 General conventions
- Use the Python version in `backend/pyproject.toml` (`requires-python`). Do not use syntax newer than it allows.
- **Type hints everywhere.** `mypy` must pass on `app/`. No `Any` unless justified in a comment.
- **Pydantic v2** for schemas and settings (`pydantic-settings`). **SQLAlchemy 2.x style** (`select()`, `Mapped[]`, `mapped_column`). Do not mix in v1/1.x idioms.
- **Project decision:** FastAPI endpoints are plain `def` using synchronous SQLAlchemy sessions. Long or heavy work goes to ARQ workers. Do not introduce `async` DB code without an ADR. (Reason: simpler for a large project; scale comes from workers and horizontal replicas.)
- Routers contain no business logic and no SQL.
- Dependency direction: `api → services → (repositories, domain modules) → models/db`. Domain modules (`profiling`, `inference`, `compiler`, `policy`, `drift`, `lineage`, `evals`, `reports`) **never import from `api`**. `models` never import from `services`.
- Naming: `snake_case` modules/functions, `PascalCase` classes, plural table names, `*_id` foreign keys, timestamps `created_at`/`updated_at` in UTC.
- Pagination is mandatory on every list endpoint. No unbounded queries.
- Configuration only via `core/config.py` (`pydantic-settings`). No `os.environ` calls scattered in code.
- Logging: structured, through `core/logging.py`. **Never log secrets, connection strings, raw customer values, or PII.**
- Errors: raise typed exceptions from `core/errors.py`; one global handler maps them to the API error shape `{ "error": { "code": str, "message": str, "details": object|null } }`.

### 7.2 Database and migrations
- Schema changes **only** through Alembic. Generate with autogenerate, then **read and edit the migration by hand**. Never edit a migration that has been applied or merged.
- `alembic heads` must show exactly one head before you finish.
- Every migration is reversible (`downgrade` implemented) unless an ADR says otherwise.
- Use transactions; services own transaction boundaries.
- Store large blobs/files in MinIO, not Postgres.

### 7.3 Source-database access and SQL safety
- Source connections use a **read-only** database role. On connect, set read-only/transaction options where the dialect supports it, **and** verify a write attempt fails in tests.
- **Never build SQL with string formatting or f-strings from user, file, or LLM input.** Use bound parameters. Identifiers (table/column names) must come from the introspected catalog and be quoted via the dialect's identifier quoting, never from raw input.
- Any SQL that is not a fixed template must pass through `compiler/sql_validator.py` (`sqlglot`): single statement, `SELECT` only, allowed tables/columns only, row/time limits enforced.
- Set statement timeouts and row limits on every source query.
- Sample, do not scan: profiling uses sampling and aggregate queries; never load whole tables into memory.

### 7.4 Privacy and PII
- Run PII detection (Presidio) during profiling and flag columns.
- **Mask before anything leaves the backend process boundary toward an LLM.** Send masked samples or statistics only. Provide a "stats-only" mode that sends no values.
- Raw customer values are never written to logs, traces, eval fixtures committed to Git, or prompts stored for analytics.
- Demo and test data must be public or synthetic.

### 7.5 File upload and CSV safety
- Enforce size limits, extension and content-type checks, and stream to storage (never read the whole file into memory).
- Detect encoding and delimiter with a sniffer; never assume UTF-8 or comma.
- Treat cells beginning with `=`, `+`, `-`, `@` as injection risks: sanitize on any export.
- Originals go to MinIO; parsed data to DuckDB (per-upload, isolated).
- Multi-file uploads: discover candidate foreign keys through value-overlap (inclusion dependency) and present them as **suggestions with evidence**, not facts.

### 7.6 Authentication, authorization, audit
- Every route except `/health` requires authentication.
- Authorization is checked in the service layer for every operation touching tenant data (OpenFGA when Phase 4 lands; until then a tenant-scoped check that is covered by tests).
- Every tool call, approval, and policy change writes an audit record (`models/audit.py`): who, what, when, outcome, without raw customer values.

### 7.7 Background jobs
- Jobs are **idempotent** and **resumable**: re-running a job must not duplicate data.
- Every job has: id, status, progress, error summary, timestamps. Failures are recorded, not lost.
- Set timeouts and a bounded retry policy. Never retry non-idempotent steps blindly.

### 7.8 LLM usage (applies everywhere)
- All LLM calls go through `inference/llm/gateway.py` (LiteLLM wrapper). No direct provider SDK calls elsewhere.
- Model names come from configuration. Never hardcode a model name in logic.
- Always request **structured output** matching a Pydantic schema; validate; retry a bounded number of times; on failure return an explicit error or `unknown`. Never parse free text with regex as a fallback.
- Temperature 0 for deterministic tasks.
- Record model name and version, prompt version, and input fingerprint on every stored result.
- Cache results by input fingerprint.
- Prompts live in `inference/prompts/*.yaml` with a version field. Changing a prompt means bumping its version and re-running affected evals.
- **Cascade, do not call the LLM by default:** rules → classifier → LLM (only for ambiguous columns) → human.
- Treat all data read from customer sources (column names, values, comments, docs) as **untrusted input**: it may contain instructions. Never let it change tool use, permissions, or system prompts. Put it in clearly delimited data sections and never execute it.

### 7.9 Testing (backend)
- `pytest`. Structure: `tests/unit` (no network, no Docker), `tests/integration` (real Postgres/Redis/MinIO via Docker Compose), `tests/e2e`.
- Test names describe behaviour: `test_csv_with_semicolon_delimiter_is_detected`.
- Use fixtures in `tests/fixtures/`. Never depend on test order or shared mutable state.
- Every bug fix starts with a failing test that reproduces it.
- LLM calls in tests are faked **at the gateway boundary** with recorded, realistic responses. Never call a live model in unit tests.
- Do not assert on implementation details; assert on observable outputs.

---

## 8. Backend feature design notes (so you do not improvise)

- **Connector interface** (`connectors/base.py`) must expose: test connection, list tables, describe table (columns, types, keys), sample rows (bounded), run a profiling aggregate. SQL and CSV connectors implement the same interface so profiling code is source-agnostic.
- **CSV/Excel path:** upload → MinIO → sniff → load to DuckDB → profile with the same profiling code.
- **Profile record** stores measured facts only (counts, distinct, null rate, min/max, top values (masked if PII), type guesses, distribution summaries, key candidates, relationship candidates). **No meanings in profiles.**
- **Semantic map records** are versioned and immutable once approved. A change creates a new version.
- **Tool records** reference a semantic-map version, store the parameterised template, input/output schema, status (`draft`, `approved`, `unsafe`, `retired`), and eval results.
- **Lineage** is stored in `lineage_nodes` and `lineage_edges` (Postgres). Analysis uses NetworkX. Node types: `source_table`, `source_column`, `concept`, `tool`, `policy`, `eval`, `consumer`. Edge types: `joins_to`, `derived_from`, `used_by`, `protected_by`, `tested_by`. Use these exact names.
- **Drift** compares a new profile snapshot to the last approved one, produces typed drift events, runs impact analysis, then flips affected tools to `unsafe` and schedules evals.

---

## 9. Frontend rules (React + TypeScript + Vite)

> **Design direction (Section 22) and the UI workflows (Section 23) are mandatory and override any default styling habits you have.** This section covers engineering rules; Section 22 covers how the product must look and read.

- **TypeScript strict.** No `any`, no `@ts-ignore` without a comment explaining why and a linked issue. No non-null assertions (`!`) to silence errors.
- **Never hand-write HTTP calls to our backend.** Use the generated client in `src/api/generated/`. Never edit generated files. If the API is missing something, change the backend, then `make openapi && make client`.
- Server state: **TanStack Query** (check the installed major version's API before writing hooks; v5 uses object-style options). No server data in global stores.
- Forms: React Hook Form + Zod. Validation schemas live next to the feature.
- Routing in `src/app/router.tsx`. Protected routes via `ProtectedRoute`.
- Styling: Tailwind + shadcn/ui components. **Check the installed Tailwind major version before writing config** (v3 and v4 configure differently). Do not mix them.
- Lineage graph: React Flow + dagre layout. Custom node components live in `features/lineage/components/nodes/`.
- **Feature folders own their code.** Cross-feature imports go through `components/`, `hooks/`, `lib/`, or `types/` only, never from one feature into another feature's internals.
- Components are small, typed, and presentational. Data fetching and mutation belong in hooks. Business rules belong in the backend.
- **Every view that loads data must implement loading, empty, error, and success states.** No blank screens, no uncaught promise rejections.
- Accessibility basics: semantic HTML, labelled inputs, keyboard-operable controls, sufficient contrast, `aria-live` for job-status changes.
- Never put secrets or API keys in frontend code or `VITE_*` variables. Only public configuration belongs there.
- Long-running operations: show progress via `useJobPolling`; never block the UI.
- Tests: Vitest for logic/components, Playwright for flows. Test behaviour, not implementation.
- Remove Vite template leftovers (`src/App.tsx`, `App.css`, unused `assets/`) as part of Phase 2 cleanup; the real app lives in `src/app/`.

---

## 10. ML rules (PyTorch)

- Training lives in `backend/ml/`. The API process **never trains**. It only loads versioned artifacts from `backend/ml/artifacts/` (or the configured artifact store).
- **Split data by schema/database, never by individual column or row.** Splitting by column leaks near-duplicate names/values across train and test and produces fake accuracy.
- Fix random seeds; log seed, data version, config, and git commit with every run. Configs in `backend/ml/configs/*.yaml`.
- Required evaluation outputs: per-class precision/recall/F1, confusion matrix, and **calibration** (reliability + expected calibration error). Apply post-hoc calibration (e.g., temperature scaling) on a validation split, not the test split.
- Write metrics to files under `docs/results/` from scripts. **Never type metrics by hand into docs.**
- Report "unknown/abstain" behaviour: the classifier must be able to abstain below a threshold chosen on validation data.
- Document every dataset in `backend/ml/datasets/sources.md`: origin, license, how labels were produced. Do not use data you cannot document.
- Model artifacts are versioned and immutable. Every stored prediction records the artifact version.
- Keep the model small and CPU-friendly unless the human approves otherwise.

---

## 11. LangGraph / agent rules

- State is a typed object (`inference/graphs/state.py`). Nodes take state and return state updates. Keep nodes small and single-purpose.
- Evidence gathering is a separate node from proposing meaning, and verification is a separate node from proposing. **The proposer and the verifier must not share the same prompt or reasoning.**
- Confidence = f(classifier probability, verifier agreement, evidence strength). **Never use the LLM's self-reported confidence as the score.**
- Required output fields for every proposal: meaning, evidence list (each pointing to a real profile fact), confidence, model/prompt/artifact versions, `unknown` flag.
- "I don't know" (`unknown`) is a valid, preferred answer over a guess.
- Human-in-the-loop: use graph interrupts/checkpoints for review steps. State must survive restarts (persist the checkpointer).
- Bound every loop: max iterations, max tokens, max time. Terminate with an explicit failure state, never spin.
- Tools available to any agent inside the graph are an allowlist. No tool may write to a source database. No tool may reach the network except the LLM gateway.
- **Prompt-injection hygiene:** data from customer sources is untrusted (see 7.8). Never concatenate it into instructions. Keep instructions and data in separate, labelled sections.
- Each graph has a deterministic test with a faked gateway, plus an eval on `demo/ground_truth.yaml` that prints real metrics.

---

## 12. TASK PROTOCOL — follow this loop for every task

### Step 1 — Orient (always)
- Read `docs/STATUS.md` (current phase, in-progress items, blockers).
- Read the files you will touch, their tests, and relevant docs/ADRs.
- `git status` and `git log -5 --oneline` to see current state. Do not start on a dirty tree without telling the human.

### Step 2 — Restate
Write, in your own words: the goal, the acceptance criteria, what is **out of scope**, and your **assumptions**. If anything blocking is ambiguous, stop and ask (Section 14).

### Step 3 — Plan (before editing)
Produce a plan using this template:

```
PLAN
Goal:
Phase: (must match docs/STATUS.md)
Files to read:
Files to create/edit:           (each must exist in the planned structure)
Tests to write first:
Commands I will run to verify:
Assumptions:
UNVERIFIED items (need checking or human input):
Risks / things that could break:
Out of scope:
```
For anything touching more than ~5 files, or any schema/API/dependency change, **wait for human approval of the plan.**

### Step 4 — Implement in small steps
- Use the matching recipe: backend → Section 21; UI → Sections 22–23; cross-stack → Section 24; bugs → Section 25.
- Tests first when feasible (failing test → implementation → passing).
- Small commits with Conventional Commit messages (`feat(profiling): …`, `fix(ingestion): …`, `test:`, `docs:`, `chore:`).
- After each meaningful step, run the fast checks (Section 15).
- If the same approach fails **3 times**, stop, summarise what you tried and learned, and ask. Do not thrash.

### Step 5 — Verify (real output only)
Run the verification commands for the area you touched (Section 15). Capture the actual output. Run the structure checker. If something cannot run in your environment, write `NOT RUN: reason`.

### Step 6 — Self-review checklist (answer each Yes/No in your report)
- [ ] I read every file before editing it
- [ ] No invented APIs, flags, env vars, paths, or columns (anything unverified is labelled UNVERIFIED)
- [ ] Diff touches only what the task needs
- [ ] No new dependency (or it was approved)
- [ ] No placeholder logic masquerading as real
- [ ] Tests assert real behaviour; none skipped, weakened, or deleted
- [ ] No secrets, PII, or raw customer values in code, logs, fixtures, or prompts
- [ ] SQL is parameterised/validated; source access is read-only
- [ ] New endpoints have authn/authz, pagination, error shape, and audit
- [ ] LLM calls go through the gateway with structured output and versions recorded
- [ ] Generated files were regenerated, not hand-edited
- [ ] Loading/empty/error states exist for new UI
- [ ] Docs updated (`STATUS.md`, `data-model.md`, ADR if a decision was made)
- [ ] All claims in my report are backed by command output or `path:line`

### Step 7 — Report (use this template)

```
REPORT
Summary (2-4 sentences):
What changed (files):
Commands run and results (real output, trimmed):
Not run / could not verify:
Assumptions made:
Decisions that need human confirmation:
Known issues or follow-ups found (not fixed):
Next suggested task:
```

### Step 8 — Update project memory
- Update `docs/STATUS.md` (what's done, what's next, blockers).
- Add or update an ADR in `docs/adr/` if you made or changed a design decision.
- Update `docs/data-model.md` if tables changed.

---

## 13. Anti-hallucination playbook (concrete techniques)

### 13.1 Ground every claim
- "This function does X" → open the function and cite `path:line`.
- "This library supports Y" → show the installed version and the source/doc line.
- "The test passes" → show the command and output.
- "This endpoint exists" → show it in `contracts/openapi.json` or the router file.

### 13.2 Dependency verification procedure
Before using any package API:
1. `pip show <pkg>` / `npm ls <pkg>` → note the version.
2. Inspect the real signature (`help()`, `inspect.signature`, read source, or the package's `.d.ts`).
3. Find at least one correct usage (repo, official docs for that version).
4. Write a tiny test that exercises the call. Only then build on it.

### 13.3 Known hallucination hotspots in this project (always check the installed version)
- **LangGraph / LangChain:** module paths, graph builder API, checkpointer classes, and interrupt mechanisms change between releases.
- **MCP Python SDK / FastMCP:** server construction, tool registration decorators, transports, and extension features (tasks, elicitation) are version-specific.
- **OpenFGA SDK:** client construction and check/list APIs differ by version; model DSL syntax is strict.
- **Docling, DuckDB, Presidio, sqlglot:** option names and result shapes vary by version.
- **Pydantic v1 vs v2** (`model_validate`, `model_dump`, `field_validator`) and **SQLAlchemy 1.x vs 2.x** idioms.
- **ARQ / Temporal:** worker and settings classes are version-specific.
- **React Router, TanStack Query (v4 vs v5), Tailwind (v3 vs v4), shadcn/ui, React Flow (`@xyflow/react` vs `reactflow`):** package names and APIs differ by version.
- **Alembic autogenerate:** it misses some changes (server defaults, enums, constraints). Read the generated migration.
- **Windows / PowerShell:** path separators, `&&` support (older PowerShell uses `;`), line endings, quoting. Prefer cross-platform commands via `make` or Python scripts.

### 13.4 Fake-success detection
A result is suspicious if: tests were not actually executed; a test asserts only that no exception occurred; the code returns constants; the number of tests did not change after "adding tests"; logs show warnings you ignored; or a mock is verifying its own setup. Report suspicious results instead of hiding them.

### 13.5 Don't chain assumptions
One unverified assumption is acceptable if labelled. Building a second step on top of it is not. Verify, then continue.

### 13.6 Prefer boring and explicit
Choose the simplest tool that works. Do not add Temporal, Kubernetes features, or new frameworks before the phase that needs them. Do not write clever abstractions for hypothetical future needs.

### 13.7 Context hygiene
- Keep tasks small enough that you can hold the relevant files in context.
- For large tasks, split into sub-tasks, finish each with a report, and update `STATUS.md` so a fresh session can continue.
- Do not rely on memory of earlier sessions. Re-read files.

---

## 14. When to stop and ask the human

Stop and ask (with a concrete question and your recommended default) when:
- The task contradicts this file, an ADR, or the current phase
- You need a new dependency, a new top-level folder, or a changed API contract
- A schema change would alter existing data or an applied migration
- Requirements are ambiguous in a way that changes the design
- You cannot verify a library API after the procedure in 13.2
- You are about to delete data, files, or tests
- Security or privacy implications are unclear (for example, a new field that might hold PII)
- The same fix failed 3 times
- Documentation and code disagree

**Blocked template:**
```
BLOCKED
What I was doing:
What I tried (with results):
What I need from you:
My recommended default if you have no preference:
```

---

## 15. Verification commands

Run from the repository root unless noted. On Windows PowerShell use `;` to chain commands in older versions.

| Check | Command |
|---|---|
| Structure vs plan | `python scripts/check_structure.py --phase N` |
| Backend lint | `cd backend; ruff check .` |
| Backend types | `cd backend; mypy app` |
| Backend tests (fast) | `cd backend; pytest tests/unit -q` |
| Backend tests (all) | `cd backend; pytest -q` |
| Migrations single head | `cd backend; alembic heads` |
| Apply migrations | `cd backend; alembic upgrade head` |
| Import sanity | `cd backend; python -c "import app.main"` |
| Run API | `cd backend; uvicorn app.main:app --reload` |
| Regenerate OpenAPI | `cd backend; python scripts/export_openapi.py` |
| Regenerate TS client | the `make client` target (see Makefile) |
| Frontend lint | `cd frontend; npm run lint` |
| Frontend build + types | `cd frontend; npm run build` |
| Frontend unit tests | `cd frontend; npx vitest run` |
| Frontend e2e | `cd frontend; npx playwright test` |
| Compose valid | `docker compose config -q` |

If a command is not defined yet in the Makefile or package scripts, **say so and propose adding it**. Do not pretend it exists.

**Definition of Done (every task):** lint clean, types clean, relevant tests pass (new ones included), structure checker clean for the current phase, docs updated, report delivered with real output.

---

## 16. Git, review, and CI rules

- Work on a feature branch: `feat/<phase>-<topic>`, `fix/<topic>`. Never commit directly to `main`.
- Commits: Conventional Commits, small and atomic. One logical change per commit.
- Do not commit: secrets, `.env`, large data files, model artifacts (use the artifact store/Git LFS if approved), `node_modules`, build output.
- Pre-commit must pass (ruff, formatting, secret scan).
- CI must be green. Never disable or loosen a CI check to get green.
- Pull request description: goal, approach, test evidence, risks, screenshots for UI changes, and links to ADRs.
- The eval gate (`evals-gate.yml`, Phase 5) blocks merges that regress tool correctness or permission safety.

---

## 17. Security and quality checklist (apply to every feature)

- [ ] AuthN on all non-health routes; AuthZ in the service layer; tenant isolation tested
- [ ] Inputs validated by Pydantic; sizes bounded; pagination enforced
- [ ] SQL parameterised; dynamic identifiers from the catalog only; `sqlglot` validation for non-template SQL
- [ ] Source access read-only; timeouts and row limits set
- [ ] PII flagged and masked before any LLM call; stats-only mode available
- [ ] File uploads: size/type limits, streaming, injection sanitization
- [ ] No secrets or raw customer values in logs, traces, prompts, fixtures, or errors
- [ ] Errors use the standard shape and never leak internals or stack traces to clients
- [ ] Audit record written for sensitive actions
- [ ] Dependencies pinned and reviewed
- [ ] Untrusted data (customer text) never treated as instructions

---

## 18. Performance and scalability rules

- Design for horizontal scale: API replicas are stateless; state lives in Postgres, Redis, MinIO, DuckDB files per upload.
- Heavy work (profiling, inference, evals, drift, reports) runs in workers, never in request handlers.
- Never load entire tables or files into memory. Sample, stream, and aggregate in the database/DuckDB.
- Cache by fingerprint (LLM results, embeddings, profiles of unchanged columns).
- Batch embeddings and LLM calls where possible; set concurrency limits and timeouts.
- Add indexes only with a measured reason (query plan or benchmark in the PR).
- Report latency/throughput only from real load-test runs (Phase 6).

---

## 19. Documentation rules

- `docs/STATUS.md` is updated at the end of every task (template in Appendix A).
- Design decisions → ADRs in `docs/adr/NNNN-title.md` (template in Appendix B). Existing ADRs: `0001-backend-first`, `0002-duckdb-for-csv`, `0003-typed-tools-over-free-sql`, `0004-postgres-lineage-before-graph-db`. The sync-DB-in-routes decision (Section 7.1) should be recorded as `0005`.
- Code comments explain **why**, not what. Public functions have short docstrings.
- Do not write README claims about features that do not exist yet.
- Result numbers in docs come from files under `docs/results/` produced by scripts.

---

## 20. Quick DO / DON'T

| DO | DON'T |
|---|---|
| Read the file, then edit it | Edit from memory |
| Verify APIs in the installed version | Trust remembered signatures |
| Say "UNVERIFIED" or "NOT RUN" | Claim success without evidence |
| Make small, tested diffs | Refactor unrelated code |
| Return `unknown` when evidence is weak | Guess a meaning |
| Validate and parameterise all SQL | Format SQL strings |
| Mask data before LLM calls | Send raw customer values |
| Regenerate generated files | Hand-edit generated files |
| Ask when blocked | Silently pick an interpretation |
| Keep to the current phase | Build future features early |
| Update STATUS.md and ADRs | Leave decisions undocumented |
| Raise `NotImplementedError` in stubs | Return fake data |

---

## 21. BACKEND WORKFLOWS (step-by-step recipes)

Use the recipe that matches your task. Do the steps **in order**. Each recipe ends with the checks that prove it works.

### 21.1 Feature slice order (the default for any backend feature)
1. **Contract first:** write the Pydantic request/response schemas and the error cases. Get human approval if the API shape is new or changes.
2. **Migration + model:** Alembic migration (read and edit by hand), SQLAlchemy model, reversible downgrade.
3. **Repository:** queries only, no business rules.
4. **Service:** business logic, transaction boundary, authz check, audit record.
5. **Router:** thin; declare response models, error responses, pagination, and a docstring that becomes API docs (with an example payload).
6. **Tests:** unit for the service (fakes at boundaries), integration against real Postgres, API test through `TestClient`.
7. **Regenerate** `contracts/openapi.json` and review the diff for unintended changes.
8. **Seed/demo data:** extend `scripts/seed_demo.py` if the frontend needs realistic data to show this feature.
9. **Docs:** `docs/data-model.md`, ADR if a decision was made, `docs/STATUS.md`.

**Definition of ready for the frontend:** endpoint is in OpenAPI with typed errors and an example, lists are paginated, and demo data exists. Do not hand a half-specified endpoint to the frontend.

### 21.2 Add an endpoint — checklist
- [ ] Resource name plural, verb implied by HTTP method; actions that start work return `202` + job id
- [ ] AuthN dependency applied; authz checked in the service; tenant id comes from the auth context, never from the request body
- [ ] Response model declared (never return ORM objects or dicts directly)
- [ ] Every documented error code is raised by a test
- [ ] Pagination (`limit`, `cursor` or `page`) with a maximum limit
- [ ] Idempotency: `POST` that creates uploads/jobs accepts an idempotency key or dedupes by content hash
- [ ] Audit record written for sensitive actions
- [ ] Structured log line with request id, tenant id, and outcome, with no customer values

### 21.3 Add or change a table
1. Write the migration; run `alembic upgrade head` on an empty database **and** on a database that already has data.
2. Run `alembic downgrade -1` then `upgrade head` to prove reversibility.
3. Add indexes only for queries you can name; record the query in the migration comment.
4. Backfill data in a separate, idempotent step, never inside a blocking migration on large tables.
5. Update `docs/data-model.md` and run `alembic heads` (exactly one head).

### 21.4 Add a data-source connector or dialect
1. Implement `SourceConnector` (test connection, list tables, describe table, bounded sample, profiling aggregate).
2. **Run the shared connector conformance tests**: one test suite parameterised over every connector. A new connector must pass the same tests as the existing ones; do not write bespoke tests that only exercise the happy path.
3. Prove read-only: a test that attempts `INSERT`/`UPDATE`/`DELETE`/DDL and expects failure.
4. Add timeouts, row limits, and identifier quoting through the dialect.
5. Register in `connectors/registry.py`; add the connection form fields to the API schema (the frontend form is generated from it, not guessed).

### 21.5 Profiling and statistics correctness (data-quality workflow)
Profiling output is the foundation of everything downstream. Wrong numbers here poison the whole system.
1. For every statistic, write a test where the expected value is computed **independently** (for example, DuckDB or plain Python on a tiny hand-checkable dataset). Never compare a function to itself.
2. Cover edge cases: empty table, all nulls, single row, constant column, high-cardinality column, mixed types, unicode, very long strings, negative and huge numbers, dates in multiple formats.
3. Sampling must be deterministic given a seed, and sampled statistics are labelled as estimates with the sample size recorded.
4. Relationship discovery: test with known true foreign keys, known false lookalikes (for example, two unrelated integer ID columns), and report precision on the demo dataset from a script.
5. Property-based tests (for example with Hypothesis, if approved as a dependency) are encouraged for invariants: null rate in [0,1], distinct ≤ count, min ≤ max.

### 21.6 Add a background job
1. Define the idempotency key (what makes two runs "the same job") and write a test that runs the job twice and asserts no duplicates.
2. Record status transitions: `queued → running → succeeded | failed | cancelled`, with progress and a human-readable error summary.
3. Set a timeout and a bounded retry policy with backoff. Only retry steps that are safe to repeat.
4. Make cancellation work (check a flag between chunks).
5. Emit logs/spans carrying the same correlation id as the request that created the job.

### 21.7 Add or change an inference step (LangGraph node, classifier, prompt)
1. Define input/output Pydantic schemas first.
2. Write a **deterministic unit test** with a faked gateway returning recorded, realistic responses (including malformed JSON and refusals).
3. Add or extend cases in `demo/ground_truth.yaml`.
4. Run the evaluation script and record real metrics under `docs/results/` (accuracy, per-class results, calibration). Compare to the previous run; a regression must be explained or fixed.
5. Wire the node into the graph with bounds (max iterations, timeout) and a defined failure state.
6. Prompt changes: bump the prompt version, re-run affected evals, note the result in the PR.

### 21.8 Add a generated tool template (compiler)
1. Express the tool as a typed spec: name, description in business language, input schema, output schema, SQL template with named parameters, tables/columns touched, sensitivity flags.
2. Validate with `sql_validator` (single `SELECT`, allowed objects only, limits applied).
3. Generate the eval cases (at least: typical, empty result, boundary values, forbidden-user).
4. Run against the demo database and assert exact expected rows.
5. Version the tool; approved versions are immutable.

### 21.9 Resilience and graceful degradation
- LLM gateway: timeout, bounded retry with exponential backoff and jitter, and a circuit breaker. When the LLM is unavailable, **degrade, do not fail the whole pipeline**: return classifier-only proposals marked `degraded=true` with lower confidence.
- Source databases: connection pooling with small limits, per-query timeouts, and clear `SOURCE_UNREACHABLE` errors with a retry hint.
- Never let one bad table or column abort a whole profiling run: record the failure for that item and continue.
- Every external call has a timeout. There are no unbounded waits.

### 21.10 Error taxonomy (use these codes, extend only via ADR)

| Code | HTTP | When |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Input fails schema validation |
| `NOT_FOUND` | 404 | Resource missing or not visible to this tenant |
| `CONFLICT` | 409 | Duplicate or version clash |
| `AUTH_REQUIRED` / `PERMISSION_DENIED` | 401 / 403 | Not signed in / not allowed |
| `SOURCE_UNREACHABLE` / `SOURCE_AUTH_FAILED` | 502 / 400 | Cannot connect / bad credentials |
| `UNSAFE_SQL_REJECTED` | 400 | Validator blocked a statement |
| `FILE_REJECTED` | 400 / 413 | Type, size, or content check failed |
| `LLM_UNAVAILABLE` / `LLM_INVALID_OUTPUT` | 503 / 502 | Gateway down / output failed schema after retries |
| `TOOL_UNSAFE` | 409 | Tool blocked by drift until re-approved |
| `JOB_FAILED` | 200 (job state) | Background job ended in failure; details in the job record |

Messages must say what happened and what to do next. Never include stack traces, SQL text with values, or connection strings.

### 21.11 Observability
- One **correlation id** per request, propagated into jobs, LLM calls, and logs.
- Create spans around: connector calls, profiling stages, LLM gateway calls, tool executions, policy checks. Span attributes carry ids and counts, never raw customer values.
- Record per LLM call: model, prompt version, token counts, latency, cache hit, outcome.
- Expose basic metrics: job durations, queue depth, error rates by code, tool latency.

### 21.12 Performance workflow (measure first)
1. State the target and how it is measured (for example, "profiling a 1M-row CSV finishes in N seconds").
2. Measure the baseline with a script. Save the result in `docs/results/`.
3. Find the bottleneck with a profiler or `EXPLAIN`, not by guessing.
4. Change one thing, re-measure, keep or revert.
5. Never trade correctness or safety for speed without an ADR.

---

## 22. FRONTEND DESIGN DIRECTION (this is what makes Unearth not look generic)

**The rule:** Unearth must not look like a template. Any engineer should be able to tell it is *this* product from a single screenshot. The design direction below is a **decision already made**. Do not drift back to defaults, and do not "improve" it with common patterns.

### 22.1 Subject, audience, and the one memorable thing
- **Subject:** turning cryptic legacy data into plain, trustworthy meaning for AI agents.
- **Audience:** forward-deployed engineers and the customer's data/security people. Expert users doing careful review work for hours at a time. They value density, speed, keyboard control, and evidence over decoration.
- **The one memorable thing — the Decode view:** every column is shown as two layers side by side. The **raw layer** (the legacy identifier and real sample values, in a monospace data face) and the **meaning layer** (plain-language meaning, in the UI face), connected by the **evidence** that justifies the link. Approving a meaning is the product's signature moment (see 22.7). Spend design boldness here. Keep everything else disciplined and quiet.

### 22.2 What to avoid (these are the tells of generated UI)
Do **not** produce any of the following unless the human explicitly asks:
- A warm cream background with a serif display and a terracotta/clay accent; or a near-black background with a single acid-green or vermilion accent
- A broadsheet look: hairline rules everywhere, zero radius, newspaper columns
- The SaaS-card kit: content chopped into identical rounded cards, one radius on everything, the same soft grey shadow under each, gradient washes as decoration
- Four identical stat cards across the top of a dashboard
- Purple/indigo-to-blue gradients, glow effects, glassmorphism, gradient text
- Tracked-out ALL-CAPS eyebrow labels above headings; meta strings joined with middle dots (`A · B · C`); labels shaped like `WORD — fragment`; arrows (`→`) appended to every link or button
- Accenting a single word of a headline in italic, bold, or a different colour
- Numbered markers (01 / 02 / 03) on content that is not truly a sequence (the pipeline stepper **is** a true sequence, so numbers are allowed there)
- Monospace for decorative small labels (monospace is reserved for real raw data; see 22.4)
- Tinted near-black (`#0B0B0B`, `#111`) used as "black"
- Fade-and-slide-up entrances on every section; hover transitions on every card
- Emoji as icons; stock illustrations; lorem ipsum; fake logos, testimonials, or metrics
- Unthemed shadcn/ui defaults (components must be restyled through the tokens in 22.3)
- Rainbow chart palettes; colour as the only carrier of meaning
- Marketing copy ("Supercharge", "Unlock", "Seamless", "Welcome back 👋")

### 22.3 Design tokens (single source: `src/index.css`)
Define tokens once as CSS variables and reference them everywhere (Tailwind theme extends from them). **No hard-coded hex values, font names, or magic spacing numbers in components.** Dark mode must be possible by overriding tokens only.

Starter palette (named choices; adjust only through the human and a tokens change):

```css
:root {
  /* Neutrals: cool, slightly green-grey, like mineral and slate */
  --limestone:    #ECEFEA;  /* page background */
  --limestone-2:  #E1E6E1;  /* inset regions, table header */
  --surface:      #F6F8F5;  /* raised panels, popovers */
  --bedrock:      #1B2A28;  /* primary text, a deep green-slate ink */
  --slate:        #566663;  /* secondary text */
  --rule:         #C9D1CC;  /* borders and dividers */

  /* Action and states */
  --malachite:     #0B7A63; /* primary action, focus ring, "approved" */
  --malachite-ink: #F3FAF7; /* text on malachite */
  --lapis:         #34567A; /* informational, links in prose */
  --sulphur:       #C99A12; /* needs attention */
  --cinnabar:      #B0352B; /* error, destructive, "unsafe" */

  /* Confidence strata: low to high (always paired with a number/label, never colour alone) */
  --strata-1: #B0352B;
  --strata-2: #C9742A;
  --strata-3: #C99A12;
  --strata-4: #7FA05A;
  --strata-5: #0B7A63;

  /* Shape and rhythm */
  --radius-data: 2px;   /* cells, inputs, tags */
  --radius-panel: 6px;  /* panels, dialogs */
  --space-unit: 4px;    /* all spacing is multiples of this */
}
```

- **Contrast is not assumed.** Check every text/background and UI-component pair with a contrast checker or an axe run. Body text needs WCAG AA (4.5:1); large text and UI boundaries need 3:1. If a token fails, change the token, not the component.
- Shadows: almost none. Separate regions with tone shifts and single rules, not with floating cards. Use a card only for a discrete object a person acts on as a unit (one tool, one report).
- Radii follow hierarchy (2px data, 6px panels), not one radius for everything.
- Spacing: multiples of 4px. Two densities: **compact** (32px rows) default for tables, **comfortable** (40px) optional.

### 22.4 Typography
- **Two families, clearly distinct, with fixed roles:**
  - **UI and prose face** (a characterful grotesk, **proposed:** Schibsted Grotesk): navigation, headings, meanings, buttons, reports.
  - **Data face** (a monospace, **proposed:** Spline Sans Mono): **only** for raw legacy identifiers, real sample values, SQL, and ids. This is the "machine layer". If it is not literally raw data, it is not monospace.
- These are proposals: before installing, **verify the font packages exist and their licences** (for example, check the `@fontsource` packages with `npm view`). Self-host fonts; do not load from a third-party CDN. The human may swap families by changing tokens only.
- Type scale from tokens (for example 12 / 13 / 14 / 16 / 20 / 28 / 40) with deliberate weights and line heights. Prose line length under 80 characters.
- Numbers in tables use tabular figures (`font-variant-numeric: tabular-nums`). Sentence case everywhere. No all-caps labels.
- Headings are real typographic hierarchy (size and weight), not decoration.

### 22.5 Layout concept
- **App shell:** a slim left rail (icon + label, collapsible) and a main workspace. The workspace header is a **context bar** showing the current source and the true pipeline sequence (1 Profile, 2 Meaning, 3 Tools, 4 Policy, 5 Evals, 6 Drift) with each stage's state. This sequence is real, so numbering is justified.
- **Alignment:** left-aligned, asymmetric, editorial grid for reading surfaces (reports, evidence); full-bleed dense grids for working surfaces (tables, graphs). Never centre-everything.
- **Command palette** (Ctrl/Cmd+K) for navigation and actions; keyboard shortcuts shown in tooltips and menus.
- **Desktop-first** (expert tool). Must be fully usable at 1024px, and read-only usable (no broken layout) at 390px.
- Ask for an ASCII wireframe before building any new screen (see 23.1).

### 22.6 Screen-by-screen direction

| Screen | Direction |
|---|---|
| **Home** (not a stat-card dashboard) | An **attention queue**: what needs a human now (low-confidence columns to review, unsafe tools, new drift events), each as a row with one primary action. Pipeline status sits in the context bar, not in a row of identical tiles. |
| **Add data** (sources + upload) | One surface. A drop zone that also offers "Connect a database". Detected CSV settings (encoding, delimiter, header) appear as **editable facts with a confidence note**, not a wizard. Chunked upload with real progress and cancel. |
| **Profile** | Table-first and dense. Inline distribution sparklines (drawn as SVG, not a chart library per cell), null-rate bar, PII flag, relationship suggestions as a list with overlap evidence. Virtualise large tables. |
| **Review / Decode** (hero) | Two-layer view (22.1). Queue ordered by lowest confidence first. Keyboard-driven triage: `J/K` move, `A` approve, `E` edit, `X` reject, `?` shows shortcuts. Evidence panel shows concrete sample values and join overlaps. Confidence shows as a segmented strip **plus the number plus a text label**. |
| **Tools** | List with status and eval pass state. Detail page shows the typed signature, the generated SQL template (data face), the MCP config snippet with a copy action, version history, and a **Try it** console whose form is generated from the tool's input schema. |
| **Policies** | Role × object matrix with clear allow/mask/deny encoding (shape + label + colour). A "view as <user>" permission tester and leak-test results with the exact probe that was tried. |
| **Drift** | A vertical, core-sample-style timeline of drift events. Side-by-side schema diff. An **affected tools** list from impact analysis with a "Re-approve" flow. |
| **Lineage** | React Flow canvas with a distinct node shape per type (table, column, concept, tool, policy, eval). **Impact mode:** select a changed node and the downstream path highlights as a blast radius. Legend, filters, keyboard navigation, collapsible groups. Handle large graphs by grouping and progressive reveal, not by rendering everything. |
| **Reports** | Live preview next to export actions. Editorial layout with comfortable measure. |

### 22.7 Motion
- Motion answers a person's action; it is not decoration. 120–200ms, ease-out; respect `prefers-reduced-motion`.
- **One signature moment:** when a meaning is approved, the raw identifier in the Decode view resolves into its plain-language meaning (a short text transition that shows what changed). Everything else stays still.
- Allowed: panel open/close, row expand, toast, progress. Not allowed: scroll-triggered reveals, hover lift on every card, animated gradients.
- Loading uses **skeletons shaped like the real content**, not generic spinners (spinners only for short in-button waits).

### 22.8 Copy and microcopy (design content, not decoration)
- Sentence case, active voice, plain verbs. A button names exactly what happens ("Approve meaning", not "Submit"). The same action keeps the same name through the flow ("Approve" → toast "Approved").
- Name things in the user's language. Internal term → UI label:

| Internal term | UI label |
|---|---|
| Semantic map | Data dictionary |
| Concept | Meaning |
| Evidence | Evidence |
| Contract | Data contract |
| Drift event | Change detected |
| Tool (status `unsafe`) | Paused (data changed) |
| Review | Review |

- Errors say what happened and how to fix it, with no apology and no blame. Empty states invite the next action and name it ("No sources yet. Connect a database or drop a CSV.").
- Real copy only: no lorem ipsum, no filler, no invented statistics.

### 22.9 Quality floor (every screen, always)
Responsive at the supported widths; visible keyboard focus; full keyboard operation; reduced motion respected; contrast verified; semantic HTML; labelled inputs; `aria-live` for job status; loading, empty, error, partial, and large-data states all designed.

---

## 23. FRONTEND WORKFLOWS (step-by-step)

### 23.1 Build a new screen (default workflow)
1. **Screen brief (write it, 8 lines max):** who uses it, the job to be done, the primary action, what data it shows (with the OpenAPI types), states to design, keyboard flow, and the empty-state copy.
2. **Design plan (before any code):** list the tokens you will use (reuse existing; propose new only with a reason), the layout in an **ASCII wireframe**, and the one thing this screen does that is specific to Unearth. **Compare it against the "What to avoid" list in 22.2.** If any part reads like a default you'd produce for any product, revise it and say what you changed.
3. **Get human approval** for new screens and any change to the shell, tokens, or signature moments. Small tweaks inside an approved screen do not need approval.
4. **Check the data contract:** types exist in the generated client; if not, request the backend change (Section 24), do not invent types.
5. **Build structure with real data:** run against the real backend and the demo seed. If the backend is not ready, use fixtures **captured from real API responses**, typed by the generated types. Never invent response shapes.
6. **Implement states in this order:** loading skeleton → empty → error → success → large data → partial/degraded.
7. **Interaction pass:** keyboard shortcuts, focus management (where focus goes after an action), optimistic updates only where reversible, undo for destructive actions.
8. **Visual QA (see 23.2).**
9. **Tests:** Vitest for logic and components; a Playwright flow for the primary action.
10. **Report** with screenshots (23.2) and the self-review checklist.

### 23.2 Visual and accessibility QA protocol
Do this for every screen before reporting. If you have a browser or screenshot tool, use it and **actually look at the images**. If you cannot, write `NOT RUN: no browser available` and ask the human to review.
1. Start the app against seeded data.
2. Capture screenshots at **1440, 1024, and 390** widths, in every state: loading, empty, error, success, and large-data.
3. Critique each screenshot against 22.2 and 22.3: Does it look like a template? Is there decoration with no job? Remove one decorative element (the "mirror test").
4. Check: alignment to the 4px grid, consistent radii by hierarchy, type roles respected (monospace only for raw data), no colour-only meaning, tabular numbers in tables, line length under 80 chars in prose.
5. **Keyboard-only pass:** reach and operate every control; focus is always visible; focus returns to a sensible place after dialogs and actions.
6. **Automated a11y:** run an axe check in Playwright (verify the package and version) and fix violations; do not suppress them.
7. Check contrast for any new token pair.
8. Run the app with reduced motion enabled and confirm nothing essential depends on animation.

### 23.3 Data-heavy UI rules
- Tables over ~200 rows are virtualised (verify the installed virtualisation library API first). Sorting, filtering, and pagination are server-side for large sets.
- Never block the UI on long work: show job progress, allow cancel, allow the user to continue elsewhere.
- Debounce search inputs; cancel in-flight requests on change.
- Optimistic updates only for reversible actions (like approving a meaning), with rollback and a clear error on failure.
- Cache keys are consistent and typed; invalidate precisely after mutations.
- Large JSON, SQL, or sample values are shown truncated with expand and copy, never dumped inline.
- Sensitive values are masked by default in the UI, with an explicit, audited reveal if the role allows it.

### 23.4 Forms
- Zod schemas next to the feature; errors appear beside the field in plain language; keep entered values on error.
- Connection forms are generated from the backend connector schema so fields never drift.
- Never store or echo secrets back to the UI after submission; show "set" status instead.

### 23.5 Component workflow
1. Check `components/ui` and `components/common` for an existing component **before** creating one.
2. New shared components must be generic (no feature knowledge), typed, themed through tokens, and keyboard-accessible.
3. If a shadcn/ui component is added, restyle it to the tokens immediately; do not leave the default look.
4. Remove unused components and dead styles in the same change.

### 23.6 Performance and bundle hygiene
- Route-level code splitting for heavy screens (lineage graph, charts).
- Memoise only after measuring a real problem (React Profiler), not by habit.
- Avoid heavy libraries for simple needs (draw sparklines as small SVG; do not import a full chart library per cell).
- Check bundle output after adding a dependency (it must be approved first, see 2.3).

---

## 24. CROSS-STACK VERTICAL SLICE WORKFLOW (a feature that touches both sides)

Build features as **thin end-to-end slices**, not as "all backend, then all frontend".

1. **Slice brief:** the user story and a **demo path** of 3–5 steps the human can follow to see it working (for example, "upload `messy.csv` → open Profile → see 14 columns with stats → see 2 suggested relationships").
2. **Contract draft:** schemas and error cases. Human approves.
3. **Backend:** follow 21.1. Merge it with tests before the frontend depends on it.
4. **Export and diff:** regenerate `contracts/openapi.json` and review the diff. **Breaking-change rule:** never change an existing response shape or remove a field without updating every consumer in the same PR (or versioning the endpoint).
5. **Regenerate the client** (`make client`) and fix type errors the compiler reports; these are exactly the places the frontend must adapt.
6. **Seed realistic demo data** so the screen is built against reality.
7. **Frontend:** follow 23.1.
8. **E2E test** that walks the demo path.
9. **Docs:** update `docs/demo-script.md` with the demo path, `STATUS.md`, and any ADR.
10. **Report** with command output and screenshots.

Slice size: if a slice takes more than a day of work for a human, split it.

---

## 25. DEBUGGING AND RECOVERY WORKFLOWS

### 25.1 Fix a bug
1. **Reproduce** with exact steps or a failing test. If you cannot reproduce it, say so; do not "fix" it blind.
2. **Write the failing test first.**
3. List **2–3 hypotheses** with the evidence that would confirm or refute each.
4. Test hypotheses one at a time (logs, a debugger, a minimal script). Change **one thing at a time**.
5. Fix the root cause, not the symptom. Explain the cause in one sentence.
6. Run the new test and the full relevant suite. Check for the same bug pattern elsewhere (`grep`) and **report** (do not silently fix) other occurrences.
7. If the same approach fails 3 times, stop and use the BLOCKED template (Section 14).

### 25.2 When a change makes things worse
- Stop adding changes. Run `git status` and `git diff` to see exactly what you changed.
- Prefer returning to a known-good state: create a safety branch (`git switch -c rescue/<topic>`), then revert the specific files or commits. **Never** use `git reset --hard`, `git clean -fd`, or `git push --force` without the human's explicit approval.
- Tell the human what happened, what was reverted, and what you learned.

### 25.3 Flaky tests
- Never "fix" a flaky test by adding sleeps or retries without understanding the cause (shared state, time, ordering, real network).
- Make time, randomness, and external calls injectable. Quarantine only with human approval and a tracked issue.

### 25.4 Environment problems (Windows, Docker, ports)
- Report the exact error text. Check versions (`python --version`, `node --version`, `docker --version`) and the documented prerequisite before changing anything.
- Do not "fix" the environment by editing system settings or global installs. Propose changes and wait.

---

## 26. REVIEW WORKFLOW (for the human reviewing an agent's work)

Use this to decide quickly whether to accept a change.
1. **Read the REPORT first.** Are commands and outputs real and specific? Is "NOT RUN" used honestly?
2. **Check scope:** does the diff touch only what the task needs? Any new dependency, folder, or generated-file edit?
3. **Run it yourself:** the verification commands in Section 15, plus the structure checker.
4. **Spot-check the riskiest part:** SQL construction, permission checks, LLM calls, file handling, or the UI states.
5. **For UI:** open the screenshots; apply the 22.2 "tells" list and the "remove one accessory" test.
6. **Check for fake success:** tests that assert nothing, hardcoded returns, silent exception handling, invented metrics.
7. **Decide:** approve, request changes with specific points, or reject with the reason. Update `docs/STATUS.md`.

---

## Appendix A — `docs/STATUS.md` template

```markdown
# Unearth — Status

**Current phase:** 0
**Last updated:** YYYY-MM-DD by <agent/human>

## Done
- ...

## In progress (claimed by)
- [ ] <task> — <agent/branch>

## Next up (ordered)
1. ...

## Blockers / questions for the human
- ...

## Known issues (found, not fixed)
- ...

## Decisions pending
- ...
```

## Appendix B — ADR template (`docs/adr/NNNN-title.md`)

```markdown
# NNNN — Title
Status: proposed | accepted | superseded by NNNN
Date: YYYY-MM-DD

## Context
What problem or constraint forced a decision?

## Decision
What we decided, in one or two sentences.

## Alternatives considered
- A: why not
- B: why not

## Consequences
Good, bad, and what we must now do or avoid.
```

## Appendix C — Planned REST resources (confirm against `contracts/openapi.json`; do not assume)

`/api/v1/health` · `/auth` · `/sources` · `/uploads` · `/profiles` · `/semantics` · `/tools` · `/policies` · `/evals` · `/drift` · `/lineage` · `/reports` · `/jobs`

Rules: plural nouns, nested only one level, standard error shape, cursor or page-based pagination on all lists, `POST` for actions that create jobs and return a job id (`202 Accepted`).

## Appendix D — Planned worker jobs

`profile_job` · `inference_job` · `compile_job` · `eval_job` · `drift_job` · `report_job`
Each: idempotent, resumable, records status and progress, bounded retries.

## Appendix E — Multi-agent / multi-session hygiene

- Claim work in `docs/STATUS.md` ("In progress") before starting. Do not touch a task claimed by another session.
- One branch per task. Do not edit the same files as another active branch without coordinating.
- End every session with a handoff note in `STATUS.md`: what is done, what is half-done, exact next step, and any traps discovered.
- A fresh session must be able to continue from `AGENTS.md` + `STATUS.md` + the git log alone.

## Appendix F — How the human should prompt agents (recommended)

```
Read AGENTS.md and docs/STATUS.md first.
Task: <one clear task from the current phase>
Acceptance criteria: <how we will know it is done>
Constraints: <anything special>
Follow the Task Protocol: restate, plan (wait for my approval if it touches >5 files or changes a schema/API/dependency), implement in small steps, verify with real command output, then report using the REPORT template.
```

**Frontend task prompt:**
```
Read AGENTS.md (Sections 9, 22, 23) and docs/STATUS.md.
Screen: <name>. Job to be done: <one sentence>. Primary action: <action>.
First give me the screen brief, the design plan with an ASCII wireframe, and your check against the 'What to avoid' list. Wait for my approval before coding.
Then build with real/seeded data, all states, keyboard flow, and send screenshots at 1440/1024/390 plus the REPORT.
```

**Backend task prompt:**
```
Read AGENTS.md (Sections 7, 8, 21) and docs/STATUS.md.
Feature: <name>. Follow the recipe in 21.x for this kind of work.
First give me the schemas, error cases, and the PLAN. Wait for approval if it changes an API, schema, or dependency.
Then implement test-first and send the REPORT with real command output.
```

Good first tasks per phase are small and testable: "implement `file_sniffer.py` with tests for semicolon, tab, and pipe delimiters and UTF-16 encoding" is a good task; "build the whole profiling module" is not.