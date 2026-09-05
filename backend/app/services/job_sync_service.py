from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.registry import adapter_registry
from app.models.company import Company
from app.models.job import Job


def sync_company_jobs(
    db: Session,
    company: Company,
) -> dict:
    """
    Sync jobs for a company using the adapter associated
    with the company's configured platform.

    Pipeline:

        Company
            ↓
        AdapterRegistry
            ↓
        Platform Adapter
            ↓
        RawJob[]
            ↓
        Database

    Existing jobs are updated when listing-level fields change.

    The sync preloads existing jobs once instead of performing
    one database lookup per discovered job. This is important
    for companies with thousands of listings.

    Richer detail fields are preserved during listing sync so that
    a later detail-enrichment step can populate them safely.
    """

    if not company.career_url:
        raise ValueError(
            "Company does not have a career URL"
        )

    if not company.platform:
        raise ValueError(
            "Company does not have a platform configured"
        )

    if not company.is_active:
        raise ValueError(
            "Company is inactive"
        )

    company_config = {
        "name": company.name,
        "career_url": str(company.career_url),
        "platform": company.platform,
        "adapter_config": (
            company.adapter_config or {}
        ),
    }

    try:
        # ---------------------------------------------------------
        # Discover jobs through the platform adapter
        # ---------------------------------------------------------

        discovered_jobs = (
            adapter_registry.discover_jobs(
                company_config
            )
        )

        created_jobs: list[Job] = []
        created_count = 0
        updated_count = 0
        skipped_count = 0

        # ---------------------------------------------------------
        # Preload all existing jobs for this company ONCE.
        #
        # The old implementation queried the database separately
        # for every discovered job. That becomes extremely slow
        # for companies such as Microsoft with 2000+ jobs.
        # ---------------------------------------------------------

        existing_jobs = db.scalars(
            select(Job).where(
                Job.company_id == company.id
            )
        ).all()

        existing_by_url: dict[str, Job] = {
            str(job.url): job
            for job in existing_jobs
            if job.url
        }

        # ---------------------------------------------------------
        # Persist discovered jobs
        # ---------------------------------------------------------

        for discovered in discovered_jobs:
            if not discovered.job_url:
                skipped_count += 1
                continue

            job_url = str(discovered.job_url)

            existing_job = existing_by_url.get(
                job_url
            )

            if existing_job is None:
                job = Job(
                    company_id=company.id,
                    title=discovered.title,
                    location=discovered.location,
                    url=job_url,

                    # Source identity
                    source=discovered.source,
                    source_job_id=discovered.source_job_id,

                    description=discovered.description,
                    employment_type=(
                        discovered.employment_type
                    ),
                    experience_level=(
                        discovered.experience
                    ),
                    posted_at=(
                        discovered.posted_date
                    ),
                    discovered_at=datetime.now(
                        timezone.utc
                    ),
                )

                db.add(job)

                # Add it to the lookup immediately so that
                # duplicate URLs in the same discovery response
                # cannot create duplicate Job records.
                existing_by_url[job_url] = job

                created_jobs.append(job)
                created_count += 1

                continue

            # -----------------------------------------------------
            # Existing job
            #
            # Update fields supplied by the source.
            # Do NOT overwrite existing values with None.
            #
            # Rich detail fields are preserved if the listing
            # response does not provide them.
            # -----------------------------------------------------

            changed = False

            if (
                discovered.source is not None
                and existing_job.source
                != discovered.source
            ):
                existing_job.source = (
                    discovered.source
                )
                changed = True

            if (
                discovered.source_job_id is not None
                and existing_job.source_job_id
                != discovered.source_job_id
            ):
                existing_job.source_job_id = (
                    discovered.source_job_id
                )
                changed = True

            if (
                discovered.title
                and existing_job.title
                != discovered.title
            ):
                existing_job.title = (
                    discovered.title
                )
                changed = True

            if (
                discovered.location is not None
                and existing_job.location
                != discovered.location
            ):
                existing_job.location = (
                    discovered.location
                )
                changed = True

            if (
                discovered.description is not None
                and existing_job.description
                != discovered.description
            ):
                existing_job.description = (
                    discovered.description
                )
                changed = True

            if (
                discovered.employment_type is not None
                and existing_job.employment_type
                != discovered.employment_type
            ):
                existing_job.employment_type = (
                    discovered.employment_type
                )
                changed = True

            if (
                discovered.experience is not None
                and existing_job.experience_level
                != discovered.experience
            ):
                existing_job.experience_level = (
                    discovered.experience
                )
                changed = True

            if (
                discovered.posted_date is not None
                and existing_job.posted_at
                != discovered.posted_date
            ):
                existing_job.posted_at = (
                    discovered.posted_date
                )
                changed = True

            if changed:
                updated_count += 1
            else:
                skipped_count += 1

        # ---------------------------------------------------------
        # Update company's scrape timestamp
        # ---------------------------------------------------------

        company.last_scraped_at = datetime.now(
            timezone.utc
        )

        # ---------------------------------------------------------
        # Single transaction commit
        # ---------------------------------------------------------

        db.commit()

        # ---------------------------------------------------------
        # Refresh created records
        # ---------------------------------------------------------

        for job in created_jobs:
            db.refresh(job)

        db.refresh(company)

        return {
            "company": company.name,
            "platform": company.platform,
            "discovered": len(discovered_jobs),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "last_scraped_at": (
                company.last_scraped_at
            ),
        }

    except Exception:
        db.rollback()
        raise