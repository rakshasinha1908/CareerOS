from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class ProfileBase(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    headline: str | None = None
    bio: str | None = None
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)