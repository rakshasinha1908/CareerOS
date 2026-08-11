from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate


URL_FIELDS = {
    "linkedin_url",
    "github_url",
    "portfolio_url",
}


def _serialize_profile_data(data) -> dict:
    values = data.model_dump(exclude_unset=True)

    for field in URL_FIELDS:
        if field in values and values[field] is not None:
            values[field] = str(values[field])

    return values


def get_profile(
    db: Session,
    user: User,
) -> Profile | None:
    return db.scalar(
        select(Profile).where(Profile.user_id == user.id)
    )


def create_profile(
    db: Session,
    user: User,
    data: ProfileCreate,
) -> Profile:
    profile = Profile(
        user_id=user.id,
        **_serialize_profile_data(data),
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


def update_profile(
    db: Session,
    profile: Profile,
    data: ProfileUpdate,
) -> Profile:
    updates = _serialize_profile_data(data)

    for field, value in updates.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile