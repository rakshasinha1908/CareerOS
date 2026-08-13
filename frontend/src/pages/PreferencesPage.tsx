import { useEffect, useState } from "react";
import "../styles/preferences-page.css";
import { apiRequest } from "../api/client";

type PreferencesForm = {
  preferredRoles: string[];
  preferredLocations: string[];
  remotePreference: "Remote" | "Hybrid" | "On-site" | "Flexible";
  employmentTypes: string[];
  experienceLevel: string;
  requiredSkills: string[];
  preferredSkills: string[];
  excludedKeywords: string[];
  minSalary: string;
  maxSalary: string;
};

type PreferencesResponse = {
  id: string;
  user_id: string;
  preferred_roles: string[];
  preferred_locations: string[];
  remote_preference: string | null;
  employment_types: string[];
  experience_level: string | null;
  required_skills: string[];
  preferred_skills: string[];
  excluded_keywords: string[];
  min_salary: number | null;
  max_salary: number | null;
};

type PreferencesPayload = {
  preferred_roles: string[];
  preferred_locations: string[];
  remote_preference: string | null;
  employment_types: string[];
  experience_level: string | null;
  required_skills: string[];
  preferred_skills: string[];
  excluded_keywords: string[];
  min_salary: number | null;
  max_salary: number | null;
};

const initialPreferences: PreferencesForm = {
  preferredRoles: [
    "Software Engineer",
    "Backend Engineer",
    "Full Stack Engineer",
  ],
  preferredLocations: ["Delhi NCR", "Gurugram", "Noida"],
  remotePreference: "Flexible",
  employmentTypes: ["Full-time"],
  experienceLevel: "Entry Level",
  requiredSkills: ["Python", "FastAPI", "SQL"],
  preferredSkills: ["React", "TypeScript", "Docker"],
  excludedKeywords: ["Sales", "Internship"],
  minSalary: "8",
  maxSalary: "20",
};

const roleSuggestions = [
  "Software Engineer",
  "Backend Engineer",
  "Full Stack Engineer",
  "Frontend Engineer",
];

const locationSuggestions = [
  "Delhi NCR",
  "Gurugram",
  "Noida",
  "Remote",
];

const skillSuggestions = [
  "Python",
  "FastAPI",
  "SQL",
  "React",
  "TypeScript",
  "Docker",
];

function mapResponseToForm(
  data: PreferencesResponse,
): PreferencesForm {
  const remotePreference =
    data.remote_preference === "Remote" ||
    data.remote_preference === "Hybrid" ||
    data.remote_preference === "On-site" ||
    data.remote_preference === "Flexible"
      ? data.remote_preference
      : "Flexible";

  return {
    preferredRoles: data.preferred_roles ?? [],
    preferredLocations: data.preferred_locations ?? [],
    remotePreference,
    employmentTypes: data.employment_types ?? [],
    experienceLevel: data.experience_level ?? "Entry Level",
    requiredSkills: data.required_skills ?? [],
    preferredSkills: data.preferred_skills ?? [],
    excludedKeywords: data.excluded_keywords ?? [],
    minSalary:
      data.min_salary !== null && data.min_salary !== undefined
        ? String(data.min_salary)
        : "",
    maxSalary:
      data.max_salary !== null && data.max_salary !== undefined
        ? String(data.max_salary)
        : "",
  };
}

function mapFormToPayload(
  data: PreferencesForm,
): PreferencesPayload {
  return {
    preferred_roles: data.preferredRoles,
    preferred_locations: data.preferredLocations,
    remote_preference: data.remotePreference,
    employment_types: data.employmentTypes,
    experience_level: data.experienceLevel || null,
    required_skills: data.requiredSkills,
    preferred_skills: data.preferredSkills,
    excluded_keywords: data.excludedKeywords,
    min_salary:
      data.minSalary.trim() === ""
        ? null
        : Number(data.minSalary),
    max_salary:
      data.maxSalary.trim() === ""
        ? null
        : Number(data.maxSalary),
  };
}

function PreferencesPage() {
  const [preferences, setPreferences] =
    useState<PreferencesForm>(initialPreferences);

  const [savedPreferences, setSavedPreferences] =
    useState<PreferencesForm>(initialPreferences);

  const [hasPreferences, setHasPreferences] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [roleInput, setRoleInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [requiredSkillInput, setRequiredSkillInput] = useState("");
  const [preferredSkillInput, setPreferredSkillInput] =
    useState("");
  const [excludedKeywordInput, setExcludedKeywordInput] =
    useState("");

  useEffect(() => {
    const loadPreferences = async () => {
      setIsLoading(true);
      setError("");
      setSuccessMessage("");

      try {
        const data =
          await apiRequest<PreferencesResponse>(
            "/api/v1/preferences",
          );

        const formData = mapResponseToForm(data);

        setPreferences(formData);
        setSavedPreferences(formData);
        setHasPreferences(true);
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : "Something went wrong";

        if (
          message.toLowerCase().includes("job preferences not found")
        ) {
          setPreferences(initialPreferences);
          setSavedPreferences(initialPreferences);
          setHasPreferences(false);
        } else {
          setError(message);
        }
      } finally {
        setIsLoading(false);
      }
    };

    loadPreferences();
  }, []);

  const updatePreferences = (
    updates: Partial<PreferencesForm>,
  ) => {
    setPreferences((current) => ({
      ...current,
      ...updates,
    }));

    setSuccessMessage("");
  };

  const addItem = (
    field:
      | "preferredRoles"
      | "preferredLocations"
      | "requiredSkills"
      | "preferredSkills"
      | "excludedKeywords",
    value: string,
  ) => {
    const trimmedValue = value.trim();

    if (!trimmedValue) {
      return;
    }

    if (preferences[field].includes(trimmedValue)) {
      return;
    }

    updatePreferences({
      [field]: [...preferences[field], trimmedValue],
    });
  };

  const removeItem = (
    field:
      | "preferredRoles"
      | "preferredLocations"
      | "requiredSkills"
      | "preferredSkills"
      | "excludedKeywords",
    value: string,
  ) => {
    updatePreferences({
      [field]: preferences[field].filter(
        (item) => item !== value,
      ),
    });
  };

  const handleDiscard = () => {
    setPreferences(savedPreferences);

    setRoleInput("");
    setLocationInput("");
    setRequiredSkillInput("");
    setPreferredSkillInput("");
    setExcludedKeywordInput("");

    setError("");
    setSuccessMessage("");
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError("");
    setSuccessMessage("");

    try {
      const payload = mapFormToPayload(preferences);

      const data = hasPreferences
        ? await apiRequest<PreferencesResponse>(
            "/api/v1/preferences",
            {
              method: "PATCH",
              body: JSON.stringify(payload),
            },
          )
        : await apiRequest<PreferencesResponse>(
            "/api/v1/preferences",
            {
              method: "POST",
              body: JSON.stringify(payload),
            },
          );

      const savedForm = mapResponseToForm(data);

      setPreferences(savedForm);
      setSavedPreferences(savedForm);
      setHasPreferences(true);

      setSuccessMessage(
        "Preferences saved successfully.",
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to save preferences.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleEnterAdd = (
    event: React.KeyboardEvent<HTMLInputElement>,
    field:
      | "preferredRoles"
      | "preferredLocations"
      | "requiredSkills"
      | "preferredSkills"
      | "excludedKeywords",
    value: string,
    clear: () => void,
  ) => {
    if (event.key !== "Enter") {
      return;
    }

    event.preventDefault();
    addItem(field, value);
    clear();
  };

  return (
    <div className="preferences-page">
      <header className="preferences-page-header">
        <div>
          <p className="preferences-eyebrow">PREFERENCES</p>

          <h1>Job Preferences</h1>

          <p className="preferences-page-description">
            Tell CareerOS what you're looking for so we can surface
            better opportunities.
          </p>

          {isLoading && (
            <p className="preferences-page-description">
              Loading your preferences...
            </p>
          )}

          {error && (
            <p
              className="preferences-page-description"
              role="alert"
            >
              {error}
            </p>
          )}

          {successMessage && (
            <p
              className="preferences-page-description"
              role="status"
            >
              {successMessage}
            </p>
          )}
        </div>

        <div className="preferences-header-actions">
          <button
            type="button"
            className="preferences-button preferences-button-secondary"
            onClick={handleDiscard}
            disabled={isSaving || isLoading}
          >
            Discard Changes
          </button>

          <button
            type="button"
            className="preferences-button preferences-button-primary"
            onClick={handleSave}
            disabled={isSaving || isLoading}
          >
            {isSaving ? "Saving..." : "Save Preferences"}
          </button>
        </div>
      </header>

      <div className="preferences-layout">
        <main className="preferences-form-column">
          {/* Roles & locations */}

          <section className="preferences-card">
            <div className="preferences-card-header">
              <h2>Target Roles & Locations</h2>

              <p>
                Define the kinds of opportunities and places you're
                targeting.
              </p>
            </div>

            <div className="preferences-card-body">
              <div className="preferences-field">
                <label htmlFor="role-input">Preferred Roles</label>

                <div className="tag-input-wrapper">
                  <div className="tag-list">
                    {preferences.preferredRoles.map((role) => (
                      <span className="preference-tag" key={role}>
                        {role}

                        <button
                          type="button"
                          onClick={() =>
                            removeItem("preferredRoles", role)
                          }
                          aria-label={`Remove ${role}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>

                  <input
                    id="role-input"
                    value={roleInput}
                    onChange={(event) =>
                      setRoleInput(event.target.value)
                    }
                    onKeyDown={(event) =>
                      handleEnterAdd(
                        event,
                        "preferredRoles",
                        roleInput,
                        () => setRoleInput(""),
                      )
                    }
                    placeholder="Add another role..."
                  />
                </div>

                <div className="suggestion-row">
                  {roleSuggestions
                    .filter(
                      (role) =>
                        !preferences.preferredRoles.includes(role),
                    )
                    .map((role) => (
                      <button
                        type="button"
                        className="suggestion-chip"
                        key={role}
                        onClick={() =>
                          addItem("preferredRoles", role)
                        }
                      >
                        + {role}
                      </button>
                    ))}
                </div>
              </div>

              <div className="preferences-field">
                <label htmlFor="location-input">
                  Preferred Locations
                </label>

                <div className="tag-input-wrapper">
                  <div className="tag-list">
                    {preferences.preferredLocations.map(
                      (location) => (
                        <span
                          className="preference-tag"
                          key={location}
                        >
                          {location}

                          <button
                            type="button"
                            onClick={() =>
                              removeItem(
                                "preferredLocations",
                                location,
                              )
                            }
                            aria-label={`Remove ${location}`}
                          >
                            ×
                          </button>
                        </span>
                      ),
                    )}
                  </div>

                  <input
                    id="location-input"
                    value={locationInput}
                    onChange={(event) =>
                      setLocationInput(event.target.value)
                    }
                    onKeyDown={(event) =>
                      handleEnterAdd(
                        event,
                        "preferredLocations",
                        locationInput,
                        () => setLocationInput(""),
                      )
                    }
                    placeholder="Add a location..."
                  />
                </div>

                <div className="suggestion-row">
                  {locationSuggestions
                    .filter(
                      (location) =>
                        !preferences.preferredLocations.includes(
                          location,
                        ),
                    )
                    .map((location) => (
                      <button
                        type="button"
                        className="suggestion-chip"
                        key={location}
                        onClick={() =>
                          addItem(
                            "preferredLocations",
                            location,
                          )
                        }
                      >
                        + {location}
                      </button>
                    ))}
                </div>
              </div>

              <div className="preferences-field">
                <label>Work Arrangement</label>

                <div className="segmented-control">
                  {(
                    [
                      "Remote",
                      "Hybrid",
                      "On-site",
                      "Flexible",
                    ] as const
                  ).map((option) => (
                    <button
                      type="button"
                      key={option}
                      className={
                        preferences.remotePreference === option
                          ? "selected"
                          : ""
                      }
                      onClick={() =>
                        updatePreferences({
                          remotePreference: option,
                        })
                      }
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Employment */}

          <section className="preferences-card">
            <div className="preferences-card-header">
              <h2>Employment</h2>

              <p>
                Narrow opportunities by employment type and
                experience level.
              </p>
            </div>

            <div className="preferences-card-body">
              <div className="preferences-two-column">
                <div className="preferences-field">
                  <label>Employment Type</label>

                  <div className="checkbox-list">
                    {[
                      "Full-time",
                      "Part-time",
                      "Contract",
                      "Internship",
                    ].map((type) => {
                      const checked =
                        preferences.employmentTypes.includes(type);

                      return (
                        <label
                          className="checkbox-option"
                          key={type}
                        >
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => {
                              const next = checked
                                ? preferences.employmentTypes.filter(
                                    (item) => item !== type,
                                  )
                                : [
                                    ...preferences.employmentTypes,
                                    type,
                                  ];

                              updatePreferences({
                                employmentTypes: next,
                              });
                            }}
                          />

                          <span>{type}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>

                <div className="preferences-field">
                  <label htmlFor="experience-level">
                    Experience Level
                  </label>

                  <select
                    id="experience-level"
                    value={preferences.experienceLevel}
                    onChange={(event) =>
                      updatePreferences({
                        experienceLevel: event.target.value,
                      })
                    }
                  >
                    <option>Entry Level</option>
                    <option>Mid Level</option>
                    <option>Senior Level</option>
                    <option>Lead</option>
                    <option>Any Level</option>
                  </select>
                </div>
              </div>
            </div>
          </section>

          {/* Skills */}

          <section className="preferences-card">
            <div className="preferences-card-header">
              <h2>Skills</h2>

              <p>
                Separate skills that are essential from skills that
                are simply nice to have.
              </p>
            </div>

            <div className="preferences-card-body">
              <div className="preferences-field">
                <label htmlFor="required-skill-input">
                  Required Skills
                </label>

                <div className="tag-input-wrapper">
                  <div className="tag-list">
                    {preferences.requiredSkills.map((skill) => (
                      <span
                        className="preference-tag required"
                        key={skill}
                      >
                        {skill}

                        <button
                          type="button"
                          onClick={() =>
                            removeItem("requiredSkills", skill)
                          }
                          aria-label={`Remove ${skill}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>

                  <input
                    id="required-skill-input"
                    value={requiredSkillInput}
                    onChange={(event) =>
                      setRequiredSkillInput(event.target.value)
                    }
                    onKeyDown={(event) =>
                      handleEnterAdd(
                        event,
                        "requiredSkills",
                        requiredSkillInput,
                        () => setRequiredSkillInput(""),
                      )
                    }
                    placeholder="Add a required skill..."
                  />
                </div>

                <div className="suggestion-row">
                  {skillSuggestions
                    .filter(
                      (skill) =>
                        !preferences.requiredSkills.includes(skill),
                    )
                    .map((skill) => (
                      <button
                        type="button"
                        className="suggestion-chip"
                        key={skill}
                        onClick={() =>
                          addItem("requiredSkills", skill)
                        }
                      >
                        + {skill}
                      </button>
                    ))}
                </div>
              </div>

              <div className="preferences-field">
                <label htmlFor="preferred-skill-input">
                  Preferred Skills
                </label>

                <div className="tag-input-wrapper">
                  <div className="tag-list">
                    {preferences.preferredSkills.map((skill) => (
                      <span
                        className="preference-tag preferred"
                        key={skill}
                      >
                        {skill}

                        <button
                          type="button"
                          onClick={() =>
                            removeItem("preferredSkills", skill)
                          }
                          aria-label={`Remove ${skill}`}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>

                  <input
                    id="preferred-skill-input"
                    value={preferredSkillInput}
                    onChange={(event) =>
                      setPreferredSkillInput(event.target.value)
                    }
                    onKeyDown={(event) =>
                      handleEnterAdd(
                        event,
                        "preferredSkills",
                        preferredSkillInput,
                        () => setPreferredSkillInput(""),
                      )
                    }
                    placeholder="Add a preferred skill..."
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Salary & exclusions */}

          <section className="preferences-card">
            <div className="preferences-card-header">
              <h2>Compensation & Exclusions</h2>

              <p>
                Set your salary expectations and tell CareerOS what
                to avoid.
              </p>
            </div>

            <div className="preferences-card-body">
              <div className="preferences-two-column">
                <div className="preferences-field">
                  <label>Expected Salary Range</label>

                  <div className="salary-inputs">
                    <div className="salary-input">
                      <span>₹</span>

                      <input
                        type="number"
                        value={preferences.minSalary}
                        onChange={(event) =>
                          updatePreferences({
                            minSalary: event.target.value,
                          })
                        }
                        aria-label="Minimum salary in lakhs"
                      />

                      <small>LPA</small>
                    </div>

                    <span className="salary-separator">to</span>

                    <div className="salary-input">
                      <span>₹</span>

                      <input
                        type="number"
                        value={preferences.maxSalary}
                        onChange={(event) =>
                          updatePreferences({
                            maxSalary: event.target.value,
                          })
                        }
                        aria-label="Maximum salary in lakhs"
                      />

                      <small>LPA</small>
                    </div>
                  </div>
                </div>

                <div className="preferences-field">
                  <label htmlFor="excluded-keyword-input">
                    Excluded Keywords
                  </label>

                  <div className="tag-input-wrapper">
                    <div className="tag-list">
                      {preferences.excludedKeywords.map(
                        (keyword) => (
                          <span
                            className="preference-tag excluded"
                            key={keyword}
                          >
                            {keyword}

                            <button
                              type="button"
                              onClick={() =>
                                removeItem(
                                  "excludedKeywords",
                                  keyword,
                                )
                              }
                              aria-label={`Remove ${keyword}`}
                            >
                              ×
                            </button>
                          </span>
                        ),
                      )}
                    </div>

                    <input
                      id="excluded-keyword-input"
                      value={excludedKeywordInput}
                      onChange={(event) =>
                        setExcludedKeywordInput(
                          event.target.value,
                        )
                      }
                      onKeyDown={(event) =>
                        handleEnterAdd(
                          event,
                          "excludedKeywords",
                          excludedKeywordInput,
                          () => setExcludedKeywordInput(""),
                        )
                      }
                      placeholder="Add keyword..."
                    />
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>

        <aside className="preferences-summary">
          <div className="preferences-summary-card">
            <div className="preferences-summary-header">
              <span className="summary-icon">✦</span>

              <div>
                <p>CAREEROS MATCHING</p>
                <h2>Your search profile</h2>
              </div>
            </div>

            <div className="summary-divider" />

            <div className="summary-stat">
              <span>Target roles</span>
              <strong>
                {preferences.preferredRoles.length}
              </strong>
            </div>

            <div className="summary-stat">
              <span>Locations</span>
              <strong>
                {preferences.preferredLocations.length}
              </strong>
            </div>

            <div className="summary-stat">
              <span>Required skills</span>
              <strong>
                {preferences.requiredSkills.length}
              </strong>
            </div>

            <div className="summary-stat">
              <span>Work arrangement</span>
              <strong>{preferences.remotePreference}</strong>
            </div>

            <div className="summary-divider" />

            <p className="summary-note">
              CareerOS will use these preferences when ranking and
              matching new opportunities.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default PreferencesPage;