from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from app.services.career_service import discover_jobs
from app.services.job_details_service import (
    fetch_job_details,
)


def _serialize_job_data(data) -> dict:
    values = data.model_dump(exclude_unset=True)

    if "url" in values and values["url"] is not None:
        values["url"] = str(values["url"])

    return values


def get_jobs(
    db: Session,
) -> list[Job]:
    return list(
        db.scalars(
            select(Job).order_by(Job.created_at.desc())
        ).all()
    )


def get_job(
    db: Session,
    job_id: UUID,
) -> Job | None:
    return db.scalar(
        select(Job).where(Job.id == job_id)
    )


def create_job(
    db: Session,
    data: JobCreate,
) -> Job:
    job = Job(
        **_serialize_job_data(data)
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def update_job(
    db: Session,
    job: Job,
    data: JobUpdate,
) -> Job:
    updates = _serialize_job_data(data)

    for field, value in updates.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job


def delete_job(
    db: Session,
    job: Job,
) -> None:
    db.delete(job)
    db.commit()


def sync_company_jobs(
    db: Session,
    company: Company,
) -> dict:
    """
    Discover jobs from a company's career page and
    persist new jobs with available job details.

    V1 intentionally keeps this simple:
    - discover jobs
    - avoid duplicate URLs
    - extract details for new jobs
    - create new Job records
    - skip already-known jobs
    """

    if not company.career_url:
        raise ValueError(
            "Company does not have a career URL"
        )

    discovered_jobs = discover_jobs(
        company.career_url
    )

    created_jobs: list[Job] = []
    skipped_jobs = 0

    for discovered in discovered_jobs:

        existing_job = db.scalar(
            select(Job).where(
                Job.company_id == company.id,
                Job.url == discovered.url,
            )
        )

        if existing_job is not None:
            skipped_jobs += 1
            continue

        # -------------------------------------------------
        # Extract details from the individual job page
        # Make sync resilient to broken job pages
        # -------------------------------------------------
        try:
            details = fetch_job_details(
                discovered.url
            )

            print()
            print("DETAILS:", discovered.title)
            print("  location:", details.location)
            print("  experience:", details.experience_level)
            print("  description:", bool(details.description))

        except Exception as exc:
            print()
            print("DETAIL FETCH FAILED:", discovered.url)
            print("ERROR:", repr(exc))

            details = None

        job = Job(
            company_id=company.id,
            title=(
                details.title
                if details and details.title
                else discovered.title
            ),
            location=(
                details.location
                if details
                else None
            ),
            url=discovered.url,
            description=(
                details.description
                if details
                else None
            ),
            about_the_job=(
                details.about_the_job
                if details
                else None
            ),
            responsibilities=(
                details.responsibilities
                if details
                else None
            ),
            minimum_qualifications=(
                details.minimum_qualifications
                if details
                else None
            ),
            preferred_qualifications=(
                details.preferred_qualifications
                if details
                else None
            ),
            experience_level=(
                details.experience_level
                if details
                else None
            ),
            discovered_at=datetime.now(
                timezone.utc
            ),
        )

        db.add(job)
        created_jobs.append(job)

    db.commit()

    for job in created_jobs:
        db.refresh(job)

    return {
        "discovered": len(discovered_jobs),
        "created": len(created_jobs),
        "skipped": skipped_jobs,
    }
