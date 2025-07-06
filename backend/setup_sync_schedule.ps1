# PowerShell script to set up Windows Task Scheduler for asset sync
# Run this script as Administrator

param(
    [string]$PythonPath = "python.exe",
    [string]$WorkingDirectory = $PSScriptRoot
)

$TaskName = "AssetSync"
$TaskDescription = "Sync assets from Snipe-IT to PostgreSQL database"
$ScriptPath = Join-Path $WorkingDirectory "scheduled_sync.py"

Write-Host "Setting up Windows Task Scheduler for Asset Sync..." -ForegroundColor Green
Write-Host "Script Path: $ScriptPath" -ForegroundColor Yellow
Write-Host "Working Directory: $WorkingDirectory" -ForegroundColor Yellow

# Check if Python script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Error "Python script not found at $ScriptPath"
    exit 1
}

# Create the scheduled task action
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDirectory

# Create triggers for 8am, 12pm, 4pm, and 8pm
$Triggers = @(
    New-ScheduledTaskTrigger -Daily -At 8:00AM
    New-ScheduledTaskTrigger -Daily -At 12:00PM
    New-ScheduledTaskTrigger -Daily -At 4:00PM
    New-ScheduledTaskTrigger -Daily -At 8:00PM
)

# Create task settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create task principal (run as SYSTEM or current user)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the scheduled task
try {
    # Remove existing task if it exists
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Write-Host "Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    # Register new task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers -Settings $Settings -Principal $Principal -Description $TaskDescription
    
    Write-Host "Successfully created scheduled task: $TaskName" -ForegroundColor Green
    Write-Host "The task will run at: 8:00 AM, 12:00 PM, 4:00 PM, and 8:00 PM daily" -ForegroundColor Green
    
    # Display task information
    Get-ScheduledTask -TaskName $TaskName | Format-List
    
} catch {
    Write-Error "Failed to create scheduled task: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "Task setup complete! You can manage the task using:" -ForegroundColor Green
Write-Host "- Task Scheduler GUI (taskschd.msc)" -ForegroundColor Cyan
Write-Host "- PowerShell: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host "- PowerShell: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Logs will be saved to: $WorkingDirectory\logs\" -ForegroundColor Green 