from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobPreferences(Base):
    __tablename__ = "job_preferences"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    preferred_roles: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    preferred_locations: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    remote_preference: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    employment_types: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    experience_level: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    required_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    preferred_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    excluded_keywords: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    min_salary: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    max_salary: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
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

    user = relationship(
        "User",
        back_populates="job_preferences",
    )