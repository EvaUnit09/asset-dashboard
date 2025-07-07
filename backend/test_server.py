#!/usr/bin/env python3
"""
Standalone test server for PDF export functionality.
Provides mock data without requiring database connectivity.
"""

import sys
import os
from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
import json

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models import Asset, ExportConfig, ExportHistory, ExportResponse
from app.pdf_export_service import PDFExportService

app = FastAPI(title="Asset Management Test Server", version="1.0.0")

# Add CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock asset data
def create_mock_assets():
    """Create comprehensive mock asset data for testing."""
    mock_assets = []
    
    # Create diverse test data
    companies = ["Acme Corp", "TechStart Inc", "Global Solutions", "Innovation Labs"]
    manufacturers = ["Apple", "Lenovo", "Dell", "HP", "Microsoft"]
    categories = ["Laptop", "Desktop", "Monitor", "Server", "Tablet"]
    statuses = ["Active", "Pending Rebuild", "Stock", "Retired"]
    locations = ["New York", "San Francisco", "London", "Tokyo", "Remote"]
    
    for i in range(50):  # Create 50 mock assets
        asset = Asset()
        asset.id = i + 1
        asset.asset_name = f"{categories[i % len(categories)]}-{i+1:03d}"
        asset.asset_tag = f"AST{i+1:04d}"
        asset.category = categories[i % len(categories)]
        asset.manufacturer = manufacturers[i % len(manufacturers)]
        asset.model = f"Model-{chr(65 + (i % 26))}{i+1}"
        asset.serial = f"SN{i+1:06d}"
        asset.status = statuses[i % len(statuses)]
        asset.company = companies[i % len(companies)]
        asset.location = locations[i % len(locations)]
        asset.warranty_expires = date(2025 + (i % 3), (i % 12) + 1, 15)
        asset.created_at = f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T10:00:00Z"
        asset.model_no = f"MN-{i+1}"
        asset.warranty = f"{(i % 3) + 1} Years"
        asset.purchase_date = f"2024-{(i % 12) + 1:02d}-01"
        
        mock_assets.append(asset)
    
    return mock_assets

MOCK_ASSETS = create_mock_assets()

@app.get("/")
def root():
    """Root endpoint with server info."""
    return {
        "message": "Asset Management Test Server",
        "version": "1.0.0",
        "endpoints": {
            "assets": "/assets",
            "export_pdf": "/assets/export-pdf",
            "export_history": "/assets/export-history",
            "docs": "/docs"
        },
        "mock_data": {
            "total_assets": len(MOCK_ASSETS),
            "companies": len(set(a.company for a in MOCK_ASSETS)),
            "categories": len(set(a.category for a in MOCK_ASSETS))
        }
    }

@app.get("/assets")
def get_assets():
    """Get all mock assets."""
    return MOCK_ASSETS

@app.post("/assets/export-pdf")
def export_assets_pdf(config: ExportConfig):
    """
    Generate PDF export based on configuration.
    Uses mock data for testing purposes.
    """
    try:
        print(f"📄 Generating PDF with config: {config.title}")
        
        # Apply any filters if specified
        filtered_assets = MOCK_ASSETS
        if config.tableFilters:
            filtered_assets = []
            for asset in MOCK_ASSETS:
                include_asset = True
                
                if config.tableFilters.company:
                    if not asset.company or config.tableFilters.company.lower() not in asset.company.lower():
                        include_asset = False
                
                if config.tableFilters.manufacturer:
                    if not asset.manufacturer or config.tableFilters.manufacturer.lower() not in asset.manufacturer.lower():
                        include_asset = False
                
                if config.tableFilters.category:
                    if not asset.category or config.tableFilters.category.lower() not in asset.category.lower():
                        include_asset = False
                
                if include_asset:
                    filtered_assets.append(asset)
        
        print(f"📊 Using {len(filtered_assets)} assets after filtering")
        
        # Generate PDF using the service
        pdf_service = PDFExportService(filtered_assets, config)
        pdf_buffer = pdf_service.generate_pdf()
        
        # Save to temporary file for response
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        # Generate filename
        timestamp = config.title.replace(' ', '_').replace('/', '_')
        filename = f"{timestamp}_export.pdf"
        
        print(f"✅ PDF generated successfully: {len(pdf_buffer.getvalue())} bytes")
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="application/pdf"
        )
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation failed: {str(e)}"
        )

@app.get("/assets/export-history")
def get_export_history():
    """Get mock export history."""
    mock_history = [
        ExportHistory(
            id=1,
            config_json='{"title": "Previous Test Export"}',
            created_at=date(2024, 12, 15),
            file_size_bytes=234567,
            download_count=1,
            export_type="pdf",
            status="completed"
        ),
        ExportHistory(
            id=2,
            config_json='{"title": "Monthly Report"}',
            created_at=date(2024, 12, 10),
            file_size_bytes=189234,
            download_count=3,
            export_type="pdf",
            status="completed"
        )
    ]
    return mock_history

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "mock_assets": len(MOCK_ASSETS)}

if __name__ == "__main__":
    import uvicorn
    import sys
    
    print("🚀 Starting Asset Management Test Server")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🧪 Test with mock data - no database required!")
    print("---")
    
    # Check if --reload flag is passed
    if "--reload" in sys.argv:
        # Use import string for reload compatibility
        uvicorn.run(
            "test_server:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    else:
        # Use app object directly
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        ) 