# Repository Guidelines

## Project Structure & Module Organization
- `main.py` boots the FastAPI app, sets lifespan hooks, and pulls services via dependency injection.
- `api/v1/` hosts versioned endpoints and shared dependencies; add new routes under `api/v1/endpoints/`.
- `domain/services/` contains orchestration logic (`EnterpriseService`, `SearchService`, etc.) that should stay framework-agnostic.
- `infrastructure/` wraps databases, external clients, and utilities; repositories live in `infrastructure/database/`.
- Configuration lives in `config/`; update `simple_settings.py` for environment defaults and use `.env` files for secrets.
- Tests sit beside the code: curated `test_*.py` scripts in the repo root and scaffolding for suites in `tests/unit/` and `tests/integration/`.

## Build, Test, and Development Commands
- Install dependencies: `pip install -r requirements.txt`.
- Run the API locally: `uvicorn main:app --reload --port 8000`.
- Execute focused checks: `python test_phase4_core_business.py` or `python test_external_services.py`.
- Run the full suite: `pytest` or `python test_complete.py`.

## Coding Style & Naming Conventions
- Use 4-space indentation, descriptive snake_case module and function names, and PascalCase classes that mirror existing services.
- Favor module-level docstrings and keep inline comments for non-obvious control flow only.
- Format with `black`, lint with `flake8`, and type-check critical paths via `mypy` before sending reviews.
- Maintain backward-compatible Python syntax; avoid newer features that existing modules do not already rely on.

## Testing Guidelines
- Mirror filename patterns like `test_<layer>.py` and write test functions as `test_<behavior>`.
- Prefer `pytest` fixtures for setup; reuse the standalone repository helpers already shared across infrastructure tests.
- Keep the curated scripts green before merging (`python test_complete.py` must succeed).
- For coverage checks, run `pytest --cov=infrastructure --cov=domain` and address any uncovered orchestration paths.

## Commit & Pull Request Guidelines
- Craft imperative subject lines that call out the affected layer, e.g., `phase5: add api health check` or `infra: harden redis client`.
- Reference related tasks from `PROGRESS_SUMMARY.md` or issue IDs in the body and document architectural decisions briefly.
- Include test evidence in the PR description (`pytest` output, targeted scripts) and screenshots for API responses when they change.
- Keep changes incremental and backward compatible; spell out migration steps or configuration toggles explicitly when needed.

## Security & Configuration Tips
- Never hardcode credentials; rely on `python-dotenv` and keep secrets in ignored `.env.local` files.
- Validate database connectivity through `infrastructure/database/connection.test_connection()` before deployment.
- Route new external calls through `infrastructure/external/` abstractions to preserve auditability and isolation.
