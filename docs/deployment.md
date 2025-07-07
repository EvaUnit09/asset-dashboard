# Deployment Documentation

## Overview

The Asset Management System is deployed on Windows Server 2022 using IIS for frontend hosting, NSSM for backend service management, and GitHub Actions for CI/CD automation. The deployment includes a PostgreSQL database, FastAPI backend, and React frontend.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IIS           │    │   Frontend      │    │   Backend       │
│   (Web Server)  │◄──►│   (React +      │◄──►│   (FastAPI +    │
│   + Reverse     │    │   Vite)         │    │   SQLAlchemy)   │
│   Proxy)        │    │                 │    │   (NSSM         │
└─────────────────┘    └─────────────────┘    │   Service)      │
         │                                              │
         │                                              │
         └──────────────────────────────────────────────┘
                                    │
                           ┌─────────────────┐
                           │   PostgreSQL    │
                           │   Database      │
                           └─────────────────┘
```

## Prerequisites

### System Requirements

- **Windows Server 2022** - Production environment
- **IIS 10** - Web server with URL Rewrite module
- **NSSM** - Non-Sucking Service Manager for Windows services
- **PostgreSQL 16** - Database server
- **4GB RAM** minimum (8GB recommended)
- **10GB** available disk space
- **GitHub Actions** - CI/CD pipeline

### Network Requirements

- **Port 80** (HTTP) - IIS entry point
- **Port 443** (HTTPS) - IIS SSL entry point
- **Port 8000** (Backend API) - Internal communication
- **Port 5433** (PostgreSQL) - Database access

## Environment Configuration

### Required Environment Variables

Create environment variables on Windows Server:

```powershell
# Database Configuration
[Environment]::SetEnvironmentVariable("POSTGRES_PASSWORD", "your_secure_password_here", "Machine")
[Environment]::SetEnvironmentVariable("POSTGRES_DB", "assetdb", "Machine")
[Environment]::SetEnvironmentVariable("POSTGRES_USER", "admin", "Machine")

# Application Configuration
[Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql://admin:password@localhost:5432/assetdb", "Machine")
[Environment]::SetEnvironmentVariable("API_BASE_URL", "http://localhost:8000", "Machine")

# Snipe-IT Integration
[Environment]::SetEnvironmentVariable("SNIPEIT_API_URL", "https://your-snipeit-instance.com/api/v1", "Machine")
[Environment]::SetEnvironmentVariable("SNIPEIT_TOKEN", "your_snipeit_api_token", "Machine")
```

### Environment Variable Descriptions

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL database password | Yes | - |
| `POSTGRES_DB` | Database name | No | `assetdb` |
| `POSTGRES_USER` | Database username | No | `admin` |
| `DOMAIN` | Public domain for the application | Yes | - |
| `SNIPEIT_API_URL` | Snipe-IT API endpoint | Yes | - |
| `SNIPEIT_TOKEN` | Snipe-IT API authentication token | Yes | - |
| `SSL_EMAIL` | Email for Let's Encrypt SSL certificates | No | - |

## Windows Server Configuration

### Services Overview

The deployment consists of several Windows services and components:

1. **PostgreSQL Database** - Database server
2. **Backend Service** (NSSM-managed) - FastAPI application
3. **IIS Web Server** - Frontend hosting and reverse proxy
4. **GitHub Actions** - CI/CD automation

### Network Configuration

```powershell
# Windows Firewall Rules
New-NetFirewallRule -DisplayName "Asset Management Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "PostgreSQL Database" -Direction Inbound -Protocol TCP -LocalPort 5433 -Action Allow
New-NetFirewallRule -DisplayName "IIS Web Server" -Direction Inbound -Protocol TCP -LocalPort 80,443 -Action Allow
```

### PostgreSQL Database Setup

```powershell
# Install PostgreSQL (if not already installed)
# Download from https://www.postgresql.org/download/windows/

# Create database and user
psql -U postgres -c "CREATE DATABASE assetdb;"
psql -U postgres -c "CREATE USER admin WITH PASSWORD 'your_secure_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE assetdb TO admin;"

# Configure PostgreSQL service
# Edit postgresql.conf for performance tuning
# Edit pg_hba.conf for authentication
```

### Backend Service (NSSM)

```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from https://nssm.cc/download

# Create backend service
nssm install AssetManagementBackend "C:\Python311\python.exe"
nssm set AssetManagementBackend AppDirectory "C:\inetpub\wwwroot\asset-management\backend"
nssm set AssetManagementBackend AppParameters "C:\inetpub\wwwroot\asset-management\backend\app\main.py"
nssm set AssetManagementBackend AppEnvironmentExtra "DATABASE_URL=postgresql://admin:password@localhost:5432/assetdb"
nssm set AssetManagementBackend AppEnvironmentExtra "SNIPEIT_API_URL=https://your-snipeit-instance.com/api/v1"
nssm set AssetManagementBackend AppEnvironmentExtra "SNIPEIT_TOKEN=your_token"

# Configure service
nssm set AssetManagementBackend Description "Asset Management Backend API"
nssm set AssetManagementBackend Start SERVICE_AUTO_START
nssm set AssetManagementBackend AppStdout "C:\logs\asset-backend.log"
nssm set AssetManagementBackend AppStderr "C:\logs\asset-backend-error.log"

# Start service
Start-Service AssetManagementBackend
```

### IIS Frontend Setup

```powershell
# Install IIS and required features
Install-WindowsFeature -Name Web-Server -IncludeManagementTools
Install-WindowsFeature -Name Web-Asp-Net45
Install-WindowsFeature -Name Web-WHC

# Install URL Rewrite module
# Download from https://www.iis.net/downloads/microsoft/url-rewrite

# Create application pool
Import-Module WebAdministration
New-WebAppPool -Name "AssetManagement"

# Create website
New-Website -Name "AssetManagement" -Port 80 -PhysicalPath "C:\inetpub\wwwroot\asset-management\frontend\dist" -ApplicationPool "AssetManagement"

# Configure URL Rewrite for API proxy
# Add web.config with rewrite rules
```

### IIS URL Rewrite Configuration

```xml
<!-- web.config for API proxy -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="API Proxy" stopProcessing="true">
                    <match url="^api/(.*)" />
                    <action type="Rewrite" url="http://localhost:8000/api/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

## Dockerfile Configurations

### Backend Dockerfile

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine as production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## GitHub Actions CI/CD

### Workflow Configuration

```yaml
# .github/workflows/deploy.yml
name: Deploy to asset server

on:
  push:
    branches: [main]

jobs:
  build-deploy:
    runs-on: [self-hosted, windows, asset]
    defaults:
      run:
        shell: powershell

    steps:
    # 1 Make Git trust the workspace -------------------------------------------------
    - name: Trust workspace for Git
      shell: cmd
      run: git config --system --add safe.directory "E:/actions-runner/_work/asset-dashboard/asset-dashboard"

    # 2 Check out code ---------------------------------------------------------------
    - uses: actions/checkout@v4
      with:
        clean: true          # or path: src  (see fix ➋)

    # 3 Copy Zscaler CA so Node / pip can use it ------------------------------------
    - name: Add corporate CA bundle
      shell: powershell
      run: |
        Copy-Item 'E:\actions-runner\ZscalerRootCA.crt' 'E:\actions-runner\ca-bundle.pem' -Force
        

    # ---------- Front-end ----------
    - name: Set up Node
      uses: actions/setup-node@v4
      env:
        NODE_EXTRA_CA_CERTS: E:\actions-runner\ca-bundle.pem
        REQUESTS_CA_BUNDLE: E:\actions-runner\ca-bundle.pem
        PIP_CERT: E:\actions-runner\ca-bundle.pem
      with:
        # use an available version (20 LTS today) —
        # change to 24.x once setup-node supports it
        node-version: '20'

    - name: Install dependencies & build
      working-directory: frontend
      env:
        NODE_EXTRA_CA_CERTS: E:\actions-runner\ca-bundle.pem
        REQUESTS_CA_BUNDLE: E:\actions-runner\ca-bundle.pem
        PIP_CERT: E:\actions-runner\ca-bundle.pem
      run: |
        npm ci
        npm run build

    - name: Deploy static files to IIS site
      run: |
        robocopy frontend\dist E:\asset-app\site\dist /MIR
        if ($LASTEXITCODE -le 7) { exit 0 }  # 0-7 = success/warning
        exit $LASTEXITCODE                    # 8+ = fail the job

    # ---------- Back-end ----------
    - name: Set up Python
      uses: actions/setup-python@v5
      env:
        NODE_EXTRA_CA_CERTS: E:\actions-runner\ca-bundle.pem
        REQUESTS_CA_BUNDLE: E:\actions-runner\ca-bundle.pem
        PIP_CERT: E:\actions-runner\ca-bundle.pem
      with:
        python-version: '3.12'

    - name: Install backend requirements (venv)
      working-directory: backend
      run: |
        E:\asset-app\backend\.venv\Scripts\python.exe -m pip install --upgrade pip
        E:\asset-app\backend\.venv\Scripts\pip.exe install -r requirements.txt

    # ---------- Restart service ----------
    - name: Restart AssetBackend service
      run: |
        nssm restart AssetBackend
      continue-on-error: true
```

## Deployment Steps

### 1. Initial Setup

```powershell
# Clone the repository
git clone <repository-url>
cd Asset-Management

# Set up environment variables
[Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql://admin:password@localhost:5432/assetdb", "Machine")

# Create log directories
New-Item -ItemType Directory -Path "C:\logs" -Force
```

### 2. Build and Deploy

```powershell
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Build frontend
cd frontend
npm install
npm run build

# Start backend service
Start-Service AssetManagementBackend

# Check service status
Get-Service AssetManagementBackend
```

### 3. Database Initialization

```powershell
# Run database migrations
cd backend
alembic upgrade head

# Optional: Load initial data
python -c "from app.sync import sync_assets; sync_assets()"
```

### 4. Verify Deployment

```powershell
# Check if services are healthy
Get-Service AssetManagementBackend
Get-Service postgresql-x64-16

# Test API endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/assets" -Method Get

# Test frontend
Invoke-WebRequest -Uri "http://localhost" -Method Get
```

## SSL Certificate Management

### IIS SSL Configuration

1. **Install SSL Certificate**: Import certificate into IIS
2. **Bind Certificate**: Configure HTTPS binding in IIS Manager
3. **Redirect HTTP to HTTPS**: Configure URL Rewrite rules

### Manual SSL Certificate Setup

```powershell
# Import SSL certificate
Import-Certificate -FilePath "C:\certificates\your-cert.pfx" -CertStoreLocation Cert:\LocalMachine\My

# Configure IIS binding
New-WebBinding -Name "AssetManagement" -Protocol "https" -Port 443 -SslFlags 1
```

## Monitoring and Logging

### Service Health Checks

```powershell
# Check service health
Get-Service AssetManagementBackend
Get-Service postgresql-x64-16

# View service logs
Get-Content "C:\logs\asset-backend.log" -Tail 50
Get-Content "C:\logs\asset-backend-error.log" -Tail 50

# Monitor resource usage
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"}
```

### Application Monitoring

- **Backend Health**: `http://localhost:8000/api/health`
- **Database Health**: Check PostgreSQL service and logs
- **Frontend Health**: Check IIS application pool and logs

### Log Management

```powershell
# View backend logs
Get-Content "C:\logs\asset-backend.log" -Wait

# View error logs
Get-Content "C:\logs\asset-backend-error.log" -Wait

# View IIS logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 100

# View PostgreSQL logs
Get-Content "C:\Program Files\PostgreSQL\16\data\pg_log\*.log" -Tail 50
```

## Backup and Recovery

### Database Backup

```powershell
# Create backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
pg_dump -U admin -h localhost assetdb > "C:\backups\backup_$timestamp.sql"

# Restore backup
psql -U admin -h localhost assetdb < "C:\backups\backup_file.sql"
```

### Application Backup

```powershell
# Backup application files
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path "C:\inetpub\wwwroot\asset-management" -DestinationPath "C:\backups\app_backup_$timestamp.zip"

# Backup configuration files
Copy-Item "C:\inetpub\wwwroot\asset-management\backend\app\settings.py" "C:\backups\settings_backup_$timestamp.py"
```

## Scaling and Performance

### Windows Service Scaling

```powershell
# Configure multiple backend instances
# Create additional NSSM services with different ports
nssm install AssetManagementBackend2 "C:\Python311\python.exe"
nssm set AssetManagementBackend2 AppParameters "C:\inetpub\wwwroot\asset-management\backend\app\main.py --port 8001"

# Configure load balancing in IIS
# Use Application Request Routing (ARR) for load balancing
```

### Resource Management

```powershell
# Configure Windows service resource limits
# Use Windows Resource Monitor to track usage

# Set process priority
Get-Process -Name "python" | ForEach-Object { $_.PriorityClass = "AboveNormal" }

# Monitor memory usage
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Select-Object ProcessName, WorkingSet, CPU
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```powershell
   # Check database status
   Get-Service postgresql-x64-16
   
   # Check database logs
   Get-Content "C:\Program Files\PostgreSQL\16\data\log\*.log" -Tail 50
   
   # Test database connection
   python -c "from app.db import engine; print('DB OK')"
   ```

2. **SSL Certificate Issues**
   ```powershell
   # Check IIS logs
    Get-Content "E:\asset-app\logs\IIS logs\W3SVC2\*.log" -Tail 50 

   # Verify domain configuration
    nslookup asset-ny.worldwide.bbc.co.uk 

   
   # Check certificate binding
   Get-WebBinding -Name "AssetUI" -Protocol "https"
   ```

3. **Service Startup Issues**
   ```powershell
   # Check service status
   Get-Service AssetBackend
   
   # Restart specific service
   Restart-Service AssetBackend
   
   # Check service logs
   Get-Content "E:\logs\asset-backend-error.log" -Tail 50
   ```

### Debug Commands

```powershell
# Connect to database
psql -U admin -h localhost assetdb

# Check network connectivity
Test-NetConnection -ComputerName localhost -Port 8000
Test-NetConnection -ComputerName localhost -Port 5432

# View environment variables
Get-ChildItem Env: | Where-Object {$_.Name -like "*ASSET*" -or $_.Name -like "*DATABASE*"}

# Check IIS application pool
Get-IISAppPool -Name "AssetUI"
```

## Security Considerations

### Network Security

- **Internal networks** for database communication
- **Public networks** only for necessary services
- **Port exposure** limited to required ports

### Data Security

- **Environment variables** for sensitive data
- **Volume encryption** for persistent data
- **Regular backups** with encryption

### Access Control

- **Firewall rules** for external access
- **VPN access** for administrative functions
- **Audit logging** for security events

## Maintenance

### Regular Maintenance Tasks

1. **Update Dependencies**
   ```powershell
   # Update Python packages
   cd backend
   pip install -r requirements.txt --upgrade
   
   # Update Node.js packages
   cd frontend
   npm update
   ```

2. **Database Maintenance**
   ```powershell
   # Vacuum database
   psql -U admin -h localhost assetdb -c "VACUUM ANALYZE;"
   
   # Check database size
   psql -U admin -h localhost assetdb -c "SELECT pg_size_pretty(pg_database_size('assetdb'));"
   ```

3. **Log Rotation**
   ```powershell
   # Configure Windows Event Log rotation
   # Use Windows Task Scheduler to archive old logs
   # Clean up old log files
   Get-ChildItem "E:\asset-app\logs\*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
   ```

### Update Procedures

1. **Backup current deployment**
   ```powershell
   # Backup database and application files
   $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
   pg_dump -U admin -h localhost assetdb > "C:\backups\pre_update_backup_$timestamp.sql"
   Compress-Archive -Path "C:\inetpub\wwwroot\asset-management" -DestinationPath "C:\backups\pre_update_app_$timestamp.zip"
   ```

2. **Deploy via GitHub Actions**
   - Push changes to main branch
   - GitHub Actions will automatically build and deploy

3. **Manual Update (if needed)**
   ```powershell
   # Stop services
   Stop-Service AssetManagementBackend
   
   # Update code
   git pull origin main
   
   # Install dependencies
   cd backend && pip install -r requirements.txt
   cd frontend && npm install && npm run build
   
   # Start services
   Start-Service AssetManagementBackend
   ```

4. **Verify functionality**
   - Check service status
   - Test API endpoints
   - Verify frontend functionality

5. **Update documentation** 