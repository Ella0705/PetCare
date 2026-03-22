import json
import logging
from typing import Any

from app.llm.openai_chat import complete_json_text
from app.schemas.common import RiskLevel
from app.schemas.feeding import FeedingGuidanceAgentOutput
from app.schemas.intake import PetMetadata
from app.schemas.risk import HealthRiskAgentOutput
from app.settings import get_settings

logger = logging.getLogger(__name__)

_FEEDING_SYSTEM = """You are a conservative pet care guidance assistant (NOT a veterinarian).
Given species, body metrics, and current risk level, produce GENERAL husbandry suggestions only.

Rules:
- No prescriptions, dosages, or drug names. No diagnosis.
- Short actionable bullets. Avoid contradicting urgent escalation (if risk is high/urgent, emphasize vet first).
- feeding_advice / hydration_advice / avoid_list / monitoring_tips: each 3-6 short strings.

Output JSON only with keys:
feeding_advice, hydration_advice, avoid_list, monitoring_tips (all arrays of strings)
"""


class FeedingGuidanceAgent:
    async def run(self, metadata: PetMetadata, risk: HealthRiskAgentOutput) -> FeedingGuidanceAgentOutput:
        settings = get_settings()
        if not settings.openai_api_key:
            return self._fallback(metadata, risk)

        user_obj = {
            "pet_metadata": {
                "species": metadata.species,
                "age_years": metadata.age_years,
                "weight_kg": metadata.weight_kg,
                "sex": metadata.sex,
                "neutered": metadata.neutered,
            },
            "risk": risk.model_dump(),
        }
        try:
            raw: dict[str, Any] = await complete_json_text(
                system=_FEEDING_SYSTEM,
                user=json.dumps(user_obj, ensure_ascii=False),
                model=settings.petcare_text_model,
            )
            return FeedingGuidanceAgentOutput(
                feeding_advice=_as_str_list(raw.get("feeding_advice"), limit=8)
                or self._fallback(metadata, risk).feeding_advice,
                hydration_advice=_as_str_list(raw.get("hydration_advice"), limit=8)
                or self._fallback(metadata, risk).hydration_advice,
                avoid_list=_as_str_list(raw.get("avoid_list"), limit=10)
                or self._fallback(metadata, risk).avoid_list,
                monitoring_tips=_as_str_list(raw.get("monitoring_tips"), limit=10)
                or self._fallback(metadata, risk).monitoring_tips,
            )
        except Exception:
            logger.exception("FeedingGuidanceAgent LLM failed; using rule fallback")
            return self._fallback(metadata, risk)

    def _fallback(self, metadata: PetMetadata, risk: HealthRiskAgentOutput) -> FeedingGuidanceAgentOutput:
        base_feed = [
            "Offer small, frequent meals with easily digestible pet-safe food.",
            "Avoid abrupt diet changes while monitoring symptoms.",
        ]
        hydration = [
            "Provide constant access to clean water.",
            "Track drinking frequency and approximate intake.",
        ]
        avoid = [
            "Human foods high in salt, fat, onion, garlic, chocolate, or xylitol.",
            "Force feeding when the pet is nauseous, lethargic, or distressed.",
        ]
        monitoring = [
            "Record appetite, stool quality, urination, and energy every 4-6 hours.",
            "Re-check temperature and behavior if condition changes.",
        ]

        if risk.risk_level in (RiskLevel.HIGH, RiskLevel.URGENT):
            hydration.append("If unable to keep water down, seek immediate veterinary support.")
            base_feed.append("Do not delay clinical care for home feeding trials.")

        if metadata.species.lower() == "cat":
            base_feed.append("Cats should not fast for prolonged periods due to metabolic risk.")

        return FeedingGuidanceAgentOutput(
            feeding_advice=base_feed,
            hydration_advice=hydration,
            avoid_list=avoid,
            monitoring_tips=monitoring,
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
