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
        전체 각성 수준(0~1). **방향·톤과 무관한 독립 축**이라고 설계
        문서에 명시돼 있으므로, 6개 감정 확률에서 유도하지 않고 인식
        계층이 별도로 공급해야 한다. 표정 근육 활성 강도나 움직임
        에너지처럼 "얼마나 세게 반응했는가"를 나타내는 값을 넣는다.
        (→ SPEC_GAPS.md 1번 참고)

    smile_au
        AU6(볼 올림)·AU12(입꼬리 당김) 활성도(0~1). 공기 방향의
        valence를 계산할 때 놀람이 '희망'인지 '불안'인지 가르는 유일한
        재료다. 이 값이 0이면 공기는 구조적으로 항상 불안 쪽으로만
        판정된다. (→ SPEC_GAPS.md 2번 참고)
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
