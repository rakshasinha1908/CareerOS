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

type Job = {
  id: string;
  company_id: string;
  title: string;
};

type CompanyForm = {
  name: string;
  career_url: string;
};

type CompanyPayload = {
  name: string;
  career_url: string;
};

type SyncResponse = {
  discovered: number;
  created: number;
  skipped: number;
};

type SyncState = {
  status: "syncing" | "success" | "error";
  message: string;
};

const emptyCompany: CompanyForm = {
  name: "",
  career_url: "",
};

function mapFormToPayload(
  data: CompanyForm,
): CompanyPayload {
  return {
    name: data.name.trim(),
    career_url: data.career_url.trim(),
  };
}

function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>(
    [],
  );

  const [jobs, setJobs] = useState<Job[]>([]);

  const [search, setSearch] = useState("");

  const [isModalOpen, setIsModalOpen] =
    useState(false);

  const [editingCompany, setEditingCompany] =
    useState<Company | null>(null);

  const [form, setForm] =
    useState<CompanyForm>(emptyCompany);

  const [isLoading, setIsLoading] =
    useState(true);

  const [isSaving, setIsSaving] =
    useState(false);

  const [deletingCompanyId, setDeletingCompanyId] =
    useState<string | null>(null);

  const [syncingCompanyId, setSyncingCompanyId] =
    useState<string | null>(null);

  const [syncStates, setSyncStates] =
    useState<Record<string, SyncState>>({});

  const [error, setError] = useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  /*
   * -------------------------------------------------
   * Load companies + jobs
   * -------------------------------------------------
   */

  const loadData = async () => {
    setIsLoading(true);
    setError("");

    try {
      const [companiesData, jobsData] =
        await Promise.all([
          apiRequest<Company[]>(
            "/api/v1/companies",
          ),
          apiRequest<Job[]>(
            "/api/v1/jobs",
          ),
        ]);

      setCompanies(companiesData);
      setJobs(jobsData);
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

  useEffect(() => {
    loadData();
  }, []);

  /*
   * -------------------------------------------------
   * Filter companies
   * -------------------------------------------------
   */

  const filteredCompanies = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return companies;
    }

    return companies.filter((company) => {
      return (
        company.name
          .toLowerCase()
          .includes(query) ||
        company.career_url
          .toLowerCase()
          .includes(query)
      );
    });
  }, [companies, search]);

  /*
   * -------------------------------------------------
   * Job count per company
   * -------------------------------------------------
   */

  const jobCountByCompany = useMemo(() => {
    const counts: Record<string, number> = {};

    for (const job of jobs) {
      counts[job.company_id] =
        (counts[job.company_id] ?? 0) + 1;
    }

    return counts;
  }, [jobs]);

  /*
   * -------------------------------------------------
   * Add company
   * -------------------------------------------------
   */

  const openAddModal = () => {
    setEditingCompany(null);
    setForm(emptyCompany);
    setError("");
    setSuccessMessage("");
    setIsModalOpen(true);
  };

  /*
   * -------------------------------------------------
   * Edit company
   * -------------------------------------------------
   */

  const openEditModal = (
    company: Company,
  ) => {
    setEditingCompany(company);

    setForm({
      name: company.name,
      career_url: company.career_url,
    });

    setError("");
    setSuccessMessage("");
    setIsModalOpen(true);
  };

  /*
   * -------------------------------------------------
   * Close modal
   * -------------------------------------------------
   */

  const closeModal = () => {
    if (isSaving) {
      return;
    }

    setIsModalOpen(false);
    setEditingCompany(null);
    setForm(emptyCompany);
  };

  /*
   * -------------------------------------------------
   * Update form
   * -------------------------------------------------
   */

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

  /*
   * -------------------------------------------------
   * Save company
   * -------------------------------------------------
   */

  const handleSave = async () => {
    if (
      !form.name.trim() ||
      !form.career_url.trim()
    ) {
      return;
    }

    setIsSaving(true);
    setError("");
    setSuccessMessage("");

    try {
      const payload =
        mapFormToPayload(form);

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
            company.id ===
            updatedCompany.id
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

  /*
   * -------------------------------------------------
   * Delete company
   * -------------------------------------------------
   */

  const handleDelete = async (
    id: string,
  ) => {
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
        current.filter(
          (item) => item.id !== id,
        ),
      );

      setJobs((current) =>
        current.filter(
          (job) => job.company_id !== id,
        ),
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

  /*
   * -------------------------------------------------
   * Sync company jobs
   * -------------------------------------------------
   */

  const handleSync = async (
    company: Company,
  ) => {
    if (syncingCompanyId) {
      return;
    }

    setSyncingCompanyId(company.id);
    setError("");
    setSuccessMessage("");

    setSyncStates((current) => ({
      ...current,
      [company.id]: {
        status: "syncing",
        message: "Syncing jobs...",
      },
    }));

    try {
      const result =
        await apiRequest<SyncResponse>(
          `/api/v1/companies/${company.id}/sync`,
          {
            method: "POST",
          },
        );

      setSyncStates((current) => ({
        ...current,
        [company.id]: {
          status: "success",
          message:
            result.created > 0
              ? `${result.created} new ${
                  result.created === 1
                    ? "job"
                    : "jobs"
                } added`
              : "No new jobs found",
        },
      }));

      setSuccessMessage(
        `${company.name}: ${result.discovered} jobs discovered, ${result.created} new.`,
      );

      /*
       * Refresh jobs so the count beside the company
       * updates immediately.
       */
      try {
        const updatedJobs =
          await apiRequest<Job[]>(
            "/api/v1/jobs",
          );

        setJobs(updatedJobs);
      } catch {
        // The sync itself succeeded.
        // A failed refresh should not show as a sync failure.
      }
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Unable to sync jobs.";

      setSyncStates((current) => ({
        ...current,
        [company.id]: {
          status: "error",
          message: "Sync failed",
        },
      }));

      setError(
        `${company.name}: ${message}`,
      );
    } finally {
      setSyncingCompanyId(null);
    }
  };

  /*
   * -------------------------------------------------
   * Render
   * -------------------------------------------------
   */

  return (
    <div className="companies-page">
      <header className="companies-page-header">
        <div>
          <p className="companies-eyebrow">
            COMPANIES
          </p>

          <h1>Companies</h1>

          <p className="companies-page-description">
            Keep track of the companies whose
            career pages you want to follow.
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
                  <th>Jobs</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>

              <tbody>
                {filteredCompanies.map(
                  (company) => {
                    const jobCount =
                      jobCountByCompany[
                        company.id
                      ] ?? 0;

                    const syncState =
                      syncStates[
                        company.id
                      ];

                    const isSyncing =
                      syncingCompanyId ===
                      company.id;

                    return (
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
                            href={
                              company.career_url
                            }
                            target="_blank"
                            rel="noreferrer"
                          >
                            {
                              company.career_url
                            }
                          </a>
                        </td>

                        <td>
                          <div className="company-jobs-cell">
                            <strong>
                              {jobCount}
                            </strong>

                            <span>
                              {jobCount === 1
                                ? "job"
                                : "jobs"}
                            </span>
                          </div>
                        </td>

                        <td>
                          <div className="company-row-actions">
                            <button
                              type="button"
                              className="sync-action"
                              onClick={() =>
                                handleSync(
                                  company,
                                )
                              }
                              disabled={
                                isSyncing ||
                                deletingCompanyId ===
                                  company.id
                              }
                            >
                              {isSyncing
                                ? "Syncing..."
                                : "Sync"}
                            </button>

                            <button
                              type="button"
                              onClick={() =>
                                openEditModal(
                                  company,
                                )
                              }
                              disabled={
                                isSyncing ||
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
                                handleDelete(
                                  company.id,
                                )
                              }
                              disabled={
                                isSyncing ||
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

                          {syncState && (
                            <div
                              className={`company-sync-status company-sync-${syncState.status}`}
                            >
                              {syncState.message}
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  },
                )}
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
              event.target ===
                event.currentTarget &&
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
                    value={
                      form.career_url
                    }
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