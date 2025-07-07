"""
Fun Queries API endpoints - predefined queries for asset analysis
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List, Dict, Any
from datetime import date, timedelta

from ..db import get_session
from ..models import Asset
from ..fun_queries_service import FunQueriesService

router = APIRouter(prefix="/fun-queries", tags=["fun-queries"])


@router.get("/templates")
async def get_query_templates() -> Dict[str, Any]:
    """Get all available query templates organized by category."""
    return FunQueriesService.get_templates()


@router.get("/execute/{template_id}")
async def execute_query(
    template_id: str,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Execute a predefined query template."""
    service = FunQueriesService(session)
    
    try:
        result = service.execute_query(template_id)
        return {
            "success": True,
            "template_id": template_id,
            "template_name": service.get_template_name(template_id),
            "data": result,
            "count": len(result)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")