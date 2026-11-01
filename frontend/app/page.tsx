"use client";
import React, { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export default function HomePage() {
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/health`).then((r) => r.json()).then(setHealth).catch(() => {});
    fetch(`${API_BASE}/api/vehicles`).then((r) => r.json()).then(setVehicles).catch(() => {});
  }, []);

  const primary = vehicles[0] || {
    brand: "Maruti Suzuki",
    model: "Alto 800",
    year: 2013,
    fuel_type: "Petrol",
    variant: "LXi • Manual (5MT) • BS-IV",
    engine: "F8D 796cc 3-Cylinder 12-Valve SOHC MPFI",
  };

  return (
    <main style={{ maxWidth: 1120, margin: "0 auto", padding: "32px 20px" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 28, fontWeight: 800 }}>AutoFix AI</h1>
          <p style={{ margin: "4px 0 0", color: "#94a3b8", fontSize: 14 }}>
            Your Vehicle Dashboard • Diagnostics • Guided DIY Repairs • Verification
          </p>
        </div>
        <span style={{ padding: "6px 12px", borderRadius: 8, background: "#1e293b", color: "#38bdf8", fontSize: 12 }}>
          {health ? `Connected: ${health.target_vehicle}` : "Backend API: http://localhost:8080"}
        </span>
      </header>

      <section style={{ padding: 24, borderRadius: 16, background: "#111827", border: "1px solid #1e3a8a", marginBottom: 24 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: "#60a5fa", textTransform: "uppercase" }}>MY GARAGE</div>
        <h2 style={{ fontSize: 26, margin: "6px 0 4px" }}>
          {primary.brand} {primary.model}
        </h2>
        <p style={{ margin: 0, color: "#cbd5e1", fontSize: 14 }}>
          {primary.year} • {primary.fuel_type} • {primary.variant} • {primary.engine}
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16, marginTop: 24 }}>
          <a href="/garage" style={{ padding: 18, borderRadius: 12, background: "#0f172a", border: "1px solid #334155", color: "#fff", textDecoration: "none" }}>
            <div style={{ fontWeight: 700, color: "#60a5fa" }}>Scan Vehicle</div>
            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>Read fault codes & F8D live PIDs</div>
          </a>
          <a href="/diagnostics" style={{ padding: 18, borderRadius: 12, background: "#0f172a", border: "1px solid #334155", color: "#fff", textDecoration: "none" }}>
            <div style={{ fontWeight: 700, color: "#38bdf8" }}>AI Diagnosis</div>
            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>Find probable causes & pinout tests</div>
          </a>
          <a href={`${API_BASE}/#diy`} style={{ padding: 18, borderRadius: 12, background: "#0f172a", border: "1px solid #334155", color: "#fff", textDecoration: "none" }}>
            <div style={{ fontWeight: 700, color: "#34d399" }}>DIY Repair</div>
            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>Guided procedures & MGP part numbers</div>
          </a>
          <a href="/reports" style={{ padding: 18, borderRadius: 12, background: "#0f172a", border: "1px solid #334155", color: "#fff", textDecoration: "none" }}>
            <div style={{ fontWeight: 700, color: "#c084fc" }}>Repair Report</div>
            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>Track & verify before/after telemetry</div>
          </a>
        </div>
      </section>
    </main>
  );
}
