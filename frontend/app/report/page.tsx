"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FinalPetHealthReport } from "../../lib/types";

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ReportPage() {
  const [report, setReport] = useState<FinalPetHealthReport | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("petcare_report");
    if (!raw) {
      return;
    }
    setReport(JSON.parse(raw));
  }, []);

  if (!report) {
    return (
      <main>
        <h1>No report found</h1>
        <p>Please submit a case first.</p>
        <Link href="/">Back to intake</Link>
      </main>
    );
  }

  return (
    <main>
      <h1>Pet Health Report</h1>
      <div className="card warning">{report.non_diagnostic_notice}</div>

      <div className="card">
        <h3>Risk Level: {report.risk.risk_level.toUpperCase()}</h3>
        <p><strong>Escalation:</strong> {report.risk.escalation_guidance}</p>
        <p><strong>Uncertainty:</strong> {report.risk.uncertainty_statement}</p>
      </div>

      <ListBlock title="Risk Reasons" items={report.risk.risk_reasons} />
      <ListBlock title="Urgent Red Flags" items={report.risk.urgent_red_flags} />
      <ListBlock title="Feeding Advice" items={report.feeding.feeding_advice} />
      <ListBlock title="Hydration Advice" items={report.feeding.hydration_advice} />
      <ListBlock title="Avoid List" items={report.feeding.avoid_list} />
      <ListBlock title="Monitoring Tips" items={report.feeding.monitoring_tips} />

      <div className="card">
        <h3>Vision Observations</h3>
        <ul>
          {report.vision.observations.map((obs, idx) => (
            <li key={`${obs.label}-${idx}`}>
              [{Math.round(obs.confidence * 100)}%] {obs.label}: {obs.note}
            </li>
          ))}
        </ul>
      </div>

      <Link href="/">Create another report</Link>
    </main>
  );
}
