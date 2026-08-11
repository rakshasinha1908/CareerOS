import "../styles/placeholder-page.css";

interface PlaceholderPageProps {
  title: string;
  description: string;
}

function PlaceholderPage({
  title,
  description,
}: PlaceholderPageProps) {
  return (
    <section>
      <div className="placeholder-page-header">
        <p className="placeholder-page-eyebrow">CAREEROS</p>

        <h1>{title}</h1>

        <p className="placeholder-page-description">
          {description}
        </p>
      </div>

      <div className="placeholder-panel">
        <p>This section is coming next.</p>
      </div>
    </section>
  );
}

export default PlaceholderPage;