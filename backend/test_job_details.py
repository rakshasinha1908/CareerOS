from pathlib import Path

from bs4 import BeautifulSoup

from app.services.job_details_service import (
    extract_job_details,
    job_details_to_json,
)


HTML_FILE = "google_job_response.html"


def main():

    html = Path(
        HTML_FILE
    ).read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    job = extract_job_details(
        html
    )

    # ---------------------------------------------------------
    # DEBUG: inspect the DOM around the actual job detail section
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("JOB DETAIL CONTAINER")
    print("=" * 60)

    target_title = (
        "Senior Software Engineer, "
        "Vertex AI, Workbench"
    )

    for h2 in soup.find_all("h2"):

        text = h2.get_text(
            " ",
            strip=True,
        )

        if text != target_title:
            continue

        # Walk up a few levels and inspect the text
        # around the actual job detail section.
        parent = h2

        for level in range(1, 6):

            parent = parent.parent

            if not parent:
                break

            text = parent.get_text(
                "\n",
                strip=True,
            )

            print()
            print(
                f"--- PARENT LEVEL {level} ---"
            )

            print(text[:5000])

        break

    # ---------------------------------------------------------
    # Extracted details
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("EXTRACTED JOB DETAILS")
    print("=" * 60)

    print(
        job_details_to_json(job)
    )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"Title            : {job.title}"
    )

    print(
        f"Location         : {job.location}"
    )

    print(
        f"Experience       : {job.experience_level}"
    )

    print(
        f"Description      : "
        f"{'YES' if job.description else 'NO'}"
    )

    print(
        f"Min qualifications: "
        f"{'YES' if job.minimum_qualifications else 'NO'}"
    )

    print(
        f"Preferred quals   : "
        f"{'YES' if job.preferred_qualifications else 'NO'}"
    )

    print(
        f"About             : "
        f"{'YES' if job.about_the_job else 'NO'}"
    )

    print(
        f"Responsibilities  : "
        f"{'YES' if job.responsibilities else 'NO'}"
    )

    print()


if __name__ == "__main__":
    main()
