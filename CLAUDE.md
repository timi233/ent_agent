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

The codebase contains FOUR separate systems:

1. **city_brain_system_refactored/** - The main refactored backend (Clean Architecture)
   - Port: 9003
   - Entry: `main.py`
   - Architecture: api/ → domain/ → infrastructure/
   - **Use this for all new development**

2. **city_brain_system/** - Legacy backend (being phased out)
   - Port: 9003
   - Simpler structure, older implementation
   - **Do not use for new features**

3. **city_brain_frontend/** - Vue 3 frontend (current production version)
   - Port: 9002
   - Simple chat-based interface
   - Proxies API requests to backend on port 9003
   - **Currently in use**

4. **city_brain_frontend_v2/** - Next-generation Vue 3 + TypeScript frontend
   - Port: 9002
   - Full domain-driven architecture with Pinia, composables, Storybook
   - Features: dashboard, insights, operations, planning, admin modules
   - **In development - not yet integrated**

## Common Commands

### Backend

```bash
# Start backend
./start_refactored_backend.sh

# Or manually
cd city_brain_system_refactored
python3 main.py  # Starts on port 9003

# Install dependencies
cd city_brain_system_refactored
pip install -r requirements.txt

# Run tests (from city_brain_system_refactored/)
# Pytest-based tests (organized in tests/ subdirectory)
python -m pytest tests/unit/               # Unit tests
python -m pytest tests/integration/        # Integration tests
python -m pytest tests/                    # All pytest tests

# Standalone test scripts (root level)
python test_infrastructure.py              # Infrastructure: DB, connections
python test_data_layer_complete.py         # Data layer: repositories, models
python test_external_services.py           # External: Bocha, DeepSeek APIs
python test_integration_e2e.py             # End-to-end integration
python test_performance_benchmark.py       # Performance benchmarks
python validate_repositories.py            # Repository validation
```

### Frontend (Current - v1)

```bash
cd city_brain_frontend
npm install          # Install dependencies
npm run start        # Start dev server on port 9002
npm run build        # Build for production
npm run serve        # Preview production build
```

### Frontend (Next Generation - v2)

```bash
cd city_brain_frontend_v2
npm install          # Install dependencies
npm run dev          # Start dev server on port 9002
npm run build        # Build for production
npm run lint         # ESLint + Prettier check
npm run test         # Vitest + @testing-library
npm run storybook    # Storybook component docs (port 7007)
```

**Note**: v2 is TypeScript-based with enhanced architecture but not yet integrated with production. Use v1 for production deployments.

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
│   │       ├── enterprise_qd_repository.py
│   │       ├── industry_repository.py
│   │       ├── area_repository.py
│   │       ├── opportunities_repository.py  # AS/IPG CRM data
│   │       ├── work_order_repository.py     # Service tickets
│   │       ├── crm_repository.py            # CRM integrations
│   │       └── crm_sync_repository.py       # CRM sync tasks
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

The system uses **multiple MySQL databases** running in Docker containers:

#### Primary Database (City_Brain_DB)
Core enterprise data tables:
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

#### feishu_crm Database
CRM and opportunity data:
- `as_opportunities` - AS system opportunities (448 records)
- `ipg_clients` - IPG system client opportunities (1,678 records)
- `sync_tasks` - Data synchronization task metadata

#### enterprise_QD Database
Qingdao enterprise archives:
- `enterprise_QD` - Qingdao enterprise profiles (268 records)
- Contains: company info, industry, revenue data, rankings

#### Task_sync_new Database
Work order/service ticket data:
- `task_service_records` - Service work orders (86 records)
- `task_service_records_raw` - Raw work order data
- `task_service_record_users` - User assignments

**Docker Containers:**
- `mysql-feishu-crm` - Hosts feishu_crm, enterprise_QD, Task_sync_new databases
- Port: 3306 (mapped to host 3306 or 3307)

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

### Adding a New Data Source

Example: Integrating a new database table with the opportunities API

1. **Create Data Model** (`infrastructure/database/models/`):
   ```python
   @dataclass
   class MyDataModel:
       field1: str
       field2: Optional[int]

       def to_dict(self): ...

       @classmethod
       def from_db_row(cls, row): ...
   ```

2. **Create Repository** (`infrastructure/database/repositories/`):
   ```python
   class MyRepository:
       def __init__(self):
           self.database = "my_database"
           self._connection_pool = None

       def search_by_company_name(self, name, limit):
           # Implementation with connection pooling
   ```

3. **Update API Endpoint** (`api/v1/endpoints/opportunities.py`):
   - Import new repository
   - Add query in `/search` endpoint
   - Include in response data and summary

4. **Update Frontend** (`city_brain_frontend/src/`):
   - Add data property in `Home.vue`
   - Update `fetchOpportunities()` to receive new data
   - Pass to `OpportunitiesSection.vue` as prop
   - Add display section with badge/cards in component

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

### Main Company Processing Flow

#### With Local Data (Complete):
User Input → Extract Company → Query Database → Check Completeness → Generate Summary with LLM → Return Result

#### With Local Data (Incomplete):
User Input → Extract Company → Query Database → Detect Missing Info → Web Search (Bocha) → Merge Data → Generate Summary with LLM → Update Database → Return Result

#### Without Local Data:
User Input → Extract Company → No Database Match → Web Search (Bocha) → Generate Summary with LLM → Store in Database → Return Result

### Opportunities/CRM Data Flow

The system integrates four data sources via `/api/v1/opportunities/search`:

1. **AS Opportunities** (feishu_crm.as_opportunities)
   - Sales opportunities from AS system
   - Searched by customer_name

2. **IPG Clients** (feishu_crm.ipg_clients)
   - Client opportunities from IPG system
   - Searched by client_name

3. **Enterprise Archives** (enterprise_QD.enterprise_QD)
   - Qingdao enterprise profiles with revenue data
   - Searched by company name

4. **Work Orders** (Task_sync_new.task_service_records)
   - Service tickets and work orders
   - Searched by customer_company

**Query Flow:**
```
User searches "临工重机" →
  ├─ OpportunitiesRepository.find_as_opportunities_by_customer()
  ├─ OpportunitiesRepository.find_ipg_clients_by_name()
  ├─ EnterpriseQDRepository.search_by_keyword()
  └─ WorkOrderRepository.search_by_company_name()
→ Aggregate results → Return to frontend
```

**Frontend Display:**
- AS system: Green badge
- IPG system: Orange badge
- Enterprise archive: Blue badge
- Work orders: Red badge

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

### Frontend Architecture (v1 - Current)

**Key Components:**
- `src/views/Home.vue` - Main page with company search and results display
- `src/components/OpportunitiesSection.vue` - Displays AS/IPG/QD/Work Order data
- `vite.config.js` - Build config with proxy to backend at `/api` → `http://localhost:9003`

**Component Communication:**
```
Home.vue
  ├─ Fetches opportunities via axios.get('/api/v1/opportunities/search')
  ├─ Stores in data: asOpportunities, ipgClients, qdEnterprises, workOrders
  └─ Passes to <OpportunitiesSection> component as props
```

**Vue Template Guidelines:**
- Use `v-if`/`v-else-if`/`v-else` chains carefully - siblings must be adjacent
- Conditional rendering with loading states: use separate `v-if` for loading skeletons
- API proxy handles `/api` routes automatically via Vite config

### Frontend Architecture (v2 - Next Gen)

**Structure:**
- `src/components/base/` - Base UI components (Card, EmptyState)
- `src/components/layout/` - Layout framework (AppShell, TopBar, Sidebar)
- `src/components/data/` - Data display (tables, charts, forms, maps)
- `src/components/feedback/` - Feedback components (Toast)
- `src/views/` - Domain views (dashboard, insights, operations, planning, admin)
- `src/stores/` - Pinia stores for state management
- `src/composables/` - Reusable composition functions
- `src/services/` - API layer aligned with backend DTOs

**Key Features:**
- TypeScript throughout for type safety
- Storybook for component documentation
- Vitest + Testing Library for unit tests
- WebSocket integration for real-time notifications
- Design tokens for consistent theming

## Important Notes

- **Always use city_brain_system_refactored** for new development (not city_brain_system)
- **Database queries**: Use repositories in `infrastructure/database/repositories/`, not direct SQL
- **External API calls**: Always go through service managers with proper error handling
- **Logging**: Use the logger from `infrastructure/utils/logger.py`, not print()
- **Text processing**: Use utilities in `infrastructure/utils/text_processor.py` for Chinese text handling
- **Time handling**: System has timezone-aware datetime utilities in `infrastructure/utils/datetime_utils.py`

## Performance Considerations

- Database connection pooling is configured in `infrastructure/database/connection.py`
- External API calls should be async where possible
- Consider caching for frequently accessed data
- See `test_performance_benchmark.py` for performance baselines
