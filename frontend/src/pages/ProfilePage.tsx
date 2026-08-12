import { useState } from "react";
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

const initialProfile: ProfileForm = {
  fullName: "Alex Rivera",
  location: "San Francisco, CA",
  email: "alex.rivera@example.com",
  phone: "+1 (555) 019-2837",
  headline: "Senior Product Designer & Systems Thinker",
  bio: "Passionate about building scalable design systems and intuitive user interfaces. With over 8 years of experience bridging the gap between design, technology, and business.",
  linkedinUrl: "https://linkedin.com/in/alex-rivera",
  githubUrl: "https://github.com/alex-rivera",
  portfolioUrl: "https://alexrivera.design",
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileForm>(initialProfile);

  const updateField = (field: keyof ProfileForm, value: string) => {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleDiscard = () => {
    setProfile(initialProfile);
  };

  const handleSave = () => {
    // API integration will be added later.
    console.log("Profile saved:", profile);
  };

  return (
    <div className="profile-page">
      <header className="profile-page-header">
        <div>
          <p className="profile-eyebrow">PROFILE</p>
          <h1>Profile Settings</h1>
          <p className="profile-page-description">
            Manage your professional identity and public presence.
          </p>
        </div>

        <div className="profile-header-actions">
          <button
            type="button"
            className="profile-button profile-button-secondary"
            onClick={handleDiscard}
          >
            Discard Changes
          </button>

          <button
            type="button"
            className="profile-button profile-button-primary"
            onClick={handleSave}
          >
            Save Profile
          </button>
        </div>
      </header>

      <div className="profile-layout">
        <main className="profile-form-column">
          <section className="profile-card">
            <div className="profile-card-header">
              <h2>Personal Details</h2>
            </div>

            <div className="profile-form-grid">
              <div className="profile-field">
                <label htmlFor="full-name">Full Name</label>
                <input
                  id="full-name"
                  type="text"
                  value={profile.fullName}
                  onChange={(event) =>
                    updateField("fullName", event.target.value)
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="location">Location</label>
                <input
                  id="location"
                  type="text"
                  value={profile.location}
                  onChange={(event) =>
                    updateField("location", event.target.value)
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="email">Email Address</label>
                <input
                  id="email"
                  type="email"
                  value={profile.email}
                  onChange={(event) =>
                    updateField("email", event.target.value)
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="phone">Phone Number</label>
                <input
                  id="phone"
                  type="tel"
                  value={profile.phone}
                  onChange={(event) =>
                    updateField("phone", event.target.value)
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
                <label htmlFor="headline">Headline</label>
                <input
                  id="headline"
                  type="text"
                  value={profile.headline}
                  onChange={(event) =>
                    updateField("headline", event.target.value)
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
                    updateField("bio", event.target.value)
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="linkedin">LinkedIn URL</label>
                <input
                  id="linkedin"
                  type="url"
                  value={profile.linkedinUrl}
                  onChange={(event) =>
                    updateField("linkedinUrl", event.target.value)
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="github">GitHub URL</label>
                <input
                  id="github"
                  type="url"
                  value={profile.githubUrl}
                  onChange={(event) =>
                    updateField("githubUrl", event.target.value)
                  }
                />
              </div>

              <div className="profile-field">
                <label htmlFor="portfolio">Portfolio URL</label>
                <input
                  id="portfolio"
                  type="url"
                  value={profile.portfolioUrl}
                  onChange={(event) =>
                    updateField("portfolioUrl", event.target.value)
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
                {profile.fullName.charAt(0).toUpperCase()}
              </div>

              <h2>{profile.fullName || "Your Name"}</h2>

              <p className="profile-preview-headline">
                {profile.headline || "Your professional headline"}
              </p>

              <p className="profile-preview-location">
                <span aria-hidden="true">⌖</span>
                {profile.location || "Your location"}
              </p>

              <p className="profile-preview-bio">
                {profile.bio || "Your professional bio will appear here."}
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

          <p className="profile-preview-label">Public Profile Preview</p>
        </aside>
      </div>
    </div>
  );
}