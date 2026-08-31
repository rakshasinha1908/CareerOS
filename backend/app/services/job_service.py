from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate



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


