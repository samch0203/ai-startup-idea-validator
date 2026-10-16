import { useState } from "react";
import { INDUSTRIES } from "../config.js";
import { SAMPLES } from "../samples.js";
import { EMPTY_FORM, LIMITS, validateIdea } from "../utils/validation.js";

function Field({ id, label, required, error, hint, count, children }) {
  return (
    <div className="field">
      <label htmlFor={id}>
        {label}
        {required && <span className="req" aria-hidden="true"> *</span>}
      </label>
      {children}
      {(error || hint || count) && (
        <div className="hint-row">
          {error ? (
            <span className="error" id={`${id}-error`}>
              {error}
            </span>
          ) : (
            <span>{hint}</span>
          )}
          {count && <span>{count}</span>}
        </div>
      )}
    </div>
  );
}

// Props:
//   onSubmit(form)  called only when every rule passes
//   loading         true while the request is running (disables the form)
//   error           readable message when the last request failed
export default function IdeaForm({ onSubmit, loading, error }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [touched, setTouched] = useState({});
  const [attempted, setAttempted] = useState(false);

  const errors = validateIdea(form);
  const show = (name) => (touched[name] || attempted ? errors[name] : undefined);
  const describedBy = (name) => (show(name) ? `${name}-error` : undefined);

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  const handleBlur = (e) => setTouched((t) => ({ ...t, [e.target.name]: true }));

  const handleSubmit = (e) => {
    e.preventDefault();
    setAttempted(true);
    const first = Object.keys(errors)[0];
    if (first) {
      document.getElementById(first)?.focus();
      return;
    }
    onSubmit(form);
  };

  const useSample = (sample) => {
    setForm({ ...EMPTY_FORM, ...sample.form });
    setTouched({});
    setAttempted(false);
  };

  const clear = () => {
    setForm(EMPTY_FORM);
    setTouched({});
    setAttempted(false);
  };

  return (
    <form className="sheet" onSubmit={handleSubmit} noValidate>
      <div className="form-head">
        <h2>Your idea</h2>
        <div className="examples">
          <span>Try an example:</span>
          {SAMPLES.map((s) => (
            <button key={s.label} type="button" className="example-btn" onClick={() => useSample(s)} disabled={loading}>
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <Field id="name" label="Startup name" required error={show("name")}>
        <input
          id="name"
          name="name"
          type="text"
          placeholder="e.g. PrepMate AI"
          value={form.name}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={Boolean(show("name"))}
          aria-describedby={describedBy("name")}
          disabled={loading}
        />
      </Field>

      <Field
        id="description"
        label="Idea description"
        required
        error={show("description")}
        hint={`At least ${LIMITS.descriptionMin} characters. Say what it is and what problem it solves.`}
        count={`${form.description.length}/${LIMITS.descriptionMax}`}
      >
        <textarea
          id="description"
          name="description"
          rows={5}
          placeholder="An app that helps..."
          value={form.description}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={Boolean(show("description"))}
          aria-describedby={describedBy("description")}
          disabled={loading}
        />
      </Field>

      <Field id="industry" label="Industry" required error={show("industry")}>
        <select
          id="industry"
          name="industry"
          value={form.industry}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={Boolean(show("industry"))}
          aria-describedby={describedBy("industry")}
          disabled={loading}
        >
          <option value="">Select an industry</option>
          {INDUSTRIES.map((i) => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </select>
      </Field>

      <Field id="target_customers" label="Target customers" required error={show("target_customers")}>
        <input
          id="target_customers"
          name="target_customers"
          type="text"
          placeholder="e.g. Final-year engineering students in India"
          value={form.target_customers}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={Boolean(show("target_customers"))}
          aria-describedby={describedBy("target_customers")}
          disabled={loading}
        />
      </Field>

      <div className="field-row">
        <Field id="location" label="Location (optional)" error={show("location")} hint="Defaults to India.">
          <input
            id="location"
            name="location"
            type="text"
            placeholder="e.g. Bengaluru"
            value={form.location}
            onChange={handleChange}
            onBlur={handleBlur}
            aria-invalid={Boolean(show("location"))}
            aria-describedby={describedBy("location")}
            disabled={loading}
          />
        </Field>
        <Field id="budget" label="Budget (optional)" error={show("budget")}>
          <input
            id="budget"
            name="budget"
            type="text"
            placeholder="e.g. Rs. 5 lakh"
            value={form.budget}
            onChange={handleChange}
            onBlur={handleBlur}
            aria-invalid={Boolean(show("budget"))}
            aria-describedby={describedBy("budget")}
            disabled={loading}
          />
        </Field>
      </div>

      <Field id="details" label="Relevant details (optional)" error={show("details")}>
        <textarea
          id="details"
          name="details"
          rows={3}
          placeholder="Business model, competitors you know of, anything else that helps."
          value={form.details}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-invalid={Boolean(show("details"))}
          aria-describedby={describedBy("details")}
          disabled={loading}
        />
      </Field>

      {error && (
        <div className="alert" role="alert">
          <strong>We could not validate your idea</strong>
          <span>{error} Your answers are still in the form, so you can try again.</span>
        </div>
      )}

      <div className="actions">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Analysing..." : "Validate my idea"}
        </button>
        <button type="button" className="btn btn-quiet" onClick={clear} disabled={loading}>
          Clear form
        </button>
      </div>
    </form>
  );
}
