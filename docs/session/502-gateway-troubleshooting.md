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

## ADDITIONAL ISSUES IDENTIFIED ✅

### 3. IIS Routing Configuration Issue
**Problem**: IIS error `0x80072efd` showing it's trying to serve API requests from static files instead of proxying to backend.
- `site/web.config` was missing `<proxy enabled="true" preserveHostHeader="false" />` 
- Using `localhost` instead of `127.0.0.1` in rewrite URL
- Frontend's correct `web.config` was not being deployed to site root

**Error**: `Physical Path E:\asset-app\site\dist\api\assets` - showing IIS treating API as static file

### 4. SSL Certificate Issue in Backend
**Problem**: Backend using `certifi.where()` instead of custom CA bundle from settings
- Snipe-IT API calls failing with SSL certificate verification errors
- `requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed`
- Code was ignoring `settings.requests_ca_bundle` configuration

**Root Cause**: `snipeit.py` was hardcoded to use `certifi.where()` instead of checking for custom CA bundle setting.

### 5. Certificate Path Mismatch Issue  
**Problem**: Backend looking for certificate at `E:\asset-app\backend\certs\ZscalerRootCA.pem` but file doesn't exist
- `requests_ca_bundle` setting in `MYSECRETS` points to non-existent path
- GitHub Actions copies certificate to `E:\actions-runner\ca-bundle.pem` 
- Backend expects it at `E:\asset-app\backend\certs\ZscalerRootCA.pem`

**Error**: `OSError: Could not find a suitable TLS CA certificate bundle, invalid path: E:\asset-app\backend\certs\ZscalerRootCA.pem`

**Resolution**: Certificate was copied to `backend\certs\` directory but with `.crt` extension instead of `.pem`. Manual rename from `ZscalerRootCA.crt` to `ZscalerRootCA.pem` resolved the issue and backend started successfully.

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
3. ✅ **Identified IIS routing issue**: Missing proxy configuration and incorrect URL
4. ✅ **Identified SSL certificate issue**: Backend not using custom CA bundle
5. ✅ **Identified certificate path mismatch**: Certificate not found at expected path
6. ✅ **Fixed GitHub Actions workflow**: Creates .env file without BOM, deploys correct web.config, copies certificate to expected location
7. ✅ **Fixed backend SSL configuration**: Uses custom CA bundle from settings
8. ✅ **Fixed IIS configuration**: Added proxy settings and correct backend URL
9. ✅ **Deploy to apply all fixes** (certificate copied to backend/certs/ directory)
10. ✅ **Manual certificate extension fix** (renamed .crt to .pem)
11. ✅ **Backend startup successful** (backend now running properly)
12. 🔄 **Test API endpoints and complete functionality**

## Manual Fix for Current Server (if needed)
If you need to fix the current issues on the server immediately:

### Fix 1: .env file BOM issue
```powershell
# Navigate to backend directory
cd E:\asset-app\backend

# Backup current .env file
Copy-Item .env .env.bak

# Read current content and recreate without BOM
$content = Get-Content .env -Raw
$utf8NoBom = New-Object System.Text.UTF8Encoding $False
[System.IO.File]::WriteAllText("E:\asset-app\backend\.env", $content, $utf8NoBom)
```

### Fix 2: IIS web.config proxy settings
```powershell
# Navigate to site directory
cd E:\asset-app\site

# Backup current web.config
Copy-Item web.config web.config.bak

# Update web.config with proxy settings
$webConfigContent = @"
<configuration>
  <system.webServer>
    <proxy enabled="true" preserveHostHeader="false" />
    <rewrite>
      <rules>
        <rule name="API to Backend" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite"
                  url="http://127.0.0.1:8000/{R:1}"
                  logRewrittenUrl="true" />
          <serverVariables>
            <set name="HTTP_X_FORWARDED_PROTO" value="http" />
          </serverVariables>
        </rule>

        <rule name="SPA fallback" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
"@

[System.IO.File]::WriteAllText("E:\asset-app\site\web.config", $webConfigContent)
```

### Apply all fixes
```powershell
# Restart the backend service
nssm restart AssetBackend

# Restart IIS (or just the site)
iisreset /noforce
```

### Fix 3: Certificate path issue
```powershell
# Create the certs directory and copy the certificate
New-Item -ItemType Directory -Force -Path 'E:\asset-app\backend\certs'
Copy-Item 'E:\actions-runner\ZscalerRootCA.crt' 'E:\asset-app\backend\certs\ZscalerRootCA.pem' -Force

# If the file was copied as .crt instead of .pem, rename it:
if (Test-Path 'E:\asset-app\backend\certs\ZscalerRootCA.crt') {
    Move-Item 'E:\asset-app\backend\certs\ZscalerRootCA.crt' 'E:\asset-app\backend\certs\ZscalerRootCA.pem' -Force
}

# Alternatively, update your MYSECRETS to use the correct path:
# requests_ca_bundle=E:\actions-runner\ca-bundle.pem
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
- `docs/session/502-gateway-troubleshooting.md` - ✅ Updated with complete issue analysis and resolution
- `.github/workflows/deploy.yml` - ✅ Updated to create .env file without BOM, deploy correct web.config, and copy certificate to expected location
- `backend/app/snipeit.py` - ✅ Updated to use custom CA bundle from settings instead of hardcoded certifi
- `site/web.config` - ✅ Updated to include proxy settings and use 127.0.0.1 instead of localhost 