from typing import List

from pydantic import BaseModel

from app.schemas.common import RiskLevel


class HealthRiskAgentOutput(BaseModel):
    risk_level: RiskLevel
    risk_reasons: List[str]
    urgent_red_flags: List[str]
    escalation_guidance: str
    uncertainty_statement: str
