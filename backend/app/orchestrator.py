from app.agents.feeding_guidance_agent import FeedingGuidanceAgent
from app.agents.health_risk_agent import HealthRiskAgent
from app.agents.intake_agent import IntakeAgent
from app.agents.vision_agent import VisionAgent
from app.schemas.intake import IntakeInput
from app.schemas.report import FinalPetHealthReport


class PetCareOrchestrator:
    def __init__(self) -> None:
        self.intake_agent = IntakeAgent()
        self.vision_agent = VisionAgent()
        self.health_risk_agent = HealthRiskAgent()
        self.feeding_guidance_agent = FeedingGuidanceAgent()

    def run(self, payload: IntakeInput) -> FinalPetHealthReport:
        intake_output = self.intake_agent.run(payload)
        vision_output = self.vision_agent.run(payload.image_paths)
        risk_output = self.health_risk_agent.run(payload.metadata, intake_output, vision_output)
        feeding_output = self.feeding_guidance_agent.run(payload.metadata, risk_output)

        return FinalPetHealthReport(
            metadata=payload.metadata,
            owner_symptoms=payload.owner_symptoms,
            intake=intake_output,
            vision=vision_output,
            risk=risk_output,
            feeding=feeding_output,
            non_diagnostic_notice=(
                "PetCare AI is an informational assistant only and does not diagnose, treat, or replace a veterinarian."
            ),
        )
