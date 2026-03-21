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
uvicorn app.main:app --reload --port 8000
```

Backend health check:

```bash
curl http://127.0.0.1:8000/health
```

## Frontend Setup (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Open:

- http://localhost:3000

Optional env:

```bash
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```

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

## Placeholder Integrations

This MVP intentionally includes placeholders for:
- LLM reasoning/extraction calls
- vision model inference
- policy guardrails beyond basic rules

These placeholders are marked in agent code and can be replaced with production services later.
