from app.adapters.greenhouse import GreenhouseAdapter


def main():
    adapter = GreenhouseAdapter()

    company_config = {
        "name": "Razorpay",
        "platform": "greenhouse",
        "board_token": "razorpaysoftwareprivatelimited",
    }

    print("=" * 60)
    print("GREENHOUSE ADAPTER TEST")
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
        print(f"   DEPARTMENT: {job.department}")
        print(f"   SOURCE ID : {job.source_job_id}")
        print()


if __name__ == "__main__":
    main()