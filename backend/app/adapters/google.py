from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Any

import requests

from app.adapters.base import BaseAdapter, RawJob


REQUEST_TIMEOUT = 20
GOOGLE_JOBS_URL = (
    "https://www.google.com/about/careers/applications/jobs/results"
)


class GoogleAdapter(BaseAdapter):
    """
    Adapter for Google's public Careers jobs page.

    Google currently embeds job data inside the HTML response
    using Google's AF_initDataCallback / ds:1 payload.

    The rendered page itself is JavaScript-driven, so we do not
    rely on normal <a href="/jobs/results/..."> links.
    """

    name = "google"

    def can_handle(
        self,
        company_config: dict[str, Any],
    ) -> bool:
        return (
            company_config.get("platform", "")
            .strip()
            .lower()
            == "google"
        )

    def discover_jobs(
        self,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        career_url = company_config.get("career_url")

        if not career_url:
            raise ValueError(
                "Google company configuration "
                "requires 'career_url'"
            )

        response = requests.get(
            GOOGLE_JOBS_URL,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/139.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

        response.raise_for_status()

        return self._extract_jobs_from_response(
            response,
            company_config,
        )

    def _extract_jobs_from_response(
        self,
        response: requests.Response,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        """
        Extract Google jobs from the embedded ds:1 payload.

        Example data observed in Google's response:

            AF_initDataCallback({
                key: 'ds:1',
                ...
                data: [[[
                    [
                        "107697501686899398",
                        "Data Scientist III, Product",
                        "https://www.google.com/about/careers/applications/signin?jobId=...",
                        [...]
                    ]
                ]]]
            })

        We intentionally parse the individual job records rather
        than attempting to parse the entire Google RPC structure.
        """

        response_text = response.text

        marker = "key: 'ds:1'"

        marker_index = response_text.find(marker)

        if marker_index == -1:
            marker = 'key: "ds:1"'
            marker_index = response_text.find(marker)

        if marker_index == -1:
            raise RuntimeError(
                "Unable to locate Google's ds:1 "
                "job data in the careers response"
            )

        # The ds:1 callback contains escaped Unicode sequences
        # such as:
        #
        #   \u003d
        #   \u0026
        #   \u003c
        #
        # Decode those before extracting records.
        data_section = response_text[marker_index:]

        data_section = (
            data_section
            .replace("\\u003d", "=")
            .replace("\\u0026", "&")
            .replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\/", "/")
        )

        jobs = self._extract_job_records(
            data_section,
            company_config,
        )

        if not jobs:
            raise RuntimeError(
                "Google's ds:1 payload was found, "
                "but no job records could be extracted"
            )

        return self._deduplicate_jobs(jobs)

    def _extract_job_records(
        self,
        data: str,
        company_config: dict[str, Any],
    ) -> list[RawJob]:
        """
        Extract job records from Google's ds:1 payload.

        We look for the stable sequence:

            "numeric internal id",
            "job title",
            "signin?...jobId=...",
            [description...]

        This avoids depending on the full internal RPC schema.
        """

        jobs: list[RawJob] = []

        pattern = re.compile(
            r'\[\s*'
            r'"(?P<internal_id>\d+)"\s*,'
            r'\s*"(?P<title>(?:\\.|[^"\\])*)"\s*,'
            r'\s*"(?P<url>https://www\.google\.com/about/careers/applications/signin\?jobId=[^"]+)"'
            r'\s*,'
            r'\s*\[null,'
            r'\s*"(?P<description>(?:\\.|[^"\\])*)"',
            re.DOTALL,
        )

        for match in pattern.finditer(data):
            internal_id = match.group("internal_id")
            title = self._decode_js_string(
                match.group("title")
            )
            raw_url = self._decode_js_string(
                match.group("url")
            )
            description = self._decode_js_string(
                match.group("description")
            )

            if not title or not raw_url:
                continue

            job_id = self._extract_job_id_from_signin_url(
                raw_url
            )

            if not job_id:
                continue

            job_url = self._build_job_url(
                job_id=job_id,
                raw_url=raw_url,
            )

            location = self._extract_query_value(
                raw_url,
                "loc",
            )

            jobs.append(
                RawJob(
                    title=title,
                    job_url=job_url,
                    location=location,
                    description=self._clean_html(
                        description
                    ),
                    employment_type=None,
                    department=None,
                    experience=None,
                    posted_date=None,
                    source=self.name,
                    source_job_id=job_id,
                    metadata={
                        "company_name": (
                            company_config.get("name")
                        ),
                        "google_internal_id": internal_id,
                        "signin_url": raw_url,
                    },
                )
            )

        return jobs

    @staticmethod
    def _decode_js_string(value: str) -> str:
        """
        Decode common JavaScript/HTML escaping used by Google's
        embedded response.
        """

        value = value.replace(
            "\\u003d",
            "=",
        )
        value = value.replace(
            "\\u0026",
            "&",
        )
        value = value.replace(
            "\\u003c",
            "<",
        )
        value = value.replace(
            "\\u003e",
            ">",
        )
        value = value.replace(
            "\\/",
            "/",
        )

        try:
            value = bytes(
                value,
                "utf-8",
            ).decode(
                "unicode_escape"
            )
        except UnicodeDecodeError:
            pass

        return html.unescape(value).strip()

    @staticmethod
    def _extract_job_id_from_signin_url(
        url: str,
    ) -> str | None:
        match = re.search(
            r"[?&]jobId=([^&]+)",
            url,
        )

        if not match:
            return None

        return match.group(1)

    @staticmethod
    def _build_job_url(
        job_id: str,
        raw_url: str,
    ) -> str:
        """
        Google currently exposes a signin URL containing the jobId.

        Keep that URL as the canonical source URL because Google's
        internal job identifier is opaque and Google may change
        the public slug format.
        """

        return raw_url

    @staticmethod
    def _extract_query_value(
        url: str,
        key: str,
    ) -> str | None:
        match = re.search(
            rf"[?&]{re.escape(key)}=([^&]+)",
            url,
        )

        if not match:
            return None

        return match.group(1)

    @staticmethod
    def _clean_html(
        value: str,
    ) -> str | None:
        if not value:
            return None

        value = re.sub(
            r"<br\s*/?>",
            "\n",
            value,
            flags=re.IGNORECASE,
        )

        value = re.sub(
            r"</li>",
            "\n",
            value,
            flags=re.IGNORECASE,
        )

        value = re.sub(
            r"<[^>]+>",
            " ",
            value,
        )

        value = html.unescape(value)

        value = re.sub(
            r"[ \t]+",
            " ",
            value,
        )

        value = re.sub(
            r"\n\s*\n+",
            "\n",
            value,
        )

        value = value.strip()

        return value or None

    @staticmethod
    def _deduplicate_jobs(
        jobs: list[RawJob],
    ) -> list[RawJob]:
        seen: set[str] = set()
        unique_jobs: list[RawJob] = []

        for job in jobs:
            identity = (
                job.source_job_id
                or job.job_url
            )

            if identity in seen:
                continue

            seen.add(identity)
            unique_jobs.append(job)

        return unique_jobs