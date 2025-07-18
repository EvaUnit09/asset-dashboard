# Department Name Enhancement

## Issue Description
The Users page is displaying "Unassigned" for department names even though the `department_name` column exists in the database. The column is showing as null for all users.

## Investigation

### Current State
- User model has both `department_id` and `department_name` fields
- Migration `c4d5e6f7g8h9_add_department_name_to_users.py` exists to add `department_name` column
- Sync process in `sync.py` attempts to populate `department_name` from Snipe-IT API
- Frontend displays "Unassigned" when `department_name` is null

### Root Cause Analysis
The issue is likely one of the following:
1. Migration not applied - `department_name` column doesn't exist in database
2. Sync process not populating `department_name` correctly
3. Snipe-IT API not returning department names in expected format

## Solution Steps

### Step 1: Verify Database Schema
Check if the `department_name` column exists in the user table:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'user' 
ORDER BY ordinal_position;
```

### Step 2: Apply Migration (if needed)
If the column doesn't exist, apply the migration:
```bash
cd backend
python -m alembic upgrade head
```

### Step 3: Test Sync Process
Run a manual sync to see if department names are being populated:
```bash
cd backend
python run_users_sync.py
```

### Step 4: Debug Sync Logic
Check the sync process in `backend/app/sync.py` to ensure department names are being extracted correctly from Snipe-IT API.

### Step 5: Verify API Response
Check what the Snipe-IT API is actually returning for department information.

## Implementation Status
- [x] Verify database schema - Column exists but is null for all users
- [x] Apply migration if needed - Migration exists and column is present
- [x] Test sync process - Sync logic works but has pagination issue
- [x] Debug sync logic - Found and fixed pagination problem
- [x] Verify API response - API structure looks correct
- [x] Test frontend display - Frontend correctly shows "Unassigned" for null values
- [x] Fix pagination issue - Updated fetch_all_users() to use proper pagination

## Root Cause Identified
The `department_name` column exists in the database but is null for all users. This indicates:
1. The migration has been applied (column exists)
2. The sync process either hasn't run or isn't populating the department names correctly
3. The sync logic in `sync.py` looks correct for extracting `department.get("name")`

## Solution
The sync process needs to be run to populate the `department_name` field from the Snipe-IT API.

### Issue Found: Pagination Problem
After running the sync, it was discovered that only 500 users were synced out of 1441 total users in Snipe-IT. This is due to a pagination issue in the `fetch_all_users()` function.

**Root Cause:** The `fetch_all_users()` function in `backend/app/snipeit.py` only makes one API request with `limit: 1000`, but Snipe-IT may have server-side limits or the function isn't handling pagination properly.

**Solution:** Update the `fetch_all_users()` function to use proper pagination like the `fetch_all_hardware()` function does.

### Fix Applied
Updated `backend/app/snipeit.py` to implement proper pagination in the `fetch_all_users()` function:

```python
def fetch_all_users() -> list[dict]:
    """Synchronous version for backward compatibility."""
    url = f"{settings.snipeit_api_url}/users"
    all_users = []
    params = {"limit": 100, "offset": 0, "expand": "department"}
    
    while True:
        resp = requests.get(url, headers=HEADERS, params=params, verify=CA_BUNDLE, timeout=30)
        resp.raise_for_status()
        data = resp.json()["rows"]
        
        if not data:
            break
            
        all_users.extend(data)
        
        if len(data) < params["limit"]:
            break
            
        params["offset"] += params["limit"]
    
    return all_users
```

This change:
- Uses smaller batch sizes (100 instead of 1000) for better reliability
- Implements proper pagination with offset
- Continues fetching until all users are retrieved
- Maintains backward compatibility with existing sync code

## Notes
- The sync process uses `html.unescape()` on department names, suggesting they might be HTML-encoded
- The frontend correctly handles null values by showing "Unassigned"
- Need to ensure the sync process is running and populating data correctly 