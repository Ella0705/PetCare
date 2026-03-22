import json
import re


def parse_json_object(text: str) -> dict:
    """解析模型返回的 JSON；兼容 ```json 围栏。"""
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*```\s*$", "", s)
    return json.loads(s)
