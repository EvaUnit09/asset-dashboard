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
- Application deployed to E:\ drive
- Logs location: E:\Asset-app\logs

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

## SECONDARY ISSUE IDENTIFIED ✅
**BOM (Byte Order Mark) Issue**: The `.env` file was being created with a BOM character, causing pydantic to see `\ufeffdatabase_url` instead of `database_url`. This leads to validation errors:
- `database_url` Field required (because it's looking for `database_url` but finding `\ufeffdatabase_url`)
- `\ufeffdatabase_url` Extra inputs are not permitted (because this field with BOM doesn't match expected field name)

Error message:
```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
database_url
  Field required [type=missing, input_value={'snipeit_api_url': 'http...127.0.0.1:5433/assetdb'}, input_type=dict]
\ufeffdatabase_url
  Extra inputs are not permitted [type=extra_forbidden, input_value='postgresql+psycopg://adm...@127.0.0.1:5433/assetdb', input_type=str]
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

# Verify the .env file was created
Get-Content .env
```

### 2. Update GitHub Actions workflow ✅
The deployment workflow has been updated to create the .env file from your existing `MYSECRETS` GitHub secret. The workflow will now:

1. Use the content from `MYSECRETS` secret (containing database_url, snipeit_api_url, snipeit_token)
2. Add the `requests_ca_bundle` and `echo_sql` entries
3. Write the complete .env file during deployment **without BOM** to avoid pydantic field name issues

Key fix: Using UTF8 encoding without BOM (`$utf8NoBom = New-Object System.Text.UTF8Encoding $False`) to prevent the `\ufeffdatabase_url` field name corruption.

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
# Check application logs
Get-Content "E:\Asset-app\logs\*.log" -Tail 50

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

### 7. Check Log Files
```powershell
# Check application logs for errors
Get-Content "E:\Asset-app\logs\*.log" -Tail 20 | Where-Object { $_ -match "error|exception|failed" }

# Check all recent log entries
Get-ChildItem "E:\Asset-app\logs\*.log" | Get-Content -Tail 50
```

## Quick Fix Attempt
If the service is failing to start due to the scheduler, we can temporarily disable it:

### Temporary Solution: Disable Scheduler
Create a version of main.py without the scheduler to test if that's the issue.

## Resolution Steps
1. ✅ **Identified root cause**: Missing environment variables
2. ✅ **Identified BOM issue**: .env file created with BOM causing field name corruption
3. ✅ **Update GitHub Actions workflow to create .env file without BOM** (Fixed UTF8 encoding)
4. 🔄 **Deploy to create new .env file without BOM** (or fix manually)
5. 🔄 **Test backend startup**
6. 🔄 **Restart service and test API**

## Manual Fix for Current Server (if needed)
If you need to fix the current .env file on the server immediately:

```powershell
# Navigate to backend directory
cd E:\asset-app\backend

# Backup current .env file
Copy-Item .env .env.bak

# Read current content and recreate without BOM
$content = Get-Content .env -Raw
$utf8NoBom = New-Object System.Text.UTF8Encoding $False
[System.IO.File]::WriteAllText("E:\asset-app\backend\.env", $content, $utf8NoBom)

# Restart the service
nssm restart AssetBackend
```

## Application Structure
```
E:\
├── asset-app\
│   ├── backend\           # FastAPI backend application
│   │   ├── .venv\        # Python virtual environment
│   │   ├── .env          # Environment variables (created by deployment)
│   │   └── app\          # Application code
│   ├── logs\             # Application log files
│   └── site\             # Frontend static files (IIS)
└── actions-runner\       # GitHub Actions runner
    └── ca-bundle.pem     # Certificate bundle
```

## Files Modified
- `docs/session/502-gateway-troubleshooting.md` - ✅ Updated with BOM issue analysis and resolution
- `.github/workflows/deploy.yml` - ✅ Updated to create .env file using MYSECRETS without BOM 