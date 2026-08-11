import "../styles/overview-page.css";

function OverviewPage() {
  return (
    <section>
      <div className="page-header">
        <p className="eyebrow">OVERVIEW</p>

        <h1>Good morning.</h1>

        <p className="page-description">
          Here's what needs your attention today.
        </p>
      </div>

      <div className="placeholder-panel">
        <p>Overview dashboard coming next.</p>
      </div>
    </section>
  );
}

export default OverviewPage;