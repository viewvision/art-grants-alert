"""판정 엔진 검증.

pytest 없이도 `python3 tests/test_engine.py` 로 바로 실행된다.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from impression_engine import (  # noqa: E402
    EmotionSignal,
    all_slot_ids,
    coverage,
    filter_phrase,
    judge,
    process,
    to_directions,
)
from impression_engine.judgment import MIXED_THRESHOLD_PP  # noqa: E402

FAILURES: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        FAILURES.append(label)


def section(title: str) -> None:
    print(f"\n── {title}")


# ────────────────────────────── 1. 4방향 변환 ──────────────────────────────
section("4방향 변환 규칙")

v = to_directions(EmotionSignal(sadness=0.8, disgust=0.4, arousal=0.5))
check(abs(sum(v.ratios.values()) - 1.0) < 1e-9, "비율 합계가 정확히 1.0")
check(v.dominant == "water", "슬픔+혐오 → 물이 1위")

v = to_directions(EmotionSignal(anger=0.9, arousal=0.8))
check(v.dominant == "fire", "분노 → 불이 1위")

v = to_directions(EmotionSignal(fear=0.7, surprise=0.5, arousal=0.6))
check(v.dominant == "air", "공포+놀람 → 공기가 1위")

v = to_directions(EmotionSignal(arousal=0.1))
check(v.dominant == "earth", "감정 반응이 없으면 흙이 1위 (잔여값)")
check(v.ratios["earth"] == 1.0, "무반응 상태에서 흙 비중 100%")

weak = to_directions(EmotionSignal(joy=0.2, arousal=0.3))
strong = to_directions(EmotionSignal(joy=0.9, arousal=0.9))
check(
    weak.ratios["earth"] > strong.ratios["earth"],
    "감정이 약할수록 흙 비중이 커진다",
)

# ────────────────────────────── 2. valence ──────────────────────────────
section("방향별 valence 계산")

v = to_directions(EmotionSignal(joy=0.8, anger=0.1, arousal=0.7))
check(v.valences["fire"] > 0, "기쁨 > 분노 → 불 valence 양수")

v = to_directions(EmotionSignal(joy=0.1, anger=0.8, arousal=0.7))
check(v.valences["fire"] < 0, "분노 > 기쁨 → 불 valence 음수")

v = to_directions(EmotionSignal(sadness=0.5, disgust=0.5, arousal=0.5))
check(v.valences["water"] < 0, "물 valence는 음수 고정")

v = to_directions(EmotionSignal(arousal=0.2))
check(v.valences["earth"] == 0.0, "흙 valence는 중립 고정")

# 공기 — 놀람은 웃음근육이 동반될 때만 '희망' 재료가 된다
no_smile = to_directions(EmotionSignal(fear=0.3, surprise=0.7, arousal=0.6))
with_smile = to_directions(
    EmotionSignal(fear=0.3, surprise=0.7, smile_au=0.9, arousal=0.6)
)
check(no_smile.valences["air"] < 0, "웃음근육 없으면 공기는 불안 쪽")
check(with_smile.valences["air"] > 0, "웃음근육 동반 시 공기가 희망 쪽으로")

# ────────────────────────────── 3. 판정 알고리즘 ──────────────────────────────
section("문구 슬롯 판정 (4단계)")

j = judge(to_directions(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5)))
check(not j.is_mixed and j.dominant == "water", "물 단일 우세형 판정")
check(j.tone is None, "물은 톤 분기가 없다")
check(j.level == "mid", "arousal 0.5 → 강도 중")

j = judge(to_directions(EmotionSignal(anger=0.9, arousal=0.9)))
check(j.slot_id == "fire_anger_high", "불·분노·고 슬롯")

j = judge(to_directions(EmotionSignal(joy=0.9, arousal=0.2)))
check(j.slot_id == "fire_joy_low", "불·기쁨·저 슬롯")

j = judge(to_directions(EmotionSignal(fear=0.8, arousal=0.5)))
check(j.slot_id == "air_anxiety_mid", "공기·불안·중 슬롯")

# 강도 경계값
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.33))).level == "low", "arousal 0.33 → 저")
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.34))).level == "mid", "arousal 0.34 → 중")
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.66))).level == "mid", "arousal 0.66 → 중")
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.67))).level == "high", "arousal 0.67 → 고")

# 혼합형
j = judge(to_directions(EmotionSignal(sadness=0.6, disgust=0.6, anger=0.6, joy=0.6, arousal=0.5)))
check(j.is_mixed, "1·2위 격차 10%p 미만 → 혼합형")
check(j.slot_id == "mixed_water_fire", "물+불 혼합 슬롯")
check(j.gap_pp < MIXED_THRESHOLD_PP, "혼합형 격차가 임계값 미만")

# 혼합형은 순서와 무관하게 같은 슬롯
a = judge(to_directions(EmotionSignal(sadness=0.61, disgust=0.61, anger=0.6, joy=0.6, arousal=0.5)))
b = judge(to_directions(EmotionSignal(sadness=0.6, disgust=0.6, anger=0.61, joy=0.61, arousal=0.5)))
check(a.slot_id == b.slot_id, "물+불 / 불+물은 같은 슬롯")

# ────────────────────────────── 4. 슬롯 총량 ──────────────────────────────
section("슬롯 구조")

slots = all_slot_ids()
check(len(slots) == 24, f"슬롯 총 24개 (실제 {len(slots)}개)")
check(len(set(slots)) == 24, "슬롯 ID 중복 없음")
single = [s for s in slots if not s.startswith("mixed_")]
mixed = [s for s in slots if s.startswith("mixed_")]
check(len(single) == 18, f"단일 우세형 18개 (실제 {len(single)}개)")
check(len(mixed) == 6, f"혼합형 6개 (실제 {len(mixed)}개)")

# ─────────────────────── 5. 입력 공간 전수 스윕 ───────────────────────
section("입력 공간 스윕 — 크래시·규칙 위반 없음")

produced: set[str] = set()
steps = (0.0, 0.25, 0.5, 0.75, 1.0)
count = 0
for joy, sadness, anger, fear, surprise in itertools.product(steps, repeat=5):
    for arousal in (0.1, 0.5, 0.9):
        for smile in (0.0, 1.0):
            sig = EmotionSignal(
                joy=joy,
                sadness=sadness,
                anger=anger,
                fear=fear,
                disgust=sadness * 0.5,
                surprise=surprise,
                smile_au=smile,
                arousal=arousal,
            )
            result = process(sig)
            produced.add(result.judgment.slot_id)
            count += 1

            assert abs(sum(result.judgment.ratios.values()) - 1.0) < 1e-9
            assert result.judgment.dominant != result.judgment.second
            assert result.palette.dominant_color.startswith("#")

check(True, f"{count}개 입력 조합 전부 예외 없이 처리")
check(produced <= set(slots), "생성된 슬롯이 전부 정의된 24개 안에 있음")
print(f"        도달한 슬롯 {len(produced)}/24 — 미도달 {sorted(set(slots) - produced)}")

# ────────────────────────────── 6. 배경색 규칙 ──────────────────────────────
section("배경색 — 1위 방향의 반대 온도")

warm_dominant = process(EmotionSignal(anger=0.9, arousal=0.8))
cool_dominant = process(EmotionSignal(sadness=0.9, disgust=0.8, arousal=0.5))
check(
    warm_dominant.palette.background[0] == "#BFE3F7",
    "불(따뜻) 1위 → 차가운 하늘색 배경",
)
check(
    cool_dominant.palette.background[0] == "#FFE0C4",
    "물(차가움) 1위 → 따뜻한 오렌지 배경",
)

# ────────────────────────────── 7. 문구 규칙 필터 ──────────────────────────────
section("3계층 작가 규칙 필터")

check(filter_phrase("지금 당신을 가라앉게 하는 건 무엇인가요?").passed, "정상 질문문 통과")
check(not filter_phrase("당신은 슬픕니다.").passed, "진단문 차단")
check(not filter_phrase("지금 기분이 어떤가요").passed, "물음표 없으면 차단")
check(not filter_phrase("가" * 50 + "?").passed, "길이 상한 초과 차단")
check(not filter_phrase("측정 결과는 무엇인가요?").passed, "'측정 결과' 금지어 차단")
check(not filter_phrase("You are sad?", lang="en").passed, "영문 진단문 차단")

# ────────────────────────────── 8. 폴백 동작 ──────────────────────────────
section("생성 실패 시 1계층 폴백")


def broken_generator(slot_id: str, lang: str, examples: list[str]) -> str:
    raise RuntimeError("모델 로드 실패")


def bad_generator(slot_id: str, lang: str, examples: list[str]) -> str:
    return "당신은 지금 불안합니다."


r = process(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5), generator=broken_generator)
check(r.phrase_source == "baseline", "생성 모델 예외 → 기준 문구로 폴백")

r = process(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5), generator=bad_generator)
check(r.phrase_source == "baseline", "필터 미통과 → 기준 문구로 폴백")


def good_generator(slot_id: str, lang: str, examples: list[str]) -> str:
    return "그 무거움은 어디서 왔을까요?"


r = process(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5), generator=good_generator)
check(r.phrase_source == "generated", "필터 통과 → 생성 문구 사용")

# ────────────────────────────── 9. 집필 진행률 ──────────────────────────────
section("1계층 문구 집필 진행률")

ko = coverage("ko")
en = coverage("en")
print(f"        한국어 {ko['written']}/{ko['total']}   영어 {en['written']}/{en['total']}")
check(ko["written"] == 8, "한국어 확정 8개 반영됨")

# ────────────────────────────── 결과 ──────────────────────────────
print("\n" + "=" * 60)
if FAILURES:
    print(f"실패 {len(FAILURES)}건")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print("전체 통과")
