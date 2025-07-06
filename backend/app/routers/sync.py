# backend/app/routers/sync.py
from fastapi import APIRouter, BackgroundTasks
from ..sync import sync_snipeit_assets
from ..scheduler import sync_scheduler

router = APIRouter(tags=["sync"])

@router.post("/sync")
def trigger_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_snipeit_assets)
    return {"status": "scheduled"}

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
