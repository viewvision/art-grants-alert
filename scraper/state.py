import json
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "state.json"


def load_state(path: Path = STATE_PATH) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict, path: Path = STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def find_new_items(items: list[dict], state: dict, today: str) -> list[dict]:
    """items 중 site의 기존 state에 없던(새로 등장한) 항목만 반환.
    반환과 별개로 state 자체는 변경하지 않는다 — 호출 측에서 update_state로 반영."""
    new_items = []
    for item in items:
        site_state = state.get(item["site"], {})
        if item["id"] not in site_state:
            new_items.append(item)
    return new_items


def update_state(items: list[dict], state: dict, today: str) -> dict:
    """모든(필터 통과 여부 무관) 스크래핑 결과를 state에 반영해 다음 실행의 기준으로 삼는다."""
    for item in items:
        site_state = state.setdefault(item["site"], {})
        if item["id"] not in site_state:
            site_state[item["id"]] = {
                "title": item.get("title"),
                "url": item.get("url"),
                "date": item.get("date"),
                "first_seen": today,
            }
    return state
