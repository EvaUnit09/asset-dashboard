# start_backend.ps1  (final form)
$Env:PORT = 8000
$Env:DATABASE_URL = "postgresql://admin:supersecret@localhost:5432/assetdb"

# change to project root so "import app" works
Set-Location E:\asset-app\backend

#  call venv's Python explicitly  (single line or use back-ticks for wrapping)

E:\asset-app\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port $Env:PORT --workers 4 --proxy-headers


