from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import select, Session
from datetime import datetime
from tempfile import NamedTemporaryFile
import json
import os

from ..db import get_session
from ..models import Asset, ExportConfig, ExportHistory, ExportResponse
from ..pdf_export_service import PDFExportService

router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("", response_model=list[Asset])
def read_assets(session=Depends(get_session)):
    """Get all assets for dashboard use."""
    return session.exec(select(Asset)).all()

@router.get("/paginated", response_model=list[Asset])
def read_assets_paginated(
    skip: int = 0, 
    limit: int = 100, 
    session=Depends(get_session)
):
    """Get assets with pagination to reduce memory usage."""
    if limit > 500:  # Cap maximum limit
        limit = 500
    
    statement = select(Asset).offset(skip).limit(limit)
    return session.exec(statement).all()


@router.post("/export-pdf")
def export_assets_pdf(
    config: ExportConfig,
    session: Session = Depends(get_session)
):
    """
    Generate PDF export of assets based on configuration.
    
    Args:
        config: Export configuration specifying what to include
        session: Database session
    
    Returns:
        FileResponse: PDF file download
    """
    try:
        # Get assets with streaming to reduce memory usage
        # For exports, we still need all assets but process them in chunks
        statement = select(Asset)
        assets = session.exec(statement).all()
        
        if not assets:
            raise HTTPException(status_code=404, detail="No assets found")
        
        # Apply any table filters to the asset list if specified
        if config.tableFilters:
            filtered_assets = []
            for asset in assets:
                include_asset = True
                
                # Apply filters
                if config.tableFilters.company:
                    if not asset.company or config.tableFilters.company.lower() not in asset.company.lower():
                        include_asset = False
                
                if config.tableFilters.manufacturer:
                    if not asset.manufacturer or config.tableFilters.manufacturer.lower() not in asset.manufacturer.lower():
                        include_asset = False
                
                if config.tableFilters.category:
                    if not asset.category or config.tableFilters.category.lower() not in asset.category.lower():
                        include_asset = False
                
                if config.tableFilters.model:
                    if not asset.model or config.tableFilters.model.lower() not in asset.model.lower():
                        include_asset = False
                
                if config.tableFilters.department:
                    if not asset.department or config.tableFilters.department.lower() not in asset.department.lower():
                        include_asset = False
                
                if config.tableFilters.searchQuery:
                    query = config.tableFilters.searchQuery.lower()
                    search_fields = [
                        asset.asset_name or '',
                        asset.asset_tag or '',
                        asset.serial or '',
                        asset.location or ''
                    ]
                    if not any(query in field.lower() for field in search_fields):
                        include_asset = False
                
                if include_asset:
                    filtered_assets.append(asset)
            
            assets = filtered_assets
        
        # Generate PDF using the service
        pdf_service = PDFExportService(list(assets), config)
        pdf_buffer = pdf_service.generate_pdf()
        
        # Save to temporary file for response
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        # Save export history to database
        try:
            export_history = ExportHistory(
                config_json=json.dumps(config.model_dump()),
                file_size_bytes=len(pdf_buffer.getvalue()),
                created_at=datetime.now().date(),
                export_type="pdf",
                status="completed"
            )
            session.add(export_history)
            session.commit()
        except Exception as e:
            # Log error but don't fail the export
            print(f"Failed to save export history: {e}")
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"asset_report_{timestamp}.pdf"
        
        # Return file response with cleanup
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="application/pdf"
        )
        
    except Exception as e:
        # Save failed export to history
        try:
            export_history = ExportHistory(
                config_json=json.dumps(config.model_dump()),
                file_size_bytes=0,
                created_at=datetime.now().date(),
                export_type="pdf",
                status="failed"
            )
            session.add(export_history)
            session.commit()
        except Exception:
            pass
        
        raise HTTPException(
            status_code=500, 
            detail=f"PDF generation failed: {str(e)}"
        )


@router.get("/export-history", response_model=list[ExportHistory])
def get_export_history(session: Session = Depends(get_session)):
    """Get export history records."""
    return session.exec(
        select(ExportHistory).limit(50)
    ).all()


