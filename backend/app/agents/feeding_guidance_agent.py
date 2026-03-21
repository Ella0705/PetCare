from app.schemas.common import RiskLevel
from app.schemas.feeding import FeedingGuidanceAgentOutput
from app.schemas.intake import PetMetadata
from app.schemas.risk import HealthRiskAgentOutput


class FeedingGuidanceAgent:
    def run(self, metadata: PetMetadata, risk: HealthRiskAgentOutput) -> FeedingGuidanceAgentOutput:
        # Placeholder for nutrition model + vet-reviewed policy layer
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
