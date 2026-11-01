import React from "react";

export const metadata = {
  title: "AutoFix AI — 2013 Maruti Alto 800 (F8D Petrol) Diagnostic SaaS",
  description: "AI Automotive Diagnostics, F8D Wiring Pinout Analyzer, Guided DIY & Repair Verification",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, backgroundColor: "#0b0f19", color: "#e2e8f0", fontFamily: "Inter, system-ui, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
