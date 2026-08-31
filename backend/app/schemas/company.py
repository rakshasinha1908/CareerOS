from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class CompanyBase(BaseModel):
    name: str
    career_url: HttpUrl
    platform: str | None = None
    adapter_config: dict[str, Any] | None = None
    is_active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    career_url: HttpUrl | None = None
    platform: str | None = None
    adapter_config: dict[str, Any] | None = None
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    id: UUID
    last_scraped_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)