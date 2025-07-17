# Department Name Enhancement for Dashboard Filtering

## Overview
This document covers the enhancement to add `department_name` to the User model to enable department filtering on the main dashboard page.

## Requirements
- Extract department name from SnipeIT API response in addition to department ID
- Store department name in the database for easy filtering
- Update frontend types to include department name
- Enable department-based filtering on dashboard

## SnipeIT API Structure
According to SnipeIT documentation, the department object structure is:
```json
{
  "department": {
    "id": 1,
    "name": "Product Management"
  }
}
```

## Implementation Steps Completed

### 1. Backend Model Update
- **File**: `backend/app/models.py`
- **Changes**: Added `department_name` field to User model
- **Field Type**: `str | None = Field(default=None, nullable=True)`
- **Position**: Added after `department_id` field

### 2. Sync Logic Enhancement
- **File**: `backend/app/sync.py`
- **Function**: `sync_snipeit_users()`
- **Changes**: Added extraction of `department.get("name")` to store department name
- **Data Source**: Existing expanded department object from SnipeIT API

### 3. Database Migration
- **File**: `backend/alembic/versions/c4d5e6f7g8h9_add_department_name_to_users.py`
- **Purpose**: Add `department_name` column to existing user table
- **Migration ID**: c4d5e6f7g8h9
- **Type**: ALTER TABLE to add nullable string column

### 4. Frontend Type Update
- **File**: `frontend/src/types/user.ts`
- **Changes**: Added `department_name: string` to User interface
- **Position**: Added after `department_id` field

## Technical Details

### Database Schema Change
```sql
-- Migration adds this column
ALTER TABLE "user" ADD COLUMN department_name VARCHAR NULL;
```

### API Response Enhancement
The `/users` endpoint will now return department names:
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "username": "john.doe",
  "email": "john.doe@company.com",
  "county": "County Name",
  "department_id": "5",
  "department_name": "Product Management",
  "location_id": "2",
  "assets_count": 3,
  "license_count": 1
}
```

### Sync Process
1. `fetch_all_users()` retrieves users with expanded department data
2. `sync_snipeit_users()` extracts both `department.id` and `department.name`
3. Database stores both ID (for relationships) and name (for display/filtering)

## Data Flow
```
SnipeIT API → fetch_all_users() → sync_snipeit_users() → Database → API → Frontend
```

## Migration Process

### Apply Database Changes
```bash
cd backend
alembic upgrade head
```

### Sync Updated Data
```bash
# Run users sync to populate department names
python run_users_sync.py

# Or full sync
python run_users_sync.py --full
```

## Dashboard Filtering Implementation (Next Steps)

### Frontend Components to Update
1. **Dashboard.tsx** - Add department filter dropdown
2. **AssetTable.tsx** - Support department filtering if applicable
3. **Layout.tsx** - Consider adding department filter to global navigation

### Filter Implementation Strategy
```tsx
// Example department filter implementation
const departments = useMemo(() => {
  return [...new Set(users.map(user => user.department_name).filter(Boolean))];
}, [users]);

const filteredAssets = useMemo(() => {
  if (!selectedDepartment) return assets;
  return assets.filter(asset => 
    // Logic to match assets to department
    // This may require additional asset-to-user relationships
  );
}, [assets, selectedDepartment]);
```

### API Enhancements Needed
- Consider adding department filtering to `/assets` endpoint
- May need to establish user-asset relationships for filtering
- Add department list endpoint for dropdown options

## Benefits

### Performance
- Department names available locally without API calls
- Faster filtering and display operations
- Reduced network requests for dropdown options

### User Experience
- Human-readable department names in UI
- Consistent department naming across components
- Improved filtering capabilities

### Data Integrity
- Single source of truth for department names
- Consistent with SnipeIT department structure
- Maintains ID for potential relationships

## Future Enhancements

### Dashboard Filtering
- Department-based asset filtering
- Multi-department selection
- Department-based user filtering
- Export filtering by department

### Reporting Features
- Department-wise asset reports
- User distribution by department
- Department usage analytics

### UI Components
- Department badge/tag components
- Department-based color coding
- Department hierarchy display

## Testing

### Database Migration Testing
```bash
# Test migration up
alembic upgrade head

# Test migration down (if needed)
alembic downgrade -1
```

### Data Sync Testing
```bash
# Test users sync
python run_users_sync.py

# Verify data in database
psql -d assetdb -c "SELECT id, username, department_id, department_name FROM \"user\" LIMIT 10;"
```

### API Testing
```bash
# Test updated API response
curl http://localhost:8000/api/users | jq '.[0] | {username, department_id, department_name}'
```

## Notes

### Backward Compatibility
- Existing API consumers will receive new `department_name` field
- Migration is additive (no breaking changes)
- Existing queries continue to work

### Data Consistency
- Department names sync with each user sync
- Names stay current with SnipeIT changes
- Fallback to ID if name unavailable

### Performance Considerations
- Minimal impact on sync performance
- Improved filtering performance vs API calls
- Consider indexing if filtering heavily used

## Related Files Modified
- `backend/app/models.py` - User model
- `backend/app/sync.py` - Sync logic
- `backend/alembic/versions/c4d5e6f7g8h9_add_department_name_to_users.py` - Migration
- `frontend/src/types/user.ts` - TypeScript types

## Configuration
No additional configuration required - uses existing SnipeIT API connection and database settings. 