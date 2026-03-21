from pydantic import BaseModel

from app.schemas.feeding import FeedingGuidanceAgentOutput
from app.schemas.intake import IntakeAgentOutput, PetMetadata
from app.schemas.risk import HealthRiskAgentOutput
from app.schemas.vision import VisionAgentOutput


class FinalPetHealthReport(BaseModel):
    metadata: PetMetadata
    owner_symptoms: str
    intake: IntakeAgentOutput
    vision: VisionAgentOutput
    risk: HealthRiskAgentOutput
    feeding: FeedingGuidanceAgentOutput
    non_diagnostic_notice: str
