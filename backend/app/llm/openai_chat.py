from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from app.llm.json_utils import parse_json_object
from app.settings import get_settings

logger = logging.getLogger(__name__)


def _mime_for_path(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
    }.get(ext, "image/jpeg")


def _async_client() -> AsyncOpenAI | None:
    s = get_settings()
    if not s.openai_api_key:
        return None
    kwargs: dict[str, Any] = {"api_key": s.openai_api_key}
    if s.openai_base_url:
        kwargs["base_url"] = s.openai_base_url
    return AsyncOpenAI(**kwargs)


async def complete_json_text(*, system: str, user: str, model: str) -> dict[str, Any]:
    client = _async_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not set")

    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=2048,
    )
    content = resp.choices[0].message.content or "{}"
    return parse_json_object(content)


async def complete_json_vision(
    *,
    system: str,
    user_text: str,
    image_paths: list[str],
    model: str,
    max_images: int = 6,
) -> dict[str, Any]:
    """多模态：将本地图片以 data URL 传入（适合 hackathon / 小规模）。"""
    client = _async_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not set")

    content: list[dict[str, Any]] = [{"type": "text", "text": user_text}]
    for path in image_paths[:max_images]:
        p = Path(path)
        if not p.is_file():
            logger.warning("Vision skip missing file: %s", path)
            continue
        try:
            raw = p.read_bytes()
            b64 = base64.standard_b64encode(raw).decode("ascii")
            mime = _mime_for_path(str(p))
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                }
            )
        except OSError:
            logger.exception("Vision failed to read: %s", path)

    # 无可用图片（未传路径或文件读失败）：走纯文本 JSON，避免发空 multimodal
    if len(content) == 1:
        return await complete_json_text(system=system, user=user_text, model=model)

    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=2048,
    )
    msg = resp.choices[0].message.content or "{}"
    return parse_json_object(msg)
