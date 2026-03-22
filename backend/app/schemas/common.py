from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    URGENT = "urgent"


_RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.LOW: 0,
    RiskLevel.MODERATE: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.URGENT: 3,
}


def max_risk_level(a: RiskLevel, b: RiskLevel) -> RiskLevel:
    """取较高严重度（用于规则策略与 LLM 建议合并）。"""
    return a if _RISK_ORDER[a] >= _RISK_ORDER[b] else b
