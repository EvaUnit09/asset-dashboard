# Mac vs Lenovo Chart Fix

## Issue Description
The Mac vs Lenovo chart is showing too many assets as "Unassigned Department" because the asset sync process is not properly assigning departments to assets.

## Root Cause Analysis

### Problem 1: Incomplete User Department Data
- The `user_department_map()` function uses `fetch_all_users()` which was limited to 500 users
- With 1441 total users, many users' department information was missing from the lookup
- This caused assets assigned to those users to be marked as "Unassigned Department"

### Problem 2: Asset Department Assignment Logic
The asset sync logic in `sync_snipeit_assets()` has this department assignment:

```python
dept = (
    dept_lookup.get(asn["id"])
    if asn.get("type") == "user"
    else (asn.get("name") if asn.get("type") == "department" else None)
)
```

This relies on `dept_lookup` which was incomplete due to the pagination issue.

## Solution

### Step 1: Fix User Department Data
- ✅ Fixed pagination in `fetch_all_users()` to get all 1441 users
- ✅ Run sync to populate all user department names

### Step 2: Fix Asset Department Assignment
The asset sync should be updated to:
1. Use the complete user department data
2. Handle cases where department information is missing
3. Provide better fallback logic

### Step 3: Update Chart Logic
The chart should handle cases where:
- Assets have no department assigned
- Users have no department assigned
- Provide better categorization

## Implementation Plan

1. **Verify user sync** - Ensure all 1441 users have department data
2. **Update asset sync logic** - Improve department assignment ✅
3. **Test chart display** - Verify proper department grouping
4. **Add fallback logic** - Handle edge cases gracefully

## Fix Applied

### Updated Asset Sync Logic
Modified `backend/app/sync.py` to use fresh department lookup data:

```python
def sync_snipeit_assets():
    # Get fresh department lookup data
    dept_lookup = user_department_map()
    
    # ... rest of sync logic using fresh dept_lookup
```

**Changes made:**
- Removed global `dept_lookup` variable that was created at module import time
- Added `dept_lookup = user_department_map()` inside the sync function
- This ensures fresh department data is used for each sync run
- Fixed html.unescape type issue for department names

### Expected Impact
- Assets will now be properly assigned to departments based on complete user data
- Reduced "Unassigned Department" count in Mac vs Lenovo chart
- Better asset categorization by department

### Chart Improvements
Updated `frontend/src/components/MacLenovoChart.tsx` to handle edge cases better:

```typescript
// Better department handling
let department = asset.department;
if (!department || department.trim() === '') {
  department = 'Unassigned Department';
}

// Sort with "Unassigned Department" at the end
.sort((a, b) => {
  if (a.department === 'Unassigned Department') return 1;
  if (b.department === 'Unassigned Department') return -1;
  return b.total - a.total;
});
```

**Improvements:**
- Better handling of empty/null department values
- "Unassigned Department" appears at the end of the chart
- More robust department name validation

## Expected Result
- Mac vs Lenovo chart should show proper department distribution
- Reduced "Unassigned Department" count
- Better asset categorization by department 