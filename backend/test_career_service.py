from app.services.career_service import discover_jobs


career_url = (
    "https://www.google.com/about/careers/applications/jobs/results"
)


jobs = discover_jobs(career_url)


print()
print("=" * 60)
print(f"FOUND {len(jobs)} CANDIDATE JOBS")
print("=" * 60)

for job in jobs[:20]:
    print()
    print("TITLE :", job.title)
    print("URL   :", job.url)

print()
print("=" * 60)