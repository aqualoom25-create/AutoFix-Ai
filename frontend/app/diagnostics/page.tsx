"use client";
import React, { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export default function DiagnosticsPage() {
  const [codes, setCodes] = useState("P0105, P0171");
  const [result, setResult] = useState<any>(null);

  async function runAnalysis() {
    const dtc_codes = codes.split(",").map((c) => c.trim()).filter(Boolean);
    const res = await fetch(`${API_BASE}/api/diagnosis/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dtc_codes, symptoms: ["rough_idle"] }),
    });
    setResult(await res.json());
  }

  return (
    <main style={{ maxWidth: 1120, margin: "0 auto", padding: "32px 20px" }}>
      <a href="/" style={{ color: "#60a5fa", fontSize: 13, textDecoration: "none" }}>← Back to Dashboard</a>
      <h1 style={{ marginTop: 12 }}>AI Diagnostic Engine — 2013 Alto 800 F8D</h1>
      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        <input
          value={codes}
          onChange={(e) => setCodes(e.target.value)}
          style={{ padding: "10px 14px", borderRadius: 8, background: "#0f172a", border: "1px solid #334155", color: "#fff", width: 320 }}
        />
        <button
          onClick={runAnalysis}
          style={{ padding: "10px 18px", borderRadius: 8, background: "#2563eb", color: "#fff", border: "none", fontWeight: 700, cursor: "pointer" }}
        >
          Analyze Faults
        </button>
      </div>
      {result && (
        <pre style={{ padding: 20, borderRadius: 12, background: "#0f172a", border: "1px solid #1e293b", overflowX: "auto", fontSize: 13 }}>
          {JSON.stringify(result.diagnosis, null, 2)}
        </pre>
      )}
    </main>
  );
}
