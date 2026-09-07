"""인식 계층 → 엔진 입력 어댑터.

3단계(분석)가 내놓는 원출력을 `EmotionSignal`로 옮긴다. 엔진 본체가
특정 모델에 묶이지 않도록 변환을 여기 한 곳에 모은다.

현재 지원: py-feat (2026-09-07 채택. → `인식모듈_후보비교.md`)

py-feat는 두 경로가 있고 감정 라벨 표기가 서로 다르다.

    v1  anger disgust fear happiness sadness surprise neutral   (소문자)
    v2  Anger Disgust Fear Happy     Sad     Surprise Neutral   (대문자)

두 표기를 모두 받는다. AU 20종(AU01~AU43)은 양쪽이 동일하며 AU06·AU12가
둘 다 들어 있어, 공기의 희망/불안 분기에 필요한 재료가 어느 경로에서든
확보된다.
"""

from __future__ import annotations

from dataclasses import dataclass

from .arousal import blend, normalise
from .signals import EmotionSignal

#: py-feat 감정 라벨 → 엔진 필드. 대소문자 구분 없이 매칭한다.
#: Neutral은 일부러 버린다 — 아래 `earth_is_neutral` 주석 참고.
EMOTION_ALIASES: dict[str, str] = {
    "anger": "anger",
    "angry": "anger",
    "disgust": "disgust",
    "fear": "fear",
    "happiness": "joy",
    "happy": "joy",
    "joy": "joy",
    "sadness": "sadness",
    "sad": "sadness",
    "surprise": "surprise",
}

#: 웃음근육 쌍. AU06 = 볼 올림(뒤셴), AU12 = 입꼬리 당김.
SMILE_AUS = ("AU06", "AU12")

#: ⚠️ 잠정값 — 현장 계측 필요.
#: py-feat의 AU 출력은 OpenFace 계열의 0~5 intensity가 아니라 0~1
#: 확률값이다. 20개를 다 더하면 이론상 20이지만, 격한 표정에서도 강하게
#: 켜지는 AU는 5~8개 수준이라 실측 합은 4~6 부근으로 예상된다.
#: arousal.DEFAULT_AU_REFERENCE(12.0)는 OpenFace 기준이므로 그대로 쓰면
#: 표정 강도가 항상 낮게 깎인다.
PYFEAT_AU_REFERENCE = 5.0


@dataclass(frozen=True)
class PyFeatReading:
    """py-feat 한 프레임 출력에서 엔진이 쓰는 것만 추린 것.

    emotions
        엔진의 6개 감정 필드. Neutral은 들어 있지 않다.
    smile_au
        AU06·AU12에서 만든 웃음근육 활성도(0~1).
    au_sum
        AU 20종 값의 합. arousal의 표정 쪽 재료(정규화 전 원값).
    native_arousal
        py-feat v2가 직접 내주는 arousal을 [-1,1]에서 [0,1]로 옮긴 값.
        v1 경로에는 없으므로 None.
    """

    emotions: dict[str, float]
    smile_au: float
    au_sum: float
    native_arousal: float | None

    @property
    def earth_is_neutral(self) -> float:
        """이 판독에서 흙이 갖게 될 비중.

        py-feat의 감정 출력은 Neutral을 포함한 7개에 대한 확률이라 합이
        1이다. 우리는 Neutral을 버리고 6개만 넘기는데, 그러면

            흙 = 1 − (물 + 불 + 공기) = 1 − 활성 감정 합 = Neutral

        이 되어 **흙 비중이 py-feat의 Neutral 확률과 정확히 일치한다.**
        Neutral을 따로 받아 쓰면 오히려 이중 계산이 된다. 잔여값으로
        평온을 정의한 설계(2026-08-12)와 모델 출력이 맞아떨어지는 지점.
        """
        return max(0.0, 1.0 - sum(self.emotions.values()))

    def face_intensity(self, reference: float = PYFEAT_AU_REFERENCE) -> float:
        """arousal의 표정 쪽 재료를 0~1로 정규화한다.

        native_arousal이 있으면 그쪽을 쓴다 — 학습된 값이라 AU 확률의
        단순 합보다 낫고, 정규화 기준을 현장에서 실측할 부담도 없다.
        다만 어느 쪽을 쓸지는 실측 후 확정한다(→ 후보비교 논점 1).
        """
        if self.native_arousal is not None:
            return self.native_arousal
        return normalise(self.au_sum, reference)

    def to_signal(self, arousal: float) -> EmotionSignal:
        """엔진 입력으로 변환한다. arousal은 밖에서 만들어 넣는다."""
        return EmotionSignal(
            arousal=arousal,
            smile_au=self.smile_au,
            **self.emotions,
        )


def read_pyfeat(
    row: dict[str, float],
    smile_mode: str = "mean",
) -> PyFeatReading:
    """py-feat 한 행(감정 + AU 컬럼)을 판독한다.

    row
        py-feat Fex 한 행을 dict로 만든 것. 컬럼 이름은 v1/v2 어느
        표기든 상관없고, 없는 컬럼은 0으로 본다.
    smile_mode
        ``"mean"``  AU06·AU12의 평균 — 기본값.
        ``"strict"`` 둘 중 작은 값. 두 근육이 함께 켜져야 웃음으로 보는
        뒤셴 판정에 가깝다. 희망 슬롯이 과하게 나오면 이쪽으로 조인다.
    """
    if smile_mode not in ("mean", "strict"):
        raise ValueError(f"smile_mode는 'mean' 또는 'strict': {smile_mode!r}")

    lower = {str(k).lower(): v for k, v in row.items()}

    emotions = {
        "joy": 0.0,
        "sadness": 0.0,
        "anger": 0.0,
        "fear": 0.0,
        "disgust": 0.0,
        "surprise": 0.0,
    }
    for label, field in EMOTION_ALIASES.items():
        if label in lower:
            emotions[field] = _clamp01(float(lower[label]))

    au_values = {
        k: float(v)
        for k, v in lower.items()
        if k.startswith("au") and k[2:].isdigit()
    }
    au_sum = sum(max(0.0, v) for v in au_values.values())

    smile_pair = [_clamp01(au_values.get(au.lower(), 0.0)) for au in SMILE_AUS]
    smile = min(smile_pair) if smile_mode == "strict" else sum(smile_pair) / 2.0

    native = lower.get("arousal")
    native_arousal = None if native is None else _clamp01((float(native) + 1.0) / 2.0)

    return PyFeatReading(
        emotions=emotions,
        smile_au=smile,
        au_sum=au_sum,
        native_arousal=native_arousal,
    )


def signal_from_pyfeat(
    row: dict[str, float],
    motion_energy: float = 0.0,
    smile_mode: str = "mean",
    au_reference: float = PYFEAT_AU_REFERENCE,
) -> EmotionSignal:
    """py-feat 한 행 + 움직임 에너지 → 엔진 입력 한 번에.

    motion_energy는 **이미 0~1로 정규화된** 값이다. 원단위(m/s)에서
    옮기려면 `arousal.normalise(speed, MOTION_REFERENCE)`를 먼저 쓴다.
    여러 프레임을 평활하려면 이 함수 대신 `arousal.ArousalTracker`를
    쓰고 결과를 `PyFeatReading.to_signal`에 넣는다.
    """
    reading = read_pyfeat(row, smile_mode=smile_mode)
    arousal = blend(reading.face_intensity(au_reference), _clamp01(motion_energy))
    return reading.to_signal(arousal)


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))
