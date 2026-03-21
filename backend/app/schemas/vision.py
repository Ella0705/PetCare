from typing import List

from pydantic import BaseModel


class VisionObservation(BaseModel):
    label: str
    confidence: float
    note: str


class VisionAgentOutput(BaseModel):
    image_count: int
    observations: List[VisionObservation]
    uncertainty_notes: List[str]
