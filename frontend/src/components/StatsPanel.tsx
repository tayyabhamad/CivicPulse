import { useEffect, useState } from "react";
interface Stats { by_category: Record<string,number>; by_priority: Record<string,number>; total: number; }
export function StatsPanel() {
  const [stats, setStats] = useState<Stats|null>(null);
  const [cacheHit, setCacheHit] = useState<boolean|null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch("/api/operations/stats").then(async res => {
      setCacheHit(res.headers.get("X-Cache") === "HIT");
      return res.json();
    }).then(d => { setStats(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);
  if (loading) return <p>Loading stats...</p>;
  if (!stats) return <p>Failed to load stats.</p>;
  return (
    <section>
      <h2>Statistics</h2>
      {cacheHit !== null && <p style={{fontSize:"0.75rem",color:cacheHit?"#16a34a":"#9ca3af"}}>{cacheHit ? "✓ Cache HIT" : "○ Cache MISS"}</p>}
      <p><strong>Total:</strong> {stats.total}</p>
      <ul>{Object.entries(stats.by_category).map(([k,v]) => <li key={k}>{k}: {v}</li>)}</ul>
      <ul>{Object.entries(stats.by_priority).map(([k,v]) => <li key={k}>{k}: {v}</li>)}</ul>
    </section>
  );
}
