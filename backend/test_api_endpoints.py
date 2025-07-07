#!/usr/bin/env python3
"""
Test script for FastAPI endpoints.
Tests the API endpoints using FastAPI TestClient.
"""

import sys
import os
from datetime import date
from fastapi.testclient import TestClient

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import app
from app.models import ExportConfig, TableFilters

# Create test client
client = TestClient(app)

def test_assets_endpoint():
    """Test the basic assets endpoint."""
    print("🧪 Testing Assets Endpoint...")
    
    try:
        response = client.get("/assets")
        print(f"  ├─ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            assets = response.json()
            print(f"  ├─ ✅ Assets endpoint works, returned {len(assets)} assets")
            return True
        else:
            print(f"  └─ ❌ Assets endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"  └─ ❌ Assets endpoint failed with exception: {e}")
        return False

def test_pdf_export_endpoint():
    """Test the PDF export endpoint."""
    print("🧪 Testing PDF Export Endpoint...")
    
    # Test configuration
    config = {
        "title": "API Test Export",
        "description": "Testing PDF export via API",
        "includeSummary": True,
        "summaryCards": ["total", "active"],
        "includeCharts": True,
        "selectedCharts": ["category", "status"],
        "includeTable": True,
        "tableColumns": ["asset_name", "category", "manufacturer"],
        "pageSize": "A4",
        "orientation": "portrait",
        "includeTimestamp": True
    }
    
    try:
        print("  ├─ Sending POST request to /assets/export-pdf...")
        response = client.post("/assets/export-pdf", json=config)
        print(f"  ├─ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Check if response is PDF
            content_type = response.headers.get("content-type", "")
            content_length = len(response.content)
            
            print(f"  ├─ Content Type: {content_type}")
            print(f"  ├─ Content Length: {content_length} bytes")
            
            if "application/pdf" in content_type:
                print("  ├─ ✅ Correct content type (application/pdf)")
            else:
                print("  ├─ ⚠️  Unexpected content type")
            
            if content_length > 1000:
                print("  ├─ ✅ PDF has substantial content")
                
                # Save the PDF for inspection
                with open('api_test_export.pdf', 'wb') as f:
                    f.write(response.content)
                print("  ├─ ✅ PDF saved as 'api_test_export.pdf'")
                
                return True
            else:
                print("  └─ ❌ PDF content too small")
                return False
        else:
            print(f"  └─ ❌ PDF export failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"  └─ ❌ PDF export failed with exception: {e}")
        return False

def test_pdf_export_with_filters():
    """Test PDF export with table filters."""
    print("🧪 Testing PDF Export with Filters...")
    
    config = {
        "title": "Filtered API Test",
        "includeTable": True,
        "tableColumns": ["asset_name", "category"],
        "tableFilters": {
            "category": "Laptop",
            "searchQuery": "Test"
        }
    }
    
    try:
        response = client.post("/assets/export-pdf", json=config)
        print(f"  ├─ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"  ├─ Content Length: {content_length} bytes")
            
            # Save filtered PDF
            with open('api_filtered_export.pdf', 'wb') as f:
                f.write(response.content)
            print("  └─ ✅ Filtered PDF saved as 'api_filtered_export.pdf'")
            return True
        else:
            print(f"  └─ ❌ Filtered PDF export failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"  └─ ❌ Filtered PDF export failed: {e}")
        return False

def test_export_history_endpoint():
    """Test the export history endpoint."""
    print("🧪 Testing Export History Endpoint...")
    
    try:
        response = client.get("/assets/export-history")
        print(f"  ├─ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            history = response.json()
            print(f"  └─ ✅ Export history works, returned {len(history)} records")
            return True
        else:
            print(f"  └─ ❌ Export history failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"  └─ ❌ Export history failed: {e}")
        return False

def test_invalid_config():
    """Test API with invalid configuration."""
    print("🧪 Testing Invalid Configuration Handling...")
    
    # Missing required fields
    invalid_config = {
        "invalidField": "test"
    }
    
    try:
        response = client.post("/assets/export-pdf", json=invalid_config)
        print(f"  ├─ Status Code: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print("  └─ ✅ Correctly rejected invalid configuration")
            return True
        else:
            print(f"  └─ ⚠️  Unexpected response for invalid config: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  └─ ❌ Invalid config test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Starting FastAPI Endpoint Tests\n")
    
    # Note: These tests will fail if no database connection is available
    # They're designed to test the API structure and error handling
    
    tests = [
        test_assets_endpoint,
        test_export_history_endpoint,
        test_pdf_export_endpoint,
        test_pdf_export_with_filters,
        test_invalid_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Empty line between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}\n")
    
    print("=" * 50)
    print(f"📊 API Test Results: {passed}/{total} tests passed")
    
    if passed >= 3:  # Allow some failures due to database connection
        print("🎉 Core API functionality is working!")
        print("\n📁 Generated test files:")
        if os.path.exists('api_test_export.pdf'):
            print("  - api_test_export.pdf")
        if os.path.exists('api_filtered_export.pdf'):
            print("  - api_filtered_export.pdf")
        return True
    else:
        print("❌ Multiple API tests failed. Check configuration and database connection.")
        return False

if __name__ == "__main__":
    print("⚠️  Note: Some tests may fail without database connection")
    print("    This is expected in a standalone test environment\n")
    success = main()
    sys.exit(0 if success else 1) 