from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 15

# Microsoft PCSX API settings
MICROSOFT_API_URL = (
    "https://apply.careers.microsoft.com/api/pcsx/search"
)

MICROSOFT_DOMAIN = "microsoft.com"

MICROSOFT_PAGE_SIZE = 100
MICROSOFT_MAX_RETRIES = 4
MICROSOFT_RETRY_BASE_DELAY = 2.0
MICROSOFT_REQUEST_DELAY = 0.35


@dataclass
class DiscoveredJob:
    title: str
    url: str


# --------------------------------------------------
# Text / URL helpers
# --------------------------------------------------


def _clean_text(value: str | None) -> str:
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def _is_valid_http_url(url: str) -> bool:
    parsed = urlparse(url)

    return parsed.scheme in {"http", "https"} and bool(
        parsed.netloc
    )


def _normalize_url(url: str) -> str:
    """
    Normalize a URL enough for safe comparison.

    We intentionally keep query parameters because
    some job URLs use them as part of the job identity.
    """
    parsed = urlparse(url)

    return parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=parsed.path.rstrip("/"),
    ).geturl()


def _same_url(
    first_url: str,
    second_url: str,
) -> bool:
    return (
        _normalize_url(first_url)
        == _normalize_url(second_url)
    )


def _same_domain(
    base_url: str,
    candidate_url: str,
) -> bool:
    base_domain = urlparse(base_url).netloc.lower()
    candidate_domain = urlparse(candidate_url).netloc.lower()

    return (
        candidate_domain == base_domain
        or candidate_domain.endswith(
            f".{base_domain}"
        )
    )


def _resolve_url(
    soup: BeautifulSoup,
    page_url: str,
    href: str,
) -> str:
    """
    Resolve a relative URL using the page's <base> tag
    when available.

    This is important for career pages where relative
    links are resolved against a base URL that differs
    from the visible page URL.
    """

    href = href.strip()

    base_tag = soup.find(
        "base",
        href=True,
    )

    if base_tag:
        base_href = str(
            base_tag.get("href")
        ).strip()

        if base_href:
            base_url = urljoin(
                page_url,
                base_href,
            )

            return urljoin(
                base_url,
                href,
            )

    return urljoin(
        page_url,
        href,
    )


# --------------------------------------------------
# Microsoft detection
# --------------------------------------------------


def _is_microsoft_career_url(
    career_url: str,
) -> bool:
    """
    Detect Microsoft career pages.

    Microsoft currently uses the Eightfold/PCSX
    career platform under apply.careers.microsoft.com.
    """

    hostname = urlparse(
        career_url
    ).netloc.lower()

    return (
        hostname == "apply.careers.microsoft.com"
        or hostname.endswith(
            ".careers.microsoft.com"
        )
    )


# --------------------------------------------------
# Microsoft PCSX API discovery
# --------------------------------------------------


def _fetch_microsoft_pcsx_page(
    start: int,
    num: int,
) -> dict:
    """
    Fetch one page from Microsoft's PCSX job-search API.

    query intentionally remains empty because CareerOS
    has not implemented user keyword filtering yet.
    """

    params = {
        "domain": MICROSOFT_DOMAIN,
        "query": "",
        "location": "",
        "start": start,
        "num": num,
    }

    for attempt in range(
        MICROSOFT_MAX_RETRIES + 1
    ):
        response = requests.get(
            MICROSOFT_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": (
                    "CareerOS/1.0 "
                    "(career discovery)"
                ),
                "Accept": "application/json",
            },
        )

        if response.status_code != 429:
            response.raise_for_status()
            return response.json()

        if attempt >= MICROSOFT_MAX_RETRIES:
            response.raise_for_status()

        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after:
            try:
                delay = float(retry_after)
            except ValueError:
                delay = (
                    MICROSOFT_RETRY_BASE_DELAY
                    * (2**attempt)
                )
        else:
            delay = (
                MICROSOFT_RETRY_BASE_DELAY
                * (2**attempt)
            )

        print(
            f"Microsoft API rate limited "
            f"(429). Retrying in {delay:.1f}s..."
        )

        time.sleep(delay)

    raise RuntimeError(
        "Microsoft PCSX API request failed "
        "after retries."
    )


def _extract_microsoft_jobs(
    payload: dict,
) -> tuple[list[DiscoveredJob], int]:
    """
    Convert one Microsoft PCSX API response into
    CareerOS DiscoveredJob objects.

    Returns:
        (jobs, total_count)
    """

    data = payload.get("data", {})

    if not isinstance(data, dict):
        return [], 0

    positions = data.get(
        "positions",
        [],
    )

    if not isinstance(positions, list):
        return [], 0

    total = data.get(
        "count",
        0,
    )

    try:
        total = int(total)
    except (
        TypeError,
        ValueError,
    ):
        total = 0

    jobs: list[DiscoveredJob] = []

    for position in positions:
        if not isinstance(position, dict):
            continue

        title = _clean_text(
            position.get("name")
        )

        position_url = position.get(
            "positionUrl"
        )

        if not title or not position_url:
            continue

        position_url = str(
            position_url
        ).strip()

        # Microsoft returns values such as:
        #
        # /careers/job/1970393556972323
        #
        # Convert them into actual job URLs.
        absolute_url = urljoin(
            "https://apply.careers.microsoft.com",
            position_url,
        )

        if not _is_valid_http_url(
            absolute_url
        ):
            continue

        jobs.append(
            DiscoveredJob(
                title=title,
                url=absolute_url,
            )
        )

    return jobs, total


def _discover_microsoft_jobs() -> list[DiscoveredJob]:
    """
    Discover Microsoft jobs through the PCSX API.

    No keyword or location filtering is applied yet.

    Pagination continues until all jobs reported by the
    API have been collected.
    """

    all_jobs: list[DiscoveredJob] = []

    seen_ids: set[str] = set()
    seen_urls: set[str] = set()

    start = 0
    total_count: int | None = None

    print()
    print(
        "Microsoft PCSX discovery started..."
    )

    while True:
        payload = _fetch_microsoft_pcsx_page(
            start=start,
            num=MICROSOFT_PAGE_SIZE,
        )

        jobs, page_total = (
            _extract_microsoft_jobs(
                payload
            )
        )

        if total_count is None:
            total_count = page_total

            print(
                f"Microsoft API reports "
                f"{total_count} jobs."
            )

        if not jobs:
            break

        for job in jobs:
            normalized_url = _normalize_url(
                job.url
            )

            if normalized_url in seen_urls:
                continue

            seen_urls.add(
                normalized_url
            )

            # Microsoft job IDs are embedded in
            # /careers/job/<id>.
            #
            # URL deduplication is the primary
            # protection, while the set keeps the
            # discovery state easy to reason about.
            seen_ids.add(
                normalized_url
            )

            all_jobs.append(job)

        print(
            f"Microsoft page: "
            f"{start} - "
            f"{start + len(jobs) - 1} | "
            f"collected: {len(all_jobs)}"
            + (
                f" / {total_count}"
                if total_count
                else ""
            )
        )

        start += MICROSOFT_PAGE_SIZE

        if (
            total_count
            and len(all_jobs) >= total_count
        ):
            break

        # If the API returned fewer jobs than the
        # requested page size, there is no useful
        # reason to continue.
        if len(jobs) < MICROSOFT_PAGE_SIZE:
            break

        time.sleep(
            MICROSOFT_REQUEST_DELAY
        )

    print(
        f"Microsoft discovery complete: "
        f"{len(all_jobs)} unique jobs."
    )

    return all_jobs


# --------------------------------------------------
# Job heuristics
# --------------------------------------------------


IGNORED_LINK_TEXT = {
    "about",
    "about us",
    "contact",
    "contact us",
    "careers",
    "career",
    "jobs",
    "view jobs",
    "view all jobs",
    "see all jobs",
    "all jobs",
    "benefits",
    "culture",
    "life at",
    "privacy",
    "privacy policy",
    "terms",
    "terms of use",
    "login",
    "sign in",
    "home",
    "students",
    "how we work",
    "how we hire",
    "your career",
    "dashboard",
    "saved jobs",
    "job alerts",
    "recommended jobs",
}


JOB_URL_TERMS = (
    "job",
    "jobs",
    "career",
    "careers",
    "position",
    "positions",
    "opening",
    "openings",
    "opportunity",
    "opportunities",
)


JOB_TITLE_TERMS = (
    "engineer",
    "developer",
    "designer",
    "manager",
    "analyst",
    "scientist",
    "architect",
    "consultant",
    "intern",
    "internship",
    "director",
    "specialist",
    "administrator",
    "recruiter",
    "researcher",
    "associate",
    "lead",
    "principal",
    "accountant",
    "coordinator",
    "product",
    "marketing",
    "sales",
    "finance",
    "security",
    "data",
    "software",
    "technology",
)


def _looks_like_job_title(
    title: str,
) -> bool:
    title = _clean_text(title)

    if not title:
        return False

    normalized = title.lower()

    if normalized in IGNORED_LINK_TEXT:
        return False

    if len(title) < 4 or len(title) > 180:
        return False

    ignored_fragments = (
        "privacy policy",
        "terms of use",
        "cookie policy",
        "accessibility",
        "learn more",
        "read more",
        "view all",
        "see all",
        "sign in",
        "log in",
    )

    if any(
        fragment in normalized
        for fragment in ignored_fragments
    ):
        return False

    return True


def _looks_like_job_url(
    url: str,
) -> bool:
    path = urlparse(url).path.lower()

    return any(
        term in path
        for term in JOB_URL_TERMS
    )


def _looks_like_job_candidate(
    title: str,
    url: str,
    context: str = "",
) -> bool:
    """
    Generic V1 heuristic.

    We intentionally do not depend on a particular
    company's CSS classes or ATS implementation.
    """

    if not _looks_like_job_title(title):
        return False

    normalized_title = title.lower()
    normalized_context = context.lower()

    url_signal = _looks_like_job_url(url)

    title_signal = any(
        term in normalized_title
        for term in JOB_TITLE_TERMS
    )

    context_signal = any(
        term in normalized_context
        for term in (
            "apply",
            "job description",
            "responsibilities",
            "qualifications",
            "requirements",
            "location",
            "employment type",
        )
    )

    if url_signal and title_signal:
        return True

    if title_signal and context_signal:
        return True

    return False


# --------------------------------------------------
# JSON-LD extraction
# --------------------------------------------------


def _extract_json_ld_jobs(
    soup: BeautifulSoup,
    career_url: str,
    current_page_url: str | None = None,
) -> list[DiscoveredJob]:
    discovered: list[DiscoveredJob] = []

    scripts = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json",
        },
    )

    for script in scripts:
        raw = script.string or script.get_text()

        if not raw.strip():
            continue

        try:
            data = json.loads(raw)
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            continue

        objects: list[dict] = []

        if isinstance(data, dict):
            objects.append(data)

            graph = data.get("@graph")

            if isinstance(graph, list):
                objects.extend(
                    item
                    for item in graph
                    if isinstance(item, dict)
                )

        elif isinstance(data, list):
            objects.extend(
                item
                for item in data
                if isinstance(item, dict)
            )

        for item in objects:
            item_type = item.get("@type")

            if isinstance(item_type, list):
                is_job_posting = (
                    "JobPosting" in item_type
                )
            else:
                is_job_posting = (
                    item_type == "JobPosting"
                )

            if not is_job_posting:
                continue

            title = _clean_text(
                item.get("title")
            )

            url = item.get("url")

            if not title or not url:
                continue

            absolute_url = _resolve_url(
                soup,
                career_url,
                str(url),
            )

            if not _is_valid_http_url(
                absolute_url
            ):
                continue

            if current_page_url and _same_url(
                absolute_url,
                current_page_url,
            ):
                continue

            if _same_url(
                absolute_url,
                career_url,
            ):
                continue

            discovered.append(
                DiscoveredJob(
                    title=title,
                    url=absolute_url,
                )
            )

    return discovered


# --------------------------------------------------
# Generic HTML extraction
# --------------------------------------------------


def _extract_anchor_jobs(
    soup: BeautifulSoup,
    career_url: str,
    current_page_url: str | None = None,
) -> list[DiscoveredJob]:
    discovered: list[DiscoveredJob] = []

    for anchor in soup.find_all(
        "a",
        href=True,
    ):
        href = anchor.get("href")

        if not href:
            continue

        absolute_url = _resolve_url(
            soup,
            career_url,
            str(href),
        )

        if not _is_valid_http_url(
            absolute_url
        ):
            continue

        if not _same_domain(
            career_url,
            absolute_url,
        ):
            continue

        if current_page_url and _same_url(
            absolute_url,
            current_page_url,
        ):
            continue

        if _same_url(
            absolute_url,
            career_url,
        ):
            continue

        title = _clean_text(
            anchor.get("aria-label")
        )

        if title.lower().startswith(
            "learn more about "
        ):
            title = title[
                len("learn more about "):
            ]

        if not title:
            title = _clean_text(
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )

        if not title:
            continue

        parent = anchor.find_parent(
            [
                "li",
                "article",
                "div",
                "section",
            ]
        )

        context = ""

        if parent:
            context = _clean_text(
                parent.get_text(
                    " ",
                    strip=True,
                )
            )

        if not _looks_like_job_candidate(
            title,
            absolute_url,
            context,
        ):
            continue

        discovered.append(
            DiscoveredJob(
                title=title,
                url=absolute_url,
            )
        )

    return discovered


# --------------------------------------------------
# Find one obvious jobs/listing page
# --------------------------------------------------


LISTING_LINK_TEXT = {
    "jobs",
    "view jobs",
    "view all jobs",
    "see all jobs",
    "all jobs",
    "search jobs",
    "find jobs",
    "job openings",
    "open positions",
}


def _find_listing_link(
    soup: BeautifulSoup,
    career_url: str,
) -> str | None:
    candidates: list[tuple[int, str]] = []

    for anchor in soup.find_all(
        "a",
        href=True,
    ):
        href = anchor.get("href")

        if not href:
            continue

        title = _clean_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        ).lower()

        absolute_url = _resolve_url(
            soup,
            career_url,
            str(href),
        )

        if not _is_valid_http_url(
            absolute_url
        ):
            continue

        if not _same_domain(
            career_url,
            absolute_url,
        ):
            continue

        if _same_url(
            absolute_url,
            career_url,
        ):
            continue

        score = 0

        if title in LISTING_LINK_TEXT:
            score += 5

        path = urlparse(
            absolute_url
        ).path.lower()

        if any(
            term in path
            for term in (
                "/jobs",
                "/careers",
                "/positions",
                "/openings",
            )
        ):
            score += 2

        if score > 0:
            candidates.append(
                (
                    score,
                    absolute_url,
                )
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1]


# --------------------------------------------------
# Deduplication
# --------------------------------------------------


def _deduplicate_jobs(
    jobs: list[DiscoveredJob],
) -> list[DiscoveredJob]:
    seen_urls: set[str] = set()
    result: list[DiscoveredJob] = []

    for job in jobs:
        normalized_url = _normalize_url(
            job.url
        )

        if normalized_url in seen_urls:
            continue

        seen_urls.add(
            normalized_url
        )
        result.append(job)

    return result


# --------------------------------------------------
# HTTP fetching
# --------------------------------------------------


def _fetch_page(
    url: str,
) -> tuple[str, BeautifulSoup]:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": (
                "CareerOS/1.0 "
                "(career page discovery)"
            )
        },
        allow_redirects=True,
    )

    response.raise_for_status()

    return (
        response.url,
        BeautifulSoup(
            response.text,
            "html.parser",
        ),
    )


# --------------------------------------------------
# JSON-LD job detail extraction
# --------------------------------------------------


def _extract_json_ld_job_details(
    soup: BeautifulSoup,
) -> dict:
    details = {}

    scripts = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json",
        },
    )

    for script in scripts:
        raw = script.string or script.get_text()

        if not raw.strip():
            continue

        try:
            data = json.loads(raw)
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            continue

        objects: list[dict] = []

        if isinstance(data, dict):
            objects.append(data)

            graph = data.get("@graph")

            if isinstance(graph, list):
                objects.extend(
                    item
                    for item in graph
                    if isinstance(item, dict)
                )

        elif isinstance(data, list):
            objects.extend(
                item
                for item in data
                if isinstance(item, dict)
            )

        for item in objects:
            item_type = item.get("@type")

            if isinstance(item_type, list):
                is_job_posting = (
                    "JobPosting" in item_type
                )
            else:
                is_job_posting = (
                    item_type == "JobPosting"
                )

            if not is_job_posting:
                continue

            details["title"] = _clean_text(
                item.get("title")
            ) or None

            details["description"] = _clean_text(
                item.get("description")
            ) or None

            details["employment_type"] = (
                _clean_text(
                    item.get("employmentType")
                )
                or None
            )

            details["posted_at"] = (
                item.get("datePosted")
                or None
            )

            location = item.get(
                "jobLocation"
            )

            if isinstance(location, list):
                location = (
                    location[0]
                    if location
                    else None
                )

            if isinstance(location, dict):
                address = location.get(
                    "address"
                )

                if isinstance(address, dict):
                    parts = [
                        address.get(
                            "addressLocality"
                        ),
                        address.get(
                            "addressRegion"
                        ),
                        address.get(
                            "addressCountry"
                        ),
                    ]

                    parts = [
                        _clean_text(str(part))
                        for part in parts
                        if part
                    ]

                    details["location"] = (
                        ", ".join(parts)
                        if parts
                        else None
                    )

            return details

    return {}


def extract_job_details(
    job_url: str,
) -> dict:
    """
    Extract basic details from an individual
    job posting page.

    V1 is best-effort. Missing fields are
    returned as None.
    """

    job_url = job_url.strip()

    if not _is_valid_http_url(job_url):
        raise ValueError(
            "job_url must be a valid HTTP "
            "or HTTPS URL"
        )

    _, soup = _fetch_page(
        job_url
    )

    details = _extract_json_ld_job_details(
        soup
    )

    return {
        "title": details.get("title"),
        "location": details.get("location"),
        "description": details.get(
            "description"
        ),
        "employment_type": details.get(
            "employment_type"
        ),
        "experience_level": details.get(
            "experience_level"
        ),
        "posted_at": details.get(
            "posted_at"
        ),
    }


# --------------------------------------------------
# Main V1 discovery service
# --------------------------------------------------


def discover_jobs(
    career_url: str,
) -> list[DiscoveredJob]:
    """
    V1 career-page job discovery.

    Microsoft:
        Uses Microsoft's PCSX search API with
        pagination and no keyword filtering.

    Other companies:
        Uses the existing generic HTML / JSON-LD
        discovery strategy.

    This function does NOT:
    - save to the database
    - apply user preferences
    - calculate match scores
    - use AI
    - use browser automation
    """

    career_url = career_url.strip()

    if not _is_valid_http_url(
        career_url
    ):
        raise ValueError(
            "career_url must be a valid HTTP "
            "or HTTPS URL"
        )

    # ----------------------------------
    # Microsoft-specific discovery
    # ----------------------------------

    if _is_microsoft_career_url(
        career_url
    ):
        return _discover_microsoft_jobs()

    # ----------------------------------
    # Generic discovery
    # ----------------------------------

    final_url, soup = _fetch_page(
        career_url
    )

    # ----------------------------------
    # First attempt: structured data
    # ----------------------------------

    jobs = _extract_json_ld_jobs(
        soup,
        final_url,
        current_page_url=final_url,
    )

    if jobs:
        return _deduplicate_jobs(
            jobs
        )

    # ----------------------------------
    # Second attempt: regular HTML
    # ----------------------------------

    jobs = _extract_anchor_jobs(
        soup,
        final_url,
        current_page_url=final_url,
    )

    if jobs:
        return _deduplicate_jobs(
            jobs
        )

    # ----------------------------------
    # Third attempt: follow ONE obvious
    # jobs/listing page.
    # ----------------------------------

    listing_url = _find_listing_link(
        soup,
        final_url,
    )

    if not listing_url:
        return []

    if _same_url(
        listing_url,
        final_url,
    ):
        return []

    listing_final_url, listing_soup = (
        _fetch_page(
            listing_url
        )
    )

    jobs = _extract_json_ld_jobs(
        listing_soup,
        listing_final_url,
        current_page_url=listing_final_url,
    )

    if not jobs:
        jobs = _extract_anchor_jobs(
            listing_soup,
            listing_final_url,
            current_page_url=listing_final_url,
        )

    return _deduplicate_jobs(
        jobs
    )