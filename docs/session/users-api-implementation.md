# Users API Implementation

## Overview
This document covers the implementation of the `/users` API endpoint with a separate database configuration for user data management.

## Implementation Steps Completed

### 1. Settings Configuration
- **File**: `backend/app/settings.py`
- **Changes**: Added `users_database_url` field to support separate database for users
- **Environment Variable**: `USERS_DATABASE_URL` must be set in environment

### 2. Database Configuration  
- **File**: `backend/app/db.py`
- **Changes**: 
  - Added `users_engine` for separate users database
  - Created `get_users_session()` dependency function
  - Maintains existing `get_session()` for assets database

### 3. Users Router
- **File**: `backend/app/routers/users.py`
- **Endpoints**:
  - `GET /users` - Fetch all users
  - `GET /users/{user_id}` - Fetch specific user by ID
- **Database**: Uses separate users database via `get_users_session()`

### 4. Main Application Updates
- **File**: `backend/app/main.py`
- **Changes**:
  - Imported `users_engine` and `User` model
  - Added users router inclusion
  - Updated lifespan to create tables in both databases

## Database Architecture

### Assets Database (Original)
- **Purpose**: Asset management data
- **Models**: Asset, ExportHistory
- **Session**: `get_session()`

### Users Database (New)
- **Purpose**: User management data  
- **Models**: User
- **Session**: `get_users_session()`

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
- **Description**: Retrieve all users from users database
- **Response**: List of User objects
- **Error Handling**: Returns 500 with error message if database query fails

### GET /users/{user_id}
- **Description**: Retrieve specific user by ID
- **Parameters**: `user_id` (integer)
- **Response**: Single User object
- **Error Handling**: Returns 404 if user not found, 500 for other errors

## Environment Setup Required

Add to your `.env` file:
```env
USERS_DATABASE_URL=your_users_database_connection_string
```

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

## Notes

- Both databases will have their tables created automatically on application startup
- The separation allows for independent scaling and management of user vs asset data
- Error handling follows existing patterns in the codebase
- All endpoints follow FastAPI best practices with proper type hints and documentation 