# 502 Bad Gateway Troubleshooting Session

## Issue Description
- API endpoint `http://10.4.208.227/api/assets` returns 502 Bad Gateway
- Backend service has been restarted but issue persists
- Need to test the APScheduler sync implementation

## Environment
- Windows Server 2022 VM
- IIS for frontend hosting
- NSSM for backend service management
- Backend runs on FastAPI with uvicorn

## Investigation Steps
1. Check backend service status and logs
2. Verify backend process is running and listening on correct port
3. Check IIS configuration for API proxy
4. Review backend application logs for startup errors
5. Test backend direct access (bypassing IIS)

## Potential Causes
- Backend service failed to start properly
- Port conflicts or binding issues
- IIS reverse proxy configuration problems
- Python/dependency issues after recent deployment
- Database connection issues

## ROOT CAUSE IDENTIFIED ✅
**Missing Environment Variables**: The backend is failing to start because the `.env` file is missing or incomplete. Required variables:
- `database_url`
- `snipeit_api_url` 
- `snipeit_token`

Error from manual start:
```
pydantic_core._pydantic_core.ValidationError: 3 validation errors for Settings
database_url: Field required
snipeit_api_url: Field required  
snipeit_token: Field required
```

## Immediate Solution
Create the missing `.env` file on the server:

### 1. Create .env file manually on server
```powershell
# Navigate to backend directory
cd E:\asset-app\backend

# Create .env file with required variables
@"
database_url=postgresql://username:password@localhost:5432/assetdb
snipeit_api_url=https://your-snipeit-url/api/v1
snipeit_token=your-snipeit-api-token
requests_ca_bundle=E:\actions-runner\ca-bundle.pem
echo_sql=false
"@ | Out-File -FilePath .env -Encoding utf8NoBOM
```

### 2. Update GitHub Actions workflow ✅
The deployment workflow has been updated to create the .env file from your existing `MYSECRETS` GitHub secret. The workflow will now:

1. Use the content from `MYSECRETS` secret (containing database_url, snipeit_api_url, snipeit_token)
2. Add the `requests_ca_bundle` and `echo_sql` entries
3. Write the complete .env file during deployment

No additional GitHub secrets needed - it uses your existing `MYSECRETS` secret!

## Troubleshooting Commands (Run on Windows Server)

### 1. Check Service Status
```powershell
# Check NSSM service status
nssm status AssetBackend

# Check Windows service status
Get-Service AssetBackend
```

### 2. Check Service Logs
```powershell
# Check NSSM logs (if configured)
# Default location: C:\Windows\System32\LogFiles\NSSM\
Get-Content "C:\Windows\System32\LogFiles\NSSM\AssetBackend_*.log" -Tail 50

# Check Windows Event Logs
Get-EventLog -LogName Application -Source AssetBackend -Newest 10
```

### 3. Check Process and Port
```powershell
# Check if Python process is running
Get-Process python* -ErrorAction SilentlyContinue

# Check what's listening on port 8000 (default FastAPI port)
netstat -ano | findstr :8000
```

### 4. Test Backend Direct Access
```powershell
# Test if backend responds directly (bypass IIS)
curl http://localhost:8000/api/assets
# or
Invoke-WebRequest -Uri http://localhost:8000/api/assets
```

### 5. Manual Backend Start (for debugging)
```powershell
# Navigate to backend directory
cd E:\asset-app\backend

# Try starting manually to see error messages
E:\asset-app\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Check Dependencies
```powershell
# Verify APScheduler is installed
E:\asset-app\backend\.venv\Scripts\pip.exe list | findstr apscheduler
```

## Quick Fix Attempt
If the service is failing to start due to the scheduler, we can temporarily disable it:

### Temporary Solution: Disable Scheduler
Create a version of main.py without the scheduler to test if that's the issue.

## Resolution Steps
1. ✅ **Identified root cause**: Missing environment variables
2. 🔄 **Create .env file manually on server**
3. ✅ **Update GitHub Actions workflow to create .env file** (Updated to use MYSECRETS)
4. 🔄 **Test backend startup**
5. 🔄 **Restart service and test API**

## Files Modified
- `docs/session/502-gateway-troubleshooting.md` - Documentation
- `.github/workflows/deploy.yml` - ✅ Updated to create .env file using MYSECRETS 