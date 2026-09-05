from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

from app.adapters.base import BaseAdapter, RawJob


class MicrosoftAdapter(BaseAdapter):
    """
    Adapter for Microsoft's public Careers jobs endpoint.

    Microsoft Careers is powered by Eightfold PCS-X.

    Discovery endpoint:
        https://apply.careers.microsoft.com/api/pcsx/search

    The adapter is responsible only for discovering and
    normalizing Microsoft job listings.

    Database persistence is handled by job_sync_service.py.
    """

    name = "microsoft"

    BASE_URL = (
        "https://apply.careers.microsoft.com"
    )

    SEARCH_URL = (
        f"{BASE_URL}/api/pcsx/search"
    )

    # Microsoft's API currently returns 10 positions
    # per request.
    PAGE_SIZE = 10

    REQUEST_TIMEOUT = 20

    # Retry configuration for HTTP 429 responses.
    MAX_RETRIES = 5
    BACKOFF_SECONDS = 3

    # Small delay between successful pagination requests.
    # We rely primarily on Microsoft's rate limiting rather
    # than intentionally sleeping several seconds per page.
    PAGE_DELAY_SECONDS = 0.25

    def can_handle(
        self,
        company_config: dict[str, Any],
    ) -> bool:
        platform = str(
            company_config.get("platform") or ""
        ).strip().lower()

        return platform == self.name

    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        """
        Discover Microsoft jobs using the PCS-X search endpoint.
        """

        if not self.can_handle(company_config):
            raise ValueError(
                "MicrosoftAdapter cannot handle "
                "the supplied company configuration"
            )

        jobs: list[RawJob] = []

        start = 0
        total_count: int | None = None
        page_number = 0

        session = requests.Session()

        session.headers.update(
            {
                "User-Agent": (
                    "CareerOS/1.0 "
                    "(job discovery)"
                ),
                "Accept": "application/json",
            }
        )

        try:
            while True:
                page_number += 1

                payload = self._search(
                    session=session,
                    start=start,
                )

                data = payload.get("data")

                if not isinstance(data, dict):
                    raise ValueError(
                        "Microsoft Careers API returned "
                        "an unexpected data structure"
                    )

                positions = data.get("positions")

                if not isinstance(
                    positions,
                    list,
                ):
                    raise ValueError(
                        "Microsoft Careers API returned "
                        "an unexpected positions structure"
                    )

                # --------------------------------------------------
                # Get total result count when available.
                # --------------------------------------------------

                if total_count is None:
                    raw_count = data.get("count")

                    if raw_count is not None:
                        try:
                            total_count = int(raw_count)
                        except (
                            TypeError,
                            ValueError,
                        ):
                            total_count = None

                # --------------------------------------------------
                # No positions means we're done.
                # --------------------------------------------------

                if not positions:
                    break

                # --------------------------------------------------
                # Normalize positions.
                # --------------------------------------------------

                for position in positions:
                    if not isinstance(
                        position,
                        dict,
                    ):
                        continue

                    job = self._normalize_position(
                        position
                    )

                    if job is not None:
                        jobs.append(job)

                # --------------------------------------------------
                # Advance by the number actually returned.
                # --------------------------------------------------

                start += len(positions)

                # --------------------------------------------------
                # Progress output.
                # --------------------------------------------------

                if total_count is not None:
                    print(
                        "Microsoft discovery: "
                        f"{start}/{total_count} jobs "
                        f"(page {page_number})"
                    )
                else:
                    print(
                        "Microsoft discovery: "
                        f"{start} jobs "
                        f"(page {page_number})"
                    )

                # --------------------------------------------------
                # Stop when we've reached Microsoft's total.
                # --------------------------------------------------

                if (
                    total_count is not None
                    and start >= total_count
                ):
                    break

                # --------------------------------------------------
                # If count is unavailable and we received fewer
                # jobs than the expected page size, this is the
                # final page.
                # --------------------------------------------------

                if (
                    total_count is None
                    and len(positions) < self.PAGE_SIZE
                ):
                    break

                # --------------------------------------------------
                # Small delay between successful requests.
                # --------------------------------------------------

                if self.PAGE_DELAY_SECONDS > 0:
                    time.sleep(
                        self.PAGE_DELAY_SECONDS
                    )

        finally:
            session.close()

        result = self._deduplicate_jobs(jobs)

        print(
            "Microsoft discovery complete: "
            f"{len(result)} unique jobs"
        )

        return result

    # --------------------------------------------------
    # API
    # --------------------------------------------------

    def _search(
        self,
        session: requests.Session,
        start: int,
    ) -> dict[str, Any]:
        """
        Fetch one page from Microsoft's PCS-X endpoint.

        Handles HTTP 429 using Retry-After when supplied,
        with exponential backoff as a fallback.
        """

        for attempt in range(
            self.MAX_RETRIES + 1
        ):
            response = session.get(
                self.SEARCH_URL,
                params={
                    "domain": "microsoft.com",
                    "query": "",
                    "location": "",
                    "start": start,
                    "sort_by": "timestamp",
                },
                timeout=self.REQUEST_TIMEOUT,
            )

            # --------------------------------------------------
            # Successful / non-429 response
            # --------------------------------------------------

            if response.status_code != 429:
                response.raise_for_status()

                payload = response.json()

                if not isinstance(
                    payload,
                    dict,
                ):
                    raise ValueError(
                        "Microsoft Careers API returned "
                        "a non-object JSON response"
                    )

                return payload

            # --------------------------------------------------
            # Rate limited
            # --------------------------------------------------

            if attempt >= self.MAX_RETRIES:
                response.raise_for_status()

            retry_after = response.headers.get(
                "Retry-After"
            )

            if retry_after:
                try:
                    wait_seconds = float(
                        retry_after
                    )
                except ValueError:
                    wait_seconds = (
                        self.BACKOFF_SECONDS
                        * (2 ** attempt)
                    )
            else:
                wait_seconds = (
                    self.BACKOFF_SECONDS
                    * (2 ** attempt)
                )

            # Never wait indefinitely because of a
            # malformed/server-provided Retry-After value.
            wait_seconds = min(
                wait_seconds,
                60,
            )

            print(
                "Microsoft Careers API rate-limited "
                f"request start={start}. "
                f"Retrying in {wait_seconds:.1f}s "
                f"(attempt {attempt + 1}/"
                f"{self.MAX_RETRIES})..."
            )

            time.sleep(
                wait_seconds
            )

        raise RuntimeError(
            "Microsoft Careers API request failed"
        )

    # --------------------------------------------------
    # Normalization
    # --------------------------------------------------

    def _normalize_position(
        self,
        position: dict[str, Any],
    ) -> RawJob | None:
        """
        Convert one Microsoft position into RawJob.
        """

        position_id = position.get("id")

        title = self._clean_text(
            position.get("name")
        )

        if not position_id or not title:
            return None

        # --------------------------------------------------
        # URL
        # --------------------------------------------------

        position_url = self._clean_text(
            position.get("positionUrl")
        )

        if position_url:
            if position_url.startswith("http"):
                job_url = position_url
            else:
                job_url = (
                    f"{self.BASE_URL}"
                    f"{position_url}"
                )
        else:
            job_url = (
                f"{self.BASE_URL}"
                f"/careers/job/{position_id}"
            )

        # --------------------------------------------------
        # Location
        # --------------------------------------------------

        location = self._normalize_locations(
            position.get("locations")
        )

        # --------------------------------------------------
        # Posted date
        # --------------------------------------------------

        posted_date = (
            self._timestamp_to_datetime(
                position.get("postedTs")
            )
        )

        # --------------------------------------------------
        # Employment type
        # --------------------------------------------------

        employment_type = self._clean_text(
            position.get("employmentType")
        )

        # --------------------------------------------------
        # Experience
        #
        # Search results do not currently provide a
        # reliable experience-level field.
        # Detail enrichment can populate this later.
        # --------------------------------------------------

        experience = None

        return RawJob(
            title=title,
            job_url=job_url,
            location=location,
            description=None,
            employment_type=employment_type,
            experience=experience,
            posted_date=posted_date,
            source=self.name,
            source_job_id=str(position_id),
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        return text or None

    @classmethod
    def _normalize_locations(
        cls,
        locations: Any,
    ) -> str | None:
        if not locations:
            return None

        if isinstance(locations, str):
            return cls._clean_text(locations)

        if not isinstance(locations, list):
            return cls._clean_text(locations)

        cleaned: list[str] = []

        for location in locations:
            text = cls._clean_text(location)

            if text:
                cleaned.append(text)

        if not cleaned:
            return None

        return "; ".join(cleaned)

    @staticmethod
    def _timestamp_to_datetime(
        timestamp: Any,
    ) -> datetime | None:
        if timestamp is None:
            return None

        try:
            value = float(timestamp)

            # Support both epoch seconds and
            # epoch milliseconds.
            if value > 10_000_000_000:
                value /= 1000

            return datetime.fromtimestamp(
                value,
                tz=timezone.utc,
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return None

    @staticmethod
    def _deduplicate_jobs(
        jobs: list[RawJob],
    ) -> list[RawJob]:
        seen_ids: set[str] = set()
        seen_urls: set[str] = set()

        result: list[RawJob] = []

        for job in jobs:
            source_job_id = (
                str(job.source_job_id)
                if job.source_job_id
                else None
            )

            normalized_url = (
                job.job_url.rstrip("/")
            )

            if (
                source_job_id
                and source_job_id in seen_ids
            ):
                continue

            if normalized_url in seen_urls:
                continue

            if source_job_id:
                seen_ids.add(source_job_id)

            seen_urls.add(normalized_url)

            result.append(job)

        return result