import json
import logging
from typing import Any

from app.llm.openai_chat import complete_json_text
from app.schemas.common import RiskLevel, max_risk_level
from app.schemas.intake import IntakeAgentOutput, PetMetadata
from app.schemas.risk import HealthRiskAgentOutput
from app.schemas.vision import VisionAgentOutput
from app.settings import get_settings

logger = logging.getLogger(__name__)

_RISK_SYSTEM = """You are a risk triage assistant for a pet wellness app (NOT a veterinarian).
Combine pet metadata, structured intake, and vision observations to produce NON-DIAGNOSTIC guidance.

Output JSON only with keys:
risk_level: one of "low", "moderate", "high", "urgent"
risk_reasons: array of short strings (why this level, conservative)
urgent_red_flags: array of short strings (what owners should watch / emergency patterns), can include educational examples
escalation_guidance: single string (when to call vet / emergency)
uncertainty_statement: single string (limits of remote assessment)

Be conservative: when unsure, choose the higher adjacent level. Never claim certainty or a diagnosis.
"""


class HealthRiskAgent:
    async def run(
        self,
        metadata: PetMetadata,
        intake: IntakeAgentOutput,
        vision: VisionAgentOutput,
    ) -> HealthRiskAgentOutput:
        settings = get_settings()
        rule_level, rule_reasons = _rule_based_risk(metadata, intake)

        if not settings.openai_api_key:
            return self._fallback_output(metadata, intake, vision, rule_level, rule_reasons)

        user_obj = {
            "pet_metadata": {
                "species": metadata.species,
                "age_years": metadata.age_years,
                "weight_kg": metadata.weight_kg,
                "sex": metadata.sex,
                "neutered": metadata.neutered,
            },
            "intake": intake.model_dump(),
            "vision": vision.model_dump(),
            "policy_hint": {
                "rule_based_risk_level": rule_level.value,
                "rule_reasons": rule_reasons,
            },
        }
        try:
            raw: dict[str, Any] = await complete_json_text(
                system=_RISK_SYSTEM,
                user=json.dumps(user_obj, ensure_ascii=False),
                model=settings.petcare_text_model,
            )
            llm_level = _parse_risk_level(raw.get("risk_level"))
            merged = max_risk_level(rule_level, llm_level)

            risk_reasons = _merge_reasons(rule_reasons, raw.get("risk_reasons"))
            urgent = _as_str_list(raw.get("urgent_red_flags"), limit=12)
            if not urgent:
                urgent = self._default_urgent_flags(intake)

            escalation = str(raw.get("escalation_guidance", "")).strip()
            uncertainty = str(raw.get("uncertainty_statement", "")).strip()

            if not escalation or not uncertainty:
                fb = self._fallback_output(metadata, intake, vision, merged, risk_reasons)
                escalation = escalation or fb.escalation_guidance
                uncertainty = uncertainty or fb.uncertainty_statement

            # 规则把等级抬高到高于模型建议时，就医指引用更保守的模板
            if merged != llm_level:
                fb_conservative = self._fallback_output(
                    metadata, intake, vision, merged, risk_reasons
                )
                escalation = fb_conservative.escalation_guidance
                risk_reasons = _merge_reasons(
                    [f"Policy merge raised level to {merged.value} (rules + model)."],
                    risk_reasons,
                )

            return HealthRiskAgentOutput(
                risk_level=merged,
                risk_reasons=risk_reasons[:12],
                urgent_red_flags=urgent,
                escalation_guidance=escalation,
                uncertainty_statement=uncertainty,
            )
        except Exception:
            logger.exception("HealthRiskAgent LLM failed; using rule fallback")
            return self._fallback_output(metadata, intake, vision, rule_level, rule_reasons)

    def _fallback_output(
        self,
        metadata: PetMetadata,
        intake: IntakeAgentOutput,
        vision: VisionAgentOutput,
        risk: RiskLevel,
        reasons: list[str],
    ) -> HealthRiskAgentOutput:
        _ = metadata, vision  # 保留签名与旧逻辑一致
        urgent_flags = list(intake.red_flag_keywords)
        if risk in (RiskLevel.HIGH, RiskLevel.URGENT):
            escalation = (
                "Seek veterinary care today. If symptoms worsen rapidly, use emergency vet services now."
            )
        elif risk == RiskLevel.MODERATE:
            escalation = "Monitor closely for 12-24h and contact a vet if symptoms persist or worsen."
        else:
            escalation = "Continue monitoring at home and schedule routine vet consultation if concerns continue."

        if not urgent_flags:
            urgent_flags = [
                "difficulty breathing",
                "continuous vomiting/diarrhea",
                "seizure, collapse, or unresponsiveness",
                "bloody stool or vomit",
            ]

        return HealthRiskAgentOutput(
            risk_level=risk,
            risk_reasons=reasons,
            urgent_red_flags=urgent_flags,
            escalation_guidance=escalation,
            uncertainty_statement=(
                "Risk output is probabilistic and non-diagnostic. Hidden conditions are possible."
            ),
        )

    def _default_urgent_flags(self, intake: IntakeAgentOutput) -> list[str]:
        if intake.red_flag_keywords:
            return list(intake.red_flag_keywords)[:12]
        return [
            "difficulty breathing",
            "continuous vomiting/diarrhea",
            "seizure, collapse, or unresponsiveness",
            "bloody stool or vomit",
        ]


def _rule_based_risk(metadata: PetMetadata, intake: IntakeAgentOutput) -> tuple[RiskLevel, list[str]]:
    urgent_flags = list(intake.red_flag_keywords)
    reasons: list[str] = []
    if urgent_flags:
        return RiskLevel.URGENT, ["Critical red-flag keywords detected in owner symptoms."]
    if metadata.age_years > 10 or metadata.weight_kg < 1.5:
        return RiskLevel.HIGH, ["Age/weight profile suggests lower physiological resilience."]
    if "vomit" in " ".join(intake.normalized_symptoms).lower():
        return RiskLevel.MODERATE, ["Gastrointestinal symptom pattern present."]
    return RiskLevel.LOW, ["No immediate high-risk indicators detected in MVP rule set."]


def _parse_risk_level(value: Any) -> RiskLevel:
    if value is None:
        return RiskLevel.MODERATE
    s = str(value).strip().lower()
    for level in RiskLevel:
        if level.value == s:
            return level
    if "urgent" in s or "emergency" in s:
        return RiskLevel.URGENT
    if "high" in s:
        return RiskLevel.HIGH
    if "moderate" in s or "medium" in s:
        return RiskLevel.MODERATE
    if "low" in s:
        return RiskLevel.LOW
    return RiskLevel.MODERATE


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


def _merge_reasons(primary: list[str], extra: Any) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in (primary, _as_str_list(extra, limit=20)):
        for r in group:
            key = r.strip().lower()
            if key and key not in seen:
                seen.add(key)
                merged.append(r.strip())
    return merged
