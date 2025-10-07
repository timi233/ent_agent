# Repository Guidelines

## Project Structure & Module Organization
The backend lives in `city_brain_system_refactored/` with FastAPI routes under `api/v1/endpoints/`, domain services in `domain/services/`, and repositories in `infrastructure/database/repositories/`. Vue client code is in `city_brain_frontend/`, grouping views in `src/views/` and shared UI or utilities in `src/components/` and `src/utils/`. Keep the legacy `city_brain_system/` untouched except for parity checks, and refer to `docs/` for architecture notes plus `scripts/` and root `start*.sh` helpers for automation.

## Build, Test, and Development Commands
- Backend: `cd city_brain_system_refactored && pip install -r requirements.txt && python main.py` launches the API on port 9003.
- Backend tests: `pytest -v` (or targeted suites like `python test_integration_e2e.py`).
- Frontend: `cd city_brain_frontend && npm install` once, then `npm run dev` for port 9002 or `npm run build` for production assets.
- Stack helpers: `./start_refactored_backend.sh`, `./start.sh`, and `./stop.sh` manage local orchestration.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indents, type hints, and docstrings for public modules. Run `black` and `pylint` as described in `docs/guides/DEVELOPMENT_GUIDE.md`. Replace `print` with the structured logger in `infrastructure/utils/logger.py`. Vue files use PascalCase filenames, `<script setup>`, and camelCase for composables; align import aliases with `vite.config.js`.

## Testing Guidelines
Tests reside in `tests/unit/`, `tests/integration/`, and repository-root `test_*.py`. Use pytest markers to flag slow/external suites and maintain ≥60% coverage. Generate HTML coverage reports with `pytest --cov --cov-report=html` (outputs to `htmlcov/`). Name tests descriptively and prefer fixture reuse for database or API scenarios.

## Commit & Pull Request Guidelines
Use Conventional Commits (e.g., `feat:` or `fix:`) with ≤72-character subjects. Branches follow `feature/<slug>` or `bugfix/<slug>`. PRs should link issues, summarize scope, list verification steps (`pytest`, `npm run build`, etc.), and attach screenshots or payload samples for UI or API changes.

## Security & Configuration Tips
Copy `.env.example` to `.env` within both backend directories and set `DATABASE_URL`, `DEEPSEEK_API_KEY`, and `BOCHA_API_KEY`. Keep default ports 9002/9003 unless updating the proxy in `city_brain_frontend/vite.config.js`. Manage schema updates via Alembic migrations and monitor runtime status with `start_city_brain.sh status` or logs under `logs/`.
