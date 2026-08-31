from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from app.adapters.base import BaseAdapter, RawJob


REQUEST_TIMEOUT = 20


class GreenhouseAdapter(BaseAdapter):
    """
    Reusable adapter for Greenhouse-powered career boards.

    One adapter can handle multiple companies.
    Company-specific information is supplied through
    company_config.
    """

    name = "greenhouse"

    def can_handle(
        self,
        company_config: dict[str, Any],
    ) -> bool:
        return (
            company_config.get("platform", "").lower()
            == "greenhouse"
        )

    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        adapter_config = company_config.get("adapter_config") or {}

        board_token = adapter_config.get("board_token")

        # Temporary backwards compatibility for
        # older direct configuration.
        if not board_token:
            board_token = company_config.get("board_token")

        if not board_token:
            raise ValueError(
                "Greenhouse company configuration "
                "requires 'board_token'"
            )

        url = (
            "https://boards-api.greenhouse.io/v1/boards/"
            f"{board_token}/jobs"
        )

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            params={
                "content": "true",
            },
            headers={
                "User-Agent": (
                    "CareerOS/1.0 "
                    "(job aggregation)"
                )
            },
        )

        response.raise_for_status()

        payload = response.json()

        jobs = payload.get("jobs", [])

        return [
            self._normalize_job(
                job,
                company_config,
            )
            for job in jobs
        ]

    def _normalize_job(
        self,
        job: dict[str, Any],
        company_config: dict[str, Any],
    ) -> RawJob:
        location = self._extract_location(job.get("location"))

        departments = self._extract_departments(job.get("departments"))

        posted_date = self._parse_date(job.get("updated_at"))

        source_job_id = job.get("id")

        job_url = job.get("absolute_url") or ""

        title = (job.get("title") or "").strip()

        description = job.get("content") or None

        return RawJob(
            title=title,
            job_url=job_url,
            location=location,
            description=description,
            department=departments,
            posted_date=posted_date,
            source=self.name,
            source_job_id=(
                str(source_job_id)
                if source_job_id is not None
                else None
            ),
            metadata={
                "company_name": company_config.get("name"),
                "greenhouse": job,
            },
        )

    @staticmethod
    def _extract_location(location: Any) -> str | None:
        if not isinstance(location, dict):
            return None

        name = location.get("name")

        if not name:
            return None

        return str(name).strip() or None

    @staticmethod
    def _extract_departments(departments: Any) -> str | None:
        if not isinstance(departments, list):
            return None

        names = []

        for department in departments:
            if not isinstance(department, dict):
                continue

            name = department.get("name")

            if name:
                names.append(str(name).strip())

        if not names:
            return None

        return ", ".join(dict.fromkeys(names))

    @staticmethod
    def _parse_date(value: Any) -> datetime | None:
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        try:
            return datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )
        except ValueError:
            return None
