# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a City Brain Enterprise Information Processing System (城市大脑企业信息处理系统) - an intelligent platform that combines local database queries, web search, and LLM technologies to provide structured summaries of enterprise and industry information.

**Key Technologies:**
- Backend: FastAPI (Python)
- Frontend: Vue 3 + Vite
- Database: MySQL
- External APIs: Bocha AI Search, DeepSeek LLM
- Deployment: Docker

## System Architecture

The codebase contains THREE separate systems:

1. **city_brain_system_refactored/** - The main refactored backend (Clean Architecture)
   - Port: 9003
   - Entry: `main.py`
   - Architecture: api/ → domain/ → infrastructure/

2. **city_brain_system/** - Legacy backend (being phased out)
   - Port: 9003
   - Simpler structure, older implementation

3. **city_brain_frontend/** - Vue 3 frontend
   - Port: 9002
   - Proxies API requests to backend on port 9003

**Use city_brain_system_refactored for new development** - it implements Clean Architecture with proper separation of concerns.

## Common Commands

### Backend (Refactored - Primary)

```bash
# Start refactored backend
./start_refactored_backend.sh

# Or manually
cd city_brain_system_refactored
python3 main.py  # Starts on port 9003

# Install dependencies
cd city_brain_system_refactored
pip install -r requirements.txt

# Run tests
python -m pytest tests/                    # All tests
python test_infrastructure.py              # Infrastructure tests
python test_data_layer_complete.py         # Data layer tests
python test_external_services.py           # External API tests
python test_integration_e2e.py            # End-to-end tests
python test_performance_benchmark.py       # Performance tests
```

### Backend (Legacy)

```bash
cd city_brain_system
make install          # Install dependencies
make test            # Run tests (pytest)
make run             # Start server
make clean           # Clean cache files
```

### Frontend

```bash
cd city_brain_frontend
npm install          # Install dependencies
npm run start        # Start dev server on port 9002
npm run build        # Build for production
npm run serve        # Preview production build
```

### Full System

```bash
# Start entire system (frontend + backend)
./start.sh           # Daily startup script
./stop.sh            # Stop all services

# Quick start (auto-installs dependencies)
./quick_start.sh

# Full-featured startup
./start_city_brain.sh start    # Start
./start_city_brain.sh status   # Check status
./start_city_brain.sh restart  # Restart
./start_city_brain.sh stop     # Stop
```

### Access URLs

- Frontend: http://localhost:9002
- Backend API Docs: http://localhost:9003/docs
- Backend Health: http://localhost:9003/api/v1/health

## Architecture Details

### Refactored Backend (Clean Architecture)

```
city_brain_system_refactored/
├── api/                          # API Layer - HTTP handlers
│   └── v1/
│       ├── endpoints/            # API endpoints (company.py, health.py)
│       ├── schemas/              # Request/Response models
│       └── dependencies.py       # Dependency injection
├── domain/                       # Domain Layer - Business logic
│   └── services/
│       ├── enterprise_service.py       # Main enterprise processing
│       ├── search_service.py           # Search logic
│       ├── data_enhancement_service.py # Data enrichment
│       └── analysis_service.py         # Analysis logic
├── infrastructure/               # Infrastructure Layer
│   ├── database/                 # Data access
│   │   ├── connection.py         # Database connection
│   │   ├── standalone_queries.py # Backward-compatible queries
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── customer.py
│   │   │   ├── enterprise.py
│   │   │   ├── industry.py
│   │   │   ├── industry_brain.py
│   │   │   ├── area.py
│   │   │   └── relations.py
│   │   └── repositories/         # Repository pattern
│   │       ├── base_repository.py
│   │       ├── customer_repository.py
│   │       ├── enterprise_repository.py
│   │       ├── industry_repository.py
│   │       └── area_repository.py
│   ├── external/                 # External service clients
│   │   ├── bocha_client.py       # Bocha AI search
│   │   ├── llm_client.py         # LLM client
│   │   ├── service_manager.py    # Service orchestration
│   │   ├── news_service.py
│   │   ├── ranking_service.py
│   │   └── revenue_service.py
│   └── utils/                    # Utility functions
│       ├── logger.py
│       ├── text_processor.py
│       └── address_processor.py
├── config/                       # Configuration
│   ├── simple_settings.py        # Simplified config
│   ├── settings.py               # Detailed config
│   └── database.py               # Database config
├── core/                         # Core business components
│   ├── ai/                       # AI integrations
│   ├── company/                  # Company-specific logic
│   └── search/                   # Search logic
└── tests/
    ├── unit/                     # Unit tests
    └── integration/              # Integration tests
```

**Key Patterns:**
- **Dependency Injection**: Services receive dependencies via constructor
- **Repository Pattern**: Data access abstracted through repositories
- **Clean Architecture**: Dependencies point inward (api → domain → infrastructure)

### Database Schema

The system uses MySQL with the following core tables:
- `QD_customer` - Customer enterprises
- `QD_area` - Geographic areas
- `QD_industry` - Industries
- `QD_industry_brain` - Industry brains (linked to areas)
- `QD_enterprise_chain_leader` - Chain leader enterprises
- `QD_brain_industry_rel` - Many-to-many: industry brains ↔ industries

**Relationships:**
- Customer → Industry (industry_id)
- Customer → Industry Brain (brain_id)
- Customer → Chain Leader (chain_leader_id)
- Industry Brain → Area (area_id)
- Chain Leader → Area + Industry

### External Services

**Bocha AI Search** (`infrastructure/external/bocha_client.py`):
- Endpoint: https://api.bochaai.com/v1/web-search
- Used for: Web search when local data is missing/incomplete
- Auth: Bearer token (API_KEY in .env)

**DeepSeek LLM** (`infrastructure/external/llm_client.py`):
- Endpoint: https://api.deepseek.com
- Model: deepseek-chat
- Used for: Structured summary generation
- Auth: API Key (DEEPSEEK_API_KEY in .env)

## Development Workflow

### Adding a New Feature

1. **Domain Layer**: Implement business logic in `domain/services/`
2. **Infrastructure**: Add data access in `infrastructure/database/repositories/`
3. **API Layer**: Create endpoint in `api/v1/endpoints/`
4. **Schema**: Define request/response in `api/v1/schemas/`
5. **Tests**: Add tests in `tests/unit/` and `tests/integration/`

### Coding Standards

- **Style**: PEP 8 (enforced via black, flake8)
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Required for all public methods
- **Imports**: Absolute imports (e.g., `from infrastructure.database.models.customer import Customer`)
- **Error Handling**: Specific exceptions, proper logging
- **Naming**:
  - Classes: PascalCase (e.g., `EnterpriseService`)
  - Functions: snake_case (e.g., `process_company_info`)
  - Constants: UPPER_CASE (e.g., `MAX_RETRY_COUNT`)
  - Private: prefix with `_` (e.g., `_internal_method`)

### Configuration

Environment variables are managed through `.env` files:
- Copy `.env.example` to `.env` in both backend directories
- Required variables: DATABASE_URL, DEEPSEEK_API_KEY, BOCHA_API_KEY
- Access via: `from config.simple_settings import load_settings`

### Testing Strategy

Tests are located at the root of `city_brain_system_refactored/`:

```bash
# Infrastructure tests (database, external services)
python test_infrastructure.py
python test_data_layer_complete.py
python test_external_services.py

# Integration tests (end-to-end)
python test_integration_e2e.py

# Performance benchmarks
python test_performance_benchmark.py

# Repository validation
python validate_repositories.py

# Pytest-based tests (in tests/ directory)
pytest tests/unit/
pytest tests/integration/
```

**Test Structure**:
- `tests/unit/` - Unit tests for services, repositories, utilities
- `tests/integration/` - Integration tests for API endpoints
- Root-level `test_*.py` - Comprehensive system tests

## Port Configuration

System uses the following ports:

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 9002 | Vue dev server |
| Backend  | 9003 | FastAPI service |

**Important**: The system previously used ports 9000/9001 but migrated to 9002/9003. References to old ports may exist in documentation.

To check port usage:
```bash
lsof -i :9002
lsof -i :9003
```

To kill processes on these ports:
```bash
pkill -f "vite"
pkill -f "uvicorn.*9003"
```

## Data Flow

### With Local Data (Complete):
User Input → Extract Company → Query Database → Check Completeness → Generate Summary with LLM → Return Result

### With Local Data (Incomplete):
User Input → Extract Company → Query Database → Detect Missing Info → Web Search (Bocha) → Merge Data → Generate Summary with LLM → Update Database → Return Result

### Without Local Data:
User Input → Extract Company → No Database Match → Web Search (Bocha) → Generate Summary with LLM → Store in Database → Return Result

## Common Troubleshooting

### Database Connection Issues
```python
# Test database connection
from infrastructure.database.connection import test_connection
result = test_connection()
```

### External Service Health Check
```python
from infrastructure.external.service_manager import ServiceManager
manager = ServiceManager()
health = manager.get_all_service_health()
```

### Port Already in Use
```bash
# Check and kill process
lsof -i :9003
kill -9 <PID>
```

### Frontend Proxy Issues
Check `city_brain_frontend/vite.config.js` - API requests to `/api` should proxy to `http://localhost:9003`

## Key Files

- `city_brain_system_refactored/main.py` - Backend entry point (FastAPI app)
- `city_brain_frontend/src/main.js` - Frontend entry point
- `city_brain_frontend/vite.config.js` - Frontend build config + API proxy
- `start.sh` - Main startup script for entire system
- `stop.sh` - Shutdown script
- `docs/guides/DEVELOPMENT_GUIDE.md` - Comprehensive development guide
- `docs/guides/STARTUP_GUIDE.md` - System startup instructions
- `docs/architecture/system-architecture.md` - Architecture documentation

## Important Notes

- **Always use city_brain_system_refactored** for new development (not city_brain_system)
- **Database queries**: Use repositories in `infrastructure/database/repositories/`, not direct SQL
- **External API calls**: Always go through service managers with proper error handling
- **Logging**: Use the logger from `infrastructure/utils/logger.py`, not print()
- **Time handling**: The system has timezone-aware datetime utilities in `infrastructure/utils/datetime_utils.py`
- **Text processing**: Use utilities in `infrastructure/utils/text_processor.py` for Chinese text handling

## Performance Considerations

- Database connection pooling is configured in `infrastructure/database/connection.py`
- External API calls should be async where possible
- Consider caching for frequently accessed data
- See `test_performance_benchmark.py` for performance baselines
