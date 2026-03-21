from typing import List

from pydantic import BaseModel


class FeedingGuidanceAgentOutput(BaseModel):
    feeding_advice: List[str]
    hydration_advice: List[str]
    avoid_list: List[str]
    monitoring_tips: List[str]
