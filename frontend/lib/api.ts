import { FinalPetHealthReport } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export async function createReport(formData: FormData): Promise<FinalPetHealthReport> {
  const res = await fetch(`${API_BASE}/api/report`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}
