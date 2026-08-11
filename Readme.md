# CareerOS

> A personal career operating system for managing the entire job search in one place.

CareerOS is being built to solve a simple problem:

**job searching shouldn't feel like managing 20 different tabs, spreadsheets, bookmarks, and reminders.**

It brings job discovery, matching, applications, companies, contacts, documents, and follow-ups into one system.

## Vision

CareerOS is designed around the complete job-search loop:

```text
Profile & Preferences
        ↓
Companies & Career Sources
        ↓
Job Discovery
        ↓
Normalization & Deduplication
        ↓
Job Matching
        ↓
Save / Apply
        ↓
Application Tracking
        ↓
Follow-ups & Notifications
````

The long-term goal is to make CareerOS an intelligent system that continuously helps manage and prioritize a person's career opportunities.

---

## V0

CareerOS V0 is being built primarily as a **single-user application** to solve my own job-search problem first.

Authentication and multi-user functionality are intentionally deferred.

However, the underlying architecture is being designed so that multi-user support can be added later without rebuilding the core system.

### V0 roadmap

| Day | Focus                             | Goal                                                  |
| --- | --------------------------------- | ----------------------------------------------------- |
| 1   | Foundation                        | Database, models, API skeleton, single-user bootstrap |
| 2   | Profile + Preferences + Companies | Manage personal career data through the UI            |
| 3   | Career Sources                    | Add and validate career-page URLs                     |
| 4   | Scraping Engine                   | Fetch, normalize and deduplicate jobs                 |
| 5   | Job Engine                        | Store jobs and detect new opportunities               |
| 6   | Matching                          | Surface relevant jobs with reasoning                  |
| 7   | Applications                      | Save, apply and track application timelines           |
| 8   | Notifications + Dashboard         | Surface what needs attention                          |
| 9   | Contacts + Documents + Insights   | Organize the broader job-search workflow              |
| 10  | Testing + Deployment              | Stable enough for daily use                           |

---

## Architecture

CareerOS separates shared career data from user-specific state.

For example, if multiple users monitor Amazon:

```text
                 Amazon
                    │
             Career Source
                    │
              Job #12345
                    │
        ┌───────────┼───────────┐
        │           │           │
      User A      User B      User C
        │           │           │
      Match       Match       Match
        │           │           │
      Saved       Applied     Ignored
```

The underlying job is stored once.

User-specific information such as matching, saved state, applications and notes belongs to the user.

This avoids duplicating the same job for every user.

---

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL

### Frontend

* React
* TypeScript
* Vite

### Infrastructure

The MVP prioritizes a **₹0/month recurring running cost**.

The architecture therefore favors:

* Free tiers
* Open-source tools
* Serverless / scheduled execution
* Local development infrastructure
* Efficient scraping
* Selective AI usage

Paid infrastructure will only be introduced if real usage eventually requires it.

---

## Current Status

**V0 — In active development**

Currently completed:

* Repository setup
* Frontend foundation
* Backend foundation
* PostgreSQL database
* SQLAlchemy configuration
* Alembic migrations
* Single-user bootstrap
* Profile API
* Job preferences API
* Company API

Next:

**Profile + Preferences + Companies UI**

---

## Project Structure

```text
CareerOS/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   │
│   └── migrations/
│
├── frontend/
│
└── README.md
```

---

## Development

### Backend

```bash
cd backend

python -m venv .venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Database migrations

Create a migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```

Check migration state:

```bash
alembic current
```

---

## Project Philosophy

CareerOS is being built with a few principles:

* **Solve the real problem first.**
* **Keep the MVP simple.**
* **Don't hardcode personal data.**
* **Prefer generic systems over dataset-specific hacks.**
* **Store shared data once.**
* **Keep user-specific state separate.**
* **Use AI selectively where it adds real value.**
* **Optimize for reliability before complexity.**
* **Design V0 so it can grow into a multi-user product.**

---

## Status

🚧 CareerOS is currently under active development.

Built initially as a personal tool, with the architecture intentionally designed to evolve beyond a single-user MVP.
