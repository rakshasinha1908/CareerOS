from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.preferences import (
    JobPreferencesCreate,
    JobPreferencesResponse,
    JobPreferencesUpdate,
)
from app.services.preferences_service import (
    create_preferences,
    get_preferences,
    update_preferences,
)


router = APIRouter(
    prefix="/api/v1/preferences",
    tags=["Preferences"],
)


@router.get(
    "",
    response_model=JobPreferencesResponse,
)
def read_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preferences = get_preferences(db, current_user)

    if preferences is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job preferences not found",
        )

    return preferences


@router.post(
    "",
    response_model=JobPreferencesResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_preferences(
    data: JobPreferencesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_preferences = get_preferences(db, current_user)

    if existing_preferences is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job preferences already exist",
        )

    return create_preferences(db, current_user, data)


@router.patch(
    "",
    response_model=JobPreferencesResponse,
)
def update_user_preferences(
    data: JobPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preferences = get_preferences(db, current_user)

    if preferences is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job preferences not found",
        )

    return update_preferences(db, preferences, data)