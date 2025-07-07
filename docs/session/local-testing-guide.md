# Local Testing Guide for PDF Export Feature

## Overview
This guide provides multiple approaches to test the PDF export feature locally without deploying to the main production environment.

## Testing Approaches

### 1. **Full Local Development Setup (Recommended)**

#### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies (if not already done)
pip install -r requirements.txt

# Set environment variables for testing
export DATABASE_URL="sqlite:///./test_assets.db"  # Use SQLite for testing
export SNIPEIT_API_URL="https://demo.snipeitapp.com/api/v1"
export SNIPEIT_TOKEN="dummy_token_for_testing"

# Start the FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Create environment file for API URL
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start the frontend development server
npm run dev
```

#### Step 3: Access and Test
- Frontend: http://localhost:5173 (or the port shown by Vite)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. **Testing with Mock Data (Frontend Only)**

If you want to test the frontend components without running the backend:

```bash
cd frontend
npm run dev
```

#### Create Mock Test Component

Create `frontend/src/components/ExportModalTest.tsx`:

```typescript
import React, { useState } from 'react';
import { ExportModal } from './ExportModal';
import { Button } from './ui/button';
import type { Asset } from '@/types/asset';

// Mock asset data
const mockAssets: Asset[] = [
  {
    id: 1,
    asset_name: "Test Laptop 1",
    asset_tag: "LAP001",
    category: "Laptop",
    manufacturer: "Apple",
    model: "MacBook Pro",
    serial: "ABC123",
    status: "Active",
    company: "Test Company",
    location: "Office A",
    warranty_expires: "2025-12-31",
    created_at: "2024-01-15",
    model_no: "MBP16",
    eol: null,
    warranty: "2 Years",
    purchase_date: "2024-01-01"
  },
  // Add more mock assets as needed
];

export function ExportModalTest() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">PDF Export Test</h1>
      <Button onClick={() => setIsOpen(true)}>
        Test Export Modal
      </Button>
      
      <ExportModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        assets={mockAssets}
        currentFilters={{
          company: "Test Company",
          category: "Laptop"
        }}
      />
    </div>
  );
}
```

Add this to your main App for testing:

```typescript
// In App.tsx, temporarily add:
import { ExportModalTest } from './components/ExportModalTest';

// Add to JSX:
<ExportModalTest />
```

### 3. **Backend API Testing Only**

Test the PDF generation endpoints directly using our existing test scripts:

```bash
cd backend

# Run the PDF generation tests
python test_pdf_export.py

# Test API endpoints (will fail without database, but tests core logic)
python test_api_endpoints.py
```

### 4. **Using API Testing Tools**

#### Using curl to test the export endpoint:

```bash
# Test the export endpoint directly
curl -X POST "http://localhost:8000/assets/export-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Export",
    "includeSummary": true,
    "summaryCards": ["total", "active"],
    "includeCharts": true,
    "selectedCharts": ["category"],
    "includeTable": true,
    "tableColumns": ["asset_name", "category"],
    "pageSize": "A4",
    "orientation": "portrait",
    "includeTimestamp": true
  }' \
  --output test_export.pdf
```

#### Using Postman/Insomnia:

1. Create a POST request to `http://localhost:8000/assets/export-pdf`
2. Set Content-Type to `application/json`
3. Use the JSON body from the curl example above
4. Set response type to download file

### 5. **Database-less Testing**

For testing without database connectivity, modify the backend temporarily:

Create `backend/test_standalone.py`:

```python
import sys
from fastapi import FastAPI
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
import json

# Add the app directory to Python path
sys.path.insert(0, 'app')

from app.models import ExportConfig
from app.pdf_export_service import PDFExportService

app = FastAPI()

# Mock asset data
mock_assets = [
    # ... (use the same mock data from our test script)
]

@app.post("/test-export")
def test_export(config: ExportConfig):
    """Test export without database."""
    try:
        pdf_service = PDFExportService(mock_assets, config)
        pdf_buffer = pdf_service.generate_pdf()
        
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            path=tmp_file_path,
            filename="test_export.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

Run: `python backend/test_standalone.py`

### 6. **Component Testing in Isolation**

Test individual React components using the browser's developer tools:

```bash
cd frontend
npm run dev
```

Open browser developer console and test components:

```javascript
// Test export configuration validation
const { validateConfig } = useExportValidation();
const errors = validateConfig({
  title: "",  // Invalid - empty title
  includeSummary: false,
  includeCharts: false,
  includeTable: false  // Invalid - nothing selected
});
console.log(errors);
```

## Testing Checklist

### Frontend Components
- [ ] Export button appears in dashboard header
- [ ] Modal opens when button is clicked
- [ ] Modal closes on Cancel or backdrop click
- [ ] Configuration sections toggle properly
- [ ] Summary card selection works
- [ ] Chart selection works
- [ ] Table column selection works
- [ ] Validation errors display correctly
- [ ] Export button states change appropriately

### API Integration
- [ ] Export API call is made with correct data
- [ ] File download triggers properly
- [ ] Error handling works for network issues
- [ ] Success feedback displays
- [ ] Export history can be retrieved

### PDF Generation
- [ ] PDF generates with mock data
- [ ] All chart types render correctly
- [ ] Table filtering works
- [ ] Different page sizes/orientations work
- [ ] PDF content matches configuration

### End-to-End Flow
- [ ] Click export button → modal opens
- [ ] Configure options → validation passes
- [ ] Click generate → API call made
- [ ] PDF generates → file downloads
- [ ] Success message → modal closes

## Troubleshooting

### Common Issues

1. **CORS Errors**
   ```bash
   # Add CORS middleware to backend main.py:
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Environment Variables**
   ```bash
   # Create .env.local in frontend:
   echo "VITE_API_URL=http://localhost:8000" > frontend/.env.local
   ```

3. **Database Connection Issues**
   ```bash
   # Use SQLite for testing:
   export DATABASE_URL="sqlite:///./test.db"
   ```

4. **Port Conflicts**
   ```bash
   # Use different ports if needed:
   uvicorn app.main:app --port 8001  # Backend
   npm run dev -- --port 5174       # Frontend
   ```

## Quick Start Commands

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend  
cd frontend
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev

# Access: http://localhost:5173
```

## Performance Testing

### Test Large Datasets
```python
# In backend, create large mock dataset:
large_assets = [mock_asset_template] * 1000
# Test PDF generation performance
```

### Test Network Conditions
```javascript
// In browser dev tools, throttle network to test slow connections
// Network tab → Throttling → Slow 3G
```

This comprehensive testing approach ensures the PDF export feature works correctly before deployment to production. 