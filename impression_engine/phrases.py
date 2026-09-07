"""표시 문구 — 1계층(작가 집필 기준 문구) + 3계층(작가 규칙 필터).

설계 근거: Project_감정의인상.md "⑤ 표시 문구 — 진단이 아니라 질문,
그리고 AI 생성" 3계층 구조.

    1계층  작가 집필 기준 문구 48개(한/영 각 24)
           생성 모델의 few-shot 예시이자, 생성 실패 시 폴백
    2계층  로컬 생성 모델        ← 모델 필요. 여기서는 인터페이스만 정의
    3계층  작가 규칙 필터        ← 이 파일에 구현

문구는 "당신은 슬픕니다" 같은 진단문이 아니라 질문이어야 한다.
읽히기 위해서가 아니라 반응을 부르기 위해 떠 있는 문장이다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Protocol

from .judgment import all_slot_ids

PENDING = None  # 아직 작가가 집필하지 않은 슬롯

#: 1계층 기준 문구 — 한국어.
#: 확정본은 신청서 "1계층 기준 문구 예시(한국어 24개 중 8개)"에 실린 8개다.
BASELINE_KO: dict[str, str | None] = {
    "water_low": PENDING,
    "water_mid": "지금 당신을 가라앉게 하는 건 무엇인가요?",
    "water_high": "그 무게를 잠시 내려놓아도 될까요?",
    "fire_joy_low": PENDING,
    "fire_joy_mid": PENDING,
    "fire_joy_high": "그 뜨거움은 어디를 향해 있나요?",
    "fire_anger_low": PENDING,
    "fire_anger_mid": PENDING,
    "fire_anger_high": "그 뜨거움은 무엇을 지키려 하나요?",
    "air_hope_low": PENDING,
    "air_hope_mid": "당신이 기다리고 있는 건 무엇인가요?",
    "air_hope_high": PENDING,
    "air_anxiety_low": PENDING,
    "air_anxiety_mid": "아직 모르는 그것이, 당신에게 무엇일까요?",
    "air_anxiety_high": PENDING,
    "earth_low": PENDING,
    "earth_mid": "지금 당신을 지탱해주는 건 무엇인가요?",
    "earth_high": PENDING,
    "mixed_water_fire": "가라앉음과 뜨거움이 함께 있네요. 어느 쪽이 먼저였나요?",
    "mixed_water_air": PENDING,
    "mixed_water_earth": PENDING,
    "mixed_fire_air": PENDING,
    "mixed_fire_earth": PENDING,
    "mixed_air_earth": PENDING,
}

#: 1계층 기준 문구 — 영어. 직역이 아니라 영어로 따로 쓴 문장이어야 한다.
#: 현재 1개만 시안 단계에서 사용됐고 작가 확정 전이다.
BASELINE_EN: dict[str, str | None] = {
    slot: PENDING for slot in BASELINE_KO
}
BASELINE_EN["mixed_water_fire"] = (
    "Something in you is sinking and burning at once. Which one came first?"
)

# ─────────────────────────── 3계층: 작가 규칙 필터 ───────────────────────────

#: 문장 길이 상한. 근접 시야에서 한 호흡에 읽히는 길이.
MAX_CHARS_KO = 40
MAX_CHARS_EN = 90

#: 진단·단정 표현 금지. "당신은 ~입니다" 형태를 걸러낸다.
BANNED_KO_PATTERNS = (
    r"당신은\s.*(입니다|이다|예요|이에요|네요)",
    r"(슬픕|화가\s*났|불안합|우울합|기쁩)",
    r"(진단|분석\s*결과|측정\s*결과|점수)",
)

BANNED_EN_PATTERNS = (
    r"\byou are\b",
    r"\byou're\b",
    r"\b(sad|angry|anxious|depressed|happy)\b\s*$",
    r"\b(diagnos|analysis result|score)\w*\b",
)

_KO_QUESTION = re.compile(r"[?？]\s*$")


@dataclass(frozen=True)
class FilterResult:
    passed: bool
    reason: str | None = None


def filter_phrase(text: str, lang: str = "ko") -> FilterResult:
    """생성된 문장이 작가 규칙을 지키는지 검사한다.

    통과하지 못하면 호출부가 1계층 기준 문구로 대체해야 한다.
    """
    stripped = text.strip()

    if not stripped:
        return FilterResult(False, "빈 문장")

    if not _KO_QUESTION.search(stripped):
        return FilterResult(False, "질문형이 아님 (물음표로 끝나지 않음)")

    limit = MAX_CHARS_KO if lang == "ko" else MAX_CHARS_EN
    if len(stripped) > limit:
        return FilterResult(False, f"길이 상한 초과 ({len(stripped)} > {limit})")

    patterns = BANNED_KO_PATTERNS if lang == "ko" else BANNED_EN_PATTERNS
    for pattern in patterns:
        if re.search(pattern, stripped, flags=re.IGNORECASE):
            return FilterResult(False, f"금지 표현 (진단·단정): /{pattern}/")

    return FilterResult(True)


# ─────────────────────────── 2계층: 생성 모델 자리 ───────────────────────────


class PhraseGenerator(Protocol):
    """로컬 생성 모델이 맞춰야 할 인터페이스.

    현장 장비에서 구동되며 외부 서버 통신이 없어야 한다.
    """

    def __call__(self, slot_id: str, lang: str, examples: list[str]) -> str: ...


def resolve_phrase(
    slot_id: str,
    lang: str = "ko",
    generator: PhraseGenerator | None = None,
) -> tuple[str | None, str]:
    """슬롯에 표시할 문구 한 문장을 결정한다.

    Returns
        (문구, 출처) — 출처는 "generated" | "baseline" | "missing"

    생성 모델이 없거나, 생성 결과가 필터를 통과하지 못하면 1계층
    기준 문구로 자동 대체한다. 기준 문구조차 없으면 (None, "missing").
    """
    table = BASELINE_KO if lang == "ko" else BASELINE_EN
    baseline = table.get(slot_id)

    if generator is not None:
        examples = [p for p in table.values() if p]
        try:
            candidate = generator(slot_id, lang, examples)
        except Exception:  # 생성 실패는 폴백으로 흡수한다
            candidate = ""
        if candidate and filter_phrase(candidate, lang).passed:
            return candidate, "generated"

    if baseline:
        return baseline, "baseline"
    return None, "missing"


def coverage(lang: str = "ko") -> dict[str, object]:
    """집필 진행률. 남은 슬롯이 무엇인지 그대로 보여준다."""
    table = BASELINE_KO if lang == "ko" else BASELINE_EN
    slots = all_slot_ids()
    missing = [s for s in slots if not table.get(s)]
    return {
        "lang": lang,
        "total": len(slots),
        "written": len(slots) - len(missing),
        "missing": missing,
    }
