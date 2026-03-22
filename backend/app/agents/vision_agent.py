import logging
from typing import Any

from app.llm.openai_chat import complete_json_vision
from app.schemas.vision import VisionAgentOutput, VisionObservation
from app.settings import get_settings

logger = logging.getLogger(__name__)

_VISION_SYSTEM = """You are a vision assistant for a pet wellness app (NOT a veterinarian).
Describe only what is visibly plausible from the photo(s). Do not diagnose.
If images are missing, unclear, or not of a pet, say so in observations.

Return JSON only with keys:
observations: array of { "label": string, "confidence": number 0-1, "note": string } (max 6 items)
uncertainty_notes: array of strings (2-4 items) about limits of visual assessment

Do NOT include image_count in JSON; it will be set by the server.
"""


class VisionAgent:
    async def run(self, image_paths: list[str]) -> VisionAgentOutput:
        settings = get_settings()
        n = len(image_paths)

        if not settings.openai_api_key:
            return self._fallback(image_paths)

        user = (
            f"The owner uploaded {n} image file path(s). "
            "Assess visible cues relevant to general appearance, posture, eyes/nose, coat, distress signs. "
            "If no usable images, explain that assessment is text-only."
        )
        try:
            raw: dict[str, Any] = await complete_json_vision(
                system=_VISION_SYSTEM,
                user_text=user,
                image_paths=image_paths,
                model=settings.petcare_vision_model,
            )
            observations = _parse_observations(raw.get("observations"))
            uncertainty = _as_str_list(raw.get("uncertainty_notes"), limit=6)
            if not uncertainty:
                uncertainty = [
                    "Visual assessment may miss internal or subtle conditions.",
                    "Image quality and angle affect reliability.",
                ]
            return VisionAgentOutput(
                image_count=n,
                observations=observations or self._fallback(image_paths).observations,
                uncertainty_notes=uncertainty,
            )
        except Exception:
            logger.exception("VisionAgent LLM failed; using placeholder fallback")
            return self._fallback(image_paths)

    def _fallback(self, image_paths: list[str]) -> VisionAgentOutput:
        observations: list[VisionObservation] = []
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


def _parse_observations(value: Any) -> list[VisionObservation]:
    if not isinstance(value, list):
        return []
    out: list[VisionObservation] = []
    for item in value[:6]:
        if not isinstance(item, dict):
            continue
        try:
            conf = float(item.get("confidence", 0.5))
            conf = max(0.0, min(1.0, conf))
            out.append(
                VisionObservation(
                    label=str(item.get("label", "observation")).strip() or "observation",
                    confidence=conf,
                    note=str(item.get("note", "")).strip() or "No detail provided.",
                )
            )
        except (TypeError, ValueError):
            continue
    return out


def _as_str_list(value: Any, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        s = str(item).strip()
        if s:
            out.append(s)
        if len(out) >= limit:
            break
    return out
