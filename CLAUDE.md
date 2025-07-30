# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚧 Current Status: Code Consolidation in Progress

**Phase 1 Complete**: Architecture analysis, legacy archival, and foundation establishment
**Current Issue**: Import dependency resolution needed in `app_real.py` ecosystem
**Branch**: `feature/code-consolidation`

**For detailed status**: See `consolidation-progress-report.md`

## Development Commands

### Starting the Application
```bash
# CURRENT (Post-Consolidation): Single entry point
python src/main.py

# ARCHIVED (Legacy): Non-functional applications moved to src/legacy/
# python src/app.py              # ❌ Archived - broken dependencies
# python src/app_enhanced.py     # ❌ Archived - missing modules
```

### Testing
```bash
# Run test suite with environment setup
./run_tests.sh

# Manual environment validation
python test-files/validate_google_apis_environment.py
python test-files/verify_google_apis.py

# Test specific components
python src/test_blueprint_fixes.py
python src/test_blueprint_refactor.py
python test-files/test_custom_search.py
```

### Environment Setup
```bash
# Check environment configuration
./check_env.sh                # Linux/macOS
check_env.bat                 # Windows

# Setup Google APIs
./setup_google_apis.sh        # Linux/macOS
setup_google_apis.bat         # Windows

# Setup credentials
./setup_credentials.sh
```

### Python Environment
```bash
# Install dependencies
pip install -r requirements.txt

# For Google APIs integration
pip install -r requirements-google-apis.txt

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

## Architecture Overview

### Core Application Structure
- **Entry Points**: `src/main.py` (Google APIs) and `src/app.py` (legacy)
- **API Routes**: Organized in `src/routes/` with modular blueprint system
- **Services**: Core business logic in `src/services/` with orchestrated components
- **Models**: Database models in `src/models/` with blueprint and user management
- **Utils**: Utility modules in `src/utils/` including Google APIs integration

### Google APIs Integration
The application features a comprehensive Google APIs integration layer:

**Core Components**:
- `src/utils/google_apis/api_manager.py` - Centralized API management
- `src/utils/google_apis/migration_manager.py` - Seamless migration from SerpAPI
- Individual client modules for each Google API service

**Supported APIs**:
- Google Custom Search API (primary search)
- Google Knowledge Graph API (entity analysis)
- Google Natural Language API (content analysis)
- Google Gemini API (AI insights)
- Google Search Console API (performance data)

### Blueprint Generation System
Modular blueprint generation architecture:

**Core Services**:
- `BlueprintGeneratorService` - Main orchestrator combining analysis components
- `BlueprintAnalyzer` - Competitor and content analysis
- `BlueprintAIGenerator` - AI-powered content structuring
- `BlueprintUtils` - Validation and utility functions

**Processing Pipeline**:
1. Input handling and validation
2. SERP data collection (Google APIs or SerpAPI fallback)
3. Competitor analysis with enhanced data
4. Content analysis using Google Natural Language
5. AI-powered blueprint generation with Gemini
6. Result rendering and export

### Database Architecture
- SQLite database (`serp_strategist.db`) with migration support
- Blueprint storage with versioning
- User authentication and session management
- Migration scripts in `migrations/` directory

### API Endpoints Structure
```
/api/
├── process              # Main processing endpoint
├── blueprints/         # Blueprint CRUD operations
├── google-apis/        # Google APIs status and testing
├── auth/               # Authentication endpoints
└── user/               # User management
```

## Environment Configuration

### Required Environment Variables
```bash
# Google APIs (Primary)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GEMINI_API_KEY=your_google_api_key

# Migration Control
USE_GOOGLE_APIS=true
FALLBACK_TO_SERPAPI=true

# Optional: SerpAPI (fallback)
SERPAPI_API_KEY=your_serpapi_key
```

### Google Cloud Setup Requirements
1. Enable required APIs: Custom Search, Knowledge Graph, Natural Language, Gemini, Search Console
2. Create API key with proper restrictions
3. Setup service account with JSON credentials
4. Configure Custom Search Engine for web search

## Key Implementation Patterns

### Service Layer Pattern
Services follow a consistent pattern with:
- Dependency injection in constructors
- Error handling with logging
- Google APIs integration with fallback mechanisms
- Data validation and transformation

### Migration Strategy
The codebase implements a migration layer that:
- Automatically detects Google APIs availability
- Falls back to SerpAPI when needed
- Maintains backward compatibility
- Provides seamless transition path

### Error Handling
Comprehensive error handling includes:
- API-specific error handling with retry logic
- Graceful degradation when services unavailable
- Detailed logging for debugging
- User-friendly error messages

## Testing Strategy

### Test Categories
- **Unit Tests**: Individual component testing in `src/test_*.py`
- **Integration Tests**: API integration testing in `test-files/`
- **Environment Validation**: Setup verification scripts
- **End-to-End Tests**: Full workflow testing

### Test Execution
Tests are designed to run in isolation and validate:
- Google APIs connectivity and functionality
- Blueprint generation pipeline
- Database operations and migrations
- API endpoint responses

## Development Notes

### Google APIs Integration Status
- Core infrastructure completed and tested
- Main API endpoints enhanced with Google APIs
- Migration layer provides seamless fallback
- Performance monitoring and cost optimization implemented

### Code Organization Principles
- Modular design with clear separation of concerns
- Service-oriented architecture with dependency injection
- Consistent error handling and logging patterns
- Environment-driven configuration management

### Performance Considerations
- Google APIs provide 30-50% faster response times
- Built-in caching mechanisms for API responses
- Rate limiting and quota management
- Fallback mechanisms ensure reliability