from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import requests

from app.adapters.base import BaseAdapter, RawJob


REQUEST_TIMEOUT = 20
PAGE_SIZE = 20


class WorkdayAdapter(BaseAdapter):
    """
    Reusable adapter for public Workday career sites.

    One adapter handles multiple Workday companies.

    Example Workday URL:

        https://adobe.wd5.myworkdayjobs.com/external_experienced

    From this URL we derive:

        tenant  = adobe
        cluster = wd5
        site    = external_experienced
    """

    name = "workday"

    def can_handle(
        self,
        company_config: dict[str, Any],
    ) -> bool:
        return (
            company_config.get("platform", "").lower()
            == "workday"
        )

    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        career_url = company_config.get(
            "career_url"
        )

        if not career_url:
            raise ValueError(
                "Workday company configuration "
                "requires 'career_url'"
            )

        config = self._parse_workday_url(
            career_url
        )

        jobs_url = (
            f"https://{config['tenant']}."
            f"{config['cluster']}."
            f"myworkdayjobs.com"
            f"/wday/cxs/"
            f"{config['tenant']}/"
            f"{config['site']}/jobs"
        )

        all_jobs: list[RawJob] = []

        offset = 0
        total = None

        while True:
            payload = {
                "appliedFacets": {},
                "limit": PAGE_SIZE,
                "offset": offset,
                "searchText": "",
            }

            response = requests.post(
                jobs_url,
                json=payload,
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent": (
                        "CareerOS/1.0 "
                        "(job aggregation)"
                    ),
                    "Content-Type": (
                        "application/json"
                    ),
                    "Accept": "application/json",
                },
            )

            response.raise_for_status()

            data = response.json()

            postings = data.get(
                "jobPostings",
                [],
            )

            if total is None:
                total = data.get("total")

            if not postings:
                break

            for job in postings:
                all_jobs.append(
                    self._normalize_job(
                        job,
                        company_config,
                        config,
                    )
                )

            offset += PAGE_SIZE

            if total is not None:
                if offset >= total:
                    break

        return all_jobs

    def _normalize_job(
        self,
        job: dict[str, Any],
        company_config: dict[str, Any],
        config: dict[str, str],
    ) -> RawJob:

        title = (
            job.get("title")
            or ""
        ).strip()

        external_path = (
            job.get("externalPath")
            or ""
        )

        job_url = self._build_job_url(
            config,
            external_path,
        )

        location = (
            job.get("locationsText")
            or None
        )

        posted_date = self._parse_posted_date(
            job.get("postedOn")
        )

        source_job_id = self._extract_source_job_id(
            external_path
        )

        return RawJob(
            title=title,
            job_url=job_url,
            location=location,
            description=None,
            employment_type=None,
            department=None,
            experience=None,
            posted_date=posted_date,
            source=self.name,
            source_job_id=source_job_id,
            metadata={
                "company_name": company_config.get(
                    "name"
                ),
                "workday": job,
            },
        )

    @staticmethod
    def _parse_workday_url(
        career_url: str,
    ) -> dict[str, str]:

        parsed = urlparse(
            career_url
        )

        hostname = (
            parsed.hostname
            or ""
        ).lower()

        match = re.match(
            r"^(?P<tenant>[a-z0-9-]+)"
            r"\.(?P<cluster>wd\d+)"
            r"\.myworkdayjobs\.com$",
            hostname,
        )

        if not match:
            raise ValueError(
                "Invalid Workday career URL. "
                "Expected a URL like "
                "https://adobe.wd5.myworkdayjobs.com/"
                "external_experienced"
            )

        path_parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if not path_parts:
            raise ValueError(
                "Unable to determine Workday site "
                "from career URL"
            )

        # Workday URLs may contain a locale:
        #
        # /en-US/external_experienced
        #
        # or simply:
        #
        # /external_experienced
        #
        if len(path_parts) == 1:
            site = path_parts[0]

        else:
            site = path_parts[-1]

        return {
            "tenant": match.group(
                "tenant"
            ),
            "cluster": match.group(
                "cluster"
            ),
            "site": site,
        }

    @staticmethod
    def _build_job_url(
        config: dict[str, str],
        external_path: str,
    ) -> str:

        base_url = (
            f"https://{config['tenant']}."
            f"{config['cluster']}."
            f"myworkdayjobs.com"
        )

        site = config["site"]

        external_path = (
            external_path or ""
        )

        if not external_path.startswith(
            "/"
        ):
            external_path = (
                "/" + external_path
            )

        return (
            f"{base_url}/{site}"
            f"{external_path}"
        )

    @staticmethod
    def _extract_source_job_id(
        external_path: str,
    ) -> str | None:

        if not external_path:
            return None

        # Workday external paths frequently end
        # with a requisition identifier such as:
        #
        # _R168948-1
        # _R165568
        #
        match = re.search(
            r"_([A-Za-z0-9-]+)"
            r"(?:/)?$",
            external_path,
        )

        if not match:
            return None

        return match.group(1)

    @staticmethod
    def _parse_posted_date(
        value: Any,
    ) -> datetime | None:
        """
        Workday commonly returns values such as:

            Posted Today
            Posted 2 Days Ago
            Posted 30+ Days Ago

        These are relative dates, not exact timestamps.

        For V1 we intentionally return None rather than
        pretending the date is exact.

        We preserve the original value inside metadata.
        """

        return None