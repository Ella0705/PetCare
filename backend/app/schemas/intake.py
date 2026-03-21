from typing import List

from pydantic import BaseModel, Field


class PetMetadata(BaseModel):
    species: str = Field(..., description="Dog, Cat, etc.")
    age_years: float = Field(..., ge=0)
    weight_kg: float = Field(..., gt=0)
    sex: str = Field(..., description="male/female")
    neutered: bool


class IntakeInput(BaseModel):
    owner_symptoms: str = Field(..., min_length=5)
    metadata: PetMetadata
    image_paths: List[str] = Field(default_factory=list)


class IntakeAgentOutput(BaseModel):
    case_summary: str
    normalized_symptoms: List[str]
    red_flag_keywords: List[str]
    safety_disclaimer: str
