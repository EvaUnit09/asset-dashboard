"""
Fun Queries Service - handles predefined asset queries
"""
from typing import List, Dict, Any
from sqlmodel import Session, select, func
from datetime import date, timedelta
from collections import defaultdict

from .models import Asset


class FunQueriesService:
    """Service to handle predefined asset queries."""
    
    def __init__(self, session: Session):
        self.session = session
    
    @staticmethod
    def get_templates() -> Dict[str, Any]:
        """Get all available query templates organized by category."""
        return {
            "warranty_analysis": {
                "title": "Warranty Analysis",
                "description": "Analyze warranty status and expiration dates",
                "queries": {
                    "expired_warranties": {
                        "name": "Assets with Expired Warranties",
                        "description": "Assets whose warranty has already expired"
                    },
                    "expiring_30_days": {
                        "name": "Expiring in 30 Days",
                        "description": "Assets with warranty expiring in the next 30 days"
                    },
                    "expiring_60_days": {
                        "name": "Expiring in 60 Days",
                        "description": "Assets with warranty expiring in the next 60 days"
                    },
                    "expiring_90_days": {
                        "name": "Expiring in 90 Days",
                        "description": "Assets with warranty expiring in the next 90 days"
                    },
                    "no_warranty_info": {
                        "name": "No Warranty Information",
                        "description": "Assets with missing warranty expiration dates"
                    }
                }
            },
            "data_quality": {
                "title": "Data Quality Checks",
                "description": "Identify assets with missing or incomplete information",
                "queries": {
                    "missing_serial": {
                        "name": "Missing Serial Numbers",
                        "description": "Assets without serial numbers"
                    },
                    "missing_asset_tag": {
                        "name": "Missing Asset Tags",
                        "description": "Assets without asset tags"
                    },
                    "missing_warranty": {
                        "name": "Missing Warranty Dates",
                        "description": "Assets without warranty expiration dates"
                    },
                    "missing_manufacturer": {
                        "name": "Missing Manufacturer",
                        "description": "Assets without manufacturer information"
                    },
                    "missing_location": {
                        "name": "Missing Location",
                        "description": "Assets without location information"
                    }
                }
            },
            "asset_insights": {
                "title": "Asset Insights",
                "description": "Analyze asset distribution and patterns",
                "queries": {
                    "status_breakdown": {
                        "name": "Assets by Status",
                        "description": "Count of assets grouped by status"
                    },
                    "manufacturer_breakdown": {
                        "name": "Assets by Manufacturer",
                        "description": "Count of assets grouped by manufacturer"
                    },
                    "category_breakdown": {
                        "name": "Assets by Category",
                        "description": "Count of assets grouped by category"
                    },
                    "recent_assets": {
                        "name": "Recently Added Assets",
                        "description": "Assets added in the last 30 days"
                    },
                    "company_breakdown": {
                        "name": "Assets by Company",
                        "description": "Count of assets grouped by company"
                    }
                }
            }
        }
    
    def get_template_name(self, template_id: str) -> str:
        """Get the display name for a template."""
        templates = self.get_templates()
        for category in templates.values():
            if template_id in category["queries"]:
                return category["queries"][template_id]["name"]
        return "Unknown Query"
    
    def execute_query(self, template_id: str) -> List[Dict[str, Any]]:
        """Execute a predefined query template."""
        query_map = {
            # Warranty Analysis
            "expired_warranties": self._get_expired_warranties,
            "expiring_30_days": lambda: self._get_expiring_warranties(30),
            "expiring_60_days": lambda: self._get_expiring_warranties(60),
            "expiring_90_days": lambda: self._get_expiring_warranties(90),
            "no_warranty_info": self._get_no_warranty_info,
            
            # Data Quality
            "missing_serial": self._get_missing_serial,
            "missing_asset_tag": self._get_missing_asset_tag,
            "missing_warranty": self._get_missing_warranty,
            "missing_manufacturer": self._get_missing_manufacturer,
            "missing_location": self._get_missing_location,
            
            # Asset Insights
            "status_breakdown": self._get_status_breakdown,
            "manufacturer_breakdown": self._get_manufacturer_breakdown,
            "category_breakdown": self._get_category_breakdown,
            "recent_assets": self._get_recent_assets,
            "company_breakdown": self._get_company_breakdown,
        }
        
        if template_id not in query_map:
            raise ValueError(f"Unknown query template: {template_id}")
        
        return query_map[template_id]()
    
    # Warranty Analysis Queries
    def _get_expired_warranties(self) -> List[Dict[str, Any]]:
        """Get assets with expired warranties."""
        today = date.today()
        statement = select(Asset).where(
            Asset.warranty_expires.is_not(None),
            Asset.warranty_expires < today
        )
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def _get_expiring_warranties(self, days: int) -> List[Dict[str, Any]]:
        """Get assets with warranties expiring in the next X days."""
        today = date.today()
        future_date = today + timedelta(days=days)
        statement = select(Asset).where(
            Asset.warranty_expires.is_not(None),
            Asset.warranty_expires >= today,
            Asset.warranty_expires <= future_date
        )
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def _get_no_warranty_info(self) -> List[Dict[str, Any]]:
        """Get assets with no warranty information."""
        statement = select(Asset).where(Asset.warranty_expires.is_(None))
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    # Data Quality Queries
    def _get_missing_serial(self) -> List[Dict[str, Any]]:
        """Get assets missing serial numbers."""
        statement = select(Asset).where(
            (Asset.serial.is_(None)) | (Asset.serial == "")
        )
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def _get_missing_asset_tag(self) -> List[Dict[str, Any]]:
        """Get assets missing asset tags."""
        statement = select(Asset).where(
            (Asset.asset_tag.is_(None)) | (Asset.asset_tag == "")
        )
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def _get_missing_warranty(self) -> List[Dict[str, Any]]:
        """Get assets missing warranty dates."""
        statement = select(Asset).where(Asset.warranty_expires.is_(None))
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def _get_missing_manufacturer(self) -> List[Dict[str, Any]]:
        """Get assets missing manufacturer information."""
        statement = select(Asset).where(
            (Asset.manufacturer.is_(None)) | (Asset.manufacturer == "")
        )
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def _get_missing_location(self) -> List[Dict[str, Any]]:
        """Get assets missing location information."""
        statement = select(Asset).where(
            (Asset.location.is_(None)) | (Asset.location == "")
        )
        assets = self.session.exec(statement).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    # Asset Insights Queries
    def _get_status_breakdown(self) -> List[Dict[str, Any]]:
        """Get count of assets by status."""
        statement = select(Asset.status, func.count(Asset.id).label("count")).group_by(Asset.status)
        results = self.session.exec(statement).all()
        return [{"status": row[0] or "Unknown", "count": row[1]} for row in results]
    
    def _get_manufacturer_breakdown(self) -> List[Dict[str, Any]]:
        """Get count of assets by manufacturer."""
        statement = select(Asset.manufacturer, func.count(Asset.id).label("count")).group_by(Asset.manufacturer)
        results = self.session.exec(statement).all()
        return [{"manufacturer": row[0] or "Unknown", "count": row[1]} for row in results]
    
    def _get_category_breakdown(self) -> List[Dict[str, Any]]:
        """Get count of assets by category."""
        statement = select(Asset.category, func.count(Asset.id).label("count")).group_by(Asset.category)
        results = self.session.exec(statement).all()
        return [{"category": row[0] or "Unknown", "count": row[1]} for row in results]
    
    def _get_recent_assets(self) -> List[Dict[str, Any]]:
        """Get assets added in the last 30 days."""
        thirty_days_ago = date.today() - timedelta(days=30)
        # Note: created_at is stored as string, so we need to handle this carefully
        statement = select(Asset).where(Asset.created_at.is_not(None))
        assets = self.session.exec(statement).all()
        
        # Filter in Python since created_at is a string
        recent_assets = []
        for asset in assets:
            if asset.created_at:
                try:
                    # Parse the created_at string (assuming ISO format)
                    created_date = date.fromisoformat(asset.created_at.split('T')[0])
                    if created_date >= thirty_days_ago:
                        recent_assets.append(asset)
                except (ValueError, AttributeError):
                    continue
        
        return [self._asset_to_dict(asset) for asset in recent_assets]
    
    def _get_company_breakdown(self) -> List[Dict[str, Any]]:
        """Get count of assets by company."""
        statement = select(Asset.company, func.count(Asset.id).label("count")).group_by(Asset.company)
        results = self.session.exec(statement).all()
        return [{"company": row[0] or "Unknown", "count": row[1]} for row in results]
    
    def _asset_to_dict(self, asset: Asset) -> Dict[str, Any]:
        """Convert Asset model to dictionary for API response."""
        return {
            "id": asset.id,
            "asset_name": asset.asset_name,
            "asset_tag": asset.asset_tag,
            "category": asset.category,
            "manufacturer": asset.manufacturer,
            "model": asset.model,
            "serial": asset.serial,
            "status": asset.status,
            "company": asset.company,
            "location": asset.location,
            "warranty_expires": asset.warranty_expires.isoformat() if asset.warranty_expires else None,
            "created_at": asset.created_at
        }