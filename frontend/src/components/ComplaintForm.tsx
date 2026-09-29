import { useState, type FormEvent } from "react";
import { ApiError, api } from "../api/client";
import type { Complaint, ComplaintCreate } from "../api/types";

const initialForm: ComplaintCreate = { text: "", location: "", reporter_contact: "" };

function validate(values: ComplaintCreate): string | null {
  if (values.text.trim().length < 10) return "Describe the complaint in at least 10 characters.";
  if (values.text.length > 2000) return "Description must be at most 2,000 characters.";
  if (values.location.trim().length < 3) return "Location must contain at least 3 characters.";
  if (values.location.length > 200) return "Location must be at most 200 characters.";
  if ((values.reporter_contact ?? "").length > 200) return "Contact must be at most 200 characters.";
  return null;
}

export function ComplaintForm({ onCreated }: { onCreated: (complaint: Complaint) => void }) {
  const [values, setValues] = useState<ComplaintCreate>(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Complaint | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function change(field: keyof ComplaintCreate, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationError = validate(values);
    if (validationError) { setError(validationError); return; }
    setError(null); setResult(null); setSubmitting(true);
    try {
      const complaint = await api.createComplaint({
        ...values,
        reporter_contact: values.reporter_contact?.trim() || null
      });
      setResult(complaint); setValues(initialForm); onCreated(complaint);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "We could not submit this complaint. Try again.");
    } finally { setSubmitting(false); }
  }

  return <section className="panel" aria-labelledby="submit-heading">
    <h2 id="submit-heading">Report a municipal issue</h2>
    <p className="muted">A triage result is generated after the complaint is received.</p>
    <form onSubmit={submit} noValidate>
      <label htmlFor="complaint-text">What happened?</label>
      <textarea id="complaint-text" value={values.text} onChange={(event) => change("text", event.target.value)} minLength={10} maxLength={2000} required />
      <label htmlFor="location">Location</label>
      <input id="location" value={values.location} onChange={(event) => change("location", event.target.value)} minLength={3} maxLength={200} required />
      <label htmlFor="contact">Contact (optional)</label>
      <input id="contact" value={values.reporter_contact ?? ""} onChange={(event) => change("reporter_contact", event.target.value)} maxLength={200} />
      {error && <p className="error" role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>{submitting ? "Submitting…" : "Submit complaint"}</button>
    </form>
    {result && <div className="result" role="status">
      <h3>Complaint received</h3>
      <p><strong>{result.category}</strong> · <strong>{result.priority}</strong> priority</p>
      <p>{result.ai_summary ?? "No summary returned."}</p>
      <p className="muted">Triage provider: {result.triaged_by} ({result.triage_latency_ms} ms)</p>
    </div>}
  </section>;
}
