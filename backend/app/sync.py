# app/sync.py
from sqlmodel import Session
from .db import engine
from .models import Asset, User
from .snipeit import fetch_all_hardware, fetch_all_users, user_department_map

dept_lookup = user_department_map()

def flat_date(val: str | dict | None) -> str | None:
    if isinstance(val, dict):
        return val.get("date")
    return val


def sync_snipeit_users():
    """Sync users from Snipe-IT API to local database."""
    with Session(engine) as session:
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
                department_name=department.get("name"),
                location_id=location.get("id") if location else None,
                assets_count=user_data.get("assets_count", 0),
                license_count=user_data.get("licenses_count", 0)
            )
            session.merge(user_obj)
        session.commit()


def sync_snipeit_assets():
    with Session(engine) as session:
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
            dept       = (
                dept_lookup.get(asn["id"])
                if asn.get("type") == "user"
                else (asn.get("name") if asn.get("type") == "department" else None)
            )

            obj = Asset(
                id                = hw["id"],
                asset_name        = hw.get("name") or str(hw["asset_tag"]),
                asset_tag         = hw["asset_tag"],
                serial            = hw["serial"],
                model             = mdl.get("name"),
                model_no          = hw.get("model_number"),
                status            = status_lbl.get("name"),
                department        = dept,
                category          = cat.get("name"),
                manufacturer      = mfr.get("name"),
                location          = loc.get("name"),
                company           = comp.get("name"),
                warranty          = hw.get("warranty_months"),
                warranty_expires  = flat_date(hw.get("warranty_expires")),
                created_at        = crt.get("datetime")
            )
            session.merge(obj)
        session.commit()


def sync_all():
    """Sync both assets and users from Snipe-IT."""
    print("Starting full sync: assets and users...")
    sync_snipeit_assets()
    print("✅ Assets sync completed")
    sync_snipeit_users()
    print("✅ Users sync completed")
    print("🚀 Full sync completed successfully!")
