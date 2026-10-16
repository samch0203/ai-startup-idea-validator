import Markdownish from "./Markdownish.jsx";

const ACRONYMS = { mvp: "MVP", swot: "SWOT", gtm: "GTM", ai: "AI", url: "URL" };
const pretty = (key) =>
  String(key)
    .replace(/[_-]+/g, " ")
    .trim()
    .split(" ")
    .map((w, i) => ACRONYMS[w.toLowerCase()] ?? (i === 0 ? w.charAt(0).toUpperCase() + w.slice(1) : w))
    .join(" ");
const isPlain = (v) => v === null || ["string", "number", "boolean"].includes(typeof v);

function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "";
  }
}

// ---------------------------------------------------------------------------
// Shows ANY JSON in a readable way, so the report keeps working whatever shape
// the backend returns (plain text, lists, or nested objects).
// ---------------------------------------------------------------------------
export function SmartValue({ value }) {
  if (value === null || value === undefined || value === "") {
    return <p className="muted">Nothing was returned for this section.</p>;
  }
  if (typeof value === "string") return <Markdownish text={value} />;
  if (typeof value === "number" || typeof value === "boolean") return <p>{String(value)}</p>;

  if (Array.isArray(value)) {
    if (value.length === 0) return <p className="muted">None.</p>;
    if (value.every(isPlain)) {
      return (
        <ul className="plain-list">
          {value.map((v, i) => (
            <li key={i}>{String(v)}</li>
          ))}
        </ul>
      );
    }
    return (
      <div>
        {value.map((v, i) => (
          <div className="subcard" key={i}>
            <SmartValue value={v} />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div>
      {Object.entries(value).map(([key, v]) =>
        key === "evidence_limit" ? (
          <div key={key} className="callout">
            <strong>Evidence limit</strong>
            <span>{typeof v === "string" ? v : JSON.stringify(v)}</span>
          </div>
        ) : (
          <div key={key} className="kv-row">
            <h4>{pretty(key)}</h4>
            <SmartValue value={v} />
          </div>
        )
      )}
    </div>
  );
}

export function Section({ id, title, className = "", children }) {
  return (
    <section id={id} className={`section ${className}`.trim()}>
      <div className="section-head">
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Your idea
// ---------------------------------------------------------------------------
const INPUT_KEYS = ["name", "description", "target_market", "industry", "location", "budget"];

export function IdeaSection({ form, extra }) {
  // Anything the backend adds beyond what the user typed (for example a structured
  // problem statement or key features) is shown under its own heading.
  const more =
    extra && typeof extra === "object" && !Array.isArray(extra)
      ? Object.fromEntries(Object.entries(extra).filter(([k]) => !INPUT_KEYS.includes(k)))
      : null;
  const location = form.location || extra?.location;
  const budget = form.budget || extra?.budget;

  return (
    <>
      <dl className="idea-grid">
        <div>
          <dt>Industry</dt>
          <dd>{form.industry}</dd>
        </div>
        <div>
          <dt>Target customers</dt>
          <dd>{form.target_customers}</dd>
        </div>
        {location && (
          <div>
            <dt>Location</dt>
            <dd>{location}</dd>
          </div>
        )}
        {budget && (
          <div>
            <dt>Budget</dt>
            <dd>{budget}</dd>
          </div>
        )}
      </dl>
      <div className="kv-row">
        <h4>Description</h4>
        <Markdownish text={form.description} />
      </div>
      {form.details && (
        <div className="kv-row">
          <h4>Relevant details</h4>
          <Markdownish text={form.details} />
        </div>
      )}
      {more && Object.keys(more).length > 0 && (
        <div className="kv-row">
          <h4>Structured by the AI</h4>
          <SmartValue value={more} />
        </div>
      )}
    </>
  );
}

// ---------------------------------------------------------------------------
// Web search results
// ---------------------------------------------------------------------------
function SourceList({ items }) {
  return (
    <ul className="sources">
      {items.map((s, i) => {
        const url = typeof s?.url === "string" ? s.url : "";
        const safe = /^https?:\/\//i.test(url); // only real web links become clickable
        const title = s?.title || url || "Untitled source";
        const text = typeof s?.content === "string" ? s.content : "";
        return (
          <li key={i}>
            {safe ? (
              <a href={url} target="_blank" rel="noopener noreferrer">
                {title}
              </a>
            ) : (
              <strong>{title}</strong>
            )}
            {safe && <span className="host">{hostOf(url)}</span>}
            {text && <p>{text.length > 320 ? `${text.slice(0, 320)}...` : text}</p>}
          </li>
        );
      })}
    </ul>
  );
}

export function SourcesSection({ sources, webSearch, webSearchError }) {
  const base = Array.isArray(sources) ? sources : [];
  const live = Array.isArray(webSearch?.results) ? webSearch.results : [];
  const placeholder = [...base, ...live].some((s) => hostOf(s?.url || "") === "example.com");
  const failed = Array.isArray(webSearch?.failed_queries) ? webSearch.failed_queries : [];
  const queries = Array.isArray(webSearch?.generated_queries) ? webSearch.generated_queries : [];

  return (
    <>
      {placeholder && (
        <div className="callout">
          <strong>Sample results</strong>
          <span>These links are placeholders. The backend is running in test mode and has not searched the web.</span>
        </div>
      )}

      {base.length > 0 && <SourceList items={base} />}

      {webSearchError && (
        <div className="alert" role="alert">
          <strong>Live web search failed</strong>
          <span>{webSearchError} The rest of the report is not affected.</span>
        </div>
      )}

      {webSearch && (
        <div className={base.length > 0 ? "live-search" : undefined}>
          <h4>Live web search</h4>
          <p className="muted">
            {webSearch.total_results ?? live.length} results
            {webSearch.status && webSearch.status !== "success" ? `, status: ${webSearch.status}` : ""}.
          </p>
          {queries.length > 0 && (
            <div className="kv-row">
              <h4>Searches run</h4>
              <SmartValue value={queries} />
            </div>
          )}
          {live.length > 0 && <SourceList items={live} />}
          {failed.length > 0 && (
            <div className="callout">
              <strong>Some searches failed</strong>
              <span>{failed.map((f) => f.error).filter(Boolean).join(" ")}</span>
            </div>
          )}
        </div>
      )}

      {base.length === 0 && !webSearch && !webSearchError && <p className="muted">No sources were returned.</p>}
    </>
  );
}

// ---------------------------------------------------------------------------
// SWOT: a 2x2 matrix, followed by risks and any other fields
// ---------------------------------------------------------------------------
const QUADRANTS = [
  { key: "strengths", label: "Strengths", tone: "good" },
  { key: "weaknesses", label: "Weaknesses", tone: "bad" },
  { key: "opportunities", label: "Opportunities", tone: "blue" },
  { key: "threats", label: "Threats", tone: "warn" },
];

export function SwotSection({ data }) {
  const isObject = data && typeof data === "object" && !Array.isArray(data);
  if (!isObject || !QUADRANTS.some((q) => data[q.key] !== undefined)) return <SmartValue value={data} />;

  const others = Object.fromEntries(
    Object.entries(data).filter(([k]) => !QUADRANTS.some((q) => q.key === k))
  );

  return (
    <>
      <div className="swot">
        {QUADRANTS.map((q) => (
          <div key={q.key} className={`swot-cell ${q.tone}`}>
            <h4>
              <span className="swot-mark" aria-hidden="true" />
              {q.label}
            </h4>
            <SmartValue value={data[q.key] ?? []} />
          </div>
        ))}
      </div>
      {Object.keys(others).length > 0 && <SmartValue value={others} />}
    </>
  );
}
