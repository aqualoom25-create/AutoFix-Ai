"use client";
import React, { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export default function GaragePage() {
  const [spec, setSpec] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/vehicles/spec/alto-800-2013`)
      .then((r) => r.json())
      .then(setSpec)
      .catch(() => {});
  }, []);

  return (
    <main style={{ maxWidth: 1120, margin: "0 auto", padding: "32px 20px" }}>
      <a href="/" style={{ color: "#60a5fa", fontSize: 13, textDecoration: "none" }}>← Back to Dashboard</a>
      <h1 style={{ marginTop: 12 }}>My Garage — 2013 Maruti Suzuki Alto 800 (Petrol)</h1>
      {spec ? (
        <pre style={{ padding: 20, borderRadius: 12, background: "#0f172a", border: "1px solid #1e293b", overflowX: "auto", fontSize: 13 }}>
          {JSON.stringify(spec, null, 2)}
        </pre>
      ) : (
        <p>Loading 2013 Alto 800 F8D engineering specification...</p>
      )}
    </main>
  );
}
