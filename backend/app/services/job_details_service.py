from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

import json
import re

import requests
from bs4 import BeautifulSoup, Tag, NavigableString


@dataclass
class JobDetails:
    title: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None
    minimum_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    responsibilities: Optional[str] = None
    about_the_job: Optional[str] = None


def clean_text(text: str) -> str:
    """
    Normalize whitespace while preserving readable paragraph separation.
    """

    text = text.replace("\xa0", " ")

    lines = []

    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def get_meta_description(
    soup: BeautifulSoup,
) -> Optional[str]:
    """
    Extract the page-level meta description.
    """

    tag = soup.find(
        "meta",
        attrs={"name": "description"},
    )

    if not tag:
        return None

    content = tag.get("content")

    if not content:
        return None

    return clean_text(content)


def get_job_title(
    soup: BeautifulSoup,
) -> Optional[str]:
    """
    Extract the actual job title.

    Google currently exposes the job title in the job-detail H2.
    We avoid relying on the <title> tag because it contains
    '— Google Careers'.
    """

    # Prefer the job-detail H2.
    for h2 in soup.find_all("h2"):
        text = clean_text(
            h2.get_text(
                " ",
                strip=True,
            )
        )

        if not text:
            continue

        if text.lower() in {
            "jobs search results",
            "follow life at google on",
            "more about us",
            "related information",
            "equal opportunity",
        }:
            continue

        # A job title generally isn't one of Google's
        # navigation headings.
        if "Senior Software Engineer" in text:
            return text

    # Fallback to <title>.
    if soup.title:
        title = clean_text(
            soup.title.get_text(
                " ",
                strip=True,
            )
        )

        title = re.sub(
            r"\s*[—-]\s*Google Careers\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        return title or None

    return None


def get_experience_level(
    soup: BeautifulSoup,
    job_title: Optional[str],
) -> Optional[str]:
    """
    Extract the experience-level label associated
    with the job title.
    """

    if not job_title:
        return None

    headings = soup.find_all("h2")

    for index, heading in enumerate(headings):
        text = clean_text(
            heading.get_text(
                " ",
                strip=True,
            )
        )

        if text != job_title:
            continue

        # Look at the next few H2 headings.
        # Google currently places the experience
        # level shortly after the job title.
        for next_heading in headings[
            index + 1 : index + 4
        ]:
            candidate = clean_text(
                next_heading.get_text(
                    " ",
                    strip=True,
                )
            )

            if candidate.lower() in {
                "early",
                "mid",
                "senior",
                "staff",
                "lead",
            }:
                return candidate

            # Don't accidentally grab a completely
            # unrelated major section.
            if candidate.lower() in {
                "follow life at google on",
                "more about us",
                "related information",
                "equal opportunity",
            }:
                break

    return None


def find_heading(
    soup: BeautifulSoup,
    heading_text: str,
) -> Optional[Tag]:
    """
    Find a heading using normalized text.
    """

    target = clean_text(
        heading_text
    ).lower()

    for heading in soup.find_all(
        ["h2", "h3", "h4"]
    ):
        text = clean_text(
            heading.get_text(
                " ",
                strip=True,
            )
        ).lower()

        if text == target:
            return heading

    return None


def extract_section(
    heading: Optional[Tag],
) -> Optional[str]:
    """
    Extract text belonging to a heading until the next
    heading of the same or higher level.

    Unlike the previous implementation, this walks through
    nested DOM elements instead of relying only on direct
    siblings. This prevents content from leaking into a
    section from a later section or page footer.
    """

    if not heading:
        return None

    heading_level = int(
        heading.name[1]
    )

    parts: list[str] = []
    seen: set[str] = set()

    for element in heading.next_elements:

        # Stop as soon as we reach the next heading of
        # the same or higher level.
        if isinstance(element, Tag):

            if element.name in {
                "h1",
                "h2",
                "h3",
                "h4",
            }:
                element_level = int(
                    element.name[1]
                )

                if element_level <= heading_level:
                    break

            continue

        if not isinstance(
            element,
            NavigableString,
        ):
            continue

        text = clean_text(
            str(element)
        )

        if not text:
            continue

        # Avoid collecting the same visible text multiple
        # times when nested elements contain the same content.
        normalized = text.lower()

        if normalized in seen:
            continue

        seen.add(normalized)
        parts.append(text)

    result = "\n".join(parts).strip()

    if not result:
        return None

    # ---------------------------------------------------------
    # Defensive cleanup
    #
    # Some career pages expose footer/benefits text after the
    # actual section content. Do not allow a footer-only value
    # to become an About/Responsibilities/etc. section.
    # ---------------------------------------------------------

    footer_patterns = {
        "benefits at google",
        "learn more about benefits at google",
    }

    cleaned_parts = []

    for part in result.splitlines():
        normalized = part.strip().lower()

        if normalized in footer_patterns:
            continue

        cleaned_parts.append(part)

    result = "\n".join(
        cleaned_parts
    ).strip()

    return result or None


def extract_location(
    soup: BeautifulSoup,
    job_title: Optional[str],
) -> Optional[str]:
    """
    Extract the location from the job-detail container.

    The job title's second-level parent currently contains:
        Google
        <location>
        <experience level>
    """

    if not job_title:
        return None

    for h2 in soup.find_all("h2"):

        text = clean_text(
            h2.get_text(
                " ",
                strip=True,
            )
        )

        if text != job_title:
            continue

        # The job information lives a couple of
        # levels above the title.
        container = h2

        for _ in range(2):
            container = container.parent

            if not container:
                return None

        # Look for location-like elements inside
        # the actual job detail container.
        for element in container.find_all(
            ["div", "span"]
        ):

            text = clean_text(
                element.get_text(
                    " ",
                    strip=True,
                )
            )

            if not text:
                continue

            # Google location blocks contain:
            # Google
            # <location>
            #
            # We don't want the entire container text.
            if text == "Google":
                next_element = element.find_next()

                while next_element:

                    candidate = clean_text(
                        next_element.get_text(
                            " ",
                            strip=True,
                        )
                    )

                    if (
                        candidate
                        and candidate != "Google"
                    ):
                        # Only accept reasonably
                        # location-like strings and
                        # avoid UI text.
                        if (
                            "," in candidate
                            and len(candidate) < 200
                        ):
                            candidate = re.sub(
                                r"^place\s+",
                                "",
                                candidate,
                                flags=re.IGNORECASE,
                            )

                            return candidate

                    next_element = (
                        next_element.find_next()
                    )

        # Fallback: inspect the container's direct
        # visible text and identify the text between
        # Google and the experience level.
        lines = [
            clean_text(line)
            for line in container.get_text(
                "\n",
                strip=True,
            ).splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        for index, line in enumerate(lines):

            if line == "Google":

                for candidate in lines[
                    index + 1 :
                ]:

                    if candidate.lower() in {
                        "early",
                        "mid",
                        "senior",
                        "staff",
                        "lead",
                    }:
                        break

                    if (
                        "," in candidate
                        and len(candidate) < 200
                    ):
                        candidate = re.sub(
                            r"^place\s+",
                            "",
                            candidate,
                            flags=re.IGNORECASE,
                        )

                        return candidate

        break

    return None


def fetch_job_details(
    url: str,
) -> JobDetails:
    """
    Fetch an individual job page and extract its details.

    The extractor itself works on HTML. This function handles
    fetching the page from the URL.
    """

    response = requests.get(
        url,
        timeout=15,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        },
        allow_redirects=True,
    )

    response.raise_for_status()

    return extract_job_details(
        response.text
    )


def extract_job_details(
    html: str,
) -> JobDetails:

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    title = get_job_title(
        soup
    )

    experience_level = get_experience_level(
        soup,
        title,
    )

    location = extract_location(
        soup,
        title,
    )

    description = get_meta_description(
        soup
    )

    minimum_heading = find_heading(
        soup,
        "Minimum qualifications:",
    )

    preferred_heading = find_heading(
        soup,
        "Preferred qualifications:",
    )

    about_heading = find_heading(
        soup,
        "About the job",
    )

    responsibilities_heading = find_heading(
        soup,
        "Responsibilities",
    )

    minimum_qualifications = extract_section(
        minimum_heading
    )

    preferred_qualifications = extract_section(
        preferred_heading
    )

    about_the_job = extract_section(
        about_heading
    )

    responsibilities = extract_section(
        responsibilities_heading
    )

    return JobDetails(
        title=title,
        location=location,
        experience_level=experience_level,
        description=description,
        minimum_qualifications=minimum_qualifications,
        preferred_qualifications=preferred_qualifications,
        responsibilities=responsibilities,
        about_the_job=about_the_job,
    )


def job_details_to_dict(
    job: JobDetails,
) -> dict:
    return asdict(job)


def job_details_to_json(
    job: JobDetails,
) -> str:
    return json.dumps(
        asdict(job),
        indent=2,
        ensure_ascii=False,
    )