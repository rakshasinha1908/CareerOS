from app.adapters.workday import WorkdayAdapter


def main():
    adapter = WorkdayAdapter()

    company_config = {
        "name": "Adobe",
        "platform": "workday",
        "career_url": (
            "https://adobe.wd5.myworkdayjobs.com/"
            "external_experienced"
        ),
    }

    print("=" * 60)
    print("WORKDAY ADAPTER TEST")
    print("=" * 60)

    jobs = adapter.discover_jobs(
        company_config
    )

    print()
    print(f"JOBS FOUND: {len(jobs)}")
    print()

    for index, job in enumerate(
        jobs[:10],
        start=1,
    ):
        print(f"{index}. {job.title}")
        print(f"   URL       : {job.job_url}")
        print(f"   LOCATION  : {job.location}")
        print(f"   SOURCE    : {job.source}")
        print(f"   SOURCE ID : {job.source_job_id}")
        print()


if __name__ == "__main__":
    main()