import { useCallback, useEffect, useState } from "react";
import { ApiError, api } from "../api/client";
import { categories, complaintStatuses, priorities, type ComplaintFilters, type ComplaintStatus, type StatsResponse } from "../api/types";

const pageSize = 10;
const defaultFilters: ComplaintFilters = { page: 1, pageSize };

function title(value: string): string { return value.replaceAll("_", " "); }

export function Dashboard({ refreshToken }: { refreshToken: number }) {
  const [filters, setFilters] = useState<ComplaintFilters>(defaultFilters);
  const [page, setPage] = useState<{ items: Awaited<ReturnType<typeof api.listComplaints>>["items"]; total: number }>({ items: [], total: 0 });
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [complaints, nextStats] = await Promise.all([api.listComplaints(filters), api.stats()]);
      setPage(complaints); setStats(nextStats);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Could not load the operations dashboard.");
    } finally { setLoading(false); }
  }, [filters]);

  useEffect(() => { void load(); }, [load, refreshToken]);

  function changeFilter(name: "category" | "priority" | "status", value: string) {
    setFilters((current) => ({ ...current, [name]: value || undefined, page: 1 }));
  }

  async function changeStatus(id: string, status: ComplaintStatus) {
    setUpdatingId(id); setError(null);
    try { await api.updateStatus(id, status); await load(); }
    catch (caught) {
      // The server's transition explanation is deliberately shown verbatim.
      setError(caught instanceof ApiError ? caught.message : "Could not update complaint status.");
    } finally { setUpdatingId(null); }
  }

  const pages = Math.max(1, Math.ceil(page.total / pageSize));
  return <section className="panel" aria-labelledby="dashboard-heading">
    <div className="section-heading"><div><h2 id="dashboard-heading">Operations dashboard</h2><p className="muted">Current municipal complaint queue.</p></div>{stats && <span className="cache-badge">Stats cache: {stats.cache}</span>}</div>
    {stats && <div className="stats" aria-label="Complaint statistics"><div><span>Total</span><strong>{stats.data.total}</strong></div>{complaintStatuses.map((status) => <div key={status}><span>{title(status)}</span><strong>{stats.data.by_status[status] ?? 0}</strong></div>)}</div>}
    <div className="filters">
      <label>Category<select aria-label="Filter category" value={filters.category ?? ""} onChange={(event) => changeFilter("category", event.target.value)}><option value="">All categories</option>{categories.map((value) => <option key={value} value={value}>{title(value)}</option>)}</select></label>
      <label>Priority<select aria-label="Filter priority" value={filters.priority ?? ""} onChange={(event) => changeFilter("priority", event.target.value)}><option value="">All priorities</option>{priorities.map((value) => <option key={value} value={value}>{title(value)}</option>)}</select></label>
      <label>Status<select aria-label="Filter status" value={filters.status ?? ""} onChange={(event) => changeFilter("status", event.target.value)}><option value="">All statuses</option>{complaintStatuses.map((value) => <option key={value} value={value}>{title(value)}</option>)}</select></label>
    </div>
    {error && <div className="error" role="alert"><p>{error}</p><button type="button" onClick={() => void load()} disabled={loading}>Retry</button></div>}
    {loading ? <p role="status">Loading complaints…</p> : <div className="table-wrap"><table><thead><tr><th>Issue</th><th>Location</th><th>Triage</th><th>Status</th><th>Action</th></tr></thead><tbody>
      {page.items.map((complaint) => <tr key={complaint.id}><td><strong>{complaint.ai_summary ?? complaint.text}</strong><small>{complaint.triaged_by}</small></td><td>{complaint.location}</td><td>{complaint.category}<small>{complaint.priority}</small></td><td>{title(complaint.status)}</td><td><select aria-label={`Update ${complaint.id}`} value={complaint.status} disabled={updatingId === complaint.id} onChange={(event) => void changeStatus(complaint.id, event.target.value as ComplaintStatus)}>{complaintStatuses.map((status) => <option key={status} value={status}>{title(status)}</option>)}</select></td></tr>)}
      {page.items.length === 0 && <tr><td colSpan={5}>No complaints match these filters.</td></tr>}
    </tbody></table></div>}
    <nav className="pagination" aria-label="Complaint pages"><button disabled={loading || filters.page === 1} onClick={() => setFilters((current) => ({ ...current, page: current.page - 1 }))}>Previous</button><span>Page {filters.page} of {pages} ({page.total} total)</span><button disabled={loading || filters.page >= pages} onClick={() => setFilters((current) => ({ ...current, page: current.page + 1 }))}>Next</button></nav>
  </section>;
}
