import { useState } from "react";
import "../styles/preferences-page.css";

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

function PreferencesPage() {
  const [preferences, setPreferences] =
    useState<PreferencesForm>(initialPreferences);

  const [roleInput, setRoleInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [requiredSkillInput, setRequiredSkillInput] = useState("");
  const [preferredSkillInput, setPreferredSkillInput] = useState("");
  const [excludedKeywordInput, setExcludedKeywordInput] =
    useState("");

  const updatePreferences = (
    updates: Partial<PreferencesForm>,
  ) => {
    setPreferences((current) => ({
      ...current,
      ...updates,
    }));
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
    setPreferences(initialPreferences);
    setRoleInput("");
    setLocationInput("");
    setRequiredSkillInput("");
    setPreferredSkillInput("");
    setExcludedKeywordInput("");
  };

  const handleSave = () => {
    // API integration will be added later.
    console.log("Preferences saved:", preferences);
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
        </div>

        <div className="preferences-header-actions">
          <button
            type="button"
            className="preferences-button preferences-button-secondary"
            onClick={handleDiscard}
          >
            Discard Changes
          </button>

          <button
            type="button"
            className="preferences-button preferences-button-primary"
            onClick={handleSave}
          >
            Save Preferences
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
                        preferences.employmentTypes.includes(
                          type,
                        );

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
                            removeItem(
                              "requiredSkills",
                              skill,
                            )
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
                        !preferences.requiredSkills.includes(
                          skill,
                        ),
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
                            removeItem(
                              "preferredSkills",
                              skill,
                            )
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