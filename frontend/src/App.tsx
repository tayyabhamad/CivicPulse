import { useState } from "react";
import { ComplaintForm } from "./components/ComplaintForm";
import { Dashboard } from "./components/Dashboard";

export default function App() {
  const [refreshToken, setRefreshToken] = useState(0);
  return (
    <main className="app-shell">
      <header>
        <p className="eyebrow">Municipal services</p>
        <h1>CivicPulse</h1>
        <p>Report local issues and help teams act on what matters first.</p>
      </header>
      <div className="layout">
        <ComplaintForm onCreated={() => setRefreshToken((value) => value + 1)} />
        <Dashboard refreshToken={refreshToken} />
      </div>
    </main>
  );
}
