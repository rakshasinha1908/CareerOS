import { useMemo, useState } from "react";
import "../styles/companies-page.css";

type Company = {
  id: number;
  name: string;
  website: string;
  industry: string;
  size: string;
  headquarters: string;
  notes: string;
};

const initialCompanies: Company[] = [
  {
    id: 1,
    name: "Stripe",
    website: "stripe.com",
    industry: "Fintech",
    size: "5,000+",
    headquarters: "San Francisco",
    notes: "Strong engineering culture and backend opportunities.",
  },
  {
    id: 2,
    name: "Linear",
    website: "linear.app",
    industry: "Software",
    size: "100–250",
    headquarters: "San Francisco",
    notes: "Interested in product engineering roles.",
  },
  {
    id: 3,
    name: "Razorpay",
    website: "razorpay.com",
    industry: "Fintech",
    size: "1,000–5,000",
    headquarters: "Bengaluru",
    notes: "Target company for backend and full-stack roles.",
  },
  {
    id: 4,
    name: "Atlassian",
    website: "atlassian.com",
    industry: "Software",
    size: "5,000+",
    headquarters: "Bengaluru",
    notes: "Good fit for distributed systems and platform roles.",
  },
  {
    id: 5,
    name: "Notion",
    website: "notion.so",
    industry: "Productivity",
    size: "500–1,000",
    headquarters: "San Francisco",
    notes: "Interested in product-focused engineering teams.",
  },
  {
    id: 6,
    name: "Microsoft",
    website: "microsoft.com",
    industry: "Technology",
    size: "5,000+",
    headquarters: "Noida",
    notes: "Explore software engineering and AI roles.",
  },
];

const emptyCompany: Omit<Company, "id"> = {
  name: "",
  website: "",
  industry: "",
  size: "",
  headquarters: "",
  notes: "",
};

const industryOptions = [
  "All industries",
  "Software",
  "Fintech",
  "Technology",
  "Productivity",
];

function CompaniesPage() {
  const [companies, setCompanies] = useState(initialCompanies);
  const [search, setSearch] = useState("");
  const [industryFilter, setIndustryFilter] =
    useState("All industries");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCompany, setEditingCompany] =
    useState<Company | null>(null);

  const [form, setForm] = useState(emptyCompany);

  const filteredCompanies = useMemo(() => {
    const query = search.trim().toLowerCase();

    return companies.filter((company) => {
      const matchesSearch =
        !query ||
        company.name.toLowerCase().includes(query) ||
        company.industry.toLowerCase().includes(query) ||
        company.headquarters.toLowerCase().includes(query);

      const matchesIndustry =
        industryFilter === "All industries" ||
        company.industry === industryFilter;

      return matchesSearch && matchesIndustry;
    });
  }, [companies, search, industryFilter]);

  const openAddModal = () => {
    setEditingCompany(null);
    setForm(emptyCompany);
    setIsModalOpen(true);
  };

  const openEditModal = (company: Company) => {
    setEditingCompany(company);

    setForm({
      name: company.name,
      website: company.website,
      industry: company.industry,
      size: company.size,
      headquarters: company.headquarters,
      notes: company.notes,
    });

    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingCompany(null);
    setForm(emptyCompany);
  };

  const updateForm = (
    field: keyof typeof emptyCompany,
    value: string,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSave = () => {
    if (!form.name.trim()) {
      return;
    }

    if (editingCompany) {
      setCompanies((current) =>
        current.map((company) =>
          company.id === editingCompany.id
            ? {
                ...company,
                ...form,
                name: form.name.trim(),
              }
            : company,
        ),
      );
    } else {
      setCompanies((current) => [
        ...current,
        {
          id: Date.now(),
          ...form,
          name: form.name.trim(),
        },
      ]);
    }

    closeModal();
  };

  const handleDelete = (id: number) => {
    setCompanies((current) =>
      current.filter((company) => company.id !== id),
    );
  };

  return (
    <div className="companies-page">
      <header className="companies-page-header">
        <div>
          <p className="companies-eyebrow">COMPANIES</p>

          <h1>Companies</h1>

          <p className="companies-page-description">
            Track companies you're interested in and keep your target
            list organized.
          </p>
        </div>

        <button
          type="button"
          className="companies-add-button"
          onClick={openAddModal}
        >
          <span>+</span>
          Add Company
        </button>
      </header>

      <section className="companies-toolbar">
        <div className="companies-search">
          <span className="companies-search-icon">⌕</span>

          <input
            type="search"
            placeholder="Search companies..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <select
          className="companies-filter"
          value={industryFilter}
          onChange={(event) =>
            setIndustryFilter(event.target.value)
          }
          aria-label="Filter by industry"
        >
          {industryOptions.map((industry) => (
            <option key={industry}>{industry}</option>
          ))}
        </select>
      </section>

      <section className="companies-content-card">
        <div className="companies-content-header">
          <div>
            <h2>All Companies</h2>
            <p>
              {filteredCompanies.length}{" "}
              {filteredCompanies.length === 1
                ? "company"
                : "companies"}
            </p>
          </div>
        </div>

        {filteredCompanies.length > 0 ? (
          <div className="companies-table-wrapper">
            <table className="companies-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Industry</th>
                  <th>Size</th>
                  <th>Headquarters</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>

              <tbody>
                {filteredCompanies.map((company) => (
                  <tr key={company.id}>
                    <td>
                      <div className="company-name-cell">
                        <div className="company-logo">
                          {company.name
                            .charAt(0)
                            .toUpperCase()}
                        </div>

                        <div>
                          <strong>{company.name}</strong>

                          <span>{company.website}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="company-industry">
                        {company.industry}
                      </span>
                    </td>

                    <td>{company.size}</td>

                    <td>{company.headquarters}</td>

                    <td>
                      <div className="company-row-actions">
                        <button
                          type="button"
                          onClick={() =>
                            openEditModal(company)
                          }
                          aria-label={`Edit ${company.name}`}
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          className="delete-action"
                          onClick={() =>
                            handleDelete(company.id)
                          }
                          aria-label={`Delete ${company.name}`}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="companies-empty-state">
            <div className="companies-empty-icon">⌂</div>

            <h3>No companies found</h3>

            <p>
              Try changing your search or filters, or add a new
              company to your target list.
            </p>

            <button
              type="button"
              onClick={openAddModal}
            >
              Add Company
            </button>
          </div>
        )}
      </section>

      {isModalOpen && (
        <div
          className="company-modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeModal();
            }
          }}
        >
          <div
            className="company-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="company-modal-title"
          >
            <div className="company-modal-header">
              <div>
                <p className="company-modal-eyebrow">
                  {editingCompany ? "EDIT COMPANY" : "NEW COMPANY"}
                </p>

                <h2 id="company-modal-title">
                  {editingCompany
                    ? "Edit company"
                    : "Add a company"}
                </h2>
              </div>

              <button
                type="button"
                className="company-modal-close"
                onClick={closeModal}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="company-modal-body">
              <div className="company-form-grid">
                <div className="company-form-field company-form-field-wide">
                  <label htmlFor="company-name">Company Name</label>

                  <input
                    id="company-name"
                    value={form.name}
                    onChange={(event) =>
                      updateForm("name", event.target.value)
                    }
                    placeholder="e.g. Stripe"
                  />
                </div>

                <div className="company-form-field">
                  <label htmlFor="company-industry">
                    Industry
                  </label>

                  <input
                    id="company-industry"
                    value={form.industry}
                    onChange={(event) =>
                      updateForm(
                        "industry",
                        event.target.value,
                      )
                    }
                    placeholder="e.g. Fintech"
                  />
                </div>

                <div className="company-form-field">
                  <label htmlFor="company-size">Company Size</label>

                  <input
                    id="company-size"
                    value={form.size}
                    onChange={(event) =>
                      updateForm("size", event.target.value)
                    }
                    placeholder="e.g. 500–1,000"
                  />
                </div>

                <div className="company-form-field">
                  <label htmlFor="company-website">
                    Website
                  </label>

                  <input
                    id="company-website"
                    value={form.website}
                    onChange={(event) =>
                      updateForm(
                        "website",
                        event.target.value,
                      )
                    }
                    placeholder="company.com"
                  />
                </div>

                <div className="company-form-field">
                  <label htmlFor="company-location">
                    Headquarters
                  </label>

                  <input
                    id="company-location"
                    value={form.headquarters}
                    onChange={(event) =>
                      updateForm(
                        "headquarters",
                        event.target.value,
                      )
                    }
                    placeholder="e.g. Bengaluru"
                  />
                </div>

                <div className="company-form-field company-form-field-wide">
                  <label htmlFor="company-notes">Notes</label>

                  <textarea
                    id="company-notes"
                    rows={4}
                    value={form.notes}
                    onChange={(event) =>
                      updateForm("notes", event.target.value)
                    }
                    placeholder="Anything you want to remember about this company..."
                  />
                </div>
              </div>
            </div>

            <div className="company-modal-footer">
              <button
                type="button"
                className="company-modal-cancel"
                onClick={closeModal}
              >
                Cancel
              </button>

              <button
                type="button"
                className="company-modal-save"
                onClick={handleSave}
                disabled={!form.name.trim()}
              >
                {editingCompany
                  ? "Save Changes"
                  : "Add Company"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CompaniesPage;