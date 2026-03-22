# PetCare AI

A **multi-agent pet wellness assistant** MVP. Owners describe symptoms, share pet metadata, and optionally upload photos; the system returns a **structured report** with a risk level, guidance on when to seek veterinary care, and practical feeding and hydration tips—while clearly stating that it is **not a substitute for a veterinarian**.

---

## Why this project matters

Pet owners often face three gaps when something seems wrong:

1. **Communication** — Symptoms are messy, emotional, and easy to describe inconsistently.
2. **Context** — A single chat message rarely captures species, age, weight, and what can be seen in a photo.
3. **Decision stress** — Search results are noisy; it is hard to know whether to monitor at home or call a clinic today.

**PetCare AI explores a structured alternative:** a **transparent pipeline** of specialized steps (intake, vision, risk triage, feeding guidance) instead of one opaque chat bubble. That design makes it easier to **audit, test, and improve** each stage—important for any health-adjacent product—and to combine **learned models with explicit safety rules** (e.g., taking the **more conservative** risk level when rules and models disagree).

This repository is a **hackathon-ready full-stack demo**: it shows how modern **LLMs and multimodal models** can support **pre-visit triage and education**, not diagnosis or treatment. The same architecture could extend toward clinics, insurers, or tele-vet workflows with proper clinical governance.

---

## What it does

| Capability | Description |
|------------|-------------|
| **Intake** | Normalizes free-text symptoms and highlights possible urgent patterns (JSON via LLM when configured). |
| **Vision** | Reviews uploaded images with a vision-capable model; surfaces **uncertainty** when images are missing or ambiguous. |
| **Health risk** | Fuses metadata, intake, and vision outputs into a **risk level** and **escalation** copy; merges model output with a **rule-based floor** so severity is not under-stated. |
| **Feeding guidance** | General, non-prescriptive husbandry suggestions (food, water, what to avoid, what to monitor). |
| **Graceful degradation** | Without `OPENAI_API_KEY`, agents fall back to **built-in rules** so the app still runs for demos and CI. |

---

## Safety notice

- PetCare AI is **not** a diagnostic or treatment system.
- Outputs may be **wrong, incomplete, or misleading**.
- For **emergencies**—difficulty breathing, seizures, collapse, severe bleeding, uncontrolled vomiting or diarrhea—contact a **veterinarian or emergency clinic immediately**.

---

## Architecture

Pipeline (async orchestration):

```text
Intake → Vision → Health Risk → Feeding Guidance → FinalPetHealthReport
```

- Text agents use an **OpenAI-compatible** Chat Completions API with **JSON** responses.
- The vision step sends **base64** images in multimodal messages (suitable for demos; production would typically use object storage and signed URLs).
- The Next.js app posts to **same-origin** `/api/report`; a **route handler** proxies to FastAPI (`BACKEND_URL`) to avoid browser CORS friction during local development.

---

## Tech stack

- **Backend:** Python 3, FastAPI, Uvicorn, Pydantic, `openai` (async), `pydantic-settings`
- **Frontend:** Next.js (App Router), TypeScript
- **Contracts:** Pydantic models in `backend/app/schemas/`; JSON Schema references in `schemas/`

---

## Repository layout

```text
PetCare-AI/
  backend/
    app/
      agents/           # Intake, Vision, HealthRisk, FeedingGuidance
      llm/              # OpenAI JSON helpers (text + vision)
      schemas/
      settings.py
      orchestrator.py
      main.py
    .env.example
    requirements.txt
    uploads/            # runtime uploads (gitignored)
  frontend/
    app/
      api/report/       # Proxy route → FastAPI
      page.tsx
      report/page.tsx
    lib/
    .env.example
  schemas/              # *_agent_output.schema.json
  README.md
```

---

## Quick start

Run **two terminals**: backend on port **8000**, frontend on **3000**.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # add OPENAI_API_KEY for full LLM/vision behavior
uvicorn app.main:app --reload --port 8000
```

Check health:

```bash
curl http://127.0.0.1:8000/health
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # optional; see table below
npm run dev
```

Open **http://localhost:3000**, submit the form, then view the report (stored in `sessionStorage` for the session).

---

## Environment variables

### Backend (`backend/.env` — see `backend/.env.example`)

| Variable | Required for LLM | Description |
|----------|------------------|-------------|
| `OPENAI_API_KEY` | Yes | Enables model-backed agents. |
| `OPENAI_BASE_URL` | No | Compatible API base URL (proxies, some cloud providers). |
| `PETCARE_TEXT_MODEL` | No | Default: `gpt-4o-mini`. |
| `PETCARE_VISION_MODEL` | No | Default: `gpt-4o-mini` (must support images). |

### Frontend (`frontend/.env.local` — see `frontend/.env.example`)

| Variable | Description |
|----------|-------------|
| `BACKEND_URL` | Proxy target for `POST /api/report` (default `http://127.0.0.1:8000`). |
| `NEXT_PUBLIC_API_BASE` | If set, the browser calls this API base **directly** (bypasses proxy); ensure FastAPI CORS includes your frontend origin. |

Do **not** commit real secrets; keep `.env` / `.env.local` local only.

---

## HTTP API (FastAPI)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service metadata and links |
| GET | `/health` | Liveness |
| POST | `/api/report` | `multipart/form-data`: `owner_symptoms`, `species`, `age_years`, `weight_kg`, `sex`, `neutered`, optional `images` (repeatable) |

Interactive docs: **http://127.0.0.1:8000/docs**

---

## JSON schemas

Agent output shapes are documented under `schemas/`:

- `intake_agent_output.schema.json`
- `vision_agent_output.schema.json`
- `health_risk_agent_output.schema.json`
- `feeding_guidance_agent_output.schema.json`

---

## Troubleshooting

| Problem | Checks |
|---------|--------|
| **Failed to fetch** | Ensure Uvicorn is running on 8000; restart Next after changing `.env.local`; try the default proxy (unset `NEXT_PUBLIC_API_BASE`). |
| **CORS** (direct API mode) | Add your frontend origin to `CORSMiddleware` in `backend/app/main.py`. |

---

## License

No license file is included yet; add one (e.g. MIT) if you distribute the project publicly.
