from app.schemas.vision import VisionAgentOutput, VisionObservation


class VisionAgent:
    def run(self, image_paths: list[str]) -> VisionAgentOutput:
        # Placeholder for future vision model call.
        observations = []
        for idx, path in enumerate(image_paths, start=1):
            observations.append(
                VisionObservation(
                    label="general appearance",
                    confidence=0.45,
                    note=f"Image {idx} ({path}) reviewed with placeholder analyzer. Manual vet review advised.",
                )
            )

        if not observations:
            observations.append(
                VisionObservation(
                    label="no image provided",
                    confidence=0.2,
                    note="No visual evidence available. Risk assessment relies on text and metadata only.",
                )
            )

        return VisionAgentOutput(
            image_count=len(image_paths),
            observations=observations,
            uncertainty_notes=[
                "Vision output is an MVP placeholder and can miss subtle or internal conditions.",
                "Image quality, angle, and lighting can reduce reliability.",
            ],
        )
