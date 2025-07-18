from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
from datetime import date
from pydantic import BaseModel
from typing import List


class Asset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # plain, snake-case attributes  ↓↓↓   ⇢ become lowercase SQL columns
    model: str | None = Field(default=None, nullable=True)
    company: str | None = Field(default=None, nullable=True)

    # these keep camel-case ONLY as an *alias* for JSON in/out;
    # the real column name is still snake-case `asset_name`, `asset_tag`, …
    asset_name: str | None = Field(default=None, sa_column=Column(String, index=True))
    asset_tag: str | None = Field(alias="AssetTag", default=None, sa_column=Column(String, unique=True))
    model_no:  str | None = Field(alias="ModelNo", default=None, sa_column=Column(String))

    category: str | None = Field(default=None, sa_column=Column(String))
    manufacturer: str | None = Field(default=None, nullable=True)
    serial: str | None = Field(default=None, nullable=True)
    warranty: str | None = Field(default=None, nullable=True)
    warranty_expires: date | None = Field(default=None, nullable=True)
    location: str | None = Field(default=None, nullable=True)
    department: str | None = Field(default=None, nullable=True)
    assigned_user_id: int | None = Field(default=None, nullable=True)
    status: str | None = Field(default=None, nullable=True)
    created_at: str | None = Field(default=None, nullable=True)
    # these were added for Snipe IT API data - careful renaming!


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str | None = Field(default=None, nullable=True)
    last_name: str | None = Field(default=None, nullable=True)
    username: str | None = Field(default=None, nullable=True)
    email: str | None = Field(default=None, nullable=True)
    county: str | None = Field(default=None, nullable=True)
    department_id: str | None = Field(default=None, nullable=True)
    department_name: str | None = Field(default=None, nullable=True)
    location_id: str | None = Field(default=None, nullable=True)
    assets_count: int | None = Field(default=None, nullable=True)
    license_count: int | None = Field(default=None, nullable=True)

class ExportHistory(SQLModel, table=True):
    """Track PDF export history and statistics."""
    __tablename__ = "export_history"  # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    config_json: str = Field()  # JSON serialized ExportConfig
    created_at: date = Field(default_factory=date.today)
    file_size_bytes: int = Field(default=0)
    download_count: int = Field(default=0)
    export_type: str = Field(default="pdf")  # pdf, excel, csv etc for future
    status: str = Field(default="completed")  # pending, completed, failed


# Pydantic models for API requests/responses (not database tables)

class TableFilters(BaseModel):
    """Filters to apply to table data."""
    company: Optional[str] = None
    manufacturer: Optional[str] = None
    category: Optional[str] = None
    model: Optional[str] = None
    department: Optional[str] = None
    searchQuery: Optional[str] = None


class ExportConfig(BaseModel):
    """Configuration for PDF export generation."""
    
    # Report metadata
    title: str = "Asset Management Report"
    description: Optional[str] = None
    includeFilters: bool = True
    
    # Summary section
    includeSummary: bool = True
    summaryCards: List[str] = ["total", "active", "pending", "stock"]  # total, active, pending, stock
    
    # Charts section
    includeCharts: bool = True
    selectedCharts: List[str] = ["category", "status"]  # category, status, trends, warranty
    
    # Table section
    includeTable: bool = True
    tableColumns: List[str] = ["asset_name", "category", "manufacturer", "status"]
    tableFilters: Optional[TableFilters] = None
    
    # Formatting options
    pageSize: str = "A4"  # A4, Letter
    orientation: str = "portrait"  # portrait, landscape
    includeTimestamp: bool = True


class ExportResponse(BaseModel):
    """Response from export API."""
    success: bool
    message: str
    file_size_bytes: Optional[int] = None
    export_id: Optional[int] = None
