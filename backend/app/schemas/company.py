from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class CompanyBase(BaseModel):
    name: str
    website: HttpUrl | None = None
    industry: str | None = None
    size: str | None = None
    headquarters: str | None = None
    notes: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    website: HttpUrl | None = None
    industry: str | None = None
    size: str | None = None
    headquarters: str | None = None
    notes: str | None = None


class CompanyResponse(CompanyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)