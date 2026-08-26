import requests


BASE_URL = "https://apply.careers.microsoft.com"

URL = (
    f"{BASE_URL}/api/pcsx/search"
    "?domain=microsoft.com"
    "&query="
    "&location="
    "&start=0"
    "&num=10"
)


def main():
    print()
    print("=" * 60)
    print("MICROSOFT PCSX JOB SEARCH")
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
            ),
            "Accept": "application/json",
        },
    )

    print(f"STATUS : {response.status_code}")
    print(f"URL    : {response.url}")
    print(f"LENGTH : {len(response.text)}")

    print()
    print("=" * 60)
    print("RAW RESPONSE")
    print("=" * 60)

    print(response.text[:5000])

    if response.status_code != 200:
        print()
        print("❌ PCSX request failed.")
        return

    try:
        data = response.json()
    except ValueError:
        print()
        print("❌ Response was not valid JSON.")
        return

    print()
    print("=" * 60)
    print("RESPONSE STRUCTURE")
    print("=" * 60)

    print(
        "Top-level keys:",
        list(data.keys()),
    )

    payload = data.get("data", data)

    if not isinstance(payload, dict):
        print()
        print("❌ Could not find response payload.")
        return

    print(
        "Payload keys:",
        list(payload.keys()),
    )

    positions = payload.get(
        "positions",
        [],
    )

    count = payload.get(
        "count"
    )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print(
        f"TOTAL COUNT : {count}"
    )

    print(
        f"RETURNED    : {len(positions)}"
    )

    print()

    for index, job in enumerate(
        positions,
        start=1,
    ):
        print(
            f"--- JOB {index} ---"
        )

        print(
            "ID       :",
            job.get("id"),
        )

        print(
            "TITLE    :",
            job.get("title"),
        )

        print(
            "LOCATION :",
            job.get("primaryLocation")
            or job.get("primary_location"),
        )

        print(
            "WORK MODE:",
            job.get("workLocationOption")
            or job.get("work_location_option"),
        )

        print(
            "JOB URL  :",
            f"{BASE_URL}/careers?pid={job.get('id')}",
        )

        print()


if __name__ == "__main__":
    main()