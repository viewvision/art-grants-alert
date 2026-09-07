"""인식 계층에서 들어오는 입력 신호 정의.

이 모듈은 카메라·모델에 의존하지 않는다. 어떤 에크만 6대 감정 분류
모델을 쓰더라도 이 형태로만 맞춰 주면 엔진이 동작한다.
"""

from __future__ import annotations

from dataclasses import dataclass


def _clamp01(value: float, name: str) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name}는 숫자여야 합니다: {value!r}")
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{name}는 0.0~1.0 범위여야 합니다: {value}")
    return float(value)


@dataclass(frozen=True)
class EmotionSignal:
    """한 번의 캡처 구간에서 산출된 인식 결과.

    에크만 6대 감정은 프레임 누적 평균값(각 0~1)이다.

    arousal
        전체 각성 수준(0~1). **방향·톤과 무관한 독립 축**이므로 6개 감정
        확률에서 유도하지 않는다. 표정 근육 강도와 몸 움직임 에너지의
        가중합으로 산출한다 (2026-09-07 확정).

            arousal = 0.5 × 표정강도 + 0.5 × 움직임에너지

        산출은 arousal.ArousalTracker가 담당한다. 여기서는 이미 계산된
        0~1 값만 받는다.

    smile_au
        AU6(볼 올림)·AU12(입꼬리 당김) 활성도(0~1). 공기 방향의
        valence를 계산할 때 놀람이 '희망'인지 '불안'인지 가르는 유일한
        재료다. 이 값이 0이면 공기는 구조적으로 항상 불안 쪽으로만
        판정된다.
    """

    joy: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    disgust: float = 0.0
    surprise: float = 0.0

    arousal: float = 0.0
    smile_au: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "joy",
            "sadness",
            "anger",
            "fear",
            "disgust",
            "surprise",
            "arousal",
            "smile_au",
        ):
            _clamp01(getattr(self, name), name)

    @property
    def ekman(self) -> dict[str, float]:
        return {
            "joy": self.joy,
            "sadness": self.sadness,
            "anger": self.anger,
            "fear": self.fear,
            "disgust": self.disgust,
            "surprise": self.surprise,
        }
