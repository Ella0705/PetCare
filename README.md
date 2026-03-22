# PetCare AI (Hackathon MVP)

PetCare AI is a multi-agent pet wellness assistant MVP.

It accepts:
- one or more pet photos
- owner symptom descriptions
- pet metadata (species, age, weight, sex, neutered status)

It outputs:
- structured pet health report
- feeding and hydration guidance
- risk level
- escalation guidance for veterinary follow-up

## Important Safety Notice

- PetCare AI is **not** a diagnosis or treatment tool.
- Outputs are uncertain and may be incomplete.
- If urgent red flags appear (breathing difficulty, seizure, collapse, blood, persistent vomiting/diarrhea), seek veterinary care immediately.

## Architecture

The backend uses FastAPI with a clear orchestrator and four agents:

1. **Intake Agent**
   - normalizes owner symptom text
   - extracts potential red-flag keywords
2. **Vision Agent**
   - analyzes uploaded images (placeholder logic)
   - emits uncertainty notes
3. **Health Risk Agent**
   - combines metadata + intake + vision
   - computes risk level and escalation guidance
4. **Feeding Guidance Agent**
   - returns feeding/hydration advice, avoid list, monitoring tips

Orchestration flow:

`Intake -> Vision -> Health Risk -> Feeding Guidance -> Final Report`

## Project Structure

```
PetCare-AI/
  backend/
    app/
      agents/
      schemas/
      orchestrator.py
      main.py
    uploads/
    requirements.txt
  frontend/
    app/
      page.tsx
      report/page.tsx
    lib/
    package.json
  schemas/
    *_agent_output.schema.json
  README.md
```

## Backend Setup (FastAPI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 然后填入 OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

LLM / 视觉：在 `backend/.env` 设置 `OPENAI_API_KEY`（可选 `OPENAI_BASE_URL`、`PETCARE_TEXT_MODEL`、`PETCARE_VISION_MODEL`）。  
未配置密钥时，各 Agent 自动回退到内置规则占位逻辑，便于本地无密钥调试。

Backend health check:

```bash
curl http://127.0.0.1:8000/health
```

## Frontend Setup (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local   # 可选；默认已指向 http://127.0.0.1:8000
npm run dev
```

Open:

- http://localhost:3000

默认前端通过 **同源** `POST /api/report` 由 Next 服务端 **代理** 到 FastAPI，避免浏览器跨域问题。  
`frontend/.env.local` 中可设置 `BACKEND_URL`（转发目标）。

若要让浏览器 **直连** 后端，再设置 `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000`（需后端 CORS 已包含你的前端来源）。

## Demo Flow

1. Open the intake form on the frontend.
2. Enter pet metadata and symptom description.
3. Upload one or more photos.
4. Submit to trigger backend orchestrator.
5. View final report page with:
   - risk level
   - escalation recommendation
   - feeding/hydration guidance
   - uncertainty and non-diagnostic notices

## JSON Schemas

Intermediate output schemas are available in `schemas/`:

- `intake_agent_output.schema.json`
- `vision_agent_output.schema.json`
- `health_risk_agent_output.schema.json`
- `feeding_guidance_agent_output.schema.json`

## LLM Integrations

Agents call an **OpenAI-compatible** Chat Completions API (default OpenAI) when `OPENAI_API_KEY` is set:

- **Intake** — symptom normalization + red-flag hints (JSON)
- **Vision** — multimodal image review (JSON; base64 data URLs)
- **Health risk** — narrative + level suggestion, merged with **rule-based floor** (`app/agents/health_risk_agent.py`)
- **Feeding** — conservative husbandry bullets (JSON)

Without an API key, behavior falls back to the original rule/placeholder implementations.
