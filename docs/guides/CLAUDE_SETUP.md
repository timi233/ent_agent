# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Overview

This is a **City Brain Enterprise Information Processing System** being refactored from a monolithic architecture to a clean architecture with modular design. The project is currently in **Phase 4 (Core Business Logic)** with 86.4% completion.

**Current Status**: Phase 4 completed, preparing for Phase 5 (API Layer Refactoring)

## 🎯 Key Architecture Principles

1. **Clean Architecture**: Infrastructure → Domain → Application → API layers
2. **Repository Pattern**: All database operations go through repository classes
3. **Backward Compatibility**: All existing APIs must continue to work
4. **No Business Logic Changes**: Only refactoring architecture, not business rules
5. **Standalone Modules**: Each module is completely independent to avoid import issues

## 🔧 Common Development Commands

### Testing
```bash
# Run infrastructure tests
python test_infrastructure.py

# Run data layer tests
python test_data_layer_complete.py

# Run external services tests
python test_external_services.py

# Run core business logic tests
python test_phase4_core_business.py

# Run all tests (comprehensive)
python test_complete.py
```

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Check current progress
cd city_brain_system_refactored && python -c "print('Current progress: Phase 4 completed, preparing Phase 5')"
```

## 📁 Directory Structure & Key Components

```
city_brain_system_refactored/
├── config/simple_settings.py      # Simplified configuration (no external deps)
├── infrastructure/                # Infrastructure layer
│   ├── database/
│   │   ├── models/               # 7 data models (Customer, Enterprise, Industry, etc.)
│   │   ├── repositories/         # 5 repository classes with CRUD operations
│   │   ├── connection.py         # Database connection management
│   │   └── standalone_queries.py # Backward-compatible query interfaces
│   ├── external/                 # External service clients
│   │   ├── bocha_client.py       # Bocha AI search client
│   │   ├── llm_client.py         # LLM client for analysis
│   │   └── service_manager.py    # Service orchestration
│   └── utils/                    # Utility classes
├── domain/                       # Business logic layer
│   └── services/                 # Core business services
│       ├── enterprise_service.py      # Main orchestration service
│       ├── data_enhancement_service.py # Data enhancement logic
│       ├── analysis_service.py        # AI analysis service
│       └── search_service.py          # Search and extraction service
└── api/                          # API layer (Phase 5 - upcoming)
```

## 🧪 Testing Patterns

- **Test Files**: Named `test_*.py` in root directory
- **Test Structure**: Each test file validates specific layer functionality
- **Success Criteria**: 100% test pass rate required for each phase
- **Test Coverage**: Infrastructure (7/7), Data Layer (9/9), External Services (6/6), Core Business (5/5)

## 🔑 Key Technical Solutions

### Import Issues Resolution
- Created **fully standalone modules** (`fully_standalone_repository.py`)
- Cleared `__init__.py` files to avoid circular imports
- Use absolute paths and independent configuration classes

### Database Configuration
- **Host**: 192.168.101.13
- **Database**: City_Brain_DB
- **User**: City_Brain_user_mysql
- **Connection Pool**: Size 10, max overflow 20

### External Services
- **Bocha AI**: Web search API for enterprise information
- **DeepSeek LLM**: Analysis and summarization services
- **Service Manager**: Handles health checks and service orchestration

## 🚦 Current Phase Tasks (Phase 5)

Next tasks to complete:
1. **5.1**: Refactor API routing structure with versioning
2. **5.2**: Create Pydantic request/response models
3. **5.3**: Implement dependency injection
4. **5.4**: Compile and test API layer

## ⚠️ Important Constraints

1. **No Syntax Changes**: Must maintain compatibility with older Python versions
2. **No Business Logic Changes**: Only refactor architecture
3. **Backward Compatibility**: All existing interfaces must work
4. **Incremental Changes**: Small, reviewable changes only
5. **Test-Driven**: Every change must pass existing tests

## 📊 Progress Tracking

- **Total Tasks**: 22
- **Completed**: 19 (86.4%)
- **Remaining**: 3 (13.6%)
- **Test Success Rate**: 100% (27/27 tests passing)

## 🚀 Working with This Codebase

When making changes:
1. **Read existing files first** to understand current patterns
2. **Follow existing code conventions** and architecture
3. **Run tests after every change** to ensure nothing breaks
4. **Maintain backward compatibility** with existing APIs
5. **Use the standalone approach** for new modules to avoid import issues
6. **Update PROGRESS_SUMMARY.md** when completing tasks

For API development (Phase 5):
- Use FastAPI framework
- Implement versioned APIs (`/api/v1/`)
- Create Pydantic models for request/response validation
- Follow dependency injection patterns from existing services