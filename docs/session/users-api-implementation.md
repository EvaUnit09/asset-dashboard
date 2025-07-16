# Users API Implementation

## Overview
This document covers the implementation of the `/users` API endpoint with a users table in the main database for user data management, including automatic synchronization from Snipe-IT.

## Implementation Steps Completed

### 1. Users Router
- **File**: `backend/app/routers/users.py`
- **Endpoints**:
  - `GET /users` - Fetch all users
  - `GET /users/{user_id}` - Fetch specific user by ID
- **Database**: Uses main database via `get_session()`

### 2. Main Application Updates
- **File**: `backend/app/main.py`
- **Changes**:
  - Imported `User` model
  - Added users router inclusion
  - Updated lifespan to create all tables in main database

### 3. Database Migration
- **File**: `backend/alembic/versions/b2c3d4e5f6a7_add_users_table.py`
- **Purpose**: Adds users table to existing database
- **Migration ID**: b2c3d4e5f6a7

### 4. Users Sync Implementation
- **File**: `backend/app/sync.py`
- **Functions**:
  - `sync_snipeit_users()` - Sync users from Snipe-IT API
  - `sync_all()` - Sync both assets and users
- **API Integration**: Uses existing `fetch_all_users()` from `snipeit.py`

### 5. Sync API Endpoints
- **File**: `backend/app/routers/sync.py`
- **New Endpoints**:
  - `POST /sync/users` - Trigger users-only sync
  - `POST /sync/all` - Trigger full sync (assets + users)
  - `POST /sync/assets` - Trigger assets-only sync (explicit)

### 6. Scheduler Updates
- **File**: `backend/app/scheduler.py`
- **Changes**: Updated scheduled jobs to run full sync (assets + users) at 8am, 12pm, 4pm, and 8pm

## Database Architecture

### Single Database Approach
- **Purpose**: All application data (assets, users, export history)
- **Models**: Asset, User, ExportHistory
- **Session**: `get_session()` for all models
- **Benefits**: 
  - Simplified configuration
  - Single connection pool
  - Easier data relationships
  - Simplified backup/restore

## User Model Structure
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str | None = Field(default=None, nullable=True)
    last_name: str | None = Field(default=None, nullable=True)
    username: str | None = Field(default=None, nullable=True)
    email: str | None = Field(default=None, nullable=True)
    county: str | None = Field(default=None, nullable=True)
    department_id: str | None = Field(default=None, nullable=True)
    location_id: str | None = Field(default=None, nullable=True)
    assets_count: int | None = Field(default=None, nullable=True)
    license_count: int | None = Field(default=None, nullable=True)
```

## API Endpoints

### Users Endpoints

#### GET /users
- **Description**: Retrieve all users from main database
- **Response**: List of User objects
- **Error Handling**: Returns 500 with error message if database query fails

#### GET /users/{user_id}
- **Description**: Retrieve specific user by ID
- **Parameters**: `user_id` (integer)
- **Response**: Single User object
- **Error Handling**: Returns 404 if user not found, 500 for other errors

### Sync Endpoints

#### POST /sync/users
- **Description**: Trigger background sync of users from Snipe-IT
- **Response**: `{"status": "users sync scheduled"}`
- **Background Task**: Runs `sync_snipeit_users()`

#### POST /sync/all
- **Description**: Trigger background sync of both assets and users from Snipe-IT
- **Response**: `{"status": "full sync scheduled (assets + users)"}`
- **Background Task**: Runs `sync_all()`

#### POST /sync/assets
- **Description**: Trigger background sync of assets only from Snipe-IT
- **Response**: `{"status": "assets sync scheduled"}`
- **Background Task**: Runs `sync_snipeit_assets()`

## Synchronization Features

### Automatic Sync
- **Scheduled Times**: 8:00 AM, 12:00 PM, 4:00 PM, 8:00 PM daily
- **Scope**: Full sync (assets + users)
- **Background Processing**: Non-blocking operations
- **Error Handling**: Comprehensive logging and error reporting

### Manual Sync Options
```bash
# Sync users only
python run_users_sync.py

# Full sync (assets + users)
python run_users_sync.py --full

# Via API
curl -X POST http://your-server/api/sync/users
curl -X POST http://your-server/api/sync/all
```

### Data Mapping
Users are mapped from Snipe-IT API to local database:
- **id**: Snipe-IT user ID (primary key)
- **first_name**: User's first name
- **last_name**: User's last name  
- **username**: User's username
- **email**: User's email address
- **county**: User's county
- **department_id**: Department ID from Snipe-IT
- **location_id**: Location ID from Snipe-IT
- **assets_count**: Number of assets assigned to user
- **license_count**: Number of licenses assigned to user

## Database Migration

To apply the users table migration:
```bash
cd backend
alembic upgrade head
```

This will create the `user` table in your existing database.

## Environment Setup

No additional environment variables needed - uses existing `DATABASE_URL`.

## Testing

### API Testing
1. **FastAPI automatic docs** at `/docs`
2. **Direct HTTP requests** to `/users` and `/sync` endpoints
3. **Existing test patterns** in `test_api_endpoints.py`

### Manual Testing
```bash
# Test users sync
cd backend
python run_users_sync.py

# Test full sync
python run_users_sync.py --full

# Check results
curl http://localhost:8000/api/users
```

## Future Enhancements

Potential additions to consider:
- POST/PUT/DELETE endpoints for user management
- User search and filtering capabilities
- Pagination for large user datasets
- User authentication and authorization
- Integration with asset assignment functionality
- Foreign key relationships between users and assets
- Real-time sync triggers
- Sync status monitoring and reporting

## Notes

- Users table will be created automatically on application startup or via migration
- Single database simplifies management and relationships
- Error handling follows existing patterns in the codebase
- All endpoints follow FastAPI best practices with proper type hints and documentation 
- Easier to implement user-asset relationships in the future
- **Automatic sync** ensures users data stays current with Snipe-IT
- **Background tasks** prevent API blocking during sync operations
- **Flexible sync options** allow for targeted or comprehensive updates 