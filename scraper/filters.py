import json
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "keywords.json"


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _matches_any(text: str, words: list[str]) -> bool:
    text_lower = text.lower()
    return any(w.lower() in text_lower for w in words)


def passes_keyword_filter(item_text: str, config: dict) -> bool:
    include = config.get("include_keywords", [])
    exclude = config.get("exclude_keywords", [])
    if exclude and _matches_any(item_text, exclude):
        return False
    if include and not _matches_any(item_text, include):
        return False
    return True


def passes_region_filter(item_text: str, config: dict) -> bool:
    region = config.get("region", {})
    include_regions = region.get("include", [])
    other_regions = region.get("other_regions", [])

    if include_regions and _matches_any(item_text, include_regions):
        return True
    if other_regions and _matches_any(item_text, other_regions):
        return False
    # 어떤 지역도 언급되지 않음 -> 전국 대상으로 간주해 포함
    return True


def passes_filters(item: dict, config: dict) -> bool:
    text = item.get("title", "")
    return passes_keyword_filter(text, config) and passes_region_filter(text, config)


def filter_items(items: list[dict], config: Optional[dict] = None) -> list[dict]:
    config = config or load_config()
    return [item for item in items if passes_filters(item, config)]
