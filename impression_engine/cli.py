"""데모 실행기.

    python3 -m impression_engine.cli            # 대표 사례 8개
    python3 -m impression_engine.cli --coverage # 문구 집필 진행률
    python3 -m impression_engine.cli --json     # 렌더 사양 JSON 출력
"""

from __future__ import annotations

import argparse
import json

from .engine import process
from .judgment import all_slot_ids
from .phrases import coverage
from .profile import Profile
from .signals import EmotionSignal

SCENARIOS: list[tuple[str, EmotionSignal]] = [
    (
        "깊이 가라앉은 사람",
        EmotionSignal(sadness=0.9, disgust=0.3, arousal=0.75),
    ),
    (
        "조용히 가라앉은 사람",
        EmotionSignal(sadness=0.6, disgust=0.2, arousal=0.45),
    ),
    (
        "크게 웃는 사람",
        EmotionSignal(joy=0.95, surprise=0.2, smile_au=0.9, arousal=0.85),
    ),
    (
        "화가 치민 사람",
        EmotionSignal(anger=0.9, disgust=0.2, arousal=0.9),
    ),
    (
        "무언가를 기다리는 사람",
        EmotionSignal(surprise=0.7, fear=0.1, smile_au=0.8, arousal=0.5),
    ),
    (
        "불안한 사람",
        EmotionSignal(fear=0.8, surprise=0.3, arousal=0.55),
    ),
    (
        "아무 일 없는 사람",
        EmotionSignal(joy=0.1, arousal=0.15),
    ),
    (
        "가라앉음과 뜨거움이 함께인 사람",
        EmotionSignal(sadness=0.6, disgust=0.6, anger=0.6, joy=0.6, arousal=0.6),
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="감정의 인상 — 판정 엔진 데모")
    parser.add_argument("--json", action="store_true", help="렌더 사양 JSON 출력")
    parser.add_argument("--coverage", action="store_true", help="문구 집필 진행률")
    parser.add_argument(
        "--all-slots", action="store_true",
        help="24개 슬롯 전체의 렌더 사양 JSON (TouchDesigner 작업 참조용)",
    )
    parser.add_argument(
        "--profile", metavar="경로",
        help="캘리브레이션 프로필 JSON (예: calibration/작업실.json)",
    )
    args = parser.parse_args()

    profile = Profile.load(args.profile) if args.profile else None
    if profile:
        print(profile.summary())

    if args.coverage:
        for lang in ("ko", "en"):
            c = coverage(lang)
            print(f"\n[{lang}] 채워짐 {c['written']}/{c['total']}"
                  f"  ·  작가 확정 {c['author_confirmed']}/{c['total']}")
            if c["draft"]:
                print(f"  초안 (작가 검토 대기) {len(c['draft'])}개:")
                for slot in c["draft"]:
                    print(f"    ◐ {slot}")
            if c["missing"]:
                print(f"  미집필 {len(c['missing'])}개:")
                for slot in c["missing"]:
                    print(f"    ✗ {slot}")
        return

    if args.all_slots:
        print(json.dumps(all_slot_specs(profile), ensure_ascii=False, indent=2))
        return

    if args.json:
        payload = [
            {"scenario": name, "spec": process(sig, profile=profile).to_render_spec()}
            for name, sig in SCENARIOS
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    for name, signal in SCENARIOS:
        print(f"\n▸ {name}")
        print(process(signal, profile=profile).summary())




def all_slot_specs(profile=None) -> list[dict]:
    """24개 슬롯 전체의 렌더 사양.

    슬롯마다 그 슬롯이 나오는 대표 입력을 찾아 실제로 엔진을 통과시킨다.
    손으로 적은 표가 아니라 엔진이 실제로 내놓는 값이므로, TouchDesigner
    쪽에서 이 JSON을 그대로 기준 삼아 작업할 수 있다.
    """
    import itertools

    found: dict[str, dict] = {}
    steps = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    levels = (0.15, 0.5, 0.85)

    for joy, sadness, anger, fear, surprise, disgust in itertools.product(steps, repeat=6):
        for arousal in levels:
            for smile in (0.0, 1.0):
                sig = EmotionSignal(
                    joy=joy, sadness=sadness, anger=anger, fear=fear,
                    surprise=surprise, disgust=disgust,
                    smile_au=smile, arousal=arousal,
                )
                result = process(sig, profile=profile)
                found.setdefault(result.judgment.slot_id, result.to_render_spec())
        if len(found) == 24:
            break

    return [found[s] for s in all_slot_ids() if s in found]

if __name__ == "__main__":
    main()
