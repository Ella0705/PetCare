# PetCare AI

Multi-agent **pet wellness assistant** MVP: owners submit symptoms, pet metadata, and optional photos; the app returns a **structured report** with risk level, veterinary escalation guidance, feeding/hydration tips, and explicit **non-diagnostic** disclaimers.

**中文概要：** 基于 **FastAPI + Next.js** 的全栈演示项目；四个 Agent（分诊、视觉、风险、喂养）由编排器串联，支持 **OpenAI 兼容 API**（可选），无密钥时自动回退规则逻辑。前端默认通过 **Next 服务端代理** 调用后端，避免浏览器跨域问题。

---

## Safety notice

- PetCare AI is **not** a diagnosis or treatment tool.
- Outputs may be wrong, incomplete, or uncertain.
- **Emergencies** (trouble breathing, seizure, collapse, severe bleeding, non-stop vomiting/diarrhea): seek **immediate** veterinary care.

---

## Features

| Area | Behavior |
|------|----------|
| **Intake** | Normalizes free-text symptoms; surfaces possible urgent keywords (LLM + JSON when API key set). |
| **Vision** | Multimodal review of uploads (base64 → vision-capable model); uncertainty notes when images are missing or unclear. |
| **Health risk** | Combines metadata + intake + vision; **model suggestion merged with rule-based floor** (more conservative level wins). |
| **Feeding** | General husbandry bullets only — no prescriptions or drug advice. |
| **Resilience** | No `OPENAI_API_KEY` → each agent falls back to built-in rules / placeholders. |
| **Frontend transport** | Browser calls same-origin `POST /api/report`; Next.js forwards to FastAPI (`BACKEND_URL`). |

---

## Tech stack

- **Backend:** Python 3, FastAPI, Uvicorn, Pydantic, `openai` (async), `pydantic-settings`
- **Frontend:** Next.js (App Router), TypeScript
- **Contracts:** Pydantic models under `backend/app/schemas/`; JSON Schema mirrors in `schemas/`

---

## Architecture

Orchestration (async):

```text
Intake → Vision → Health Risk → Feeding Guidance → FinalPetHealthReport
```

- **OpenAI-compatible** Chat Completions with `response_format: json_object` for text agents; vision agent uses multimodal messages.
- CORS on FastAPI allows local Next dev origins (`localhost` / `127.0.0.1` on ports 3000–3001); `allow_credentials` is **false** (compatible with strict browsers).

---

## Repository layout

```text
PetCare-AI/
  backend/
    app/
      agents/           # Intake, Vision, HealthRisk, FeedingGuidance
      llm/              # OpenAI JSON helpers (text + vision)
      schemas/          # Pydantic I/O models
      settings.py       # env-driven config
      orchestrator.py
      main.py           # FastAPI app, CORS, /health, /api/report
    .env.example
    requirements.txt
    uploads/            # created at runtime (gitignored)
  frontend/
    app/
      api/report/       # Route handler: proxy to FastAPI
      page.tsx
      report/page.tsx
    lib/api.ts
    .env.example
  schemas/              # *_agent_output.schema.json
  README.md
```

---

## Prerequisites

- Python **3.10+** recommended
- **Node.js** + npm (for the frontend)
- Optional: **OpenAI API key** (or compatible gateway) for full LLM/vision behavior

---

## Quick start (local)

Use **two terminals**: backend always on **:8000**, frontend on **:3000**.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # add OPENAI_API_KEY if you want LLM mode
uvicorn app.main:app --reload --port 8000
```

Smoke test:

```bash
curl http://127.0.0.1:8000/health
# curl http://127.0.0.1:8000/       # service JSON + doc links
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local         # optional; defaults shown below
npm run dev
```

Open **http://localhost:3000** → fill the form → **Generate Report** → report page (data stored in `sessionStorage` for the session).

---

## Environment variables

### `backend/.env` (see `backend/.env.example`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No* | Enables LLM + vision paths; omit to use rule fallback only. |
| `OPENAI_BASE_URL` | No | Compatible API base (proxies, Azure-style endpoints). |
| `PETCARE_TEXT_MODEL` | No | Default `gpt-4o-mini`. |
| `PETCARE_VISION_MODEL` | No | Default `gpt-4o-mini` (must support images). |

\*Required only if you want model-backed agents.

### `frontend/.env.local` (see `frontend/.env.example`)

| Variable | Description |
|----------|-------------|
| `BACKEND_URL` | Where Next proxies `POST /api/report` (default `http://127.0.0.1:8000`). |
| `NEXT_PUBLIC_API_BASE` | If set, the **browser** calls this base URL directly instead of the proxy; ensure FastAPI CORS includes your frontend origin. |

**Never commit** real `.env` files; only `.env.example` belongs in git.

---

## HTTP API (FastAPI)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info + links to docs |
| GET | `/health` | Liveness |
| POST | `/api/report` | `multipart/form-data`: `owner_symptoms`, `species`, `age_years`, `weight_kg`, `sex`, `neutered`, optional repeated `images` |

Interactive docs: **http://127.0.0.1:8000/docs**

---

## JSON schemas

Reference schemas for agent outputs live in `schemas/`:

- `intake_agent_output.schema.json`
- `vision_agent_output.schema.json`
- `health_risk_agent_output.schema.json`
- `feeding_guidance_agent_output.schema.json`

---

## Troubleshooting

| Issue | What to check |
|--------|----------------|
| **Failed to fetch** | Backend running on 8000; restart Next after `.env.local` changes; try default proxy (clear `NEXT_PUBLIC_API_BASE`). |
| **CORS errors** when using direct API | Use listed dev origins or add yours in `backend/app/main.py` (`CORSMiddleware`). |
| **404 on `/`** (backend) | Use `/health` or `/docs`; root route returns JSON service card. |

---

## License

No license file is bundled yet; add one (e.g. MIT) if you open-source publicly.

---

## 中文：本地怎么跑

1. **终端 A**：`cd backend` → 虚拟环境 → `pip install -r requirements.txt` → 配置 `.env`（可选填 Key）→ `uvicorn app.main:app --reload --port 8000`。  
2. **终端 B**：`cd frontend` → `npm install` → `npm run dev`。  
3. 浏览器打开 **http://localhost:3000** 提交表单。  
4. 密钥只放在 **`backend/.env`**，不要提交到 Git；前端代理地址用 **`frontend/.env.local`** 里的 `BACKEND_URL` 即可。
