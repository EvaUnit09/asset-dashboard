# Users API Implementation

## Overview
This document covers the implementation of the `/users` API endpoint with a users table in the main database for user data management.

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

### GET /users
- **Description**: Retrieve all users from main database
- **Response**: List of User objects
- **Error Handling**: Returns 500 with error message if database query fails

### GET /users/{user_id}
- **Description**: Retrieve specific user by ID
- **Parameters**: `user_id` (integer)
- **Response**: Single User object
- **Error Handling**: Returns 404 if user not found, 500 for other errors

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

The API endpoints can be tested via:
1. FastAPI automatic docs at `/docs`
2. Direct HTTP requests to `/users` endpoints
3. Existing test patterns in `test_api_endpoints.py`

## Future Enhancements

Potential additions to consider:
- POST/PUT/DELETE endpoints for user management
- User search and filtering capabilities
- Pagination for large user datasets
- User authentication and authorization
- Integration with asset assignment functionality
- Foreign key relationships between users and assets

## Notes

- Users table will be created automatically on application startup or via migration
- Single database simplifies management and relationships
- Error handling follows existing patterns in the codebase
- All endpoints follow FastAPI best practices with proper type hints and documentation 
- Easier to implement user-asset relationships in the future 