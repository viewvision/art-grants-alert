"""에크만 6대 감정 → 4방향(물·불·공기·흙) 비중 + 방향별 valence.

설계 근거: Project_감정의인상.md "AU/감정 점수 → 4방향 비중 변환 로직
(2026-08-12 확정)" 및 "valence 계산 방식 — 방향별로 다르게" 표.
"""

from __future__ import annotations

from dataclasses import dataclass

from .signals import EmotionSignal

WATER = "water"
FIRE = "fire"
AIR = "air"
EARTH = "earth"

DIRECTIONS = (WATER, FIRE, AIR, EARTH)

KO_NAME = {WATER: "물", FIRE: "불", AIR: "공기", EARTH: "흙"}

#: 물은 대결시킬 밝은 짝이 없어 valence를 음수로 고정한다.
#: 문서상 권장 범위 -0.3 ~ -0.6 의 중앙값.
WATER_FIXED_VALENCE = -0.45

#: 흙은 잔여값이라 valence 계산 재료 자체가 없다. 중립 고정.
EARTH_FIXED_VALENCE = 0.0


def _opposition(bright: float, dark: float) -> float:
    """같은 방향 안의 '밝은 감정 ↔ 어두운 감정' 대결 공식.

    두 값이 모두 0이면 대결할 재료가 없으므로 중립(0)을 돌려준다.
    """
    total = bright + dark
    if total <= 0.0:
        return 0.0
    return (bright - dark) / total


@dataclass(frozen=True)
class DirectionVector:
    """4방향 비중(합 1.0)과 방향별 valence."""

    ratios: dict[str, float]
    valences: dict[str, float]
    arousal: float

    @property
    def ranked(self) -> list[tuple[str, float]]:
        """비중 내림차순 정렬. 동률이면 DIRECTIONS 선언 순서로 안정 정렬."""
        return sorted(
            self.ratios.items(),
            key=lambda kv: (-kv[1], DIRECTIONS.index(kv[0])),
        )

    @property
    def dominant(self) -> str:
        return self.ranked[0][0]

    @property
    def second(self) -> str:
        return self.ranked[1][0]

    def percent(self) -> dict[str, float]:
        return {k: round(v * 100, 1) for k, v in self.ratios.items()}


def to_directions(signal: EmotionSignal) -> DirectionVector:
    """6개 감정값을 4방향 비중으로 재배분한다.

    배정 규칙
        물   = 슬픔 + 혐오      (내면으로 가라앉음)
        불   = 분노 + 기쁨      (밖으로 터져 나감)
        공기 = 공포 + 놀람      (아직 오지 않은 것을 향함)
        흙   = 잔여값           (현재에 머묾)

    흙은 나머지 셋이 채우지 못한 자리다. 물·불·공기 활성 총합이
    낮을수록 흙 비중이 커지고, 총합이 1을 넘으면 흙은 0이 된다.
    """
    # 각 방향은 배정된 감정 2개의 합(0~2)이다. 여기서 2로 나눠 평균을
    # 내면 감정 하나만 강한 경우(분노 0.9, 기쁨 0)에 활성도가 절반으로
    # 깎여 흙이 1위가 되어버린다. 합을 그대로 쓴다.
    water_raw = signal.sadness + signal.disgust
    fire_raw = signal.anger + signal.joy
    air_raw = signal.fear + signal.surprise

    active_total = water_raw + fire_raw + air_raw
    earth_raw = max(0.0, 1.0 - active_total)

    raw = {WATER: water_raw, FIRE: fire_raw, AIR: air_raw, EARTH: earth_raw}
    total = sum(raw.values())

    if total <= 0.0:
        # 이론상 도달 불가(모든 감정이 0이면 earth_raw == 1.0)지만 방어.
        ratios = {WATER: 0.0, FIRE: 0.0, AIR: 0.0, EARTH: 1.0}
    else:
        ratios = {k: v / total for k, v in raw.items()}

    # 놀람은 그 자체로 valence 중립이다. 웃음 근육(AU6·12)이 함께
    # 활성화된 만큼만 '희망' 쪽 재료로 인정한다.
    positive_surprise = signal.surprise * signal.smile_au

    valences = {
        WATER: WATER_FIXED_VALENCE,
        FIRE: _opposition(bright=signal.joy, dark=signal.anger),
        AIR: _opposition(bright=positive_surprise, dark=signal.fear),
        EARTH: EARTH_FIXED_VALENCE,
    }

    return DirectionVector(ratios=ratios, valences=valences, arousal=signal.arousal)
