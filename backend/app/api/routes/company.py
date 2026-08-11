from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.company import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
)
from app.services.company_service import (
    create_company,
    delete_company,
    get_companies,
    get_company,
    update_company,
)


router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Companies"],
)


@router.get(
    "",
    response_model=list[CompanyResponse],
)
def list_companies(
    db: Session = Depends(get_db),
):
    return get_companies(db)


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
def read_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    company = get_company(db, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_company(db, data)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this name already exists",
        )


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
)
def update_existing_company(
    company_id: UUID,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
):
    company = get_company(db, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    try:
        return update_company(db, company, data)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this name already exists",
        )


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    company = get_company(db, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    delete_company(db, company)