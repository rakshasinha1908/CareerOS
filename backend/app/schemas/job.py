from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class JobBase(BaseModel):
    company_id: UUID
    title: str
    location: str | None = None
    url: HttpUrl
    description: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    posted_at: datetime | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company_id: UUID | None = None
    title: str | None = None
    location: str | None = None
    url: HttpUrl | None = None
    description: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    posted_at: datetime | None = None


class JobResponse(JobBase):
    id: UUID
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)