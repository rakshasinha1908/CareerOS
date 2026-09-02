from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import requests

from app.adapters.base import BaseAdapter, RawJob


REQUEST_TIMEOUT = 20
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_PAGES = 500


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
            company_config.get("platform", "").strip().lower()
            == "workday"
        )

    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        career_url = company_config.get("career_url")

        if not career_url:
            raise ValueError(
                "Workday company configuration "
                "requires 'career_url'"
            )

        config = self._parse_workday_url(career_url)

        adapter_config = (
            company_config.get("adapter_config")
            or {}
        )

        page_size = self._get_page_size(
            adapter_config
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
        total: int | None = None
        page_number = 0

        while True:
            page_number += 1

            if page_number > MAX_PAGES:
                raise RuntimeError(
                    "Workday pagination exceeded the safety "
                    f"limit of {MAX_PAGES} pages for "
                    f"{company_config.get('name') or 'company'}"
                )

            payload = {
                "appliedFacets": {},
                "limit": page_size,
                "offset": offset,
                "searchText": "",
            }

            response = self._request_jobs(
                jobs_url=jobs_url,
                payload=payload,
                company_config=company_config,
            )

            data = self._parse_response(
                response,
                company_config,
            )

            postings = data.get("jobPostings")

            if postings is None:
                raise RuntimeError(
                    "Workday response did not contain "
                    "'jobPostings' for "
                    f"{company_config.get('name') or 'company'}"
                )

            if not isinstance(postings, list):
                raise RuntimeError(
                    "Workday response contains an invalid "
                    "'jobPostings' value for "
                    f"{company_config.get('name') or 'company'}"
                )

            if total is None:
                total = self._parse_total(
                    data.get("total")
                )

            if not postings:
                break

            for job in postings:
                if not isinstance(job, dict):
                    continue

                all_jobs.append(
                    self._normalize_job(
                        job,
                        company_config,
                        config,
                    )
                )

            returned_count = len(postings)

            # Advance by the number actually returned rather
            # than assuming Workday honored the requested page size.
            offset += returned_count

            # If Workday tells us the total, stop once we've
            # reached it.
            if total is not None and offset >= total:
                break

            # A short page with no known total is the safest
            # indication that there are no more results.
            if total is None and returned_count < page_size:
                break

            # Workday public search endpoints can expose a
            # maximum result window. If we hit exactly 2,000
            # records and Workday still claims more exist,
            # do NOT silently report the result as complete.
            if (
                total is not None
                and total > offset
                and offset >= 2000
            ):
                raise RuntimeError(
                    "Workday returned only the first 2,000 "
                    "results while reporting more available "
                    f"jobs for "
                    f"{company_config.get('name') or 'company'}. "
                    "The search likely requires partitioning "
                    "or additional Workday facets."
                )

        return all_jobs

    @staticmethod
    def _get_page_size(
        adapter_config: dict[str, Any],
    ) -> int:
        value = adapter_config.get(
            "page_size",
            DEFAULT_PAGE_SIZE,
        )

        try:
            page_size = int(value)
        except (TypeError, ValueError):
            page_size = DEFAULT_PAGE_SIZE

        return max(
            1,
            min(page_size, MAX_PAGE_SIZE),
        )

    @staticmethod
    def _request_jobs(
        jobs_url: str,
        payload: dict[str, Any],
        company_config: dict[str, Any],
    ) -> requests.Response:
        try:
            response = requests.post(
                jobs_url,
                json=payload,
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent": (
                        "CareerOS/1.0 "
                        "(job aggregation)"
                    ),
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                "Unable to connect to Workday career "
                f"endpoint for "
                f"{company_config.get('name') or 'company'}: "
                f"{exc}"
            ) from exc

        if response.ok:
            return response

        company_name = (
            company_config.get("name")
            or "company"
        )

        status_code = response.status_code

        if status_code == 401:
            raise RuntimeError(
                f"Workday rejected the request with HTTP 401 "
                f"(Unauthorized) for {company_name}. "
                "The public jobs endpoint may require a "
                "different configuration or access pattern."
            )

        if status_code == 403:
            raise RuntimeError(
                f"Workday rejected the request with HTTP 403 "
                f"(Forbidden) for {company_name}. "
                "The career site may be blocking automated "
                "requests."
            )

        if status_code == 404:
            raise RuntimeError(
                f"Workday returned HTTP 404 (Not Found) for "
                f"{company_name}. Verify the Workday tenant, "
                "cluster, and career-site path."
            )

        if status_code == 422:
            detail = WorkdayAdapter._response_detail(
                response
            )

            raise RuntimeError(
                f"Workday returned HTTP 422 "
                f"(Unprocessable Entity) for "
                f"{company_name}. "
                f"{detail}"
            )

        detail = WorkdayAdapter._response_detail(
            response
        )

        raise RuntimeError(
            f"Workday returned HTTP {status_code} for "
            f"{company_name}. {detail}"
        )

    @staticmethod
    def _parse_response(
        response: requests.Response,
        company_config: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Workday returned a non-JSON response for "
                f"{company_config.get('name') or 'company'}"
            ) from exc

        if not isinstance(data, dict):
            raise RuntimeError(
                "Workday returned an unexpected response "
                f"format for "
                f"{company_config.get('name') or 'company'}"
            )

        return data

    @staticmethod
    def _response_detail(
        response: requests.Response,
    ) -> str:
        try:
            data = response.json()

            if isinstance(data, dict):
                for key in (
                    "error",
                    "message",
                    "errorMessage",
                    "detail",
                ):
                    value = data.get(key)

                    if value:
                        return str(value)

                return str(data)

        except ValueError:
            pass

        text = (response.text or "").strip()

        if text:
            return text[:500]

        return "No additional error details were provided."

    @staticmethod
    def _parse_total(
        value: Any,
    ) -> int | None:
        if value is None:
            return None

        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None

        if parsed < 0:
            return None

        return parsed

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

        source_job_id = (
            self._extract_source_job_id(
                external_path
            )
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
        parsed = urlparse(career_url)

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
        site = path_parts[-1]

        return {
            "tenant": match.group("tenant"),
            "cluster": match.group("cluster"),
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

        if not external_path.startswith("/"):
            external_path = "/" + external_path

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

        match = re.search(
            r"_([A-Za-z0-9-]+)(?:/)?$",
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

        The original value remains available in the raw
        Workday metadata.
        """

        return None