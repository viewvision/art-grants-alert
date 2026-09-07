"""arousal(강도) 산출 — 표정 강도와 몸 움직임의 가중합.

설계 근거: Project_감정의인상.md "arousal 산출 방식 확정 (2026-09-07)".

왜 6개 감정에서 유도하지 않는가
    arousal은 방향·톤과 무관한 **독립 축**이다. 감정 확률에서 유도하면
    방향축과 같은 재료를 쓰게 되어 축이 하나로 무너지고, 구조적으로
    도달 불가능한 슬롯이 생긴다. 전수 검증 결과:

        arousal = 감정 총합    → 24개 중 6개 미도달
        arousal = 최대 감정값  → 24개 중 3개 미도달

    대표적으로 흙·고(earth_high) — "고요해 보이지만 속이 들끓는 사람"이
    시스템상 존재할 수 없게 된다. 흙이 1위라는 건 감정 활성이 낮다는
    뜻인데, 같은 재료로 arousal을 뽑으면 강도도 자동으로 낮아지기 때문이다.

두 재료를 섞는 이유
    표정 강도만 쓰면 무표정한 사람의 arousal이 항상 0이 되어 흙·고가
    여전히 죽는다. 움직임만 쓰면 격한 표정을 지은 채 가만히 선 사람이
    낮게 잡힌다. 두 약점이 서로를 메운다.

        arousal = 0.5 × 표정강도 + 0.5 × 움직임에너지

    가중치는 현장 튜닝 대상이다. 초기값 50:50에서 시작한다.
"""

from __future__ import annotations

from dataclasses import dataclass

#: 두 재료의 초기 가중치. 합이 1.0이어야 한다.
#: 「일상비일상의틈」처럼 관객이 잠깐 서 있는 공간에서는 움직임 신호가
#: 약하게 잡힐 수 있다. 현장 캘리브레이션에서 조정한다.
DEFAULT_FACE_WEIGHT = 0.5
DEFAULT_MOTION_WEIGHT = 0.5

#: ⚠️ 정규화 기준값 — 현장 계측 전까지의 잠정값이다.
#:
#: AU: OpenFace 계열은 AU당 intensity 0~5를 내고 한 표정에서 3~6개가
#: 함께 활성화된다. 격한 표정의 합을 12.0으로 잡았다.
#: 움직임: 상체 관절의 평균 이동 속도(m/s). 팔을 크게 젓는 수준을
#: 0.35로 잡았다.
#:
#: 두 값 모두 설치 현장에서 "가장 격한 반응"을 실측해 갱신해야 한다.
DEFAULT_AU_REFERENCE = 12.0
DEFAULT_MOTION_REFERENCE = 0.35

#: 프레임 간 평활 계수(EMA). 1.0이면 평활 없음.
#: 눈 깜빡임 한 번이나 지나가는 사람 때문에 강도가 튀는 것을 막는다.
#: 값이 작을수록 둔하게 반응한다. 캡처 구간이 3초 이내이므로 과하게
#: 둔해지면 반응이 늦어 보인다.
DEFAULT_SMOOTHING = 0.4


def normalise(raw: float, reference: float) -> float:
    """관측 원값을 0~1로 정규화한다. 기준값 이상은 전부 1.0."""
    if reference <= 0:
        raise ValueError(f"기준값은 양수여야 합니다: {reference}")
    if raw < 0:
        return 0.0
    return min(1.0, raw / reference)


def blend(
    face_intensity: float,
    motion_energy: float,
    face_weight: float = DEFAULT_FACE_WEIGHT,
    motion_weight: float = DEFAULT_MOTION_WEIGHT,
) -> float:
    """정규화된 두 신호(각 0~1)를 가중합해 arousal을 만든다."""
    total = face_weight + motion_weight
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"가중치 합은 1.0이어야 합니다: {total}")
    for name, value in (("face_intensity", face_intensity), ("motion_energy", motion_energy)):
        if value < 0.0 or value > 1.0:
            raise ValueError(f"{name}는 0.0~1.0 범위여야 합니다: {value}")
    return face_weight * face_intensity + motion_weight * motion_energy


def motion_energy_from_joints(
    previous: dict[str, tuple[float, float, float]],
    current: dict[str, tuple[float, float, float]],
    dt_seconds: float,
) -> float:
    """스켈레톤 두 프레임에서 평균 관절 이동 속도(m/s)를 낸다.

    Kinect가 이미 관절 좌표를 주므로 캡처 계층에서 바로 계산할 수 있다.
    두 프레임에 공통으로 잡힌 관절만 쓴다 — 일부 관절이 가려져 사라지는
    경우가 흔한데, 그것을 '움직임'으로 세면 안 된다.
    """
    if dt_seconds <= 0:
        raise ValueError(f"dt는 양수여야 합니다: {dt_seconds}")

    shared = previous.keys() & current.keys()
    if not shared:
        return 0.0

    total = 0.0
    for name in shared:
        px, py, pz = previous[name]
        cx, cy, cz = current[name]
        total += ((cx - px) ** 2 + (cy - py) ** 2 + (cz - pz) ** 2) ** 0.5

    return (total / len(shared)) / dt_seconds


@dataclass
class ArousalTracker:
    """캡처 구간 동안 arousal을 누적·평활해 최종값 하나를 만든다.

    엔진은 캡처 구간당 EmotionSignal 하나를 받는다. 그 구간의 여러
    프레임을 이 트래커에 흘려 넣고 마지막에 value를 읽는다.

        tracker = ArousalTracker()
        for frame in capture_window:
            tracker.update(au_intensity_sum=..., motion_speed=...)
        signal = EmotionSignal(..., arousal=tracker.value)
    """

    face_weight: float = DEFAULT_FACE_WEIGHT
    motion_weight: float = DEFAULT_MOTION_WEIGHT
    au_reference: float = DEFAULT_AU_REFERENCE
    motion_reference: float = DEFAULT_MOTION_REFERENCE
    smoothing: float = DEFAULT_SMOOTHING

    _value: float | None = None

    def update(self, au_intensity_sum: float, motion_speed: float) -> float:
        """한 프레임을 반영하고 갱신된 arousal을 돌려준다.

        au_intensity_sum
            그 프레임에서 활성화된 AU들의 intensity 합 (모델 원단위).
        motion_speed
            직전 프레임 대비 평균 관절 이동 속도 (m/s).
        """
        raw = blend(
            normalise(au_intensity_sum, self.au_reference),
            normalise(motion_speed, self.motion_reference),
            self.face_weight,
            self.motion_weight,
        )
        if self._value is None:
            self._value = raw
        else:
            self._value = self.smoothing * raw + (1.0 - self.smoothing) * self._value
        return self._value

    @property
    def value(self) -> float:
        """현재 arousal(0~1). 아직 프레임이 없으면 0.0."""
        return 0.0 if self._value is None else self._value

    def reset(self) -> None:
        """관객이 바뀔 때 호출한다. 이전 사람의 강도가 넘어오면 안 된다."""
        self._value = None
