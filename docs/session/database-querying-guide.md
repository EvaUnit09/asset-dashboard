# Database Querying Guide

## Overview
This guide covers how to query the database from the Asset Management System server using various methods including SQLModel/SQLAlchemy ORM, direct SQL queries, and database management tools.

## Database Architecture

The system uses a single PostgreSQL database containing all application data:

### Main Database
- **Purpose**: All application data (assets, users, export history)
- **Models**: `Asset`, `User`, `ExportHistory`
- **Session**: `get_session()`
- **Engine**: `engine`

## Database Connection

### Environment Variables
```bash
# Single database for all data
DATABASE_URL=postgresql+asyncpg://admin:password@db:5433/assetdb
```

### Session Management
```python
from app.db import get_session
from sqlmodel import Session

# For all database operations
async def get_data():
    async with get_session() as session:
        # Your queries here
        pass
```

## SQLModel/SQLAlchemy Queries

### Basic Select Operations

#### Get All Records
```python
from sqlmodel import select
from app.models import Asset, User

# Get all assets
async def get_all_assets(session: Session):
    statement = select(Asset)
    result = await session.exec(statement)
    return result.all()

# Get all users
async def get_all_users(session: Session):
    statement = select(User)
    result = await session.exec(statement)
    return result.all()
```

#### Get Single Record by ID
```python
# Get asset by ID
async def get_asset_by_id(session: Session, asset_id: int):
    statement = select(Asset).where(Asset.id == asset_id)
    result = await session.exec(statement)
    return result.first()

# Get user by ID
async def get_user_by_id(session: Session, user_id: int):
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    return result.first()
```

### Filtering and Conditions

#### Where Clauses
```python
# Assets by category
async def get_assets_by_category(session: Session, category: str):
    statement = select(Asset).where(Asset.category == category)
    result = await session.exec(statement)
    return result.all()

# Users by department
async def get_users_by_department(session: Session, department_id: str):
    statement = select(User).where(User.department_id == department_id)
    result = await session.exec(statement)
    return result.all()

# Assets with warranty expiring soon
from datetime import date, timedelta
async def get_expiring_warranties(session: Session, days: int = 30):
    cutoff_date = date.today() + timedelta(days=days)
    statement = select(Asset).where(
        Asset.warranty_expires <= cutoff_date,
        Asset.warranty_expires.is_not(None)
    )
    result = await session.exec(statement)
    return result.all()
```

#### Multiple Conditions
```python
# Complex filtering
async def get_filtered_assets(session: Session, category: str, status: str):
    statement = select(Asset).where(
        Asset.category == category,
        Asset.status == status
    )
    result = await session.exec(statement)
    return result.all()

# OR conditions
from sqlmodel import or_
async def get_laptops_or_desktops(session: Session):
    statement = select(Asset).where(
        or_(Asset.category == "Laptop", Asset.category == "Desktop")
    )
    result = await session.exec(statement)
    return result.all()
```

### Joins and Relationships

#### Cross-Table Queries
```python
# Example: Find users with assets (when relationships are implemented)
async def get_users_with_assets(session: Session):
    statement = select(User, Asset).where(
        # This assumes a future relationship field
        # User.id == Asset.assigned_user_id
    )
    result = await session.exec(statement)
    return result.all()

# Count assets per user (example)
from sqlmodel import func
async def get_user_asset_counts(session: Session):
    statement = select(
        User.username,
        func.count(Asset.id).label("asset_count")
    ).select_from(
        User.__table__.outerjoin(Asset.__table__)
        # This assumes a future relationship
    ).group_by(User.id, User.username)
    result = await session.exec(statement)
    return result.all()
```

### Sorting and Limiting

#### Order By
```python
# Sort assets by name
async def get_assets_sorted(session: Session):
    statement = select(Asset).order_by(Asset.asset_name)
    result = await session.exec(statement)
    return result.all()

# Sort users by last name
async def get_users_sorted(session: Session):
    statement = select(User).order_by(User.last_name, User.first_name)
    result = await session.exec(statement)
    return result.all()
```

#### Pagination
```python
# Paginated results
async def get_assets_paginated(session: Session, skip: int = 0, limit: int = 100):
    statement = select(Asset).offset(skip).limit(limit)
    result = await session.exec(statement)
    return result.all()
```

### Aggregation Queries

#### Count Records
```python
from sqlmodel import func

# Count all assets
async def count_assets(session: Session):
    statement = select(func.count(Asset.id))
    result = await session.exec(statement)
    return result.one()

# Count users
async def count_users(session: Session):
    statement = select(func.count(User.id))
    result = await session.exec(statement)
    return result.one()

# Count by category
async def count_assets_by_category(session: Session):
    statement = select(Asset.category, func.count(Asset.id)).group_by(Asset.category)
    result = await session.exec(statement)
    return result.all()
```

#### Group By Operations
```python
# Assets count by status
async def get_status_summary(session: Session):
    statement = select(
        Asset.status,
        func.count(Asset.id).label("count")
    ).group_by(Asset.status)
    result = await session.exec(statement)
    return result.all()

# Users by department
async def get_department_summary(session: Session):
    statement = select(
        User.department_id,
        func.count(User.id).label("user_count")
    ).group_by(User.department_id)
    result = await session.exec(statement)
    return result.all()
```

## Direct SQL Queries

### Using Raw SQL
```python
from sqlalchemy import text

# Execute raw SQL query
async def execute_raw_query(session: Session, query: str):
    result = await session.exec(text(query))
    return result.all()

# Example: Complex reporting query
async def get_warranty_report(session: Session):
    query = """
    SELECT 
        manufacturer,
        category,
        COUNT(*) as total_assets,
        COUNT(CASE WHEN warranty_expires < CURRENT_DATE THEN 1 END) as expired,
        COUNT(CASE WHEN warranty_expires BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days' THEN 1 END) as expiring_soon
    FROM asset 
    WHERE warranty_expires IS NOT NULL
    GROUP BY manufacturer, category
    ORDER BY manufacturer, category
    """
    result = await session.exec(text(query))
    return result.all()
```

### Cross-Table Analysis
```python
# Users and assets overview
async def get_user_asset_overview(session: Session):
    query = """
    SELECT 
        u.username,
        u.department_id,
        COUNT(a.id) as assigned_assets,
        STRING_AGG(DISTINCT a.category, ', ') as asset_categories
    FROM "user" u
    LEFT JOIN asset a ON u.id = a.assigned_user_id  -- Future relationship
    GROUP BY u.id, u.username, u.department_id
    ORDER BY u.username
    """
    result = await session.exec(text(query))
    return result.all()
```

## Database Management Operations

### Creating Records
```python
# Create new asset
async def create_asset(session: Session, asset_data: dict):
    asset = Asset(**asset_data)
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    return asset

# Create new user
async def create_user(session: Session, user_data: dict):
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Bulk insert
async def create_multiple_assets(session: Session, assets_data: list):
    assets = [Asset(**data) for data in assets_data]
    session.add_all(assets)
    await session.commit()
    return assets
```

### Updating Records
```python
# Update single asset
async def update_asset(session: Session, asset_id: int, update_data: dict):
    statement = select(Asset).where(Asset.id == asset_id)
    result = await session.exec(statement)
    asset = result.first()
    
    if asset:
        for field, value in update_data.items():
            setattr(asset, field, value)
        await session.commit()
        await session.refresh(asset)
    return asset

# Update user information
async def update_user(session: Session, user_id: int, update_data: dict):
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    user = result.first()
    
    if user:
        for field, value in update_data.items():
            setattr(user, field, value)
        await session.commit()
        await session.refresh(user)
    return user
```

## Performance Optimization

### Query Optimization
```python
# Use indexes effectively (asset_tag is indexed)
async def get_assets_by_tag_optimized(session: Session, asset_tag: str):
    statement = select(Asset).where(Asset.asset_tag == asset_tag)
    result = await session.exec(statement)
    return result.first()

# Limit fields for better performance
async def get_asset_summary(session: Session):
    statement = select(Asset.id, Asset.asset_name, Asset.status)
    result = await session.exec(statement)
    return result.all()

# Efficient user lookup
async def get_user_summary(session: Session):
    statement = select(User.id, User.username, User.email)
    result = await session.exec(statement)
    return result.all()
```

## Command Line Database Access

### Using psql
```bash
# Connect to main database
psql -h localhost -p 5433 -U admin -d assetdb

# Common psql commands
\dt                    # List tables
\d asset              # Describe asset table
\d user               # Describe user table  
\d+ asset             # Detailed table info
\q                    # Quit
```

### Useful SQL Commands
```sql
-- Check table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public';

-- Check all tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM asset WHERE category = 'Laptop';
EXPLAIN ANALYZE SELECT * FROM "user" WHERE department_id = 'IT';
```

## Database Schema Overview

### Current Tables
```sql
-- asset table (existing)
CREATE TABLE asset (
    id SERIAL PRIMARY KEY,
    asset_name VARCHAR,
    asset_tag VARCHAR UNIQUE,
    category VARCHAR,
    -- ... other asset fields
);

-- user table (new)
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR,
    last_name VARCHAR,
    username VARCHAR,
    email VARCHAR,
    department_id VARCHAR,
    -- ... other user fields
);

-- export_history table (existing)
CREATE TABLE export_history (
    id SERIAL PRIMARY KEY,
    config_json VARCHAR NOT NULL,
    created_at DATE NOT NULL,
    -- ... other export fields
);
```

## Best Practices

1. **Always use async sessions** for database operations
2. **Handle exceptions** properly with try/catch blocks
3. **Use indexes** for frequently queried fields
4. **Limit query results** for large datasets
5. **Use transactions** for multi-step operations
6. **Close sessions** properly (async context managers handle this)
7. **Validate input** before database operations
8. **Use SQLModel/SQLAlchemy ORM** instead of raw SQL when possible
9. **Monitor query performance** and optimize slow queries
10. **Use connection pooling** for production deployments
11. **Consider foreign key relationships** for data integrity

## Future Enhancements

### Potential Relationship Improvements
```python
# Example: Future asset-user relationship
class Asset(SQLModel, table=True):
    # ... existing fields ...
    assigned_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
# This would enable:
# - Direct asset assignment to users
# - Better reporting capabilities
# - Data integrity constraints
```

This guide provides comprehensive coverage of database querying techniques for the Asset Management System's single database architecture. Use these patterns and examples as reference for implementing database operations in your application. 