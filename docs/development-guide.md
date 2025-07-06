# Development Guide

## Overview

This guide provides comprehensive information for developers working on the Asset Management System, including setup instructions, coding standards, testing procedures, and contribution guidelines.

## Prerequisites

### Required Software

- **Python 3.11+** - Backend development
- **Node.js 18+** - Frontend development
- **Git** - Version control
- **PostgreSQL 16** - Database
- **Windows Server 2022** - Production environment
- **IIS** - Web server for production
- **NSSM** - Windows service management

### Recommended Tools

- **VS Code** - IDE with extensions:
  - Python
  - TypeScript and JavaScript
  - Docker
  - GitLens
  - Prettier
  - ESLint
- **Postman** or **Insomnia** - API testing
- **pgAdmin** or **DBeaver** - Database management

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Asset-Management
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with your configuration
```

### 4. Database Setup

#### Option A: Using Docker (Development Only)

```bash
# Start PostgreSQL container
docker run --name asset-db \
  -e POSTGRES_DB=assetdb \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:16-alpine

# Run migrations
cd backend
alembic upgrade head
```

#### Option B: Local PostgreSQL (Production-like)

```bash
# Install PostgreSQL locally
# Create database and user
createdb assetdb
psql -d assetdb -c "CREATE USER admin WITH PASSWORD 'password';"
psql -d assetdb -c "GRANT ALL PRIVILEGES ON DATABASE assetdb TO admin;"

# Run migrations
cd backend
alembic upgrade head
```

### 5. Start Development Servers

#### Backend Development Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development Server

```bash
cd frontend
npm run dev
```

## Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── db.py                # Database configuration
│   ├── models.py            # SQLModel models
│   ├── settings.py          # Application settings
│   ├── snipeit.py           # Snipe-IT integration
│   ├── sync.py              # Data synchronization
│   └── routers/
│       ├── __init__.py
│       ├── assets.py        # Asset endpoints
│       └── sync.py          # Sync endpoints
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                   # Test files
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── test_assets.py       # Asset tests
│   └── test_sync.py         # Sync tests
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── alembic.ini             # Alembic configuration
└── .env.example            # Environment template
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── AssetChart.tsx
│   │   ├── AssetTable.tsx
│   │   └── ...
│   ├── hooks/              # Custom React hooks
│   │   └── useAssets.ts
│   ├── lib/                # Utility functions
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── types/              # TypeScript types
│   │   └── asset.ts
│   ├── App.tsx
│   └── main.tsx
├── tests/                  # Test files
│   ├── components/
│   └── hooks/
├── public/                 # Static assets
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.example
```

## Coding Standards

### Python (Backend)

#### Code Style

- Follow **PEP 8** style guide
- Use **Black** for code formatting
- Use **isort** for import sorting
- Use **flake8** for linting

#### Configuration

Create `pyproject.toml` in the backend directory:

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
```

#### Naming Conventions

- **Classes**: PascalCase (e.g., `Asset`, `AssetRouter`)
- **Functions**: snake_case (e.g., `get_assets`, `create_asset`)
- **Variables**: snake_case (e.g., `asset_list`, `user_id`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)

#### Type Hints

Always use type hints:

```python
from typing import List, Optional
from datetime import date

def get_assets(company: Optional[str] = None) -> List[Asset]:
    """Retrieve assets from database."""
    pass

def create_asset(asset_data: dict) -> Asset:
    """Create a new asset."""
    pass
```

#### Documentation

Use docstrings for all functions and classes:

```python
def sync_assets(force: bool = False) -> dict:
    """
    Synchronize assets from Snipe-IT API.
    
    Args:
        force: Force full synchronization
        
    Returns:
        dict: Sync results with statistics
        
    Raises:
        SnipeITError: When API communication fails
    """
    pass
```

### TypeScript/JavaScript (Frontend)

#### Code Style

- Use **Prettier** for code formatting
- Use **ESLint** for linting
- Follow **Airbnb** style guide

#### Configuration

Update `package.json`:

```json
{
  "scripts": {
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx}\"",
    "lint": "eslint src --ext .ts,.tsx,.js,.jsx",
    "lint:fix": "eslint src --ext .ts,.tsx,.js,.jsx --fix"
  }
}
```

#### Naming Conventions

- **Components**: PascalCase (e.g., `AssetTable`, `StatusPieChart`)
- **Functions**: camelCase (e.g., `getAssets`, `handleSubmit`)
- **Variables**: camelCase (e.g., `assetList`, `isLoading`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`, `MAX_RETRIES`)
- **Files**: kebab-case (e.g., `asset-table.tsx`, `use-assets.ts`)

#### TypeScript Best Practices

```typescript
// Use interfaces for object shapes
interface Asset {
  id?: number;
  asset_name?: string;
  asset_tag?: string;
  // ... other properties
}

// Use type aliases for unions
type AssetStatus = 'Active' | 'Pending Rebuild' | 'Stock' | 'Retired';

// Use enums for constants
enum AssetCategory {
  LAPTOP = 'Laptop',
  DESKTOP = 'Desktop',
  MONITOR = 'Monitor',
  SERVER = 'Server'
}

// Use generic types
function useAssets<T = Asset>(): UseQueryResult<T[], Error> {
  // implementation
}
```

## Testing

### Backend Testing

#### Test Structure

```python
# tests/test_assets.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_assets():
    """Test retrieving all assets."""
    response = client.get("/api/assets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_asset():
    """Test creating a new asset."""
    asset_data = {
        "asset_name": "Test Asset",
        "asset_tag": "TEST001",
        "company": "Test Company"
    }
    response = client.post("/api/assets", json=asset_data)
    assert response.status_code == 201
    assert response.json()["asset_name"] == "Test Asset"
```

#### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_assets.py

# Run with verbose output
pytest -v
```

#### Test Configuration

Create `tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Frontend Testing

#### Test Structure

```typescript
// tests/components/AssetTable.test.tsx
import { render, screen } from '@testing-library/react';
import { AssetTable } from '../../src/components/AssetTable';

const mockAssets = [
  {
    id: 1,
    asset_name: 'Test Asset',
    asset_tag: 'TEST001',
    company: 'Test Company',
    status: 'Active'
  }
];

describe('AssetTable', () => {
  it('renders asset data correctly', () => {
    render(<AssetTable data={mockAssets} />);
    
    expect(screen.getByText('Test Asset')).toBeInTheDocument();
    expect(screen.getByText('TEST001')).toBeInTheDocument();
    expect(screen.getByText('Test Company')).toBeInTheDocument();
  });
});
```

#### Running Tests

```bash
# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

#### Test Configuration

Create `vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

## Database Development

### Creating Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new field to assets"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Database Seeding

Create `backend/scripts/seed.py`:

```python
from app.db import SessionLocal
from app.models import Asset

def seed_assets():
    """Seed database with sample assets."""
    db = SessionLocal()
    
    sample_assets = [
        Asset(
            asset_name="Laptop-001",
            asset_tag="LT001",
            company="Company A",
            category="Laptop",
            status="Active"
        ),
        # ... more assets
    ]
    
    for asset in sample_assets:
        db.add(asset)
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_assets()
```

## API Development

### Adding New Endpoints

1. **Create router function** in appropriate router file:

```python
# app/routers/assets.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Asset

router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("/{asset_id}")
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get asset by ID."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
```

2. **Include router** in main application:

```python
# app/main.py
from app.routers.assets import router as assets_router

app.include_router(assets_router)
```

3. **Add tests** for the new endpoint:

```python
# tests/test_assets.py
def test_get_asset_by_id(client):
    """Test retrieving asset by ID."""
    # Create test asset first
    asset_data = {"asset_name": "Test Asset", "asset_tag": "TEST001"}
    create_response = client.post("/api/assets", json=asset_data)
    asset_id = create_response.json()["id"]
    
    # Get asset by ID
    response = client.get(f"/api/assets/{asset_id}")
    assert response.status_code == 200
    assert response.json()["asset_name"] == "Test Asset"
```

## Frontend Development

### Adding New Components

1. **Create component file**:

```typescript
// src/components/NewComponent.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface NewComponentProps {
  data: any[];
  title: string;
}

export function NewComponent({ data, title }: NewComponentProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Component content */}
      </CardContent>
    </Card>
  );
}
```

2. **Add component to main application**:

```typescript
// src/App.tsx
import { NewComponent } from './components/NewComponent';

export default function DashboardPage() {
  // ... existing code
  
  return (
    <div>
      {/* ... existing components */}
      <NewComponent data={filtered} title="New Component" />
    </div>
  );
}
```

3. **Add tests** for the component:

```typescript
// tests/components/NewComponent.test.tsx
import { render, screen } from '@testing-library/react';
import { NewComponent } from '../../src/components/NewComponent';

describe('NewComponent', () => {
  it('renders with title', () => {
    render(<NewComponent data={[]} title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });
});
```

### Adding New Hooks

```typescript
// src/hooks/useNewData.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useNewData() {
  return useQuery({
    queryKey: ['new-data'],
    queryFn: async () => {
      const response = await api.get('/new-endpoint');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

## Debugging

### Backend Debugging

#### Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

#### Debugging with pdb

```python
import pdb

def problematic_function():
    # ... some code
    pdb.set_trace()  # Debugger will stop here
    # ... more code
```

#### FastAPI Debug Mode

```bash
# Run with debug mode
uvicorn app.main:app --reload --log-level debug
```

### Frontend Debugging

#### React Developer Tools

Install React Developer Tools browser extension for debugging React components.

#### Console Logging

```typescript
// Use console.log for debugging
console.log('Debug data:', data);

// Use console.error for errors
console.error('Error occurred:', error);

// Use console.table for tabular data
console.table(assets);
```

#### Browser DevTools

- **Network tab**: Monitor API requests
- **Console tab**: View logs and errors
- **Elements tab**: Inspect DOM structure
- **Sources tab**: Debug JavaScript code

## Performance Optimization

### Backend Optimization

#### Database Queries

```python
# Use eager loading to avoid N+1 queries
assets = db.query(Asset).options(
    joinedload(Asset.company),
    joinedload(Asset.category)
).all()

# Use pagination for large datasets
assets = db.query(Asset).offset(offset).limit(limit).all()
```

#### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_asset_categories():
    """Cache asset categories."""
    return db.query(Asset.category).distinct().all()
```

### Frontend Optimization

#### React Optimization

```typescript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  // Component logic
});

// Use useMemo for expensive calculations
const expensiveValue = useMemo(() => {
  return data.filter(item => item.status === 'Active').length;
}, [data]);

// Use useCallback for stable function references
const handleClick = useCallback(() => {
  // Handle click
}, []);
```

#### Bundle Optimization

```typescript
// Use dynamic imports for code splitting
const LazyComponent = lazy(() => import('./LazyComponent'));

// Use React.Suspense for loading states
<Suspense fallback={<div>Loading...</div>}>
  <LazyComponent />
</Suspense>
```

## Git Workflow

### Branch Naming

- **Feature branches**: `feature/asset-export`
- **Bug fixes**: `fix/asset-filter-issue`
- **Hotfixes**: `hotfix/critical-bug`
- **Documentation**: `docs/api-documentation`

### Commit Messages

Follow conventional commits:

```
feat: add asset export functionality
fix: resolve asset filter issue
docs: update API documentation
test: add tests for asset creation
refactor: improve asset table performance
```

### Pull Request Process

1. **Create feature branch** from `main`
2. **Make changes** following coding standards
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Create pull request** with description
6. **Request review** from team members
7. **Address feedback** and make changes
8. **Merge** after approval

## Deployment

### Development Deployment

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Deployment (Windows Server)

```powershell
# Set up environment variables
[Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql://admin:password@localhost:5432/assetdb", "Machine")

# Install backend service with NSSM
nssm install AssetManagementBackend "C:\Python311\python.exe"
nssm set AssetManagementBackend AppDirectory "C:\inetpub\wwwroot\asset-management\backend"
nssm set AssetManagementBackend AppParameters "C:\inetpub\wwwroot\asset-management\backend\app\main.py"

# Start service
Start-Service AssetManagementBackend

# Configure IIS for frontend
# See deployment.md for detailed IIS configuration
```

## Troubleshooting

### Common Issues

#### Backend Issues

1. **Database Connection Error**
   ```bash
   # Check database status
   docker-compose ps db
   
   # Check database logs
   docker-compose logs db
   ```

2. **Import Errors**
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

#### Frontend Issues

1. **Build Errors**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **TypeScript Errors**
   ```bash
   # Check TypeScript configuration
   npx tsc --noEmit
   ```

### Getting Help

- **Documentation**: Check this guide and API docs
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions
- **Team Chat**: Use team communication platform

## Contributing

### Before Contributing

1. **Read documentation** thoroughly
2. **Check existing issues** and discussions
3. **Discuss changes** with the team
4. **Follow coding standards** and conventions

### Contribution Checklist

- [ ] Code follows style guidelines
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

### Code Review Guidelines

- **Be constructive** and respectful
- **Focus on code quality** and maintainability
- **Consider edge cases** and error handling
- **Check for security issues**
- **Verify test coverage**
- **Ensure documentation clarity** 