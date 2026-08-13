import { useEffect, useMemo, useState } from "react";
import "../styles/companies-page.css";
import { apiRequest } from "../api/client";

type Company = {
  id: string;
  name: string;
  website: string;
  industry: string;
  size: string;
  headquarters: string;
  notes: string;
};

type CompanyPayload = {
  name: string;
  website: string | null;
  industry: string | null;
  size: string | null;
  headquarters: string | null;
  notes: string | null;
};

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

function mapCompanyToForm(data: Company): Company {
  return {
    id: data.id,
    name: data.name ?? "",
    website: data.website ?? "",
    industry: data.industry ?? "",
    size: data.size ?? "",
    headquarters: data.headquarters ?? "",
    notes: data.notes ?? "",
  };
}

function mapFormToPayload(
  data: Omit<Company, "id">,
): CompanyPayload {
  return {
    name: data.name.trim(),
    website: data.website.trim() || null,
    industry: data.industry.trim() || null,
    size: data.size.trim() || null,
    headquarters: data.headquarters.trim() || null,
    notes: data.notes.trim() || null,
  };
}

function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);

  const [search, setSearch] = useState("");
  const [industryFilter, setIndustryFilter] =
    useState("All industries");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCompany, setEditingCompany] =
    useState<Company | null>(null);

  const [form, setForm] = useState(emptyCompany);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingCompanyId, setDeletingCompanyId] =
    useState<string | null>(null);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

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

  useEffect(() => {
    const loadCompanies = async () => {
      setIsLoading(true);
      setError("");

      try {
        const data = await apiRequest<Company[]>(
          "/api/v1/companies",
        );

        setCompanies(data.map(mapCompanyToForm));
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load companies.",
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadCompanies();
  }, []);

  const openAddModal = () => {
    setEditingCompany(null);
    setForm(emptyCompany);
    setError("");
    setSuccessMessage("");
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

    setError("");
    setSuccessMessage("");
    setIsModalOpen(true);
  };

  const closeModal = () => {
    if (isSaving) {
      return;
    }

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

    setError("");
  };

  const handleSave = async () => {
    if (!form.name.trim()) {
      return;
    }

    setIsSaving(true);
    setError("");
    setSuccessMessage("");

    try {
      const payload = mapFormToPayload(form);

      if (editingCompany) {
        const updatedCompany =
          await apiRequest<Company>(
            `/api/v1/companies/${editingCompany.id}`,
            {
              method: "PATCH",
              body: JSON.stringify(payload),
            },
          );

        const updated = mapCompanyToForm(updatedCompany);

        setCompanies((current) =>
          current.map((company) =>
            company.id === updated.id
              ? updated
              : company,
          ),
        );

        setSuccessMessage("Company updated successfully.");
      } else {
        const createdCompany =
          await apiRequest<Company>(
            "/api/v1/companies",
            {
              method: "POST",
              body: JSON.stringify(payload),
            },
          );

        const created = mapCompanyToForm(createdCompany);

        setCompanies((current) => [
          ...current,
          created,
        ]);

        setSuccessMessage("Company added successfully.");
      }

      setIsModalOpen(false);
      setEditingCompany(null);
      setForm(emptyCompany);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to save company.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    const company = companies.find(
      (item) => item.id === id,
    );

    if (!company) {
      return;
    }

    const confirmed = window.confirm(
      `Delete ${company.name}?`,
    );

    if (!confirmed) {
      return;
    }

    setDeletingCompanyId(id);
    setError("");
    setSuccessMessage("");

    try {
      await apiRequest<void>(
        `/api/v1/companies/${id}`,
        {
          method: "DELETE",
        },
      );

      setCompanies((current) =>
        current.filter((item) => item.id !== id),
      );

      setSuccessMessage("Company deleted successfully.");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to delete company.",
      );
    } finally {
      setDeletingCompanyId(null);
    }
  };

  return (
    <div className="companies-page">
      <header className="companies-page-header">
        <div>
          <p className="companies-eyebrow">COMPANIES</p>

          <h1>Companies</h1>

          <p className="companies-page-description">
            Track companies you're interested in and keep your
            target list organized.
          </p>

          {isLoading && (
            <p className="companies-page-description">
              Loading companies...
            </p>
          )}

          {error && (
            <p
              className="companies-page-description"
              role="alert"
            >
              {error}
            </p>
          )}

          {successMessage && (
            <p
              className="companies-page-description"
              role="status"
            >
              {successMessage}
            </p>
          )}
        </div>

        <button
          type="button"
          className="companies-add-button"
          onClick={openAddModal}
          disabled={isLoading}
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
            onChange={(event) =>
              setSearch(event.target.value)
            }
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

                          <span>
                            {company.website || "—"}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="company-industry">
                        {company.industry || "—"}
                      </span>
                    </td>

                    <td>{company.size || "—"}</td>

                    <td>
                      {company.headquarters || "—"}
                    </td>

                    <td>
                      <div className="company-row-actions">
                        <button
                          type="button"
                          onClick={() =>
                            openEditModal(company)
                          }
                          disabled={
                            deletingCompanyId === company.id
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
                          disabled={
                            deletingCompanyId === company.id
                          }
                          aria-label={`Delete ${company.name}`}
                        >
                          {deletingCompanyId === company.id
                            ? "Deleting..."
                            : "Delete"}
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

            <h3>
              {isLoading
                ? "Loading companies..."
                : "No companies found"}
            </h3>

            {!isLoading && (
              <>
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
              </>
            )}
          </div>
        )}
      </section>

      {isModalOpen && (
        <div
          className="company-modal-backdrop"
          onMouseDown={(event) => {
            if (
              event.target === event.currentTarget &&
              !isSaving
            ) {
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
                  {editingCompany
                    ? "EDIT COMPANY"
                    : "NEW COMPANY"}
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
                disabled={isSaving}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="company-modal-body">
              <div className="company-form-grid">
                <div className="company-form-field company-form-field-wide">
                  <label htmlFor="company-name">
                    Company Name
                  </label>

                  <input
                    id="company-name"
                    value={form.name}
                    onChange={(event) =>
                      updateForm(
                        "name",
                        event.target.value,
                      )
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
                  <label htmlFor="company-size">
                    Company Size
                  </label>

                  <input
                    id="company-size"
                    value={form.size}
                    onChange={(event) =>
                      updateForm(
                        "size",
                        event.target.value,
                      )
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
                    placeholder="https://company.com"
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
                  <label htmlFor="company-notes">
                    Notes
                  </label>

                  <textarea
                    id="company-notes"
                    rows={4}
                    value={form.notes}
                    onChange={(event) =>
                      updateForm(
                        "notes",
                        event.target.value,
                      )
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
                disabled={isSaving}
              >
                Cancel
              </button>

              <button
                type="button"
                className="company-modal-save"
                onClick={handleSave}
                disabled={
                  !form.name.trim() || isSaving
                }
              >
                {isSaving
                  ? "Saving..."
                  : editingCompany
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