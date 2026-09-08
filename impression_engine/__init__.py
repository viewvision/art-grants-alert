"""감정의 인상 — 판정 엔진 코어.

카메라·렌더러에 의존하지 않는 순수 로직 계층. 감정 수치를 받아
24개 문구 슬롯 중 하나로 판정하고, 화면에 칠할 색과 표시 문구를
결정한다.

기본 사용:

    from impression_engine import EmotionSignal, process

    result = process(EmotionSignal(sadness=0.7, disgust=0.2, arousal=0.5))
    print(result.summary())
"""

from .adapters import PyFeatReading, read_pyfeat, signal_from_pyfeat
from .arousal import ArousalTracker, blend, motion_energy_from_joints, normalise
from .directions import DirectionVector, to_directions
from .engine import Impression, process
from .judgment import Judgment, all_slot_ids, judge
from .palette import RenderPalette, palette_for
from .phrases import coverage, filter_phrase, resolve_phrase
from .profile import DEFAULT_PROFILE, Profile
from .signals import EmotionSignal

__all__ = [
    "EmotionSignal",
    "DirectionVector",
    "Judgment",
    "RenderPalette",
    "Impression",
    "Profile",
    "DEFAULT_PROFILE",
    "ArousalTracker",
    "PyFeatReading",
    "read_pyfeat",
    "signal_from_pyfeat",
    "blend",
    "normalise",
    "motion_energy_from_joints",
    "to_directions",
    "judge",
    "palette_for",
    "resolve_phrase",
    "filter_phrase",
    "coverage",
    "all_slot_ids",
    "process",
]
