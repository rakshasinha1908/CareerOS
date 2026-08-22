from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 15


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

    # Strongest case:
    # job-like URL + meaningful title.
    if url_signal and title_signal:
        return True

    # A meaningful job title with job-related
    # surrounding content is also a good candidate.
    if title_signal and context_signal:
        return True

    return False


# --------------------------------------------------
# JSON-LD extraction
# --------------------------------------------------


def _extract_json_ld_jobs(
    soup: BeautifulSoup,
    career_url: str,
) -> list[DiscoveredJob]:
    discovered: list[DiscoveredJob] = []

    scripts = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json"
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


# --------------------------------------------------
# Generic HTML extraction
# --------------------------------------------------


def _extract_anchor_jobs(
    soup: BeautifulSoup,
    career_url: str,
) -> list[DiscoveredJob]:
    discovered: list[DiscoveredJob] = []

    for anchor in soup.find_all(
        "a",
        href=True,
    ):
        href = anchor.get("href")

        if not href:
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

        # Prefer aria-label because many modern
        # career pages use visually empty links
        # with accessible job titles.
        title = _clean_text(
            anchor.get("aria-label")
        )

        if title.lower().startswith(
            "learn more about "
        ):
            title = title[
                len("learn more about "):
            ]

        # Fall back to visible link text.
        if not title:
            title = _clean_text(
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )

        if not title:
            continue

        # Use the closest meaningful parent as context.
        parent = anchor.find_parent(
            ["li", "article", "div", "section"]
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
        normalized_url = job.url.rstrip("/")

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        result.append(job)

    return result


# --------------------------------------------------
# Main V1 discovery service
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


def discover_jobs(
    career_url: str,
) -> list[DiscoveredJob]:
    """
    V1 generic career-page job discovery.

    Strategy:

    1. Fetch the supplied career URL.
    2. Look for structured JobPosting data.
    3. Look for obvious job links/cards.
    4. If nothing useful is found, follow ONE
       obvious jobs/listing link.
    5. Return normalized candidate jobs.

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

    final_url, soup = _fetch_page(
        career_url
    )

    # ----------------------------------
    # First attempt: structured data
    # ----------------------------------

    jobs = _extract_json_ld_jobs(
        soup,
        final_url,
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

    if listing_url.rstrip("/") == final_url.rstrip("/"):
        return []

    listing_final_url, listing_soup = (
        _fetch_page(listing_url)
    )

    jobs = _extract_json_ld_jobs(
        listing_soup,
        listing_final_url,
    )

    if not jobs:
        jobs = _extract_anchor_jobs(
            listing_soup,
            listing_final_url,
        )

    return _deduplicate_jobs(
        jobs
    )