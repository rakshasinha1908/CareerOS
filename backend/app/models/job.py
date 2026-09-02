from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        Index(
            "ix_jobs_company_source_source_job_id",
            "company_id",
            "source",
            "source_job_id",
        ),
        Index(
            "ix_jobs_company_url",
            "company_id",
            "url",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    company = relationship(
        "Company",
        lazy="joined",
    )

    @property
    def company_name(self) -> str | None:
        if self.company is None:
            return None

        return self.company.name

    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_job_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    about_the_job: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    responsibilities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    minimum_qualifications: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_qualifications: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    experience_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )