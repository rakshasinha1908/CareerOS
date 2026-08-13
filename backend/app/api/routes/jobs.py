from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobUpdate,
)
from app.services.job_service import (
    create_job,
    delete_job,
    get_job,
    get_jobs,
    update_job,
)


router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["Jobs"],
)


@router.get(
    "",
    response_model=list[JobResponse],
)
def list_jobs(
    db: Session = Depends(get_db),
):
    return get_jobs(db)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def read_job(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    job = get_job(db, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_job(
    data: JobCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_job(db, data)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create job",
        )


@router.patch(
    "/{job_id}",
    response_model=JobResponse,
)
def update_existing_job(
    job_id: UUID,
    data: JobUpdate,
    db: Session = Depends(get_db),
):
    job = get_job(db, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    try:
        return update_job(db, job, data)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update job",
        )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_job(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    job = get_job(db, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    delete_job(db, job)