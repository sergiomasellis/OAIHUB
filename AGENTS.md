# Repository Guidelines

## Build, Test, and Development Commands

### Full Stack (Recommended)
- All services: `docker-compose up --build`

### Backend Commands
- Setup: `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Install test dependencies: `cd backend && pip install pytest fastapi[all]`
- Start API: `cd backend && python main.py` (defaults to `PORT=8001`)
- Init DynamoDB: `cd backend && python ../infrastructure/setup_dynamodb.py`
- Run all tests: `cd backend && python -m pytest`
- Run single test: `cd backend && python -m pytest test_main.py::test_function_name -v`
- Run tests with coverage: `cd backend && python -m pytest --cov=.`

### Frontend Commands
- Install: `cd frontend && npm install`
- Dev server: `cd frontend && npm run dev` (Next.js, default port 3000)
- Build: `cd frontend && npm run build`
- Start production: `cd frontend && npm start`
- Lint: `cd frontend && npm run lint`
- Type check: `cd frontend && npx tsc --noEmit`

## Code Style Guidelines

### TypeScript/React
- **Components**: PascalCase (e.g., `KPICards`, `DataTable`)
- **Files**: kebab-case with extensions (e.g., `kpi-cards.tsx`, `data-table.ts`)
- **Functions/Methods**: camelCase (e.g., `formatValue`, `handleSubmit`)
- **Variables**: camelCase (e.g., `userData`, `isLoading`)
- **Types/Interfaces**: PascalCase (e.g., `UserProps`, `ApiResponse`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)

### Python
- **Classes**: PascalCase (e.g., `UserModel`, `ApiClient`)
- **Functions/Methods**: snake_case (e.g., `get_user_data`, `validate_input`)
- **Variables**: snake_case (e.g., `user_data`, `is_active`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `MAX_CONNECTIONS`)
- **Type hints**: Required for function parameters and return types

### Import Organization
```typescript
// React imports first
import * as React from "react"
import { useState, useEffect } from "react"

// External libraries (alphabetical)
import { IconArrowUpRight } from "@tabler/icons-react"
import { Card, CardHeader } from "@/components/ui/card"

// Internal imports (alphabetical)
import { api } from "@/lib/api"
import { type Filters } from "@/lib/analytics"
```

### Error Handling
- Use try-catch for async operations
- Provide meaningful error messages
- Handle loading states appropriately
- Log errors for debugging but don't expose sensitive information

### TypeScript Best Practices
- Strict mode enabled - no implicit any types
- Define interfaces for API responses and component props
- Use union types for state that can have multiple values
- Prefer `type` over `interface` for primitive type aliases
- Use path aliases (`@/*`) for internal imports

### Testing Guidelines
- Backend: pytest with FastAPI TestClient; test files named `test_*.py`
  - Note: pytest not in requirements.txt - install with `pip install pytest fastapi[all]`
  - Use FastAPI TestClient for API endpoint testing
- Frontend: No specific test framework configured yet; use Testing Library + Vitest/Jest when adding tests
- Co-locate test files as `*.test.tsx` or `*.spec.ts`
- Aim for meaningful coverage on routes, models, and critical UI components

## Commit & Pull Request Guidelines
- Commits: Conventional Commits style (e.g., `feat(backend): add metrics endpoint`)
- PRs: Clear description, linked issues, test results, screenshots for UI changes
- Keep changes scoped; update `docs/` and example commands when behavior changes

## Local Development Setup

### Sample Data Population
After running `docker-compose up -d`, populate sample data for testing:

**Automated Script (Recommended)**
```bash
# Make script executable (first time only)
chmod +x scripts/setup-local-data.sh

# Run the setup script
./scripts/setup-local-data.sh
```

This script will:
- ✅ Wait for services to be ready
- ✅ Create DynamoDB tables
- ✅ Populate sample metrics data
- ✅ Add sample events for agents
- ✅ Verify everything is working

**What gets populated:**
- ✅ DynamoDB tables creation
- ✅ Sample metrics data (July-Aug 2025)
- ✅ Sample events data for agents
- ✅ Realistic KPI values and time series data

**After setup, your dashboard will show:**
- 📊 **KPI Metrics**: 850+ calls, 1.2% error rate, 223ms latency
- 📈 **Time Series**: Visitors, calls, and errors over time
- 👥 **Agents**: agent-1, agent-2 with filtering
- 📅 **Date Range**: July 25 - August 24, 2025

### Resetting Data
If you need to reset the sample data:
```bash
# Stop containers and remove volumes
docker-compose down -v

# Restart services
docker-compose up -d

# Repopulate sample data
./scripts/setup-local-data.sh
```

## Security & Configuration
- Do not commit secrets; use `.env` files (backend reads via `python-dotenv`)
- Local dev uses DynamoDB Local (`:8000`); production uses AWS
- Configure `AWS_REGION`, table names, and credentials via environment variables
