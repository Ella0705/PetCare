from app.schemas.common import RiskLevel
from app.schemas.intake import IntakeAgentOutput, PetMetadata
from app.schemas.risk import HealthRiskAgentOutput
from app.schemas.vision import VisionAgentOutput


class HealthRiskAgent:
    def run(
        self,
        metadata: PetMetadata,
        intake: IntakeAgentOutput,
        vision: VisionAgentOutput,
    ) -> HealthRiskAgentOutput:
        # Placeholder for future reasoning LLM + policy engine
        urgent_flags = list(intake.red_flag_keywords)
        reasons = []

        if urgent_flags:
            risk = RiskLevel.URGENT
            reasons.append("Critical red-flag keywords detected in owner symptoms.")
        elif metadata.age_years > 10 or metadata.weight_kg < 1.5:
            risk = RiskLevel.HIGH
            reasons.append("Age/weight profile suggests lower physiological resilience.")
        elif "vomit" in " ".join(intake.normalized_symptoms):
            risk = RiskLevel.MODERATE
            reasons.append("Gastrointestinal symptom pattern present.")
        else:
            risk = RiskLevel.LOW
            reasons.append("No immediate high-risk indicators detected in MVP rule set.")

        if risk in (RiskLevel.HIGH, RiskLevel.URGENT):
            escalation = "Seek veterinary care today. If symptoms worsen rapidly, use emergency vet services now."
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
