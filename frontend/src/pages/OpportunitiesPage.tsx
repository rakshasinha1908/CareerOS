import { useMemo, useState } from "react";
import "../styles/opportunities-page.css";

type Opportunity = {
  id: number;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  experience: string;
  source: string;
  posted: string;
  salary: string;
  match: number;
  status: "New" | "Saved" | "Applied";
  tags: string[];
};

const initialOpportunities: Opportunity[] = [
  {
    id: 1,
    title: "Software Engineer — Backend",
    company: "Microsoft",
    location: "Noida, India",
    remote: true,
    experience: "0–2 years",
    source: "Microsoft Careers",
    posted: "2 hours ago",
    salary: "₹12–18 LPA",
    match: 94,
    status: "New",
    tags: ["Python", "FastAPI", "PostgreSQL"],
  },
  {
    id: 2,
    title: "Software Development Engineer",
    company: "Razorpay",
    location: "Bengaluru, India",
    remote: false,
    experience: "0–2 years",
    source: "Razorpay Careers",
    posted: "5 hours ago",
    salary: "₹10–16 LPA",
    match: 91,
    status: "New",
    tags: ["Java", "Backend", "REST APIs"],
  },
  {
    id: 3,
    title: "Frontend Engineer",
    company: "Atlassian",
    location: "Bengaluru, India",
    remote: true,
    experience: "0–2 years",
    source: "Atlassian Careers",
    posted: "Yesterday",
    salary: "₹14–22 LPA",
    match: 88,
    status: "Saved",
    tags: ["React", "TypeScript", "CSS"],
  },
  {
    id: 4,
    title: "Full Stack Engineer",
    company: "Linear",
    location: "Remote",
    remote: true,
    experience: "1–3 years",
    source: "Company Career Page",
    posted: "Yesterday",
    salary: "Not disclosed",
    match: 86,
    status: "New",
    tags: ["React", "Node.js", "TypeScript"],
  },
  {
    id: 5,
    title: "Software Engineer — Platform",
    company: "Stripe",
    location: "Bengaluru, India",
    remote: false,
    experience: "1–3 years",
    source: "Stripe Careers",
    posted: "2 days ago",
    salary: "₹16–25 LPA",
    match: 82,
    status: "Applied",
    tags: ["Python", "Distributed Systems", "APIs"],
  },
  {
    id: 6,
    title: "AI Engineer",
    company: "Y Combinator Startup",
    location: "Remote",
    remote: true,
    experience: "0–2 years",
    source: "Y Combinator Jobs",
    posted: "2 days ago",
    salary: "₹8–14 LPA",
    match: 79,
    status: "New",
    tags: ["Python", "LLMs", "Machine Learning"],
  },
];

const roleFilters = [
  "All roles",
  "Software Engineer",
  "Backend",
  "Frontend",
  "Full Stack",
  "AI Engineer",
];

const experienceFilters = [
  "Any experience",
  "0–2 years",
  "1–3 years",
  "3–5 years",
];

const sourceFilters = [
  "All sources",
  "Microsoft Careers",
  "Razorpay Careers",
  "Atlassian Careers",
  "Company Career Page",
  "Stripe Careers",
  "Y Combinator Jobs",
];

function getRoleCategory(title: string) {
  const value = title.toLowerCase();

  if (value.includes("backend")) {
    return "Backend";
  }

  if (value.includes("frontend")) {
    return "Frontend";
  }

  if (value.includes("full stack")) {
    return "Full Stack";
  }

  if (value.includes("ai")) {
    return "AI Engineer";
  }

  return "Software Engineer";
}

function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState(
    initialOpportunities,
  );

  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("All roles");
  const [location, setLocation] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [experienceFilter, setExperienceFilter] =
    useState("Any experience");
  const [sourceFilter, setSourceFilter] =
    useState("All sources");
  const [minMatch, setMinMatch] = useState(0);

  const [selectedOpportunity, setSelectedOpportunity] =
    useState<Opportunity | null>(null);

  const filteredOpportunities = useMemo(() => {
    const query = search.trim().toLowerCase();
    const locationQuery = location.trim().toLowerCase();

    return opportunities.filter((opportunity) => {
      const searchableText = [
        opportunity.title,
        opportunity.company,
        opportunity.location,
        opportunity.source,
        ...opportunity.tags,
      ]
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        !query || searchableText.includes(query);

      const matchesRole =
        roleFilter === "All roles" ||
        getRoleCategory(opportunity.title) === roleFilter;

      const matchesLocation =
        !locationQuery ||
        opportunity.location
          .toLowerCase()
          .includes(locationQuery);

      const matchesRemote =
        !remoteOnly || opportunity.remote;

      const matchesExperience =
        experienceFilter === "Any experience" ||
        opportunity.experience === experienceFilter;

      const matchesSource =
        sourceFilter === "All sources" ||
        opportunity.source === sourceFilter;

      const matchesScore =
        opportunity.match >= minMatch;

      return (
        matchesSearch &&
        matchesRole &&
        matchesLocation &&
        matchesRemote &&
        matchesExperience &&
        matchesSource &&
        matchesScore
      );
    });
  }, [
    opportunities,
    search,
    roleFilter,
    location,
    remoteOnly,
    experienceFilter,
    sourceFilter,
    minMatch,
  ]);

  const toggleSaved = (id: number) => {
    setOpportunities((current) =>
      current.map((opportunity) =>
        opportunity.id === id
          ? {
              ...opportunity,
              status:
                opportunity.status === "Saved"
                  ? "New"
                  : "Saved",
            }
          : opportunity,
      ),
    );

    setSelectedOpportunity((current) =>
      current?.id === id
        ? {
            ...current,
            status:
              current.status === "Saved"
                ? "New"
                : "Saved",
          }
        : current,
    );
  };

  const markApplied = (id: number) => {
    setOpportunities((current) =>
      current.map((opportunity) =>
        opportunity.id === id
          ? {
              ...opportunity,
              status: "Applied",
            }
          : opportunity,
      ),
    );

    setSelectedOpportunity((current) =>
      current?.id === id
        ? {
            ...current,
            status: "Applied",
          }
        : current,
    );
  };

  const clearFilters = () => {
    setSearch("");
    setRoleFilter("All roles");
    setLocation("");
    setRemoteOnly(false);
    setExperienceFilter("Any experience");
    setSourceFilter("All sources");
    setMinMatch(0);
  };

  const activeFilterCount =
    Number(roleFilter !== "All roles") +
    Number(Boolean(location)) +
    Number(remoteOnly) +
    Number(experienceFilter !== "Any experience") +
    Number(sourceFilter !== "All sources") +
    Number(minMatch > 0);

  return (
    <div className="opportunities-page">
      <header className="opportunities-header">
        <div>
          <p className="opportunities-eyebrow">
            OPPORTUNITIES
          </p>

          <h1>Find your next move.</h1>

          <p className="opportunities-description">
            Roles discovered from your career sources and matched
            against your preferences.
          </p>
        </div>

        <div className="opportunities-header-meta">
          <strong>{opportunities.length}</strong>
          <span>opportunities</span>
        </div>
      </header>

      <section className="opportunities-search-row">
        <div className="opportunities-main-search">
          <span>⌕</span>

          <input
            type="search"
            placeholder="Search roles, companies, skills..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>
      </section>

      <section className="opportunities-filter-panel">
        <div className="opportunities-filter-group">
          <label htmlFor="role-filter">Role</label>

          <select
            id="role-filter"
            value={roleFilter}
            onChange={(event) =>
              setRoleFilter(event.target.value)
            }
          >
            {roleFilters.map((filter) => (
              <option key={filter}>{filter}</option>
            ))}
          </select>
        </div>

        <div className="opportunities-filter-group">
          <label htmlFor="location-filter">Location</label>

          <input
            id="location-filter"
            type="text"
            placeholder="e.g. Delhi"
            value={location}
            onChange={(event) =>
              setLocation(event.target.value)
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
            {experienceFilters.map((filter) => (
              <option key={filter}>{filter}</option>
            ))}
          </select>
        </div>

        <div className="opportunities-filter-group">
          <label htmlFor="source-filter">Source</label>

          <select
            id="source-filter"
            value={sourceFilter}
            onChange={(event) =>
              setSourceFilter(event.target.value)
            }
          >
            {sourceFilters.map((filter) => (
              <option key={filter}>{filter}</option>
            ))}
          </select>
        </div>

        <label className="opportunities-remote-toggle">
          <input
            type="checkbox"
            checked={remoteOnly}
            onChange={(event) =>
              setRemoteOnly(event.target.checked)
            }
          />

          <span className="opportunities-toggle-track">
            <span />
          </span>

          Remote only
        </label>

        <div className="opportunities-match-filter">
          <label htmlFor="match-filter">
            Match
          </label>

          <select
            id="match-filter"
            value={minMatch}
            onChange={(event) =>
              setMinMatch(Number(event.target.value))
            }
          >
            <option value={0}>Any match</option>
            <option value={80}>80%+</option>
            <option value={85}>85%+</option>
            <option value={90}>90%+</option>
          </select>
        </div>
      </section>

      <div className="opportunities-results-bar">
        <div>
          <strong>
            {filteredOpportunities.length}{" "}
            {filteredOpportunities.length === 1
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
          {filteredOpportunities.length > 0 ? (
            filteredOpportunities.map((opportunity) => (
              <article
                className={`opportunity-card ${
                  selectedOpportunity?.id === opportunity.id
                    ? "selected"
                    : ""
                }`}
                key={opportunity.id}
                onClick={() =>
                  setSelectedOpportunity(opportunity)
                }
              >
                <div className="opportunity-card-main">
                  <div className="opportunity-company-mark">
                    {opportunity.company
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div className="opportunity-card-info">
                    <div className="opportunity-title-row">
                      <h2>{opportunity.title}</h2>

                      {opportunity.status !== "New" && (
                        <span
                          className={`opportunity-status ${
                            opportunity.status.toLowerCase()
                          }`}
                        >
                          {opportunity.status}
                        </span>
                      )}
                    </div>

                    <p className="opportunity-company">
                      {opportunity.company}
                    </p>

                    <div className="opportunity-meta">
                      <span>
                        {opportunity.location}
                      </span>

                      <span>•</span>

                      <span>
                        {opportunity.experience}
                      </span>

                      <span>•</span>

                      <span>
                        {opportunity.posted}
                      </span>
                    </div>

                    <div className="opportunity-tags">
                      {opportunity.tags.map((tag) => (
                        <span key={tag}>{tag}</span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="opportunity-card-side">
                  <div
                    className={`opportunity-match match-${Math.floor(
                      opportunity.match / 5,
                    ) * 5}`}
                  >
                    <strong>
                      {opportunity.match}%
                    </strong>

                    <span>match</span>
                  </div>

                  <button
                    type="button"
                    className={`opportunity-save ${
                      opportunity.status === "Saved"
                        ? "saved"
                        : ""
                    }`}
                    onClick={(event) => {
                      event.stopPropagation();
                      toggleSaved(opportunity.id);
                    }}
                    aria-label={
                      opportunity.status === "Saved"
                        ? "Remove from saved"
                        : "Save opportunity"
                    }
                  >
                    {opportunity.status === "Saved"
                      ? "★"
                      : "☆"}
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
                Try adjusting your search or filters to see
                more roles.
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
          {selectedOpportunity ? (
            <>
              <div className="opportunity-detail-header">
                <div className="opportunity-detail-company-mark">
                  {selectedOpportunity.company
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <button
                  type="button"
                  className="opportunity-detail-close"
                  onClick={() =>
                    setSelectedOpportunity(null)
                  }
                  aria-label="Close opportunity details"
                >
                  ×
                </button>
              </div>

              <div className="opportunity-detail-content">
                <p className="opportunity-detail-eyebrow">
                  {selectedOpportunity.source}
                </p>

                <h2>{selectedOpportunity.title}</h2>

                <p className="opportunity-detail-company">
                  {selectedOpportunity.company}
                </p>

                <div className="opportunity-detail-location">
                  <span>
                    {selectedOpportunity.location}
                  </span>

                  {selectedOpportunity.remote && (
                    <span className="remote-badge">
                      Remote
                    </span>
                  )}
                </div>

                <div className="opportunity-detail-match">
                  <div>
                    <span>CareerOS match</span>
                    <strong>
                      {selectedOpportunity.match}%
                    </strong>
                  </div>

                  <div className="match-bar">
                    <span
                      style={{
                        width: `${selectedOpportunity.match}%`,
                      }}
                    />
                  </div>

                  <p>
                    Strong alignment with your role,
                    experience, and skills preferences.
                  </p>
                </div>

                <div className="opportunity-detail-grid">
                  <div>
                    <span>Experience</span>
                    <strong>
                      {selectedOpportunity.experience}
                    </strong>
                  </div>

                  <div>
                    <span>Salary</span>
                    <strong>
                      {selectedOpportunity.salary}
                    </strong>
                  </div>

                  <div>
                    <span>Posted</span>
                    <strong>
                      {selectedOpportunity.posted}
                    </strong>
                  </div>

                  <div>
                    <span>Source</span>
                    <strong>
                      {selectedOpportunity.source}
                    </strong>
                  </div>
                </div>

                <div className="opportunity-detail-section">
                  <h3>Why this matches</h3>

                  <div className="opportunity-detail-tags">
                    {selectedOpportunity.tags.map(
                      (tag) => (
                        <span key={tag}>{tag}</span>
                      ),
                    )}
                  </div>
                </div>
              </div>

              <div className="opportunity-detail-actions">
                <button
                  type="button"
                  className="opportunity-detail-save"
                  onClick={() =>
                    toggleSaved(
                      selectedOpportunity.id,
                    )
                  }
                >
                  {selectedOpportunity.status ===
                  "Saved"
                    ? "Remove from saved"
                    : "Save opportunity"}
                </button>

                <button
                  type="button"
                  className="opportunity-detail-apply"
                  onClick={() =>
                    markApplied(
                      selectedOpportunity.id,
                    )
                  }
                  disabled={
                    selectedOpportunity.status ===
                    "Applied"
                  }
                >
                  {selectedOpportunity.status ===
                  "Applied"
                    ? "Applied"
                    : "Mark as applied"}
                </button>
              </div>
            </>
          ) : (
            <div className="opportunity-detail-empty">
              <div>↖</div>

              <h3>Select an opportunity</h3>

              <p>
                Choose a role from the list to see its details,
                match score, and actions.
              </p>
            </div>
          )}
        </aside>
      </section>
    </div>
  );
}

export default OpportunitiesPage;