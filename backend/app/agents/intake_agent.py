import json
import logging
from typing import Any

from app.llm.openai_chat import complete_json_text
from app.schemas.intake import IntakeAgentOutput, IntakeInput
from app.settings import get_settings

logger = logging.getLogger(__name__)

_INTAKE_SYSTEM = """You are a clinical-triage language assistant for a pet wellness app (NOT a veterinarian).
Normalize the owner's free-text symptoms into structured JSON only.
Rules:
- Accept any human language in the input; output case_summary and safety_disclaimer in the SAME language as the owner's symptoms when possible.
- normalized_symptoms: up to 8 short bullet phrases (stable, clinical-style wording).
- red_flag_keywords: English snake_case or short English tokens for urgent patterns you detect (e.g. seizure, difficulty_breathing, collapse, bloody_vomit). Use [] if none.
- Never claim a diagnosis. safety_disclaimer must state uncertainty and that this is not a substitute for a vet.

Respond with JSON object keys exactly:
case_summary (string), normalized_symptoms (array of strings), red_flag_keywords (array of strings), safety_disclaimer (string)
"""


class IntakeAgent:
    async def run(self, payload: IntakeInput) -> IntakeAgentOutput:
        settings = get_settings()
        if not settings.openai_api_key:
            return self._fallback(payload)

        user_payload = {
            "species": payload.metadata.species,
            "age_years": payload.metadata.age_years,
            "weight_kg": payload.metadata.weight_kg,
            "sex": payload.metadata.sex,
            "neutered": payload.metadata.neutered,
            "owner_symptoms": payload.owner_symptoms,
        }
        try:
            raw: dict[str, Any] = await complete_json_text(
                system=_INTAKE_SYSTEM,
                user=json.dumps(user_payload, ensure_ascii=False),
                model=settings.petcare_text_model,
            )
            return IntakeAgentOutput(
                case_summary=str(raw.get("case_summary", "")).strip() or self._fallback(payload).case_summary,
                normalized_symptoms=_as_str_list(raw.get("normalized_symptoms"), limit=8)
                or self._fallback(payload).normalized_symptoms,
                red_flag_keywords=_as_str_list(raw.get("red_flag_keywords"), limit=20)
                or self._fallback(payload).red_flag_keywords,
                safety_disclaimer=str(raw.get("safety_disclaimer", "")).strip()
                or self._fallback(payload).safety_disclaimer,
            )
        except Exception:
            logger.exception("IntakeAgent LLM failed; using rule fallback")
            return self._fallback(payload)

    def _fallback(self, payload: IntakeInput) -> IntakeAgentOutput:
        symptom_text = payload.owner_symptoms.lower()
        symptoms = [s.strip() for s in symptom_text.replace(".", ",").split(",") if s.strip()]

        red_flags: list[str] = []
        for keyword in ["seizure", "bloody", "collapse", "not breathing", "unconscious"]:
            if keyword in symptom_text:
                red_flags.append(keyword)

        return IntakeAgentOutput(
            case_summary=f"{payload.metadata.species} with owner-reported concerns: {payload.owner_symptoms}",
            normalized_symptoms=symptoms[:8],
            red_flag_keywords=red_flags,
            safety_disclaimer=(
                "This tool is not a diagnosis system. Information may be incomplete or uncertain."
            ),
        )


def _as_str_list(value: Any, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        s = str(item).strip()
        if s:
            out.append(s)
        if len(out) >= limit:
            break
    return out
