import "../styles/overview-page.css";

const actionItems = [
  {
    icon: "✉",
    count: "3 Applications",
    label: "Need follow-up today",
    badge: "Urgent",
    badgeType: "urgent",
  },
  {
    icon: "□",
    count: "2 Outreach",
    label: "Follow-ups due",
    badge: null,
    badgeType: "",
  },
  {
    icon: "▣",
    count: "1 Interview",
    label: "Product Designer @ Vercel",
    badge: "Tomorrow",
    badgeType: "success",
  },
];

const pipeline = [
  { label: "Saved", value: 12, state: "" },
  { label: "Applied", value: 8, state: "active" },
  { label: "OA", value: 3, state: "" },
  { label: "Interview", value: 1, state: "success" },
  { label: "Offer", value: 0, state: "muted" },
];

const matches = [
  {
    role: "Senior Product Designer",
    company: "Stripe",
    location: "Remote (US)",
    match: "94%",
  },
  {
    role: "UX Engineer",
    company: "Vercel",
    location: "San Francisco, CA",
    match: "88%",
  },
  {
    role: "Interaction Designer",
    company: "Figma",
    location: "New York, NY",
    match: "82%",
  },
];

const activities = [
  {
    title: "Interview scheduled with Vercel",
    time: "2 hours ago",
    active: true,
  },
  {
    title: "Application sent to Linear",
    time: "Yesterday",
    active: false,
  },
  {
    title: "Followed up with Sarah from Stripe",
    time: "Yesterday",
    active: false,
  },
  {
    title: "Saved 3 new opportunities",
    time: "Oct 24",
    active: false,
  },
];

function OverviewPage() {
  return (
    <div className="overview-page">
      <header className="page-header">
        <p className="eyebrow">OVERVIEW</p>

        <h1>Good morning.</h1>

        <p className="page-description">
          Here's what needs your attention today.
        </p>
      </header>

      <section className="overview-section">
        <div className="section-heading">
          <span>ACTION REQUIRED</span>
        </div>

        <div className="action-grid">
          {actionItems.map((item) => (
            <article
              className={`action-card ${
                item.badgeType === "success" ? "action-card-success" : ""
              }`}
              key={item.count}
            >
              <div className="action-card-top">
                <span className="action-icon">{item.icon}</span>

                {item.badge && (
                  <span className={`status-badge ${item.badgeType}`}>
                    {item.badge}
                  </span>
                )}
              </div>

              <div className="action-card-count">{item.count}</div>

              <div className="action-card-label">{item.label}</div>
            </article>
          ))}
        </div>
      </section>

      <section className="pipeline-card">
        <div className="pipeline-header">
          <span className="pipeline-title">APPLICATION PIPELINE</span>

          <button className="text-button">
            View Board <span>→</span>
          </button>
        </div>

        <div className="pipeline">
          {pipeline.map((item, index) => (
            <div className="pipeline-step-wrapper" key={item.label}>
              <div className={`pipeline-step ${item.state}`}>
                <div className="pipeline-number">{item.value}</div>
                <div className="pipeline-label">{item.label}</div>
              </div>

              {index < pipeline.length - 1 && (
                <div className="pipeline-line" />
              )}
            </div>
          ))}
        </div>
      </section>

      <div className="overview-lower-grid">
        <section className="matches-card">
          <div className="card-header">
            <span>NEW MATCHES</span>

            <button
              className="card-icon-button"
              aria-label="Filter matches"
            >
              ☷
            </button>
          </div>

          <div className="matches-list">
            {matches.map((match) => (
              <article className="match-row" key={match.role}>
                <div className="company-placeholder">
                  {match.company.charAt(0)}
                </div>

                <div className="match-info">
                  <h3>{match.role}</h3>

                  <p>
                    {match.company}
                    <span> • </span>
                    {match.location}
                  </p>
                </div>

                <span className="match-badge">
                  ↯ {match.match} Match
                </span>
              </article>
            ))}
          </div>
        </section>

        <section className="activity-card">
          <div className="card-header">
            <span>RECENT ACTIVITY</span>
          </div>

          <div className="activity-list">
            {activities.map((activity) => (
              <article className="activity-item" key={activity.title}>
                <div
                  className={`activity-dot ${
                    activity.active ? "active" : ""
                  }`}
                >
                  {activity.active && <span />}
                </div>

                <div className="activity-content">
                  <p>{activity.title}</p>
                  <span>{activity.time}</span>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default OverviewPage;