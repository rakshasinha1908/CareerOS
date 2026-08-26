import json
import re

import requests
from bs4 import BeautifulSoup


URL = (
    "https://apply.careers.microsoft.com/"
    "careers?start=0&pid=1970393556952487"
    "&sort_by=timestamp"
)


def main():
    print()
    print("=" * 60)
    print("MICROSOFT CAREER PAGE INSPECTION")
    print("=" * 60)

    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            )
        },
    )

    response.raise_for_status()

    html = response.text

    print(f"STATUS : {response.status_code}")
    print(f"FINAL  : {response.url}")
    print(f"LENGTH : {len(html)}")

    with open(
        "microsoft_careers_response.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(html)

    print()
    print("Saved: microsoft_careers_response.html")

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # -------------------------------------------------
    # TITLE
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("PAGE TITLE")
    print("=" * 60)

    print(
        soup.title.get_text(
            " ",
            strip=True,
        )
        if soup.title
        else "None"
    )

    # -------------------------------------------------
    # JSON-LD
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("JSON-LD")
    print("=" * 60)

    scripts = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json"
        },
    )

    print(
        f"JSON-LD blocks: {len(scripts)}"
    )

    for index, script in enumerate(
        scripts,
        start=1,
    ):
        print()
        print(f"--- JSON-LD BLOCK {index} ---")

        text = script.string or script.get_text()

        print(
            text[:5000]
        )

    # -------------------------------------------------
    # SCRIPT INSPECTION
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("INTERESTING SCRIPT CONTENT")
    print("=" * 60)

    keywords = [
        "api",
        "job",
        "jobs",
        "search",
        "graphql",
        "careers",
        "posting",
        "pid",
    ]

    found_scripts = 0

    for script in soup.find_all("script"):
        text = script.string or script.get_text()

        if not text:
            continue

        lower = text.lower()

        if any(
            keyword in lower
            for keyword in keywords
        ):
            found_scripts += 1

            print()
            print(
                f"--- SCRIPT {found_scripts} ---"
            )

            print(
                text[:8000]
            )

            if found_scripts >= 10:
                break

    # -------------------------------------------------
    # LINKS
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("CAREER / JOB LINKS")
    print("=" * 60)

    links = []

    for anchor in soup.find_all("a"):
        href = anchor.get("href")

        if not href:
            continue

        text = anchor.get_text(
            " ",
            strip=True,
        )

        href_lower = href.lower()

        if (
            "career" in href_lower
            or "job" in href_lower
            or "pid=" in href_lower
        ):
            links.append(
                (
                    text,
                    href,
                )
            )

    print(
        f"Relevant links found: {len(links)}"
    )

    for text, href in links[:50]:
        print()
        print(f"TEXT : {text}")
        print(f"HREF : {href}")


if __name__ == "__main__":
    main()