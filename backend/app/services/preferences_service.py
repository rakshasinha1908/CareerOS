from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_preferences import JobPreferences
from app.models.user import User
from app.schemas.preferences import (
    JobPreferencesCreate,
    JobPreferencesUpdate,
)


def get_preferences(
    db: Session,
    user: User,
) -> JobPreferences | None:
    return db.scalar(
        select(JobPreferences).where(
            JobPreferences.user_id == user.id
        )
    )


def create_preferences(
    db: Session,
    user: User,
    data: JobPreferencesCreate,
) -> JobPreferences:
    preferences = JobPreferences(
        user_id=user.id,
        **data.model_dump(),
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


def update_preferences(
    db: Session,
    preferences: JobPreferences,
    data: JobPreferencesUpdate,
) -> JobPreferences:
    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)

    return preferences