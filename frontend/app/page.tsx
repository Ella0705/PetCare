"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createReport } from "../lib/api";
import { FinalPetHealthReport } from "../lib/types";

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const form = event.currentTarget;
    const formData = new FormData(form);

    const neuteredValue = formData.get("neutered");
    formData.set("neutered", neuteredValue === "true" ? "true" : "false");

    const files = (form.elements.namedItem("images") as HTMLInputElement).files;
    if (files) {
      for (let i = 0; i < files.length; i += 1) {
        formData.append("images", files[i]);
      }
    }

    try {
      const report: FinalPetHealthReport = await createReport(formData);
      sessionStorage.setItem("petcare_report", JSON.stringify(report));
      router.push("/report");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>PetCare AI MVP</h1>
      <p>Multi-agent pet wellness assistant for hackathon demos.</p>

      <div className="card warning">
        This is not a diagnosis tool. If severe symptoms appear, contact a veterinarian immediately.
      </div>

      <form className="card" onSubmit={onSubmit}>
        <label>
          Species
          <select name="species" defaultValue="dog" required>
            <option value="dog">Dog</option>
            <option value="cat">Cat</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label>
          Age (years)
          <input name="age_years" type="number" min="0" step="0.1" required />
        </label>

        <label>
          Weight (kg)
          <input name="weight_kg" type="number" min="0.1" step="0.1" required />
        </label>

        <label>
          Sex
          <select name="sex" defaultValue="female" required>
            <option value="female">Female</option>
            <option value="male">Male</option>
          </select>
        </label>

        <label>
          Neutered?
          <select name="neutered" defaultValue="true" required>
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </label>

        <label>
          Owner Symptom Description
          <textarea
            name="owner_symptoms"
            rows={5}
            placeholder="e.g., low appetite for 2 days, vomiting once, seems tired"
            required
          />
        </label>

        <label>
          Pet Photos (one or more)
          <input name="images" type="file" accept="image/*" multiple />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Generating report..." : "Generate Report"}
        </button>

        {error ? <p style={{ color: "crimson" }}>Error: {error}</p> : null}
      </form>
    </main>
  );
}
