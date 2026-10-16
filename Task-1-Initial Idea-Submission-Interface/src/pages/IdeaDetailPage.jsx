import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { config, MODULES } from "../config.js";
import { getIdea } from "../storage.js";
import { downloadReport } from "../utils/reportMarkdown.js";
import AdvisorChat from "../components/AdvisorChat.jsx";
import Markdownish from "../components/Markdownish.jsx";
import { IdeaSection, Section, SmartValue, SourcesSection, SwotSection } from "../components/ReportSections.jsx";

// Finds the first matching key from the backend response (see MODULES in config.js).
function findSection(result, keys) {
  if (!result || typeof result !== "object") return undefined;
  const key = keys.find((k) => result[k] !== undefined && result[k] !== null);
  return key ? result[key] : undefined;
}

const formatDate = (iso) => {
  try {
    return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
  } catch {
    return "";
  }
};

export default function IdeaDetailPage() {
  const { id } = useParams();
  const item = useMemo(() => getIdea(id), [id]);
  const [active, setActive] = useState("");

  // The form page is long, so a new report would otherwise open part-way down the page.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  const result = item?.result ?? {};
  const data = {};
  for (const m of MODULES) data[m.id] = findSection(result, m.keys);

  const hasSearch = data.search !== undefined || Boolean(result.web_search_agent) || Boolean(result.web_search_error);
  const advisorAvailable = config.useMock || Boolean(config.endpoints.advisor);

  // Left rail: only sections that exist, plus the two that always do.
  const nav = [
    data.report !== undefined && { id: "summary", label: "Summary" },
    { id: "idea", label: "Your idea" },
    hasSearch && { id: "search", label: "Web search" },
    data.market !== undefined && { id: "market", label: "Market analysis" },
    data.competitors !== undefined && { id: "competitors", label: "Competitors" },
    data.swot !== undefined && { id: "swot", label: "SWOT and risks" },
    data.mvp !== undefined && { id: "mvp", label: "MVP features" },
    { id: "gtm", label: "Go-to-market" },
    { id: "advisor", label: "Advisor" },
  ].filter(Boolean);
  const navKey = nav.map((n) => n.id).join(",");

  // Highlight the rail entry for the section currently on screen.
  useEffect(() => {
    if (!item || !("IntersectionObserver" in window)) return undefined;
    const ids = navKey.split(",");
    const elements = ids.map((i) => document.getElementById(i)).filter(Boolean);
    if (elements.length === 0) return undefined;
    setActive((a) => a || ids[0]);
    const observer = new IntersectionObserver(
      (entries) => {
        const hit = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (hit) setActive(hit.target.id);
      },
      { rootMargin: "-15% 0px -70% 0px" }
    );
    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [item, navKey]);

  const go = (sectionId) => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    document.getElementById(sectionId)?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    setActive(sectionId);
  };

  if (!item) {
    return (
      <div className="empty">
        <h1>We could not find that idea</h1>
        <p>It may have been deleted, or it was saved in a different browser.</p>
        <Link className="btn btn-primary" to="/workspace">
          Back to your ideas
        </Link>
      </div>
    );
  }

  const { form } = item;
  const location = form.location || data.extraction?.location;
  const budget = form.budget || data.extraction?.budget;

  return (
    <div className="report">
      <nav className="rail" aria-label="Report sections">
        <ol>
          {nav.map((n) => (
            <li key={n.id}>
              <button type="button" onClick={() => go(n.id)} aria-current={active === n.id ? "true" : undefined}>
                {n.label}
              </button>
            </li>
          ))}
        </ol>
      </nav>

      <article className="report-body">
        <header className="report-head">
          <Link to="/workspace" className="back">
            Back to your ideas
          </Link>
          <h1>{form.name || "Untitled idea"}</h1>
          <dl className="meta">
            <div>
              <dt>Industry</dt>
              <dd>{form.industry}</dd>
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
            <div>
              <dt>Submitted</dt>
              <dd>{formatDate(item.createdAt)}</dd>
            </div>
          </dl>
          <div className="actions">
            <button type="button" className="btn btn-primary btn-small" onClick={() => downloadReport(item)}>
              Download report
            </button>
            <button type="button" className="btn btn-small" onClick={() => window.print()}>
              Print
            </button>
            <Link className="btn btn-small" to="/">
              Validate another idea
            </Link>
          </div>
        </header>

        {data.report !== undefined && (
          <Section id="summary" title="Summary">
            <div className="sheet summary">
              {typeof data.report === "string" ? <Markdownish text={data.report} /> : <SmartValue value={data.report} />}
            </div>
          </Section>
        )}

        <Section id="idea" title="Your idea">
          <div className="sheet">
            <IdeaSection form={form} extra={data.extraction} />
          </div>
        </Section>

        {hasSearch && (
          <Section id="search" title="Web search">
            <div className="sheet">
              <SourcesSection
                sources={data.search}
                webSearch={result.web_search_agent}
                webSearchError={result.web_search_error}
              />
            </div>
          </Section>
        )}

        {data.market !== undefined && (
          <Section id="market" title="Market analysis">
            <div className="sheet">
              <SmartValue value={data.market} />
            </div>
          </Section>
        )}

        {data.competitors !== undefined && (
          <Section id="competitors" title="Competitors">
            <div className="sheet">
              <SmartValue value={data.competitors} />
            </div>
          </Section>
        )}

        {data.swot !== undefined && (
          <Section id="swot" title="SWOT and risks">
            <div className="sheet">
              <SwotSection data={data.swot} />
            </div>
          </Section>
        )}

        {data.mvp !== undefined && (
          <Section id="mvp" title="MVP features">
            <div className="sheet">
              <SmartValue value={data.mvp} />
            </div>
          </Section>
        )}

        <Section id="gtm" title="Go-to-market">
          {data.gtm !== undefined ? (
            <div className="sheet">
              <SmartValue value={data.gtm} />
            </div>
          ) : (
            <div className="empty-note">
              The backend does not produce a go-to-market strategy yet. It will appear here once it does.
            </div>
          )}
        </Section>

        <Section id="advisor" title="Ask the advisor" className="advisor-section">
          {advisorAvailable ? (
            <div className="sheet">
              <AdvisorChat ideaId={item.id} />
            </div>
          ) : (
            <div className="empty-note">
              Follow-up questions will be available once the backend supports the advisor.
            </div>
          )}
        </Section>
      </article>
    </div>
  );
}
