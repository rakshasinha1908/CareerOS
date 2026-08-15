import { useMemo, useState } from "react";
import "../styles/opportunities-page.css";

type Job = {
  id: string;
  company_id: string;
  title: string;
  location: string | null;
  url: string;
  description: string | null;
  employment_type: string | null;
  experience_level: string | null;
  posted_at: string | null;
  discovered_at: string;
  created_at: string;
  updated_at: string;
};

const initialJobs: Job[] = [
  {
    id: "1",
    company_id: "company-1",
    title: "Junior Software Engineer",
    location: "Bengaluru, India",
    url: "https://example.com/jobs/software-engineer",
    description:
      "Build backend systems using Python and FastAPI. Work with APIs, databases, and distributed systems.",
    employment_type: "Full-time",
    experience_level: "Entry",
    posted_at: "2026-08-13T17:14:45.611Z",
    discovered_at: "2026-08-13T17:11:08.372173Z",
    created_at: "2026-08-13T17:11:08.372173Z",
    updated_at: "2026-08-13T17:20:19.683851Z",
  },
  {
    id: "2",
    company_id: "company-2",
    title: "Software Development Engineer",
    location: "Noida, India",
    url: "https://example.com/jobs/sde",
    description:
      "Develop scalable software systems and work closely with engineering teams.",
    employment_type: "Full-time",
    experience_level: "Entry",
    posted_at: "2026-08-12T10:00:00.000Z",
    discovered_at: "2026-08-13T11:00:00.000Z",
    created_at: "2026-08-13T11:00:00.000Z",
    updated_at: "2026-08-13T11:00:00.000Z",
  },
];

function formatDate(value: string | null) {
  if (!value) {
    return "Not specified";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Not specified";
  }

  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function OpportunitiesPage() {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);

  const [search, setSearch] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [experienceFilter, setExperienceFilter] =
    useState("Any experience");
  const [employmentFilter, setEmploymentFilter] =
    useState("Any employment");

  const [selectedJob, setSelectedJob] = useState<Job | null>(
    initialJobs[0] ?? null,
  );

  const filteredJobs = useMemo(() => {
    const query = search.trim().toLowerCase();
    const locationQuery = locationFilter.trim().toLowerCase();

    return jobs.filter((job) => {
      const searchableText = [
        job.title,
        job.location ?? "",
        job.description ?? "",
        job.employment_type ?? "",
        job.experience_level ?? "",
      ]
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        !query || searchableText.includes(query);

      const matchesLocation =
        !locationQuery ||
        (job.location ?? "")
          .toLowerCase()
          .includes(locationQuery);

      const matchesExperience =
        experienceFilter === "Any experience" ||
        job.experience_level === experienceFilter;

      const matchesEmployment =
        employmentFilter === "Any employment" ||
        job.employment_type === employmentFilter;

      return (
        matchesSearch &&
        matchesLocation &&
        matchesExperience &&
        matchesEmployment
      );
    });
  }, [
    jobs,
    search,
    locationFilter,
    experienceFilter,
    employmentFilter,
  ]);

  const clearFilters = () => {
    setSearch("");
    setLocationFilter("");
    setExperienceFilter("Any experience");
    setEmploymentFilter("Any employment");
  };

  const activeFilterCount =
    Number(Boolean(locationFilter)) +
    Number(experienceFilter !== "Any experience") +
    Number(employmentFilter !== "Any employment");

  const selectJob = (job: Job) => {
    setSelectedJob(job);
  };

  return (
    <div className="opportunities-page">
      <header className="opportunities-header">
        <div>
          <p className="opportunities-eyebrow">
            OPPORTUNITIES
          </p>

          <h1>Find your next move.</h1>

          <p className="opportunities-description">
            Jobs discovered from the career pages you're
            tracking.
          </p>
        </div>

        <div className="opportunities-header-meta">
          <strong>{jobs.length}</strong>
          <span>opportunities</span>
        </div>
      </header>

      <section className="opportunities-search-row">
        <div className="opportunities-main-search">
          <span>⌕</span>

          <input
            type="search"
            placeholder="Search jobs, companies, skills..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>
      </section>

      <section className="opportunities-filter-panel">
        <div className="opportunities-filter-group">
          <label htmlFor="location-filter">
            Location
          </label>

          <input
            id="location-filter"
            type="text"
            placeholder="e.g. Delhi"
            value={locationFilter}
            onChange={(event) =>
              setLocationFilter(event.target.value)
            }
          />
        </div>

        <div className="opportunities-filter-group">
          <label htmlFor="experience-filter">
            Experience
          </label>

          <select
            id="experience-filter"
            value={experienceFilter}
            onChange={(event) =>
              setExperienceFilter(event.target.value)
            }
          >
            <option>Any experience</option>
            <option>Entry</option>
            <option>0–2 years</option>
            <option>1–3 years</option>
            <option>3–5 years</option>
            <option>Mid</option>
            <option>Senior</option>
          </select>
        </div>

        <div className="opportunities-filter-group">
          <label htmlFor="employment-filter">
            Employment
          </label>

          <select
            id="employment-filter"
            value={employmentFilter}
            onChange={(event) =>
              setEmploymentFilter(event.target.value)
            }
          >
            <option>Any employment</option>
            <option>Full-time</option>
            <option>Part-time</option>
            <option>Contract</option>
            <option>Internship</option>
          </select>
        </div>
      </section>

      <div className="opportunities-results-bar">
        <div>
          <strong>
            {filteredJobs.length}{" "}
            {filteredJobs.length === 1
              ? "result"
              : "results"}
          </strong>

          {activeFilterCount > 0 && (
            <span>
              {activeFilterCount} active{" "}
              {activeFilterCount === 1
                ? "filter"
                : "filters"}
            </span>
          )}
        </div>

        {activeFilterCount > 0 && (
          <button
            type="button"
            onClick={clearFilters}
          >
            Clear filters
          </button>
        )}
      </div>

      <section className="opportunities-layout">
        <div className="opportunities-list">
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => (
              <article
                className={`opportunity-card ${
                  selectedJob?.id === job.id
                    ? "selected"
                    : ""
                }`}
                key={job.id}
                onClick={() => selectJob(job)}
              >
                <div className="opportunity-card-main">
                  <div className="opportunity-company-mark">
                    {job.title
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div className="opportunity-card-info">
                    <div className="opportunity-title-row">
                      <h2>{job.title}</h2>
                    </div>

                    <p className="opportunity-company">
                      Company
                    </p>

                    <div className="opportunity-meta">
                      {job.location && (
                        <>
                          <span>{job.location}</span>
                          <span>•</span>
                        </>
                      )}

                      {job.employment_type && (
                        <>
                          <span>
                            {job.employment_type}
                          </span>
                          <span>•</span>
                        </>
                      )}

                      <span>
                        {formatDate(job.posted_at)}
                      </span>
                    </div>

                    {job.experience_level && (
                      <div className="opportunity-tags">
                        <span>
                          {job.experience_level}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="opportunity-card-side">
                  <button
                    type="button"
                    className="opportunity-open-link"
                    onClick={(event) => {
                      event.stopPropagation();
                      window.open(
                        job.url,
                        "_blank",
                        "noopener,noreferrer",
                      );
                    }}
                  >
                    View job →
                  </button>
                </div>
              </article>
            ))
          ) : (
            <div className="opportunities-empty">
              <div className="opportunities-empty-icon">
                ⌕
              </div>

              <h2>No opportunities found</h2>

              <p>
                Try adjusting your search or filters to
                see more roles.
              </p>

              <button
                type="button"
                onClick={clearFilters}
              >
                Clear filters
              </button>
            </div>
          )}
        </div>

        <aside className="opportunity-detail-panel">
          {selectedJob ? (
            <>
              <div className="opportunity-detail-header">
                <div className="opportunity-detail-company-mark">
                  {selectedJob.title
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <button
                  type="button"
                  className="opportunity-detail-close"
                  onClick={() =>
                    setSelectedJob(null)
                  }
                  aria-label="Close opportunity details"
                >
                  ×
                </button>
              </div>

              <div className="opportunity-detail-content">
                <p className="opportunity-detail-eyebrow">
                  JOB OPPORTUNITY
                </p>

                <h2>{selectedJob.title}</h2>

                <p className="opportunity-detail-company">
                  Company
                </p>

                {selectedJob.location && (
                  <div className="opportunity-detail-location">
                    <span>
                      {selectedJob.location}
                    </span>
                  </div>
                )}

                <div className="opportunity-detail-grid">
                  <div>
                    <span>Experience</span>
                    <strong>
                      {selectedJob.experience_level ??
                        "Not specified"}
                    </strong>
                  </div>

                  <div>
                    <span>Employment</span>
                    <strong>
                      {selectedJob.employment_type ??
                        "Not specified"}
                    </strong>
                  </div>

                  <div>
                    <span>Posted</span>
                    <strong>
                      {formatDate(
                        selectedJob.posted_at,
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Discovered</span>
                    <strong>
                      {formatDate(
                        selectedJob.discovered_at,
                      )}
                    </strong>
                  </div>
                </div>

                <div className="opportunity-detail-section">
                  <h3>Description</h3>

                  <p className="opportunity-description">
                    {selectedJob.description ??
                      "No description available."}
                  </p>
                </div>

                <div className="opportunity-detail-section">
                  <h3>Company</h3>

                  <p className="opportunity-company-id">
                    {selectedJob.company_id}
                  </p>
                </div>
              </div>

              <div className="opportunity-detail-actions">
                <button
                  type="button"
                  className="opportunity-detail-apply"
                  onClick={() =>
                    window.open(
                      selectedJob.url,
                      "_blank",
                      "noopener,noreferrer",
                    )
                  }
                >
                  Open job posting
                </button>
              </div>
            </>
          ) : (
            <div className="opportunity-detail-empty">
              <div>↖</div>

              <h3>Select an opportunity</h3>

              <p>
                Choose a role from the list to see its
                details.
              </p>
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}

export default OpportunitiesPage;