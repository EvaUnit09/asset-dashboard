#!/usr/bin/env python3
"""
Test script for PDF export functionality.
Tests the core PDF generation without requiring database connection.
"""

import sys
import os
from datetime import date, datetime
from io import BytesIO

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models import Asset, ExportConfig, TableFilters
from app.pdf_export_service import PDFExportService
from app.chart_generator import ChartGenerator

def create_mock_assets():
    """Create mock asset data for testing."""
    # Create assets and set properties
    asset1 = Asset()
    asset1.asset_name = "Laptop-001"
    asset1.asset_tag = "LT001"
    asset1.category = "Laptop"
    asset1.manufacturer = "Apple"
    asset1.model = "MacBook Pro"
    asset1.serial = "ABC123"
    asset1.status = "Active"
    asset1.company = "Company A"
    asset1.location = "New York"
    asset1.warranty_expires = date(2025, 12, 31)
    asset1.created_at = "2024-01-15T10:00:00Z"
    
    asset2 = Asset()
    asset2.asset_name = "Desktop-001"
    asset2.asset_tag = "DT001"
    asset2.category = "Desktop"
    asset2.manufacturer = "Lenovo"
    asset2.model = "ThinkCentre"
    asset2.serial = "DEF456"
    asset2.status = "Active"
    asset2.company = "Company A"
    asset2.location = "New York"
    asset2.warranty_expires = date(2026, 6, 30)
    asset2.created_at = "2024-02-20T14:30:00Z"
    
    asset3 = Asset()
    asset3.asset_name = "Laptop-002"
    asset3.asset_tag = "LT002"
    asset3.category = "Laptop"
    asset3.manufacturer = "Lenovo"
    asset3.model = "X13 Gen 1"
    asset3.serial = "GHI789"
    asset3.status = "Pending Rebuild"
    asset3.company = "Company B"
    asset3.location = "London"
    asset3.warranty_expires = date(2025, 9, 15)
    asset3.created_at = "2024-03-10T09:15:00Z"
    
    asset4 = Asset()
    asset4.asset_name = "Monitor-001"
    asset4.asset_tag = "MN001"
    asset4.category = "Monitor"
    asset4.manufacturer = "Dell"
    asset4.model = "UltraSharp"
    asset4.serial = "JKL012"
    asset4.status = "Stock"
    asset4.company = "Company A"
    asset4.location = "Storage"
    asset4.warranty_expires = date(2027, 1, 20)
    asset4.created_at = "2024-01-25T16:45:00Z"
    
    asset5 = Asset()
    asset5.asset_name = "Laptop-003"
    asset5.asset_tag = "LT003"
    asset5.category = "Laptop"
    asset5.manufacturer = "Apple"
    asset5.model = "MacBook Air"
    asset5.serial = "MNO345"
    asset5.status = "Active"
    asset5.company = "Company B"
    asset5.location = "Tokyo"
    asset5.warranty_expires = date(2025, 8, 10)
    asset5.created_at = "2024-04-05T11:20:00Z"
    
    return [asset1, asset2, asset3, asset4, asset5]

def test_chart_generation():
    """Test chart generation functionality."""
    print("🧪 Testing Chart Generation...")
    
    assets = create_mock_assets()
    chart_gen = ChartGenerator()
    
    try:
        # Test category chart
        print("  ├─ Testing category chart...")
        category_chart = chart_gen.generate_category_chart(assets)
        assert isinstance(category_chart, BytesIO)
        assert category_chart.getvalue()  # Has content
        print("  ├─ ✅ Category chart generated successfully")
        
        # Test status pie chart
        print("  ├─ Testing status pie chart...")
        status_chart = chart_gen.generate_status_pie_chart(assets)
        assert isinstance(status_chart, BytesIO)
        assert status_chart.getvalue()  # Has content
        print("  ├─ ✅ Status pie chart generated successfully")
        
        # Test trends chart
        print("  ├─ Testing trends chart...")
        trends_chart = chart_gen.generate_trends_chart(assets)
        assert isinstance(trends_chart, BytesIO)
        assert trends_chart.getvalue()  # Has content
        print("  ├─ ✅ Trends chart generated successfully")
        
        # Test warranty expiration chart
        print("  ├─ Testing warranty expiration chart...")
        warranty_chart = chart_gen.generate_warranty_expiration_chart(assets)
        assert isinstance(warranty_chart, BytesIO)
        assert warranty_chart.getvalue()  # Has content
        print("  └─ ✅ Warranty expiration chart generated successfully")
        
        return True
        
    except Exception as e:
        print(f"  └─ ❌ Chart generation failed: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation functionality."""
    print("🧪 Testing PDF Generation...")
    
    assets = create_mock_assets()
    
    # Test basic configuration
    config = ExportConfig(
        title="Test Asset Report",
        description="This is a test PDF export",
        includeSummary=True,
        summaryCards=["total", "active", "pending", "stock"],
        includeCharts=True,
        selectedCharts=["category", "status"],
        includeTable=True,
        tableColumns=["asset_name", "category", "manufacturer", "status"],
        pageSize="A4",
        orientation="portrait",
        includeTimestamp=True
    )
    
    try:
        print("  ├─ Creating PDF service...")
        pdf_service = PDFExportService(assets, config)
        
        print("  ├─ Generating PDF...")
        pdf_buffer = pdf_service.generate_pdf()
        
        assert isinstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        assert len(pdf_content) > 1000  # Should be substantial
        assert pdf_content.startswith(b'%PDF')  # Valid PDF header
        
        print(f"  ├─ ✅ PDF generated successfully ({len(pdf_content)} bytes)")
        
        # Save test PDF for manual inspection
        with open('test_export.pdf', 'wb') as f:
            f.write(pdf_content)
        print("  └─ ✅ Test PDF saved as 'test_export.pdf'")
        
        return True
        
    except Exception as e:
        print(f"  └─ ❌ PDF generation failed: {e}")
        return False

def test_pdf_with_filters():
    """Test PDF generation with table filters."""
    print("🧪 Testing PDF Generation with Filters...")
    
    assets = create_mock_assets()
    
    # Test with filters
    config = ExportConfig(
        title="Filtered Asset Report",
        includeSummary=True,
        includeCharts=True,
        selectedCharts=["category"],
        includeTable=True,
        tableColumns=["asset_name", "category", "manufacturer"],
        tableFilters=TableFilters(
            company="Company A",
            category="Laptop"
        )
    )
    
    try:
        pdf_service = PDFExportService(assets, config)
        pdf_buffer = pdf_service.generate_pdf()
        
        assert isinstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        assert len(pdf_content) > 500  # Should have content
        
        print("  └─ ✅ Filtered PDF generated successfully")
        
        # Save filtered test PDF
        with open('test_filtered_export.pdf', 'wb') as f:
            f.write(pdf_content)
        print("  └─ ✅ Filtered test PDF saved as 'test_filtered_export.pdf'")
        
        return True
        
    except Exception as e:
        print(f"  └─ ❌ Filtered PDF generation failed: {e}")
        return False

def test_landscape_pdf():
    """Test PDF generation in landscape mode."""
    print("🧪 Testing Landscape PDF Generation...")
    
    assets = create_mock_assets()
    
    config = ExportConfig(
        title="Landscape Asset Report",
        includeCharts=True,
        selectedCharts=["trends", "warranty"],
        includeTable=True,
        tableColumns=["asset_name", "category", "manufacturer", "status", "location"],
        pageSize="Letter",
        orientation="landscape"
    )
    
    try:
        pdf_service = PDFExportService(assets, config)
        pdf_buffer = pdf_service.generate_pdf()
        
        assert isinstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        assert len(pdf_content) > 500
        
        print("  └─ ✅ Landscape PDF generated successfully")
        
        # Save landscape test PDF
        with open('test_landscape_export.pdf', 'wb') as f:
            f.write(pdf_content)
        print("  └─ ✅ Landscape test PDF saved as 'test_landscape_export.pdf'")
        
        return True
        
    except Exception as e:
        print(f"  └─ ❌ Landscape PDF generation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting PDF Export Tests\n")
    
    tests = [
        test_chart_generation,
        test_pdf_generation,
        test_pdf_with_filters,
        test_landscape_pdf
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
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PDF export functionality is working correctly.")
        print("\n📁 Generated test files:")
        print("  - test_export.pdf (basic export)")
        print("  - test_filtered_export.pdf (with filters)")
        print("  - test_landscape_export.pdf (landscape mode)")
        return True
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 