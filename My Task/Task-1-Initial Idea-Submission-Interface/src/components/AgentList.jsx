import { AGENTS } from "../config.js";

function Check() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
      <path d="M2.5 7.5l3 3 6-7" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// The six agents in the order they run. Pass `activeIndex` to show progress;
// leave it out for a plain explanation list.
export default function AgentList({ activeIndex }) {
  const staged = typeof activeIndex === "number";
  return (
    <ol className="agent-list">
      {AGENTS.map((agent, i) => {
        const state = !staged ? "" : i < activeIndex ? "done" : i === activeIndex ? "active" : "todo";
        return (
          <li key={agent.id} className={state}>
            <span className="step-no">{state === "done" ? <Check /> : i + 1}</span>
            <span>
              <strong>{agent.name}</strong>
              <small>{agent.job}</small>
            </span>
          </li>
        );
      })}
    </ol>
  );
}
