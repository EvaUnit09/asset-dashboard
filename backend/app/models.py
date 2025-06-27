from typing import Optional
from sqlmodel import SQLModel, Field, Date
from sqlalchemy import Column, String, Integer
from datetime import date


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
    status: str | None = Field(default=None, nullable=True)
    created_at: str | None = Field(default=None, nullable=True)
