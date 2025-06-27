# backend/app/routers/sync.py
from fastapi import APIRouter, BackgroundTasks
from ..sync import sync_snipeit_assets

router = APIRouter(tags=["sync"])

@router.post("/sync")
def trigger_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_snipeit_assets)
    return {"status": "scheduled"}
