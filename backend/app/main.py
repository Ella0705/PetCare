from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.orchestrator import PetCareOrchestrator
from app.schemas.intake import IntakeInput, PetMetadata
from app.schemas.report import FinalPetHealthReport

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="PetCare AI MVP", version="0.1.0")
orchestrator = PetCareOrchestrator()

# 勿同时使用 allow_origins=["*"] 与 allow_credentials=True（浏览器会拒绝跨域响应）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    """根路径说明（浏览器打开 8000 端口时不再 404）。"""
    return {
        "service": app.title,
        "version": app.version,
        "message": "PetCare AI API is running. Use the Next.js frontend at http://localhost:3000 for the UI.",
        "endpoints": {
            "health": "/health",
            "generate_report": "POST /api/report (multipart form)",
            "openapi_docs": "/docs",
            "openapi_redoc": "/redoc",
        },
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/report", response_model=FinalPetHealthReport)
async def generate_report(
    owner_symptoms: str = Form(...),
    species: str = Form(...),
    age_years: float = Form(...),
    weight_kg: float = Form(...),
    sex: str = Form(...),
    neutered: bool = Form(...),
    images: List[UploadFile] | None = File(default=None),
) -> FinalPetHealthReport:
    saved_paths: list[str] = []
    for image in images or []:
        ext = Path(image.filename or "").suffix or ".jpg"
        target = UPLOAD_DIR / f"{uuid4().hex}{ext}"
        content = await image.read()
        target.write_bytes(content)
        saved_paths.append(str(target))

    payload = IntakeInput(
        owner_symptoms=owner_symptoms,
        metadata=PetMetadata(
            species=species,
            age_years=age_years,
            weight_kg=weight_kg,
            sex=sex,
            neutered=neutered,
        ),
        image_paths=saved_paths,
    )
    return await orchestrator.run(payload)
