# backend/app/routers/sync.py
from fastapi import APIRouter, BackgroundTasks
from ..sync import sync_snipeit_assets, sync_snipeit_users, sync_all
from ..scheduler import sync_scheduler

router = APIRouter(tags=["sync"])

@router.post("/sync")
def trigger_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_snipeit_assets)
    return {"status": "scheduled"}

@router.post("/sync/assets")
def trigger_assets_sync(background_tasks: BackgroundTasks):
    """Sync only assets from Snipe-IT."""
    background_tasks.add_task(sync_snipeit_assets)
    return {"status": "assets sync scheduled"}

@router.post("/sync/users")
def trigger_users_sync(background_tasks: BackgroundTasks):
    """Sync only users from Snipe-IT."""
    background_tasks.add_task(sync_snipeit_users)
    return {"status": "users sync scheduled"}

@router.post("/sync/all")
def trigger_full_sync(background_tasks: BackgroundTasks):
    """Sync both assets and users from Snipe-IT."""
    background_tasks.add_task(sync_all)
    return {"status": "full sync scheduled (assets + users)"}

@router.post("/sync/now")
def trigger_sync_now():
    """Manually trigger a sync job immediately."""
    sync_scheduler.trigger_sync_now()
    return {"status": "manual sync triggered"}

@router.get("/sync/schedule")
def get_sync_schedule():
    """Get the next scheduled sync times."""
    next_runs = sync_scheduler.get_next_run_times()
    return {
        "next_scheduled_runs": next_runs,
        "scheduler_running": sync_scheduler.scheduler.running
    }

@router.post("/sync/scheduler/start")
def start_scheduler():
    """Start the sync scheduler."""
    sync_scheduler.start()
    return {"status": "scheduler started"}

@router.post("/sync/scheduler/stop")
def stop_scheduler():
    """Stop the sync scheduler."""
    sync_scheduler.stop()
    return {"status": "scheduler stopped"}
