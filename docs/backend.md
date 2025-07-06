# Backend Documentation

## Overview

The backend is built with **FastAPI** and provides a RESTful API for the Asset Management System. It uses **SQLAlchemy** with **SQLModel** for database operations and **PostgreSQL** as the database.

## Technology Stack

- **FastAPI 0.115.13** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0.41** - SQL toolkit and ORM
- **SQLModel 0.0.24** - SQL databases in Python, designed for compatibility with both SQLAlchemy and Pydantic
- **PostgreSQL 16** - Primary database
- **Alembic 1.16.2** - Database migration tool
- **Uvicorn 0.34.3** - ASGI server
- **Pydantic 2.11.7** - Data validation using Python type annotations

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # Database configuration and session management
│   ├── models.py            # SQLModel database models
│   ├── settings.py          # Application settings and configuration
│   ├── snipeit.py           # Snipe-IT API integration
│   ├── sync.py              # Data synchronization logic
│   └── routers/
│       ├── assets.py        # Asset-related API endpoints
│       └── sync.py          # Synchronization API endpoints
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── requirements.txt         # Python dependencies
└── alembic.ini             # Alembic configuration
```

## Database Models

### Asset Model

The main `Asset` model represents IT assets in the system:

```python
class Asset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic identification
    asset_name: str | None = Field(default=None, sa_column=Column(String, index=True))
    asset_tag: str | None = Field(alias="AssetTag", default=None, sa_column=Column(String, unique=True))
    model_no: str | None = Field(alias="ModelNo", default=None, sa_column=Column(String))
    
    # Asset details
    model: str | None = Field(default=None, nullable=True)
    company: str | None = Field(default=None, nullable=True)
    category: str | None = Field(default=None, sa_column=Column(String))
    manufacturer: str | None = Field(default=None, nullable=True)
    serial: str | None = Field(default=None, nullable=True)
    
    # Warranty information
    warranty: str | None = Field(default=None, nullable=True)
    warranty_expires: date | None = Field(default=None, nullable=True)
    
    # Location and status
    location: str | None = Field(default=None, nullable=True)
    department: str | None = Field(default=None, nullable=True)
    status: str | None = Field(default=None, nullable=True)
    
    # Timestamps
    created_at: str | None = Field(default=None, nullable=True)
```

## API Endpoints

### Assets Router (`/api/assets`)

#### GET `/api/assets`
Retrieves all assets from the database.

**Response:**
```json
[
  {
    "id": 1,
    "asset_name": "Laptop-001",
    "asset_tag": "LT001",
    "model_no": "XPS-13",
    "model": "Dell XPS 13",
    "company": "Company A",
    "category": "Laptop",
    "manufacturer": "Dell",
    "serial": "ABC123456",
    "warranty": "3 Years",
    "warranty_expires": "2026-01-15",
    "location": "Office A",
    "department": "IT",
    "status": "Active",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### Sync Router (`/api/sync`)

#### POST `/api/sync`
Synchronizes assets from Snipe-IT API to the local database.

**Request Body:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "message": "Sync completed successfully",
  "assets_synced": 150,
  "timestamp": "2024-01-15T10:30:00"
}
```

## Database Configuration

### Connection Setup

The database connection is configured in `app/db.py`:

```python
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database URL from environment
DATABASE_URL = "postgresql+asyncpg://admin:password@db:5433/assetdb"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://admin:password@db:5433/assetdb

# Snipe-IT Integration
SNIPEIT_API_URL=https://your-snipeit-instance.com/api/v1
SNIPEIT_TOKEN=your_api_token

# Application
POSTGRES_PASSWORD=your_secure_password
```

## Snipe-IT Integration

The backend integrates with Snipe-IT for asset synchronization:

### Features
- Fetches assets from Snipe-IT API
- Maps Snipe-IT fields to local database schema
- Handles pagination for large datasets
- Provides sync status and error reporting

### Configuration
- API URL and token configuration
- Field mapping between Snipe-IT and local schema
- Sync frequency and error handling

## Database Migrations

### Using Alembic

1. **Create a new migration:**
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Rollback migrations:**
   ```bash
   alembic downgrade -1
   ```

### Migration History

- `641895e746f5_.py` - Initial database schema
- `97a592f9fb09_warranty_expires_to_date.py` - Convert warranty_expires to date type

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request** - Invalid request data
- **404 Not Found** - Resource not found
- **422 Validation Error** - Pydantic validation failures
- **500 Internal Server Error** - Server-side errors

## CORS Configuration

CORS is configured to allow requests from specific origins:

```python
origins = [
    "http://10.4.208.227",
    "http://asset-ny.worldwide.bbc.co.uk"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development

### Running Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access API documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app
```

## Production Deployment

### Docker Configuration

The backend is containerized with a multi-stage Dockerfile:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
# ... build dependencies

# Production stage
FROM python:3.11-slim as production
# ... runtime configuration
```

### Health Checks

The application includes health check endpoints for container orchestration:

- Database connectivity checks
- Snipe-IT API connectivity checks
- Application status monitoring

## Monitoring and Logging

- **Structured logging** with Python's logging module
- **Request/response logging** for debugging
- **Database query logging** in development mode
- **Error tracking** and reporting

## Security Considerations

- **Environment variable** configuration for sensitive data
- **CORS** restrictions to allowed origins
- **Input validation** using Pydantic models
- **SQL injection protection** through SQLAlchemy ORM
- **HTTPS enforcement** in production 