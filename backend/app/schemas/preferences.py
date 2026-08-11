from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobPreferencesBase(BaseModel):
    preferred_roles: list[str] = []
    preferred_locations: list[str] = []
    remote_preference: str | None = None
    employment_types: list[str] = []
    experience_level: str | None = None
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    excluded_keywords: list[str] = []
    min_salary: int | None = None
    max_salary: int | None = None


class JobPreferencesCreate(JobPreferencesBase):
    pass


class JobPreferencesUpdate(BaseModel):
    preferred_roles: list[str] | None = None
    preferred_locations: list[str] | None = None
    remote_preference: str | None = None
    employment_types: list[str] | None = None
    experience_level: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    excluded_keywords: list[str] | None = None
    min_salary: int | None = None
    max_salary: int | None = None


class JobPreferencesResponse(JobPreferencesBase):
    id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)