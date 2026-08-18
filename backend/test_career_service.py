from pathlib import Path
import re


html = Path(
    "google_careers_response.html"
).read_text(
    encoding="utf-8"
)

matches = list(
    re.finditer(
        r"/jobs/results/",
        html,
        flags=re.IGNORECASE,
    )
)

print()
print("=" * 60)
print(f"Found {len(matches)} occurrences")
print("=" * 60)

for index, match in enumerate(matches, start=1):
    start = max(0, match.start() - 500)
    end = min(
        len(html),
        match.end() + 1000,
    )

    print()
    print("-" * 60)
    print(f"OCCURRENCE {index}")
    print("-" * 60)
    print(html[start:end])