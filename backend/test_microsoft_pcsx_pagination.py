import time

import requests


API_URL = "https://apply.careers.microsoft.com/api/pcsx/search"

MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 3
PAGE_DELAY_SECONDS = 1.5


def fetch_page(start: int, num: int = 10):
    params = {
        "domain": "microsoft.com",
        "query": "",
        "location": "",
        "start": start,
        "num": num,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        response = requests.get(
            API_URL,
            params=params,
            timeout=30,
        )

        if response.status_code == 429:
            if attempt == MAX_RETRIES:
                response.raise_for_status()

            wait_time = RETRY_DELAY_SECONDS * attempt

            print(
                f"Rate limited at start={start}. "
                f"Retrying in {wait_time}s..."
            )

            time.sleep(wait_time)
            continue

        response.raise_for_status()

        return response.json()

    raise RuntimeError(f"Unable to fetch page at start={start}")


def main():
    print()
    print("=" * 60)
    print("MICROSOFT PAGINATION VALIDATION")
    print("=" * 60)

    page_size = 10
    start = 0

    seen_ids = set()
    duplicate_ids = set()

    api_total = None
    pages_fetched = 0

    while True:
        payload = fetch_page(start, page_size)

        data = payload.get("data", {})
        positions = data.get("positions", [])

        if api_total is None:
            api_total = data.get("count")

        if not positions:
            break

        pages_fetched += 1

        for job in positions:
            job_id = job.get("id")

            if job_id in seen_ids:
                duplicate_ids.add(job_id)
            else:
                seen_ids.add(job_id)

        # Don't hammer Microsoft's endpoint.
        time.sleep(PAGE_DELAY_SECONDS)

        start += page_size

        if api_total is not None and len(seen_ids) >= api_total:
            break

    print()
    print("-" * 60)
    print(f"API TOTAL        : {api_total}")
    print(f"JOBS FETCHED     : {len(seen_ids)}")
    print(f"DUPLICATE IDS    : {len(duplicate_ids)}")
    print(f"PAGES FETCHED    : {pages_fetched}")
    print("-" * 60)

    print()

    if (
        api_total is not None
        and len(seen_ids) == api_total
        and len(duplicate_ids) == 0
    ):
        print("STATUS           : PASS")
        print("Pagination successfully fetched all unique jobs.")
    else:
        print("STATUS           : CHECK")
        print("Pagination did not exactly match the API total.")

    print()


if __name__ == "__main__":
    main()