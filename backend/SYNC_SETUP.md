# Asset Sync Scheduling Setup

This document describes the automated syncing of assets from Snipe-IT to your PostgreSQL database every 4 hours from 8 AM to 8 PM using **APScheduler** integrated into your FastAPI application.

## Sync Times

The sync will run automatically at:
- 8:00 AM
- 12:00 PM (noon)  
- 4:00 PM
- 8:00 PM

## Implementation: APScheduler (In-Application)

Your asset management system uses **APScheduler** for scheduling, which integrates directly into your FastAPI application.

### **Advantages:**
- ✅ Integrated with FastAPI application - no external dependencies
- ✅ Starts automatically when your service starts
- ✅ Programmatic control via API endpoints
- ✅ Real-time monitoring through web interface
- ✅ No complex file management or permissions issues
- ✅ Uses your existing `.env` configuration

### **How It Works:**
- The scheduler starts automatically when your FastAPI app starts
- It runs in the background as part of your existing `AssetBackend` service
- Sync jobs are configured using cron triggers for precise timing
- All logging goes through your existing application logs

## API Endpoints

Your application provides API endpoints to control and monitor the sync:

### **Manual Control:**
- `POST /sync/now` - Trigger sync immediately
- `POST /sync` - Trigger sync as background task

### **Scheduler Management:**
- `GET /sync/schedule` - View next scheduled runs and scheduler status
- `POST /sync/scheduler/start` - Start the scheduler
- `POST /sync/scheduler/stop` - Stop the scheduler

### **Example Usage:**
```bash
# Check scheduler status
curl http://localhost:8000/sync/schedule

# Trigger manual sync
curl -X POST http://localhost:8000/sync/now

# View next scheduled runs
curl http://localhost:8000/sync/schedule
```

## Configuration

### Environment Variables

Your existing `.env` file is used automatically:
```
DATABASE_URL=postgresql://username:password@localhost:5432/assetdb
SNIPEIT_API_URL=https://your-snipeit-instance.com/api/v1
SNIPEIT_TOKEN=your-api-token
REQUESTS_CA_BUNDLE=E:\actions-runner\ZscalerRootCA.crt
```

### Logging

The scheduler provides comprehensive logging through your FastAPI application:
- Sync start/end times
- Success/failure status  
- Error details if sync fails
- Performance metrics (duration)
- Job execution events

## Deployment

### **Automatic Deployment**
Your GitHub Actions workflow handles everything automatically:
1. ✅ Deploys the updated code
2. ✅ Installs APScheduler dependency
3. ✅ Restarts the AssetBackend service
4. ✅ Scheduler starts automatically with the service

### **No Manual Steps Required**
Unlike traditional cron jobs or Windows Task Scheduler, there's no manual setup needed:
- No task creation
- No file permissions to manage
- No separate environment configuration
- No certificate copying

## Monitoring

### **Real-time Status**
```bash
# Check if scheduler is running and view next sync times
curl http://localhost:8000/sync/schedule
```

Example response:
```json
{
  "next_scheduled_runs": {
    "Asset Sync 08:00": "2025-01-31T08:00:00",
    "Asset Sync 12:00": "2025-01-31T12:00:00", 
    "Asset Sync 16:00": "2025-01-31T16:00:00",
    "Asset Sync 20:00": "2025-01-31T20:00:00"
  },
  "scheduler_running": true
}
```

### **Application Logs**
Monitor sync activity through your existing application logs:
- NSSM service logs
- Application stdout/stderr
- Windows Event Viewer (for service events)

## Troubleshooting

### **Common Issues**

1. **Scheduler not running**: Check if AssetBackend service is running
2. **Sync failures**: Check application logs for database/API connectivity
3. **Missed schedules**: Scheduler automatically handles missed runs with grace period

### **Quick Diagnostics**

```bash
# Check service status
Get-Service -Name "AssetBackend"

# Check scheduler status via API
curl http://localhost:8000/sync/schedule

# Trigger manual sync to test
curl -X POST http://localhost:8000/sync/now
```

### **Restart Scheduler**
If needed, restart the scheduler without restarting the entire service:

```bash
# Stop scheduler
curl -X POST http://localhost:8000/sync/scheduler/stop

# Start scheduler  
curl -X POST http://localhost:8000/sync/scheduler/start
```

## Benefits Over External Schedulers

### **Compared to Windows Task Scheduler:**
- ✅ No complex setup or permissions
- ✅ Better integration with application lifecycle
- ✅ Real-time control and monitoring
- ✅ Automatic startup/shutdown with service

### **Compared to Cron Jobs:**
- ✅ Platform independent
- ✅ Integrated logging and error handling
- ✅ Dynamic control without editing system files
- ✅ Better suited for Windows environments

## Security

- Uses existing application authentication and environment variables
- No separate credential management needed
- Runs within application security context
- All API endpoints can be secured with your existing auth system

---

**Summary:** Your sync is fully automated and integrated into your FastAPI application. No manual setup required - just deploy and it works! 