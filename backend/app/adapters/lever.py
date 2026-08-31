from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from app.adapters.base import BaseAdapter, RawJob


REQUEST_TIMEOUT = 20


class LeverAdapter(BaseAdapter):
    """
    Reusable adapter for public Lever job boards.

    One adapter handles multiple companies.

    Company-specific information is supplied through:
        company_config["adapter_config"]["board_token"]

    Example:
        https://jobs.lever.co/meesho
        -> board_token = "meesho"

        https://jobs.lever.co/cred
        -> board_token = "cred"
    """

    name = "lever"

    def can_handle(
        self,
        company_config: dict[str, Any],
    ) -> bool:
        return (
            company_config.get("platform", "").lower()
            == "lever"
        )

    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        adapter_config = company_config.get("adapter_config") or {}

        board_token = adapter_config.get("board_token")

        if not board_token:
            # Backwards compatibility with the older
            # flat configuration style.
            board_token = company_config.get("board_token")

        if not board_token:
            raise ValueError(
                "Lever company configuration "
                "requires 'board_token'"
            )

        url = (
            "https://api.lever.co/v0/postings/"
            f"{board_token}"
        )

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            params={
                "mode": "json",
            },
            headers={
                "User-Agent": (
                    "CareerOS/1.0 "
                    "(job aggregation)"
                ),
                "Accept": "application/json",
            },
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, list):
            raise ValueError("Unexpected Lever API response")

        return [
            self._normalize_job(job, company_config)
            for job in payload
            if isinstance(job, dict)
        ]

    def _normalize_job(
        self,
        job: dict[str, Any],
        company_config: dict[str, Any],
    ) -> RawJob:
        title = (job.get("text") or "").strip()

        hosted_url = (
            job.get("hostedUrl")
            or job.get("applyUrl")
            or ""
        )

        # Some environments / responses may return URLs
        # wrapped in Markdown link syntax:
        #
        # [https://example.com](https://example.com)
        #
        # CareerOS should always persist the actual URL.
        if hosted_url.startswith("[") and "](" in hosted_url:
            hosted_url = hosted_url.split("](", 1)[1]
            hosted_url = hosted_url.rstrip(")")

        categories = job.get("categories") or {}

        location = categories.get("location") or None
        department = categories.get("department") or None
        commitment = categories.get("commitment") or None

        description = (
            job.get("descriptionPlain")
            or job.get("description")
            or None
        )

        source_job_id = job.get("id")

        created_at = self._parse_timestamp(job.get("createdAt"))

        return RawJob(
            title=title,
            job_url=hosted_url,
            location=location,
            description=description,
            employment_type=commitment,
            department=department,
            experience=None,
            posted_date=created_at,
            source=self.name,
            source_job_id=(
                str(source_job_id)
                if source_job_id is not None
                else None
            ),
            metadata={
                "company_name": company_config.get("name"),
                "lever": job,
            },
        )

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        try:
            # Lever commonly returns milliseconds
            # since Unix epoch.
            timestamp = float(value)

            if timestamp > 10_000_000_000:
                timestamp /= 1000

            return datetime.fromtimestamp(timestamp)

        except (TypeError, ValueError, OverflowError):
            return None
