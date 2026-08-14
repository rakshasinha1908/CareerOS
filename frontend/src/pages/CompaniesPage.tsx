import { useEffect, useMemo, useState } from "react";
import "../styles/companies-page.css";
import { apiRequest } from "../api/client";

type Company = {
  id: string;
  name: string;
  career_url: string;
  created_at: string;
  updated_at: string;
};

type CompanyForm = {
  name: string;
  career_url: string;
};

type CompanyPayload = {
  name: string;
  career_url: string;
};

const emptyCompany: CompanyForm = {
  name: "",
  career_url: "",
};

function mapCompanyToForm(data: Company): CompanyForm {
  return {
    name: data.name ?? "",
    career_url: data.career_url ?? "",
  };
}

function mapFormToPayload(data: CompanyForm): CompanyPayload {
  return {
    name: data.name.trim(),
    career_url: data.career_url.trim(),
  };
}

function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);

  const [search, setSearch] = useState("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCompany, setEditingCompany] =
    useState<Company | null>(null);

  const [form, setForm] = useState<CompanyForm>(emptyCompany);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingCompanyId, setDeletingCompanyId] =
    useState<string | null>(null);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const filteredCompanies = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return companies;
    }

    return companies.filter((company) => {
      return (
        company.name.toLowerCase().includes(query) ||
        company.career_url.toLowerCase().includes(query)
      );
    });
  }, [companies, search]);

  useEffect(() => {
    const loadCompanies = async () => {
      setIsLoading(true);
      setError("");

      try {
        const data = await apiRequest<Company[]>(
          "/api/v1/companies",
        );

        setCompanies(data);
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
      career_url: company.career_url,
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
    field: keyof CompanyForm,
    value: string,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    setError("");
  };

  const handleSave = async () => {
    if (!form.name.trim() || !form.career_url.trim()) {
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

        setCompanies((current) =>
          current.map((company) =>
            company.id === updatedCompany.id
              ? updatedCompany
              : company,
          ),
        );

        setSuccessMessage(
          "Company updated successfully.",
        );
      } else {
        const createdCompany =
          await apiRequest<Company>(
            "/api/v1/companies",
            {
              method: "POST",
              body: JSON.stringify(payload),
            },
          );

        setCompanies((current) => [
          ...current,
          createdCompany,
        ]);

        setSuccessMessage(
          "Company added successfully.",
        );
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

      setSuccessMessage(
        "Company deleted successfully.",
      );
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
          <p className="companies-eyebrow">
            COMPANIES
          </p>

          <h1>Companies</h1>

          <p className="companies-page-description">
            Keep track of the companies whose career
            pages you want to follow.
          </p>

          {isLoading && (
            <p className="companies-status">
              Loading companies...
            </p>
          )}

          {error && (
            <p
              className="companies-status companies-status-error"
              role="alert"
            >
              {error}
            </p>
          )}

          {successMessage && (
            <p
              className="companies-status companies-status-success"
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
          <span className="companies-search-icon">
            ⌕
          </span>

          <input
            type="search"
            placeholder="Search companies..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>
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
                  <th>Career Page</th>
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
                          <strong>
                            {company.name}
                          </strong>
                        </div>
                      </div>
                    </td>

                    <td>
                      <a
                        className="company-career-link"
                        href={company.career_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {company.career_url}
                      </a>
                    </td>

                    <td>
                      <div className="company-row-actions">
                        <button
                          type="button"
                          onClick={() =>
                            openEditModal(company)
                          }
                          disabled={
                            deletingCompanyId ===
                            company.id
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
                            deletingCompanyId ===
                            company.id
                          }
                          aria-label={`Delete ${company.name}`}
                        >
                          {deletingCompanyId ===
                          company.id
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
            <div className="companies-empty-icon">
              ⌂
            </div>

            <h3>
              {isLoading
                ? "Loading companies..."
                : search
                  ? "No companies found"
                  : "No companies yet"}
            </h3>

            {!isLoading && (
              <>
                <p>
                  {search
                    ? "Try a different search or add a new company."
                    : "Add the career pages of companies you want to track."}
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
                <div className="company-form-field">
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
                  <label htmlFor="company-career-url">
                    Career Page URL
                  </label>

                  <input
                    id="company-career-url"
                    type="url"
                    value={form.career_url}
                    onChange={(event) =>
                      updateForm(
                        "career_url",
                        event.target.value,
                      )
                    }
                    placeholder="https://company.com/careers"
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
                  !form.name.trim() ||
                  !form.career_url.trim() ||
                  isSaving
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