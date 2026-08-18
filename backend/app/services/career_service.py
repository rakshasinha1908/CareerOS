from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 15

# URL patterns that commonly indicate an actual job posting.
JOB_URL_PATTERNS = (
    "/jobs/",
    "/job/",
    "/careers/",
    "/career/",
    "/positions/",
    "/position/",
    "/openings/",
    "/opening/",
    "/opportunities/",
)

# Navigation / informational links that should never become jobs.
IGNORED_LINK_TEXT = {
    "about",
    "about us",
    "contact",
    "contact us",
    "careers",
    "career",
    "jobs",
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
}


@dataclass
class DiscoveredJob:
    title: str
    url: str


def _clean_text(value: str | None) -> str:
    if not value:
        return ""

    return re.sub(r"\s+", " ", value).strip()


def _is_valid_http_url(url: str) -> bool:
    parsed = urlparse(url)

    return parsed.scheme in {"http", "https"} and bool(
        parsed.netloc
    )


def _same_domain(base_url: str, candidate_url: str) -> bool:
    base_domain = urlparse(base_url).netloc.lower()
    candidate_domain = urlparse(candidate_url).netloc.lower()

    return (
        candidate_domain == base_domain
        or candidate_domain.endswith(
            f".{base_domain}"
        )
    )


def _looks_like_job_url(url: str) -> bool:
    """
    Determine whether a URL looks like an individual
    job posting rather than a general career page.
    """

    path = urlparse(url).path.lower().rstrip("/")

    # ----------------------------------
    # Explicit individual-job patterns
    # ----------------------------------

    individual_job_patterns = (
        r"/jobs/[^/]+/[^/]+",
        r"/job/[^/]+",
        r"/jobs/results/\d+-",
        r"/jobs/results/\d+",
        r"/positions/[^/]+",
        r"/openings/[^/]+",
        r"/opening/[^/]+",
        r"/career/[^/]+/[^/]+",
    )

    for pattern in individual_job_patterns:
        if re.search(pattern, path):
            return True

    return False


def _looks_like_job_title(title: str) -> bool:
    title = _clean_text(title)

    if not title:
        return False

    normalized = title.lower()

    if normalized in IGNORED_LINK_TEXT:
        return False

    if len(title) < 4 or len(title) > 180:
        return False

    # Navigation-style text is usually not a job title.
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


def _extract_json_ld_jobs(
    soup: BeautifulSoup,
    career_url: str,
) -> list[DiscoveredJob]:
    discovered: list[DiscoveredJob] = []

    scripts = soup.find_all(
        "script",
        attrs={"type": "application/ld+json"},
    )

    for script in scripts:
        raw = script.string or script.get_text()

        if not raw.strip():
            continue

        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
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

            absolute_url = urljoin(
                career_url,
                str(url),
            )

            if not _is_valid_http_url(
                absolute_url
            ):
                continue

            discovered.append(
                DiscoveredJob(
                    title=title,
                    url=absolute_url,
                )
            )

    return discovered


def _extract_anchor_jobs(
    soup: BeautifulSoup,
    career_url: str,
) -> list[DiscoveredJob]:
    discovered: list[DiscoveredJob] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")

        if not href:
            continue

        title = _clean_text(
            anchor.get_text(" ", strip=True)
        )

        if not _looks_like_job_title(title):
            continue

        absolute_url = urljoin(
            career_url,
            href,
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

        if not _looks_like_job_url(
            absolute_url
        ):
            continue

        discovered.append(
            DiscoveredJob(
                title=title,
                url=absolute_url,
            )
        )

    return discovered


def _deduplicate_jobs(
    jobs: list[DiscoveredJob],
) -> list[DiscoveredJob]:
    seen_urls: set[str] = set()
    result: list[DiscoveredJob] = []

    for job in jobs:
        normalized_url = job.url.rstrip("/")

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        result.append(job)

    return result


def discover_jobs(
    career_url: str,
) -> list[DiscoveredJob]:
    """
    Discover candidate job postings from a company's
    career page.

    This function only discovers job links.

    It does NOT:
    - save anything to the database
    - apply user preferences
    - calculate match scores
    - extract the full job description
    """

    career_url = career_url.strip()

    if not _is_valid_http_url(career_url):
        raise ValueError(
            "career_url must be a valid HTTP or HTTPS URL"
        )

    response = requests.get(
        career_url,
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

    final_url = response.url

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # Prefer structured JobPosting data first.
    json_ld_jobs = _extract_json_ld_jobs(
        soup,
        final_url,
    )

    # Then inspect regular career-page links.
    anchor_jobs = _extract_anchor_jobs(
        soup,
        final_url,
    )

    return _deduplicate_jobs(
        json_ld_jobs + anchor_jobs
    )
    
    
def _looks_like_job_listing_page(
    text: str,
    url: str,
) -> bool:
    """
    Determine whether a URL appears to be a job
    listing/search page rather than an individual
    job page or general career navigation page.
    """

    normalized_text = _clean_text(text).lower()

    parsed = urlparse(url)
    path = parsed.path.lower().rstrip("/")

    segments = [
        segment
        for segment in path.split("/")
        if segment
    ]

    # ----------------------------------
    # 1. Explicit listing/search signals
    # ----------------------------------

    listing_path_patterns = (
        "/job-search",
        "/job-search-results",
        "/jobs/search",
        "/jobs/results",
        "/open-positions",
        "/job-openings",
        "/career-search",
        "/careers/search",
    )

    if any(
        pattern in path
        for pattern in listing_path_patterns
    ):
        # A deeper path after /results/ is most
        # likely an individual job posting.
        if "/results/" in path:
            return False

        return True

    # ----------------------------------
    # 2. Exact listing pages
    # ----------------------------------

    listing_endings = {
        "/jobs",
        "/careers",
        "/positions",
        "/openings",
    }

    if path in listing_endings:
        return True

    # ----------------------------------
    # 3. Listing-like link text
    # ----------------------------------

    listing_text = {
        "jobs",
        "view jobs",
        "view all jobs",
        "see all jobs",
        "search jobs",
        "find jobs",
        "job openings",
        "open positions",
        "all jobs",
    }

    if normalized_text in listing_text:
        return True

    # ----------------------------------
    # 4. Generic search/results pages
    # ----------------------------------

    search_result_segments = {
        "search",
        "results",
        "job-search",
        "job-search-results",
    }

    if any(
        segment in search_result_segments
        for segment in segments
    ):
        return True

    return False


def discover_job_listing_pages(
    career_url: str,
) -> list[str]:
    """
    Find pages that appear to contain a company's
    job listings or job search results.

    This function does not extract individual jobs
    and does not write to the database.
    """

    career_url = career_url.strip()

    if not _is_valid_http_url(career_url):
        raise ValueError(
            "career_url must be a valid HTTP or HTTPS URL"
        )

    response = requests.get(
        career_url,
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

    final_url = response.url

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    listing_pages: list[str] = []

    for anchor in soup.find_all(
        "a",
        href=True,
    ):
        href = anchor.get("href")

        if not href:
            continue

        absolute_url = urljoin(
            final_url,
            href,
        )

        if not _is_valid_http_url(
            absolute_url
        ):
            continue

        if not _same_domain(
            final_url,
            absolute_url,
        ):
            continue

        text = _clean_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        )

        if not _looks_like_job_listing_page(
            text,
            absolute_url,
        ):
            continue

        listing_pages.append(
            absolute_url
        )

    return list(
        dict.fromkeys(
            url.rstrip("/")
            for url in listing_pages
        )
    )
    
    
def discover_job_links(
    listing_url: str,
) -> list[DiscoveredJob]:
    """
    Discover individual job posting links from a
    job listing/search page.

    This function only identifies candidate job links.
    It does not fetch individual job pages, extract
    descriptions, or write anything to the database.
    """

    listing_url = listing_url.strip()

    if not _is_valid_http_url(listing_url):
        raise ValueError(
            "listing_url must be a valid HTTP or HTTPS URL"
        )

    response = requests.get(
        listing_url,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": (
                "CareerOS/1.0 "
                "(job link discovery)"
            )
        },
        allow_redirects=True,
    )

    response.raise_for_status()

    final_url = response.url

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    discovered: list[DiscoveredJob] = []

    for anchor in soup.find_all(
        "a",
        href=True,
    ):
        href = anchor.get("href")

        if not href:
            continue

        absolute_url = urljoin(
            final_url,
            href,
        )

        if not _is_valid_http_url(
            absolute_url
        ):
            continue

        if not _same_domain(
            final_url,
            absolute_url,
        ):
            continue

        title = _clean_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        )

        if not _looks_like_job_title(title):
            continue

        path = urlparse(
            absolute_url
        ).path.lower().rstrip("/")

        # Individual job pages are usually deeper than
        # the listing/search page.
        if path == urlparse(
            final_url
        ).path.lower().rstrip("/"):
            continue

        # Avoid obvious navigation/account pages.
        ignored_path_fragments = (
            "/students",
            "/teams",
            "/how-we-hire",
            "/dashboard",
            "/recommendations",
            "/saved",
            "/alerts",
            "/privacy",
            "/privacy-policy",
            "/eeo",
        )

        if any(
            fragment in path
            for fragment in ignored_path_fragments
        ):
            continue

        # A candidate job URL should normally contain
        # a job-related path and be deeper than the
        # listing page.
        if not _looks_like_job_url(
            absolute_url
        ):
            continue

        discovered.append(
            DiscoveredJob(
                title=title,
                url=absolute_url,
            )
        )

    return _deduplicate_jobs(
        discovered
    )