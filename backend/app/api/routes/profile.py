from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile_service import (
    create_profile,
    get_profile,
    update_profile,
)


router = APIRouter(
    prefix="/api/v1/profile",
    tags=["Profile"],
)


@router.get(
    "",
    response_model=ProfileResponse,
)
def read_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_profile(db, current_user)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return profile


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_profile(
    data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_profile = get_profile(db, current_user)

    if existing_profile is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists",
        )

    return create_profile(db, current_user, data)


@router.patch(
    "",
    response_model=ProfileResponse,
)
def update_user_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_profile(db, current_user)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return update_profile(db, profile, data)