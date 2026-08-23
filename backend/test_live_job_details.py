from app.services.job_details_service import (
    fetch_job_details,
)


URL = (
    "https://www.google.com/about/careers/applications/jobs/"
    "results/114905638462464710-senior-software-engineer-"
    "vertex-ai-workbench"
)


def main():
    print()
    print("=" * 60)
    print("LIVE JOB DETAILS TEST")
    print("=" * 60)

    print()
    print("URL:")
    print(URL)

    print()
    print("Fetching...")

    details = fetch_job_details(
        URL
    )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print()
    print("TITLE:")
    print(details.title)

    print()
    print("LOCATION:")
    print(details.location)

    print()
    print("EXPERIENCE:")
    print(details.experience_level)

    print()
    print("DESCRIPTION:")
    print(
        "YES"
        if details.description
        else "NO"
    )

    print()
    print("MIN QUALIFICATIONS:")
    print(
        "YES"
        if details.minimum_qualifications
        else "NO"
    )

    print()
    print("PREFERRED QUALIFICATIONS:")
    print(
        "YES"
        if details.preferred_qualifications
        else "NO"
    )

    print()
    print("ABOUT:")
    print(
        "YES"
        if details.about_the_job
        else "NO"
    )

    print()
    print("RESPONSIBILITIES:")
    print(
        "YES"
        if details.responsibilities
        else "NO"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()