import { useState } from "react";
import { Link } from "react-router-dom";
import { deleteIdea, listIdeas } from "../storage.js";

const formatDate = (iso) => {
  try {
    return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
  } catch {
    return "";
  }
};

export default function WorkspacePage() {
  const [ideas, setIdeas] = useState(() => listIdeas());

  const remove = (item) => {
    if (!window.confirm(`Delete "${item.form?.name || "this idea"}" from your workspace?`)) return;
    deleteIdea(item.id);
    setIdeas(listIdeas());
  };

  return (
    <>
      <div className="page-head">
        <h1>Your ideas</h1>
        <Link className="btn btn-primary" to="/">
          Validate a new idea
        </Link>
      </div>

      {ideas.length === 0 ? (
        <div className="empty">
          <h2>No ideas yet</h2>
          <p>Submit an idea and its report will be saved here.</p>
          <Link className="btn btn-primary" to="/">
            Validate your first idea
          </Link>
        </div>
      ) : (
        <ul className="rows">
          {ideas.map((item) => (
            <li key={item.id} className="row">
              <div>
                <Link to={`/workspace/${item.id}`} className="row-title">
                  {item.form?.name || "Untitled idea"}
                </Link>
                <p>{item.form?.description}</p>
                <dl className="meta">
                  <div>
                    <dt>Industry</dt>
                    <dd>{item.form?.industry}</dd>
                  </div>
                  <div>
                    <dt>Submitted</dt>
                    <dd>{formatDate(item.createdAt)}</dd>
                  </div>
                </dl>
              </div>
              <div>
                <button type="button" className="btn btn-quiet btn-small" onClick={() => remove(item)}>
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
