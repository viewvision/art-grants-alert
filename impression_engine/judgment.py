"""문구 슬롯 판정 알고리즘 (4단계).

설계 근거: Project_감정의인상.md "④ 문구 슬롯 판정 알고리즘 (4단계)".

    1단계  4방향 비율 산출 (합계 100%로 정규화)   → directions.py
    2단계  1위−2위 격차 10%p 이상 → 단일 우세형 / 미만 → 혼합형
    3단계  톤 판정 — 불·공기는 valence로 2갈래, 물·흙은 고정값
    4단계  강도 구간화 — arousal 저(0~33)/중(34~66)/고(67~100)

슬롯 총 24개 = 단일 우세형 18개(물3 + 불6 + 공기6 + 흙3) + 혼합형 6개
"""

from __future__ import annotations

from dataclasses import dataclass

from .directions import AIR, DIRECTIONS, EARTH, FIRE, KO_NAME, WATER, DirectionVector

#: 1위와 2위의 격차가 이 값(%p) 미만이면 혼합형으로 처리한다.
#: 애매한 신호를 억지로 하나의 감정으로 확정하지 않기 위한 장치.
MIXED_THRESHOLD_PP = 10.0

#: arousal 3단계 구간 경계 (0~100 스케일)
LEVEL_LOW_MAX = 33
LEVEL_MID_MAX = 66

LEVELS = ("low", "mid", "high")
KO_LEVEL = {"low": "저", "mid": "중", "high": "고"}

#: 톤이 valence로 갈라지는 방향과 그 톤 이름
TONED_DIRECTIONS = {
    FIRE: ("joy", "anger"),  # 양수 = 기쁨, 음수 = 분노
    AIR: ("hope", "anxiety"),  # 양수 = 희망, 음수 = 불안
}

KO_TONE = {"joy": "기쁨", "anger": "분노", "hope": "희망", "anxiety": "불안"}


def _level_from_arousal(arousal: float) -> str:
    """arousal(0~1)을 저/중/고 3단계로 구간화한다."""
    scaled = arousal * 100.0
    if scaled <= LEVEL_LOW_MAX:
        return "low"
    if scaled <= LEVEL_MID_MAX:
        return "mid"
    return "high"


def _mixed_slot_id(first: str, second: str) -> str:
    """혼합형 슬롯은 순서와 무관하게 같은 슬롯이어야 한다."""
    pair = sorted((first, second), key=DIRECTIONS.index)
    return f"mixed_{pair[0]}_{pair[1]}"


@dataclass(frozen=True)
class Judgment:
    """판정 결과. 렌더 계층과 문구 계층이 공유하는 단일 진실."""

    slot_id: str
    is_mixed: bool
    dominant: str
    second: str
    gap_pp: float
    tone: str | None
    level: str | None
    ratios: dict[str, float]
    arousal: float

    @property
    def ko_label(self) -> str:
        if self.is_mixed:
            return f"혼합 · {KO_NAME[self.dominant]}+{KO_NAME[self.second]}"
        parts = [KO_NAME[self.dominant]]
        if self.tone:
            parts.append(KO_TONE[self.tone])
        if self.level:
            parts.append(KO_LEVEL[self.level])
        return " · ".join(parts)

    @property
    def visible_directions(self) -> tuple[str, str]:
        """한 화면에 나타나는 두 원소. 4가지를 동시에 노출하지 않는다."""
        return (self.dominant, self.second)


def judge(vector: DirectionVector) -> Judgment:
    """4방향 벡터를 24개 슬롯 중 하나로 판정한다."""
    ranked = vector.ranked
    first_dir, first_ratio = ranked[0]
    second_dir, second_ratio = ranked[1]

    gap_pp = (first_ratio - second_ratio) * 100.0

    # 2단계 — 우세 여부 분기
    if gap_pp < MIXED_THRESHOLD_PP:
        return Judgment(
            slot_id=_mixed_slot_id(first_dir, second_dir),
            is_mixed=True,
            dominant=first_dir,
            second=second_dir,
            gap_pp=gap_pp,
            tone=None,  # 혼합형은 강도·톤 구분 없이 6개로 단순화
            level=None,
            ratios=dict(vector.ratios),
            arousal=vector.arousal,
        )

    # 3단계 — 톤 판정
    tone: str | None = None
    if first_dir in TONED_DIRECTIONS:
        bright, dark = TONED_DIRECTIONS[first_dir]
        tone = bright if vector.valences[first_dir] > 0 else dark

    # 4단계 — 강도 구간화
    level = _level_from_arousal(vector.arousal)

    slot_id = "_".join(part for part in (first_dir, tone, level) if part)

    return Judgment(
        slot_id=slot_id,
        is_mixed=False,
        dominant=first_dir,
        second=second_dir,
        gap_pp=gap_pp,
        tone=tone,
        level=level,
        ratios=dict(vector.ratios),
        arousal=vector.arousal,
    )


def all_slot_ids() -> list[str]:
    """설계상 존재하는 24개 슬롯 전체를 돌려준다."""
    slots: list[str] = []
    for direction in DIRECTIONS:
        if direction in TONED_DIRECTIONS:
            for tone in TONED_DIRECTIONS[direction]:
                slots.extend(f"{direction}_{tone}_{lv}" for lv in LEVELS)
        else:
            slots.extend(f"{direction}_{lv}" for lv in LEVELS)

    for i, first in enumerate(DIRECTIONS):
        for second in DIRECTIONS[i + 1 :]:
            slots.append(_mixed_slot_id(first, second))

    return slots
