import { useEffect, useState } from "react";
import { AGENTS } from "../config.js";
import AgentList from "./AgentList.jsx";

// Shown while the backend works. The backend runs its agents one after another but
// does not report progress, so the highlighted step advances on a timer to show the order.
export default function AnalyzingPanel({ name }) {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setActive((i) => Math.min(i + 1, AGENTS.length - 1)), 2500);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-labelledby="analysing-title">
      <div className="overlay-panel">
        <h2 id="analysing-title">Analysing {name || "your idea"}</h2>
        <p className="muted">The agents run one after another. This can take up to two minutes.</p>
        <AgentList activeIndex={active} />
      </div>
    </div>
  );
}
