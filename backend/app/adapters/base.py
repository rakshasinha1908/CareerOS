from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RawJob:
    """
    Common job representation returned by every adapter.

    Adapters are responsible only for extracting data from
    their source and mapping it into this structure.
    """

    title: str
    job_url: str

    location: str | None = None
    description: str | None = None
    employment_type: str | None = None
    department: str | None = None
    experience: str | None = None
    posted_date: datetime | None = None

    source: str | None = None
    source_job_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class BaseAdapter(ABC):
    """
    Base interface for all CareerOS job-source adapters.

    One adapter should represent one reusable platform/ATS,
    not one company.
    """

    name: str = "base"

    @abstractmethod
    def can_handle(
        self,
        company_config: dict[str, Any],
    ) -> bool:
        """
        Return True when this adapter can handle the
        supplied company configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        """
        Discover jobs from the company's configured source.
        """
        raise NotImplementedError