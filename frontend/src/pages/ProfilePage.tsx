import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import "../styles/profile-page.css";

type ProfileForm = {
  fullName: string;
  location: string;
  email: string;
  phone: string;
  headline: string;
  bio: string;
  linkedinUrl: string;
  githubUrl: string;
  portfolioUrl: string;
};

type ProfileResponse = {
  id: string;
  user_id: string;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  headline: string | null;
  bio: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
};

const emptyProfile: ProfileForm = {
  fullName: "",
  location: "",
  email: "",
  phone: "",
  headline: "",
  bio: "",
  linkedinUrl: "",
  githubUrl: "",
  portfolioUrl: "",
};

function profileResponseToForm(
  data: ProfileResponse,
): ProfileForm {
  return {
    fullName: data.full_name ?? "",
    location: data.location ?? "",
    email: data.email ?? "",
    phone: data.phone ?? "",
    headline: data.headline ?? "",
    bio: data.bio ?? "",
    linkedinUrl: data.linkedin_url ?? "",
    githubUrl: data.github_url ?? "",
    portfolioUrl: data.portfolio_url ?? "",
  };
}

function profileFormToPayload(profile: ProfileForm) {
  return {
    full_name: profile.fullName || null,
    email: profile.email || null,
    phone: profile.phone || null,
    location: profile.location || null,
    headline: profile.headline || null,
    bio: profile.bio || null,
    linkedin_url: profile.linkedinUrl || null,
    github_url: profile.githubUrl || null,
    portfolio_url: profile.portfolioUrl || null,
  };
}

export default function ProfilePage() {
  const [profile, setProfile] =
    useState<ProfileForm>(emptyProfile);

  const [savedProfile, setSavedProfile] =
    useState<ProfileForm>(emptyProfile);

  const [profileId, setProfileId] =
    useState<string | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] =
    useState<string | null>(null);

  const updateField = (
    field: keyof ProfileForm,
    value: string,
  ) => {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));

    setSuccessMessage(null);
  };

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await apiRequest<ProfileResponse>(
          "/api/v1/profile",
        );

        if (cancelled) {
          return;
        }

        const form = profileResponseToForm(data);

        setProfile(form);
        setSavedProfile(form);
        setProfileId(data.id);
      } catch (err) {
        if (cancelled) {
          return;
        }

        const message =
          err instanceof Error ? err.message : "";

        if (message === "Profile not found") {
          setProfile(emptyProfile);
          setSavedProfile(emptyProfile);
          setProfileId(null);
        } else {
          setError(
            message || "Unable to load your profile.",
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadProfile();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleDiscard = () => {
    setProfile(savedProfile);
    setSuccessMessage(null);
    setError(null);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const payload = profileFormToPayload(profile);

      const data = profileId
        ? await apiRequest<ProfileResponse>(
            "/api/v1/profile",
            {
              method: "PATCH",
              body: JSON.stringify(payload),
            },
          )
        : await apiRequest<ProfileResponse>(
            "/api/v1/profile",
            {
              method: "POST",
              body: JSON.stringify(payload),
            },
          );

      const updatedForm =
        profileResponseToForm(data);

      setProfile(updatedForm);
      setSavedProfile(updatedForm);
      setProfileId(data.id);

      setSuccessMessage("Profile saved successfully.");
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Unable to save your profile.";

      setError(message);
    } finally {
      setIsSaving(false);
    }
  };

  const hasChanges =
    JSON.stringify(profile) !==
    JSON.stringify(savedProfile);

  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="profile-loading-state">
          Loading your profile...
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <header className="profile-page-header">
        <div>
          <p className="profile-eyebrow">PROFILE</p>

          <h1>Profile Settings</h1>

          <p className="profile-page-description">
            Manage your professional identity and public
            presence.
          </p>
        </div>

        <div className="profile-header-actions">
          <button
            type="button"
            className="profile-button profile-button-secondary"
            onClick={handleDiscard}
            disabled={!hasChanges || isSaving}
          >
            Discard Changes
          </button>

          <button
            type="button"
            className="profile-button profile-button-primary"
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
          >
            {isSaving ? "Saving..." : "Save Profile"}
          </button>
        </div>
      </header>

      {error && (
        <div className="profile-message profile-message-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="profile-message profile-message-success">
          {successMessage}
        </div>
      )}

      <div className="profile-layout">
        <main className="profile-form-column">
          <section className="profile-card">
            <div className="profile-card-header">
              <h2>Personal Details</h2>
            </div>

            <div className="profile-form-grid">
              <div className="profile-field">
                <label htmlFor="full-name">
                  Full Name
                </label>

                <input
                  id="full-name"
                  type="text"
                  value={profile.fullName}
                  onChange={(event) =>
                    updateField(
                      "fullName",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="location">
                  Location
                </label>

                <input
                  id="location"
                  type="text"
                  value={profile.location}
                  onChange={(event) =>
                    updateField(
                      "location",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="email">
                  Email Address
                </label>

                <input
                  id="email"
                  type="email"
                  value={profile.email}
                  onChange={(event) =>
                    updateField(
                      "email",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="phone">
                  Phone Number
                </label>

                <input
                  id="phone"
                  type="tel"
                  value={profile.phone}
                  onChange={(event) =>
                    updateField(
                      "phone",
                      event.target.value,
                    )
                  }
                />
              </div>
            </div>
          </section>

          <section className="profile-card">
            <div className="profile-card-header">
              <h2>Professional Identity</h2>
            </div>

            <div className="profile-form-stack">
              <div className="profile-field">
                <label htmlFor="headline">
                  Headline
                </label>

                <input
                  id="headline"
                  type="text"
                  value={profile.headline}
                  onChange={(event) =>
                    updateField(
                      "headline",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="bio">Bio</label>

                <textarea
                  id="bio"
                  rows={5}
                  value={profile.bio}
                  onChange={(event) =>
                    updateField(
                      "bio",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="linkedin">
                  LinkedIn URL
                </label>

                <input
                  id="linkedin"
                  type="url"
                  value={profile.linkedinUrl}
                  onChange={(event) =>
                    updateField(
                      "linkedinUrl",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="github">
                  GitHub URL
                </label>

                <input
                  id="github"
                  type="url"
                  value={profile.githubUrl}
                  onChange={(event) =>
                    updateField(
                      "githubUrl",
                      event.target.value,
                    )
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="portfolio">
                  Portfolio URL
                </label>

                <input
                  id="portfolio"
                  type="url"
                  value={profile.portfolioUrl}
                  onChange={(event) =>
                    updateField(
                      "portfolioUrl",
                      event.target.value,
                    )
                  }
                />
              </div>
            </div>
          </section>
        </main>

        <aside className="profile-preview-column">
          <div className="profile-preview-card">
            <div className="profile-preview-cover" />

            <div className="profile-preview-body">
              <div className="profile-avatar">
                {profile.fullName
                  ? profile.fullName
                      .charAt(0)
                      .toUpperCase()
                  : "?"}
              </div>

              <h2>
                {profile.fullName || "Your Name"}
              </h2>

              <p className="profile-preview-headline">
                {profile.headline ||
                  "Your professional headline"}
              </p>

              <p className="profile-preview-location">
                <span aria-hidden="true">⌖</span>

                {profile.location || "Your location"}
              </p>

              <p className="profile-preview-bio">
                {profile.bio ||
                  "Your professional bio will appear here."}
              </p>

              <div className="profile-preview-divider" />

              <div className="profile-social-links">
                {profile.linkedinUrl && (
                  <a
                    href={profile.linkedinUrl}
                    target="_blank"
                    rel="noreferrer"
                    aria-label="LinkedIn"
                  >
                    in
                  </a>
                )}

                {profile.githubUrl && (
                  <a
                    href={profile.githubUrl}
                    target="_blank"
                    rel="noreferrer"
                    aria-label="GitHub"
                  >
                    &lt;/&gt;
                  </a>
                )}

                {profile.portfolioUrl && (
                  <a
                    href={profile.portfolioUrl}
                    target="_blank"
                    rel="noreferrer"
                    aria-label="Portfolio"
                  >
                    ◎
                  </a>
                )}
              </div>
            </div>
          </div>

          <p className="profile-preview-label">
            Public Profile Preview
          </p>
        </aside>
      </div>
    </div>
  );
}