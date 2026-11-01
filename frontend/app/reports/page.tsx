"use client";
import React, { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/reports`)
      .then((r) => r.json())
      .then(setReports)
      .catch(() => {});
  }, []);

  return (
    <main style={{ maxWidth: 1120, margin: "0 auto", padding: "32px 20px" }}>
      <a href="/" style={{ color: "#60a5fa", fontSize: 13, textDecoration: "none" }}>← Back to Dashboard</a>
      <h1 style={{ marginTop: 12 }}>Repair Verification Reports</h1>
      <div style={{ display: "grid", gap: 16 }}>
        {reports.map((r) => (
          <div key={r.id} style={{ padding: 18, borderRadius: 12, background: "#0f172a", border: "1px solid #334155" }}>
            <div style={{ fontWeight: 700, color: r.verified ? "#34d399" : "#fbbf24" }}>
              {r.verified ? "✓ VERIFIED REPAIR" : "⚠ UNVERIFIED"}
            </div>
            <p style={{ margin: "8px 0" }}>{r.repair_description}</p>
            <div style={{ fontSize: 13, color: "#38bdf8" }}>{r.verification_report?.engineering_verdict}</div>
          </div>
        ))}
      </div>
    </main>
  );
}
