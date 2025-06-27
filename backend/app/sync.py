# app/sync.py
from sqlmodel import Session
from .db import engine
from .models import Asset
from .snipeit import fetch_all_hardware, user_department_map

dept_lookup = user_department_map()

def flat_date(val: str | dict | None) -> str | None:
    if isinstance(val, dict):
        return val.get("date")
    return val


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
                status_type       = status_lbl.get("status_type"),
                department        = dept,
                category          = cat.get("name"),
                manufacturer      = mfr.get("name"),
                location          = loc.get("name"),
                company           = comp.get("name"),
                warranty  = hw.get("warranty_months"),
                warranty_expires = flat_date(hw.get("warranty_expires")),
                created_at        = crt.get("datetime")


                # …any other fields your Asset model has…
            )
            session.merge(obj)
        session.commit()
