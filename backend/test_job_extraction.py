from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup


HTML_FILE = Path("google_careers_response.html")

BASE_URL = (
    "https://www.google.com/about/careers/applications/"
)


html = HTML_FILE.read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "html.parser",
)


jobs = []
seen_urls = set()


for link in soup.find_all("a", href=True):
    href = link["href"].strip()

    # Google uses relative URLs such as:
    # jobs/results/12345-software-engineer
    if "jobs/results/" not in href:
        continue

    url = urljoin(
        BASE_URL,
        href,
    )

    if url in seen_urls:
        continue

    seen_urls.add(url)

    title = link.get(
        "aria-label",
        "",
    ).strip()

    if title.lower().startswith(
        "learn more about "
    ):
        title = title[
            len("learn more about "):
        ]

    if not title:
        title = link.get_text(
            " ",
            strip=True,
        )

    if not title:
        continue

    jobs.append(
        {
            "title": title,
            "url": url,
        }
    )


print()
print("=" * 60)
print(
    f"FOUND {len(jobs)} CANDIDATE JOBS"
)
print("=" * 60)


for job in jobs[:20]:
    print()
    print("TITLE :", job["title"])
    print("URL   :", job["url"])


print()
print("=" * 60)