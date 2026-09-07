"""엔진 통합 API.

인식 계층이 준 감정 신호 하나를 받아, 렌더 계층이 그대로 쓸 수 있는
화면 사양(색·문구·판정 근거)을 돌려준다.

파이프라인 9단계 중 이 모듈이 담당하는 구간:

    3·분석  ← 외부 (에크만 6 감정 분류 모델)
    4·변환  → directions.to_directions
    5·판정  → judgment.judge
    6·문구  → phrases.resolve_phrase
    7·렌더  → palette.palette_for 가 만든 사양을 TouchDesigner가 소비

얼굴 원본은 이 계층에 들어오지 않는다. 숫자만 들어온다.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .directions import DirectionVector, to_directions
from .judgment import Judgment, judge
from .palette import RenderPalette, palette_for
from .phrases import PhraseGenerator, resolve_phrase
from .signals import EmotionSignal


@dataclass(frozen=True)
class Impression:
    """한 관객, 한 순간의 화면 사양."""

    judgment: Judgment
    palette: RenderPalette
    phrase_ko: str | None
    phrase_en: str | None
    phrase_source: str
    vector: DirectionVector = field(repr=False)

    def to_render_spec(self) -> dict[str, object]:
        """TouchDesigner 등 렌더 계층에 넘길 직렬화 가능한 사양."""
        return {
            "slot": self.judgment.slot_id,
            "label": self.judgment.ko_label,
            "is_mixed": self.judgment.is_mixed,
            "ratios_percent": {
                k: round(v * 100, 1) for k, v in self.judgment.ratios.items()
            },
            "gap_pp": round(self.judgment.gap_pp, 1),
            "arousal": round(self.judgment.arousal, 3),
            "palette": self.palette.as_dict(),
            "phrase": {
                "ko": self.phrase_ko,
                "en": self.phrase_en,
                "source": self.phrase_source,
            },
        }

    def summary(self) -> str:
        pct = self.judgment.ratios
        order = sorted(pct.items(), key=lambda kv: -kv[1])
        ratio_text = "  ".join(f"{k}:{v*100:4.1f}%" for k, v in order)
        if self.palette.second_color:
            color_text = (
                f"{self.palette.dominant_color}({self.palette.dominant_weight*100:.0f}%)"
                f" + {self.palette.second_color}({self.palette.second_weight*100:.0f}%)"
            )
        else:
            color_text = (
                f"{self.palette.dominant_color}"
                f"({self.palette.dominant_weight*100:.0f}%) 단독"
            )
        return (
            f"[{self.judgment.slot_id}] {self.judgment.ko_label}\n"
            f"  {ratio_text}   격차 {self.judgment.gap_pp:.1f}%p\n"
            f"  색 {color_text}"
            f"  배경 {self.palette.background[0]}→{self.palette.background[1]}\n"
            f"  문구({self.phrase_source}) {self.phrase_ko or '— 미집필 —'}"
        )


def process(
    signal: EmotionSignal,
    generator: PhraseGenerator | None = None,
) -> Impression:
    """감정 신호 → 화면 사양. 엔진의 단일 진입점."""
    vector = to_directions(signal)
    verdict = judge(vector)
    colors = palette_for(verdict)

    phrase_ko, source = resolve_phrase(verdict.slot_id, "ko", generator)
    phrase_en, _ = resolve_phrase(verdict.slot_id, "en", generator)

    return Impression(
        judgment=verdict,
        palette=colors,
        phrase_ko=phrase_ko,
        phrase_en=phrase_en,
        phrase_source=source,
        vector=vector,
    )
