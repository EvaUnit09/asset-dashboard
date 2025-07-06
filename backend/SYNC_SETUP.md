# Asset Sync Scheduling Setup

This document describes how to set up automated syncing of assets from Snipe-IT to your PostgreSQL database every 4 hours from 8 AM to 8 PM.

## Sync Times

The sync will run at:
- 8:00 AM
- 12:00 PM (noon)
- 4:00 PM
- 8:00 PM

## Implementation Options

### Option 1: Windows Task Scheduler (Recommended)

**Best for:** Production environments where reliability is critical.

**Advantages:**
- Native Windows solution, very reliable
- Excellent logging via Windows Event Viewer
- No impact on FastAPI application performance
- Easy to manage and monitor

**Setup Steps:**

1. **Install dependencies** (if using APScheduler option later):
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the setup script as Administrator**:
   ```powershell
   cd backend
   .\setup_sync_schedule.ps1
   ```

3. **Or set up manually via Task Scheduler GUI**:
   - Open Task Scheduler (`taskschd.msc`)
   - Create Basic Task
   - Set triggers for 8:00 AM, 12:00 PM, 4:00 PM, and 8:00 PM
   - Set action to run `python.exe "C:\path\to\backend\scheduled_sync.py"`

**Monitoring:**
- Logs are saved to `backend/logs/sync_YYYYMMDD.log`
- Windows Event Viewer for task execution status
- PowerShell commands:
  ```powershell
  Get-ScheduledTask -TaskName "AssetSync"
  Get-ScheduledTaskInfo -TaskName "AssetSync"
  ```

### Option 2: APScheduler (In-Application)

**Best for:** Development environments or when you want programmatic control.

**Advantages:**
- Integrated with FastAPI application
- Programmatic control via API endpoints
- Real-time monitoring through web interface

**Setup Steps:**

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **The scheduler starts automatically with your FastAPI app**

3. **API endpoints available**:
   - `POST /sync/now` - Trigger sync immediately
   - `GET /sync/schedule` - View next scheduled runs
   - `POST /sync/scheduler/start` - Start scheduler
   - `POST /sync/scheduler/stop` - Stop scheduler

**Monitoring:**
- Check scheduler status: `GET /sync/schedule`
- Application logs will contain sync information
- Monitor via your existing application monitoring

## Configuration

### Environment Variables

Make sure these are set in your `.env` file:
```
DATABASE_URL=postgresql://username:password@localhost:5432/assetdb
SNIPEIT_API_URL=https://your-snipeit-instance.com/api/v1
SNIPEIT_TOKEN=your-api-token
```

### Logging

Both options provide comprehensive logging:
- Sync start/end times
- Success/failure status
- Error details if sync fails
- Performance metrics (duration)

## Manual Sync

You can trigger a sync manually using any of these methods:

1. **Command line**:
   ```bash
   cd backend
   python scheduled_sync.py
   ```

2. **API endpoint** (if using APScheduler):
   ```bash
   curl -X POST http://localhost:8000/sync/now
   ```

3. **Windows Task Scheduler**:
   ```powershell
   Start-ScheduledTask -TaskName "AssetSync"
   ```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Database connection**: Check `DATABASE_URL` environment variable
3. **API errors**: Verify `SNIPEIT_API_URL` and `SNIPEIT_TOKEN`
4. **Permissions**: Windows Task Scheduler may need elevated permissions

### Log Analysis

Check the logs for:
- Connection errors to Snipe-IT API
- Database connection issues
- Sync duration (should be reasonable)
- Number of assets processed

### Performance Considerations

- Sync duration depends on number of assets
- Consider rate limiting if API responses are slow
- Monitor database performance during sync operations

## Production Recommendations

For production environments:

1. **Use Windows Task Scheduler** (Option 1)
2. **Set up monitoring** alerts for failed syncs
3. **Regular log rotation** to prevent disk space issues
4. **Test sync process** before deploying to production
5. **Have rollback plan** in case of sync issues

## Security Considerations

- Store API tokens securely (use environment variables)
- Run scheduled tasks with minimum required permissions
- Monitor for suspicious sync activity
- Regular security updates for all dependencies 