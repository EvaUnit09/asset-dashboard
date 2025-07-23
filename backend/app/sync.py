# app/sync.py
from sqlmodel import Session
from .db import engine
from .models import Asset, User
from .snipeit import fetch_all_hardware, fetch_all_users, user_department_map
from .performance_monitor import monitor_performance, sync_circuit_breaker, is_system_under_load
import time
import html

def flat_date(val: str | dict | None) -> str | None:
    if isinstance(val, dict):
        return val.get("date")
    return val


def sync_snipeit_users():
    """Sync users from Snipe-IT API to local database with batch processing."""
    BATCH_SIZE = 50
    batch_count = 0
    processed_count = 0
    
    with Session(engine) as session:
        user_batch = []
        
        for user_data in fetch_all_users():
            # Extract user information from Snipe-IT API response
            department = user_data.get("department") or {}
            location = user_data.get("location") or {}
            
            # Create User object
            user_obj = User(
                id=user_data["id"],
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                username=user_data.get("username"),
                email=user_data.get("email"),
                county=user_data.get("county"),
                department_id=department.get("id"),
                department_name=html.unescape(str(department.get("name"))) if department.get("name") else None,
                location_id=location.get("id") if location else None,
                assets_count=user_data.get("assets_count", 0),
                license_count=user_data.get("licenses_count", 0)
            )
            user_batch.append(user_obj)
            processed_count += 1
            
            # Process in batches to reduce memory usage
            if len(user_batch) >= BATCH_SIZE:
                for user in user_batch:
                    session.merge(user)
                session.commit()
                batch_count += 1
                print(f"  Processed batch {batch_count} ({len(user_batch)} users)")
                user_batch.clear()
        
        # Process remaining users
        if user_batch:
            for user in user_batch:
                session.merge(user)
            session.commit()
            batch_count += 1
            print(f"  Processed final batch {batch_count} ({len(user_batch)} users)")
        
        print(f"  Total users processed: {processed_count} in {batch_count} batches")


def sync_snipeit_assets():
    """Sync assets from Snipe-IT API to local database with batch processing."""
    BATCH_SIZE = 50
    batch_count = 0
    processed_count = 0
    
    # Get fresh department lookup data
    dept_lookup = user_department_map()
    
    # Debug: Show what's in the department lookup
    print(f"\n=== DEPARTMENT LOOKUP DEBUG ===")
    print(f"Total users in dept_lookup: {len(dept_lookup)}")
    users_with_depts = {k: v for k, v in dept_lookup.items() if v is not None}
    print(f"Users with departments: {len(users_with_depts)}")
    print("Sample entries:")
    for i, (user_id, dept) in enumerate(list(users_with_depts.items())[:5]):
        print(f"  User ID {user_id}: {dept}")
    print("=== END DEPT LOOKUP DEBUG ===\n")
    
    with Session(engine) as session:
        asset_batch = []
        
        for hw in fetch_all_hardware():
            # safe getters
            mdl        = hw.get("model") or {}
            status_lbl = hw.get("status_label") or {}
            dept       = hw.get("assigned_to_department") or {}
            cat        = hw.get("category") or {}
            mfr        = hw.get("manufacturer") or {}
            loc        = hw.get("location") or {}
            comp       = hw.get("company") or {}
            asn        = hw.get("assigned_to") or {}
            crt        = hw.get("created_at") or {}
            # Extract assigned user name and department
            assigned_user_name = None
            if asn.get("type") == "user":
                # Extract user name from assigned_to object
                first_name = asn.get("first_name", "")
                last_name = asn.get("last_name", "")
                assigned_user_name = f"{first_name} {last_name}".strip() if first_name or last_name else asn.get("name")
            
            # Determine department - use fresh lookup data
            dept = (
                dept_lookup.get(asn["id"])
                if asn.get("type") == "user"
                else (asn.get("name") if asn.get("type") == "department" else None)
            )

            # Debug asset assignment and department mapping
            if hw.get("manufacturer", "").lower() == "lenovo":
                print(f"\n--- DEBUG LENOVO ASSET: {hw.get('asset_tag')} ---")
                print(f"Asset name: {hw.get('name')}")
                print(f"Assigned_to object: {asn}")
                print(f"Assigned_to type: {asn.get('type')}")
                print(f"Assigned_to ID: {asn.get('id')}")
                print(f"Assigned user name: {assigned_user_name}")
                print(f"Department from lookup: {dept}")
                print(f"Available in dept_lookup: {asn.get('id') in dept_lookup if asn.get('id') else 'No ID'}")
                if asn.get("id") and asn.get("id") in dept_lookup:
                    print(f"Dept lookup value: {dept_lookup.get(asn['id'])}")
                print("--- END DEBUG ---\n")

            obj = Asset(
                id                = hw["id"],
                asset_name        = hw.get("name") or str(hw["asset_tag"]),
                asset_tag         = hw["asset_tag"],
                serial            = hw["serial"],
                model             = mdl.get("name"),
                model_no          = hw.get("model_number"),
                status            = status_lbl.get("name"),
                department        = dept,
                assigned_user_name = assigned_user_name,
                category          = cat.get("name"),
                manufacturer      = mfr.get("name"),
                location          = loc.get("name"),
                company           = comp.get("name"),
                warranty          = hw.get("warranty_months"),
                warranty_expires  = flat_date(hw.get("warranty_expires")),
                created_at        = crt.get("datetime")
            )
            asset_batch.append(obj)
            processed_count += 1
            
            # Process in batches to reduce memory usage
            if len(asset_batch) >= BATCH_SIZE:
                for asset in asset_batch:
                    session.merge(asset)
                session.commit()
                batch_count += 1
                print(f"  Processed batch {batch_count} ({len(asset_batch)} assets)")
                asset_batch.clear()
        
        # Process remaining assets
        if asset_batch:
            for asset in asset_batch:
                session.merge(asset)
            session.commit()
            batch_count += 1
            print(f"  Processed final batch {batch_count} ({len(asset_batch)} assets)")
        
        print(f"  Total assets processed: {processed_count} in {batch_count} batches")


@sync_circuit_breaker
@monitor_performance
def sync_all():
    """Sync both assets and users from Snipe-IT with performance monitoring."""
    # Check system load before starting intensive operation
    if is_system_under_load():
        print("System under high load, delaying sync by 5 minutes...")
        time.sleep(300)  # Wait 5 minutes
        
        # Check again after delay
        if is_system_under_load():
            print("System still under load, skipping sync this time")
            return
    
    print("Starting full sync: assets and users...")
    sync_snipeit_assets()
    print("Assets sync completed")
    sync_snipeit_users()
    print("Users sync completed")
    print("Full sync completed successfully!")
