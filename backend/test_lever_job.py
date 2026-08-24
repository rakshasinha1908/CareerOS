from pathlib import Path

import requests
from bs4 import BeautifulSoup


URL = (
    "https://jobs.lever.co/levelai/"
    "498dfb1d-2f80-4a74-8d08-ecadccd8a221"
)


def main():
    response = requests.get(
        URL,
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

    print()
    print("=" * 60)
    print("LEVEL AI / LEVER JOB PAGE")
    print("=" * 60)

    print("STATUS :", response.status_code)
    print("FINAL  :", response.url)
    print("LENGTH :", len(response.text))

    html = response.text

    Path(
        "levelai_job_response.html"
    ).write_text(
        html,
        encoding="utf-8",
    )

    print()
    print("Saved: levelai_job_response.html")

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    print()
    print("=" * 60)
    print("BASIC HTML INSPECTION")
    print("=" * 60)

    if soup.title:
        print()
        print("TITLE:")
        print(
            soup.title.get_text(
                " ",
                strip=True,
            )
        )

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"},
    )

    print()
    print("META DESCRIPTION:")

    if meta_description:
        print(
            meta_description.get(
                "content"
            )
        )
    else:
        print("None")

    print()
    print("=" * 60)
    print("HEADINGS")
    print("=" * 60)

    for heading in soup.find_all(
        ["h1", "h2", "h3", "h4"]
    ):
        text = heading.get_text(
            " ",
            strip=True,
        )

        if text:
            print(
                f"{heading.name.upper()}: "
                f"{text}"
            )

    print()
    print("=" * 60)
    print("STRUCTURED DATA")
    print("=" * 60)

    scripts = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json"
        },
    )

    print(
        "JSON-LD blocks:",
        len(scripts),
    )

    for index, script in enumerate(
        scripts,
        start=1,
    ):
        print()
        print(
            f"--- JSON-LD BLOCK {index} ---"
        )

        text = script.get_text(
            strip=True
        )

        print(
            text[:10000]
        )

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()