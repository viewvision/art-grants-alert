"""판정 결과 → 화면 색.

설계 근거
    - "4방향 원소색 HEX 최종 확정 (2026-08-19)" — 1차/2차 중간값
    - "배경색 결정 원칙 — 고정 아이보리에서 동적 보색으로 전환"
    - "혼합형 보색쌍(물+불, 공기+흙) 예외 여부 — 예외 없이 그대로 확정"
"""

from __future__ import annotations

from dataclasses import dataclass

from .directions import AIR, EARTH, FIRE, WATER
from .judgment import Judgment

#: 원소색 — 강도 저/중/고 3단계. 강도는 채도로 옮겨진다.
ELEMENT_COLORS: dict[str, dict[str, str]] = {
    WATER: {"low": "#96E2EC", "mid": "#49D2E3", "high": "#00C0D8"},
    FIRE: {"low": "#F7B49C", "mid": "#F8825A", "high": "#F6521B"},
    AIR: {"low": "#C2A9F0", "mid": "#9A72EB", "high": "#753EE4"},
    EARTH: {"low": "#EED09C", "mid": "#E7B258", "high": "#DC9418"},
}

COLOR_NAME = {
    WATER: "시안 · 아쿠아",
    FIRE: "코랄 · 버밀리언",
    AIR: "라벤더 · 바이올렛",
    EARTH: "앰버 · 골드",
}

#: 화면 위 운동 성질 — 색만 다른 평면이 아니라 움직임의 성질이 다르다.
MOTION = {
    WATER: "가라앉으며 고인다",
    FIRE: "피어오르며 번진다",
    AIR: "경계 없이 흩어진다",
    EARTH: "구조를 이루며 응집한다",
}

#: 원소의 색 온도. 배경색은 1위 방향의 반대 온도로 정해진다.
WARM_DIRECTIONS = frozenset({FIRE, EARTH})
COOL_DIRECTIONS = frozenset({WATER, AIR})

#: 배경 그라데이션. 어둡거나 탁한 배경은 쓰지 않는다(밝은 톤 원칙).
#: ⚠️ 이 값은 대비 테스트에서 쓴 잠정값이다. 실제 렌더 단계에서
#: 작가 확정 필요. (→ SPEC_GAPS.md 3번)
COOL_BACKGROUND = ("#BFE3F7", "#78C4F0")  # 하늘색 — 불·흙이 1위일 때
WARM_BACKGROUND = ("#FFE0C4", "#FFB37A")  # 오렌지·피치 — 물·공기가 1위일 때


#: 2위 원소의 비중이 이 값 미만이면 화면에 올리지 않는다.
#: 비중 0%인 원소를 1위와 같은 강도로 칠하면 판정 결과가 왜곡된다.
SECOND_VISIBILITY_FLOOR = 0.02


@dataclass(frozen=True)
class RenderPalette:
    """한 화면에 실제로 칠해지는 색 일습.

    weight는 각 원소가 차지하는 면적·농도 비중이다. 렌더 계층은 색만
    받는 게 아니라 이 비중까지 받아야 "4가지 방향의 비중이 그대로 색의
    면적과 농도가 된다"는 원칙을 지킬 수 있다.
    """

    dominant_color: str
    second_color: str | None
    background: tuple[str, str]
    dominant_direction: str
    second_direction: str | None
    dominant_weight: float
    second_weight: float
    level: str

    def as_dict(self) -> dict[str, object]:
        second: dict[str, object] | None = None
        if self.second_direction is not None:
            second = {
                "direction": self.second_direction,
                "color": self.second_color,
                "weight": round(self.second_weight, 3),
            }
        return {
            "dominant": {
                "direction": self.dominant_direction,
                "color": self.dominant_color,
                "weight": round(self.dominant_weight, 3),
            },
            "second": second,
            "background": {"from": self.background[0], "to": self.background[1]},
            "level": self.level,
        }


def background_for(dominant: str) -> tuple[str, str]:
    """1위 방향의 반대 온도를 배경에 배정한다.

    혼합형에도 같은 규칙을 그대로 적용한다. 예외를 두지 않기로 확정했고,
    물+불처럼 두 원소가 서로 보색인 조합에서 2위 원소의 대비가 다소
    낮아지는 것은 감수 가능한 수준으로 판단했다.
    """
    if dominant in WARM_DIRECTIONS:
        return COOL_BACKGROUND
    return WARM_BACKGROUND


def palette_for(judgment: Judgment) -> RenderPalette:
    """판정 결과를 화면 색으로 옮긴다.

    혼합형은 강도 구분이 없으므로 색은 '중' 단계를 쓴다.
    2위 비중이 사실상 0이면 그 원소는 화면에 올리지 않는다 — 한 원소만
    나타나는 화면이 되며, 이는 "한 화면에 두 원소만"이라는 상한 규칙을
    어기지 않는다.
    """
    level = judgment.level or "mid"

    dominant_weight = judgment.ratios[judgment.dominant]
    second_weight = judgment.ratios[judgment.second]

    if second_weight < SECOND_VISIBILITY_FLOOR:
        return RenderPalette(
            dominant_color=ELEMENT_COLORS[judgment.dominant][level],
            second_color=None,
            background=background_for(judgment.dominant),
            dominant_direction=judgment.dominant,
            second_direction=None,
            dominant_weight=dominant_weight,
            second_weight=0.0,
            level=level,
        )

    return RenderPalette(
        dominant_color=ELEMENT_COLORS[judgment.dominant][level],
        second_color=ELEMENT_COLORS[judgment.second][level],
        background=background_for(judgment.dominant),
        dominant_direction=judgment.dominant,
        second_direction=judgment.second,
        dominant_weight=dominant_weight,
        second_weight=second_weight,
        level=level,
    )
