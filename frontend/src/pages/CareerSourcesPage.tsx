import { useMemo, useState } from "react";
import "../styles/career-sources-page.css";

type SourceType =
  | "Company Career Page"
  | "Job Board"
  | "Startup Board";

type SourceStatus = "Active" | "Paused" | "Needs Attention";

type CareerSource = {
  id: number;
  name: string;
  type: SourceType;
  url: string;
  status: SourceStatus;
  lastSync: string;
  jobsFound: number;
  description: string;
};

const initialSources: CareerSource[] = [
  {
    id: 1,
    name: "Microsoft Careers",
    type: "Company Career Page",
    url: "careers.microsoft.com",
    status: "Active",
    lastSync: "18 min ago",
    jobsFound: 42,
    description: "Software engineering and AI roles.",
  },
  {
    id: 2,
    name: "Y Combinator Jobs",
    type: "Startup Board",
    url: "ycombinator.com/jobs",
    status: "Active",
    lastSync: "34 min ago",
    jobsFound: 27,
    description: "Engineering roles from YC startups.",
  },
  {
    id: 3,
    name: "Wellfound",
    type: "Job Board",
    url: "wellfound.com/jobs",
    status: "Active",
    lastSync: "1 hr ago",
    jobsFound: 61,
    description: "Startup and technology opportunities.",
  },
  {
    id: 4,
    name: "Atlassian Careers",
    type: "Company Career Page",
    url: "atlassian.com/company/careers",
    status: "Paused",
    lastSync: "Yesterday",
    jobsFound: 18,
    description: "Engineering and platform roles.",
  },
  {
    id: 5,
    name: "Stripe Careers",
    type: "Company Career Page",
    url: "stripe.com/jobs",
    status: "Needs Attention",
    lastSync: "2 days ago",
    jobsFound: 12,
    description: "Backend and infrastructure opportunities.",
  },
];

const sourceTypes = [
  "All source types",
  "Company Career Page",
  "Job Board",
  "Startup Board",
];

const emptySource: Omit<CareerSource, "id"> = {
  name: "",
  type: "Company Career Page",
  url: "",
  status: "Active",
  lastSync: "Never",
  jobsFound: 0,
  description: "",
};

function CareerSourcesPage() {
  const [sources, setSources] = useState(initialSources);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All source types");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSource, setEditingSource] =
    useState<CareerSource | null>(null);

  const [form, setForm] = useState(emptySource);

  const filteredSources = useMemo(() => {
    const query = search.trim().toLowerCase();

    return sources.filter((source) => {
      const matchesSearch =
        !query ||
        source.name.toLowerCase().includes(query) ||
        source.url.toLowerCase().includes(query) ||
        source.description.toLowerCase().includes(query);

      const matchesType =
        typeFilter === "All source types" ||
        source.type === typeFilter;

      return matchesSearch && matchesType;
    });
  }, [sources, search, typeFilter]);

  const activeSources = sources.filter(
    (source) => source.status === "Active",
  ).length;

  const totalJobsFound = sources.reduce(
    (total, source) => total + source.jobsFound,
    0,
  );

  const needsAttention = sources.filter(
    (source) => source.status === "Needs Attention",
  ).length;

  const openAddModal = () => {
    setEditingSource(null);
    setForm(emptySource);
    setIsModalOpen(true);
  };

  const openEditModal = (source: CareerSource) => {
    setEditingSource(source);

    setForm({
      name: source.name,
      type: source.type,
      url: source.url,
      status: source.status,
      lastSync: source.lastSync,
      jobsFound: source.jobsFound,
      description: source.description,
    });

    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingSource(null);
    setForm(emptySource);
  };

  const updateForm = (
    field: keyof typeof emptySource,
    value: string,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSave = () => {
    if (!form.name.trim() || !form.url.trim()) {
      return;
    }

    if (editingSource) {
      setSources((current) =>
        current.map((source) =>
          source.id === editingSource.id
            ? {
                ...source,
                ...form,
                name: form.name.trim(),
                url: form.url.trim(),
              }
            : source,
        ),
      );
    } else {
      setSources((current) => [
        ...current,
        {
          id: Date.now(),
          ...form,
          name: form.name.trim(),
          url: form.url.trim(),
        },
      ]);
    }

    closeModal();
  };

  const toggleSource = (id: number) => {
    setSources((current) =>
      current.map((source) => {
        if (source.id !== id) {
          return source;
        }

        return {
          ...source,
          status:
            source.status === "Active"
              ? "Paused"
              : "Active",
        };
      }),
    );
  };

  const handleDelete = (id: number) => {
    setSources((current) =>
      current.filter((source) => source.id !== id),
    );
  };

  return (
    <div className="career-sources-page">
      <header className="career-sources-header">
        <div>
          <p className="career-sources-eyebrow">
            CAREER SOURCES
          </p>

          <h1>Career Sources</h1>

          <p className="career-sources-description">
            Manage the places CareerOS checks for new
            opportunities.
          </p>
        </div>

        <button
          type="button"
          className="career-sources-add-button"
          onClick={openAddModal}
        >
          <span>+</span>
          Add Source
        </button>
      </header>

      <section className="career-sources-stats">
        <div className="career-source-stat">
          <span className="career-source-stat-label">
            Active Sources
          </span>
          <strong>{activeSources}</strong>
          <small>currently syncing</small>
        </div>

        <div className="career-source-stat">
          <span className="career-source-stat-label">
            Jobs Discovered
          </span>
          <strong>{totalJobsFound}</strong>
          <small>across all sources</small>
        </div>

        <div
          className={`career-source-stat ${
            needsAttention > 0 ? "attention" : ""
          }`}
        >
          <span className="career-source-stat-label">
            Needs Attention
          </span>
          <strong>{needsAttention}</strong>
          <small>
            {needsAttention === 1
              ? "source needs review"
              : "sources need review"}
          </small>
        </div>
      </section>

      <section className="career-sources-toolbar">
        <div className="career-sources-search">
          <span className="career-sources-search-icon">⌕</span>

          <input
            type="search"
            placeholder="Search sources..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>

        <select
          className="career-sources-filter"
          value={typeFilter}
          onChange={(event) =>
            setTypeFilter(event.target.value)
          }
          aria-label="Filter source type"
        >
          {sourceTypes.map((type) => (
            <option key={type}>{type}</option>
          ))}
        </select>
      </section>

      <section className="career-sources-card">
        <div className="career-sources-card-header">
          <div>
            <h2>Connected Sources</h2>

            <p>
              {filteredSources.length}{" "}
              {filteredSources.length === 1
                ? "source"
                : "sources"}
            </p>
          </div>

          <span className="career-sources-sync-note">
            Last sync status
          </span>
        </div>

        {filteredSources.length > 0 ? (
          <div className="career-sources-list">
            {filteredSources.map((source) => (
              <article
                className="career-source-row"
                key={source.id}
              >
                <div className="career-source-main">
                  <div className="career-source-icon">
                    {source.name.charAt(0).toUpperCase()}
                  </div>

                  <div className="career-source-info">
                    <div className="career-source-title-row">
                      <h3>{source.name}</h3>

                      <span
                        className={`career-source-status ${source.status
                          .toLowerCase()
                          .replace(" ", "-")}`}
                      >
                        <span />
                        {source.status}
                      </span>
                    </div>

                    <p>{source.description}</p>

                    <div className="career-source-meta">
                      <span>{source.type}</span>
                      <span>•</span>
                      <span>{source.url}</span>
                    </div>
                  </div>
                </div>

                <div className="career-source-sync">
                  <span>Last sync</span>
                  <strong>{source.lastSync}</strong>
                </div>

                <div className="career-source-jobs">
                  <strong>{source.jobsFound}</strong>
                  <span>jobs found</span>
                </div>

                <div className="career-source-actions">
                  <button
                    type="button"
                    onClick={() => toggleSource(source.id)}
                  >
                    {source.status === "Active"
                      ? "Pause"
                      : "Activate"}
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      openEditModal(source)
                    }
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    className="delete-action"
                    onClick={() =>
                      handleDelete(source.id)
                    }
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="career-sources-empty">
            <div className="career-sources-empty-icon">
              ↗
            </div>

            <h3>No career sources found</h3>

            <p>
              Try a different search or add a source to start
              discovering opportunities.
            </p>

            <button
              type="button"
              onClick={openAddModal}
            >
              Add Source
            </button>
          </div>
        )}
      </section>

      {isModalOpen && (
        <div
          className="career-source-modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeModal();
            }
          }}
        >
          <div
            className="career-source-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="career-source-modal-title"
          >
            <div className="career-source-modal-header">
              <div>
                <p className="career-source-modal-eyebrow">
                  {editingSource
                    ? "EDIT SOURCE"
                    : "NEW SOURCE"}
                </p>

                <h2 id="career-source-modal-title">
                  {editingSource
                    ? "Edit career source"
                    : "Add a career source"}
                </h2>
              </div>

              <button
                type="button"
                className="career-source-modal-close"
                onClick={closeModal}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="career-source-modal-body">
              <div className="career-source-form-grid">
                <div className="career-source-form-field">
                  <label htmlFor="source-name">
                    Source Name
                  </label>

                  <input
                    id="source-name"
                    value={form.name}
                    onChange={(event) =>
                      updateForm(
                        "name",
                        event.target.value,
                      )
                    }
                    placeholder="e.g. Microsoft Careers"
                  />
                </div>

                <div className="career-source-form-field">
                  <label htmlFor="source-type">
                    Source Type
                  </label>

                  <select
                    id="source-type"
                    value={form.type}
                    onChange={(event) =>
                      updateForm(
                        "type",
                        event.target.value,
                      )
                    }
                  >
                    <option>Company Career Page</option>
                    <option>Job Board</option>
                    <option>Startup Board</option>
                  </select>
                </div>

                <div className="career-source-form-field source-field-wide">
                  <label htmlFor="source-url">
                    Source URL
                  </label>

                  <input
                    id="source-url"
                    type="url"
                    value={form.url}
                    onChange={(event) =>
                      updateForm(
                        "url",
                        event.target.value,
                      )
                    }
                    placeholder="https://example.com/careers"
                  />
                </div>

                <div className="career-source-form-field source-field-wide">
                  <label htmlFor="source-description">
                    Description
                  </label>

                  <textarea
                    id="source-description"
                    rows={4}
                    value={form.description}
                    onChange={(event) =>
                      updateForm(
                        "description",
                        event.target.value,
                      )
                    }
                    placeholder="What kind of opportunities does this source contain?"
                  />
                </div>
              </div>
            </div>

            <div className="career-source-modal-footer">
              <button
                type="button"
                className="career-source-modal-cancel"
                onClick={closeModal}
              >
                Cancel
              </button>

              <button
                type="button"
                className="career-source-modal-save"
                onClick={handleSave}
                disabled={
                  !form.name.trim() || !form.url.trim()
                }
              >
                {editingSource
                  ? "Save Changes"
                  : "Add Source"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CareerSourcesPage;