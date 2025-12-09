from fastapi import APIRouter, Depends, HTTPException
import logging
from fastapi.responses import FileResponse
from numpy.linalg import det
from sqlalchemy import exc
from sqlmodel import select, Session
from datetime import datetime
from tempfile import NamedTemporaryFile
import json
import os
import pandas as pd
from io import BytesIO
from sqlmodel import select
from ..snipeit import create_asset_in_snipeit, update_asset_in_snipeit

from ..db import get_session
from ..models import Asset, ExportConfig, ExportHistory, AssetCreate, AssetUpdate
from ..pdf_export_service import PDFExportService

router = APIRouter(prefix="/assets", tags=["assets"])
logger = logging.getLogger(__name__)

@router.post("/create", response_model=Asset)
def create_asset(asset_data: AssetCreate, session: Session = Depends(get_session)):

    """Create a new asset in both Snipe-IT and the database
    
    Args:
        asset_data: AssetCreate model
        session: Database session
    Returns:
        Asset: The created asset with Snipe-IT ID
    """
    try:
        # 1. Validate asset_tag uniqueness
        existing = session.exec(
            select(Asset).where(Asset.asset_tag == asset_data.asset_tag)
        ).first()
        if existing:
            raise HTTPException(status_code=400,
            detail="Asset tag already exists"
            )
        # 2. Create asset in Snipe IT first to get the ID
        snipeit_response = create_asset_in_snipeit(asset_data.model_dump(mode='json'))
        snipeit_id = snipeit_response["id"]
        # 3. Create asset in the database with Snipe-IT's ID
        db_asset = Asset(
            id=snipeit_id,
            **asset_data.model_dump()
        )
        session.add(db_asset)
        session.commit()
        session.refresh(db_asset)

        logger.info(f"Created Asset: {db_asset.asset_tag} (ID: {snipeit_id})")
        return db_asset

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.exception(f"Failed to create asset: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create asset: {str(e)}"
        )
@router.put("/{asset_id}", response_model=Asset)
def update_assets(asset_id: int, asset_data: AssetUpdate, session: Session = Depends(get_session)):
    """Updates an asset in both Snipe-IT and the database
    
    Args:
        asset_name: ID of the asset to update
        asset_data: AssetUpdate model with field to update
        session: Database session
    Returns:
        Asset: The updated asset
    """
    # Fetch existing asset from database
    existing_asset = session.get(Asset, asset_id)
    try:
        # 1. Validate asset_tag uniqueness
        existing = session.get(Asset, asset_id)
        if not existing_asset:
            raise HTTPException(
                status_code=404,
                detail=f"Asset with ID {asset_id} not found"
            )
        # 3. existing asset contains db record so we can use it
        update_dict = asset_data.model_dump(exclude_unset=True)
        
        if update_dict:
            # Convert to JSON-serializable format for Snipe-IT API
            update_dict_json = asset_data.model_dump(mode='json', exclude_unset=True)
            snipeit_response = update_asset_in_snipeit(asset_id, update_dict_json)

            # 4. Update the existing_asset objects fields with Python types
            for key, value in update_dict.items():
                setattr(existing_asset, key, value)
            session.add(existing_asset)
            session.commit()
            session.refresh(existing_asset)

            logger.info(f"Updated Asset: {existing_asset.asset_tag} (ID:) {asset_id}")
        
        return existing_asset
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.exception(f"Failed to update asset: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update asset: {str(e)}"
        )
@router.delete("/{asset_id}",status_code=204)
def delete_asset(asset_id: int, session: Session = Depends(get_session)):
    """
    Soft delete an asset by changing its status to 'Disposed'

    Args:
        asset_name: Id of the asset to mark as disposed
        session: Database session

    Returns:
        None (204 No Content on success)
    """
    try:
        # 1. check if asset exists
        existing_asset = session.get(Asset, asset_id)
        if not existing_asset:
            raise HTTPException(
                status_code=404,
                detail=f"Asset with ID {asset_id} not found"
            )
        # 2. Update status to "Disposed" in Snipe-IT
        update_data = {"status": "Disposed"}
        update_asset_in_snipeit(asset_id, update_data)

        # 3. Update status to "Disposed" in local DB
        existing_asset.status = "Disposed"
        session.add(existing_asset)
        session.commit()

        logger.info(f"Marked asset as disposed: {existing_asset}")

        # 4. Return None
        return None
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.exception(f"Failed to mark asset as disposed")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark asset as disposed: {str(e)}"
        )



@router.get("", response_model=list[Asset])
def read_assets(session=Depends(get_session)):
    """Get all assets for dashboard use."""
    return session.exec(select(Asset)).all()
    
@router.get("/{asset_id}", response_model=Asset)
def get_asset(asset_id: int, session: Session = Depends(get_session)):
    """
    Get single asset by ID.
    """
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset with ID {asset_id} not found"
        )
    return asset


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
        logger.info("Received export-pdf request", extra={
            'config': config.model_dump() if hasattr(config, 'model_dump') else str(config)
        })
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
            logger.exception("Failed to save export history", extra={'error': str(e)})
        
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
        logger.exception("PDF export failed", extra={
            'error': str(e),
            'config': config.model_dump() if hasattr(config, 'model_dump') else str(config)
        })
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


@router.post("/export-excel")
def export_assets_excel(
    config: ExportConfig,
    session: Session = Depends(get_session)
):
    """
    Generate Excel export of asset details for interactive analysis.
    
    Args:
        config: Export configuration specifying filters
        session: Database session
    
    Returns:
        FileResponse: Excel file download
    """
    try:
        # Get all assets
        statement = select(Asset)
        assets = session.exec(statement).all()
        
        if not assets:
            raise HTTPException(status_code=404, detail="No assets found")
        
        # Filter assets to match dashboard (Active, Stock, Pending Rebuild only)
        filtered_assets = [a for a in assets if a.status in ['Active', 'Stock', 'Pending Rebuild']]
        
        # Apply additional table filters if specified
        if config.tableFilters:
            additional_filtered = []
            for asset in filtered_assets:
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
                    additional_filtered.append(asset)
            
            filtered_assets = additional_filtered
        
        # Convert to pandas DataFrame
        asset_data = []
        for asset in filtered_assets:
            asset_data.append({
                'Asset Tag': asset.asset_tag or '',
                'Asset Name': asset.asset_name or '',
                'Category': asset.category or '',
                'Manufacturer': asset.manufacturer or '',
                'Model': asset.model or '', 
                'Model No': asset.model_no or '',
                'Serial Number': asset.serial or '',
                'Status': asset.status or '',
                'Company': asset.company or '',
                'Location': asset.location or '',
                'Department': asset.department or '',
                'Assigned User': asset.assigned_user_name or '',
                'Warranty': asset.warranty or '',
                'Warranty Expires': asset.warranty_expires.strftime('%Y-%m-%d') if asset.warranty_expires else '',
                'Created At': asset.created_at or ''
            })
        
        df = pd.DataFrame(asset_data)
        
        # Create Excel file in memory
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Asset Details', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Asset Details']
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        excel_buffer.seek(0)
        
        # Save to temporary file for response
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(excel_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        # Save export history to database
        try:
            export_history = ExportHistory(
                config_json=json.dumps(config.model_dump()),
                file_size_bytes=len(excel_buffer.getvalue()),
                created_at=datetime.now().date(),
                export_type="excel",
                status="completed"
            )
            session.add(export_history)
            session.commit()
        except Exception as e:
            print(f"Failed to save export history: {e}")
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"asset_details_{timestamp}.xlsx"
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        # Save failed export to history
        try:
            export_history = ExportHistory(
                config_json=json.dumps(config.model_dump()),
                file_size_bytes=0,
                created_at=datetime.now().date(),
                export_type="excel",
                status="failed"
            )
            session.add(export_history)
            session.commit()
        except Exception:
            pass
        
        raise HTTPException(
            status_code=500, 
            detail=f"Excel generation failed: {str(e)}"
        )


@router.get("/export-history", response_model=list[ExportHistory])
def get_export_history(session: Session = Depends(get_session)):
    """Get export history records."""
    return session.exec(
        select(ExportHistory).limit(50)
    ).all()


