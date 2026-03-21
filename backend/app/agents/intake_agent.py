from app.schemas.intake import IntakeAgentOutput, IntakeInput


class IntakeAgent:
    def run(self, payload: IntakeInput) -> IntakeAgentOutput:
        # Placeholder for future LLM extraction call
        symptom_text = payload.owner_symptoms.lower()
        symptoms = [s.strip() for s in symptom_text.replace(".", ",").split(",") if s.strip()]

        red_flags = []
        for keyword in ["seizure", "bloody", "collapse", "not breathing", "unconscious"]:
            if keyword in symptom_text:
                red_flags.append(keyword)

        return IntakeAgentOutput(
            case_summary=f"{payload.metadata.species} with owner-reported concerns: {payload.owner_symptoms}",
            normalized_symptoms=symptoms[:8],
            red_flag_keywords=red_flags,
            safety_disclaimer=(
                "This tool is not a diagnosis system. Information may be incomplete or uncertain."
            ),
        )
