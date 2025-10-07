# Repository Guidelines

## Project Structure & Module Organization
- Backend refactor lives in `city_brain_system_refactored/`, with FastAPI routes in `api/v1/endpoints/`, services in `domain/services/`, repositories under `infrastructure/database/repositories/`, and shared logger utilities in `infrastructure/utils/`.
- Legacy backend is kept in `city_brain_system/`; consult it only for parity checks and never modify it without explicit instructions.
- Vue client code resides in `city_brain_frontend/`; place page views in `src/views/`, shared components in `src/components/`, and helpers in `src/utils/`.
- Tests sit under `tests/unit/`, `tests/integration/`, plus root-level `test_*.py`; coverage reports land in `htmlcov/`.

## Build, Test, and Development Commands
- `cd city_brain_system_refactored && pip install -r requirements.txt && python main.py` starts the API on port 9003.
- `pytest -v` (or `pytest --cov --cov-report=html`) exercises backend test suites and produces coverage output.
- `cd city_brain_frontend && npm install` once per environment, then `npm run dev` for local development on port 9002 and `npm run build` for production assets.
- Use scripts like `./start_refactored_backend.sh` or `./start.sh` / `./stop.sh` for orchestrating the stack.

## Coding Style & Naming Conventions
- Follow PEP 8 with four-space indentation, type hints, and docstrings for public modules. Run `black` and `pylint` (see `docs/guides/DEVELOPMENT_GUIDE.md`) before committing.
- Replace `print` with the structured logger exposed in `infrastructure/utils/logger.py`.
- Vue single-file components use PascalCase filenames, `<script setup>`, and camelCase composables aligned with aliases in `city_brain_frontend/vite.config.js`.

## Testing Guidelines
- Prefer pytest fixtures for API/database scenarios and mark slow/external suites appropriately.
- Maintain ≥60% coverage; regenerate reports with `pytest --cov --cov-report=html`.
- Name tests descriptively (e.g., `test_user_auth_flow.py`) and group shared fixtures in `tests/conftest.py`.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat:`, `fix:`, etc.) with subjects ≤72 characters and branches like `feature/<slug>`.
- PRs should link relevant issues, summarize scope, list verification steps (e.g., `pytest`, `npm run build`), and include payload samples or screenshots for UI/API tweaks.

## Security & Configuration Tips
- Copy `.env.example` to `.env` in both backend directories; provide `DATABASE_URL`, `DEEPSEEK_API_KEY`, and `BOCHA_API_KEY`.
- Keep default ports 9002/9003 unless adjusting the proxy settings in `city_brain_frontend/vite.config.js`.
- Manage schema changes through Alembic migrations and monitor runtime status via `start_city_brain.sh status` or logs in `logs/`.
