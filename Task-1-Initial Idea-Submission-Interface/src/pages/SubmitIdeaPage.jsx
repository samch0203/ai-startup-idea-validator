import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { config } from "../config.js";
import { submitIdea, searchWeb } from "../api/ideaApi.js";
import { saveIdea } from "../storage.js";
import IdeaForm from "../components/IdeaForm.jsx";
import AgentList from "../components/AgentList.jsx";
import AnalyzingPanel from "../components/AnalyzingPanel.jsx";

export default function SubmitIdeaPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [name, setName] = useState("");

  const handleSubmit = async (form) => {
    setError("");
    setName(form.name.trim());
    setLoading(true);
    try {
      const result = { ...(await submitIdea(form)) };

      // Optional extra: Task 3's live web search. A failure here never blocks the report.
      if (config.enableWebSearch) {
        try {
          result.web_search_agent = await searchWeb(form);
        } catch (err) {
          result.web_search_error = err.message;
        }
      }

      const saved = saveIdea({ form, result });
      navigate(`/workspace/${saved.id}`);
    } catch (err) {
      setError(err.message || "Something went wrong.");
      setLoading(false);
    }
  };

  return (
    <>
      <section className="hero">
        <h1>Find out if your startup idea holds up.</h1>
        <p className="lede">
          Describe it in a few lines. Six AI agents research the market, check competitors and write you a report.
        </p>
      </section>

      <div className="submit-grid">
        <IdeaForm onSubmit={handleSubmit} loading={loading} error={error} />

        <aside className="pipeline" aria-labelledby="pipeline-title">
          <h2 id="pipeline-title">What happens next</h2>
          <p className="sub">The agents run in this order, each building on the last.</p>
          <AgentList />
        </aside>
      </div>

      {loading && <AnalyzingPanel name={name} />}
    </>
  );
}
