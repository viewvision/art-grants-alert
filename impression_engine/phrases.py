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

PENDING = None  # 아직 집필하지 않은 슬롯

#: 작가가 직접 쓰고 확정한 슬롯. 신청서에 실린 8개다.
#:
#: 왜 따로 표시하는가 — 1계층은 생성 모델의 few-shot 예시이므로 **모델이
#: 여기서 문체를 배운다.** 실측 프로토콜 B(문체 일치도)는 "작가가 자기
#: 문장과 생성 문장을 블라인드로 못 가려내야 통과"인데, 1계층에 작가
#: 문장과 초안이 섞여 있으면 그 검사의 기준 자체가 흐려진다. 어느 줄이
#: 작가의 것인지 알아야 판정이 성립한다.
AUTHOR_CONFIRMED_KO: frozenset[str] = frozenset({
    "water_mid",
    "water_high",
    "fire_joy_high",
    "fire_anger_high",
    "air_hope_mid",
    "air_anxiety_mid",
    "earth_mid",
    "mixed_water_fire",
})

#: 1계층 기준 문구 — 한국어 24개.
#:
#: 구조: **비춰준 다음 묻는다** (2026-09-07 확정)
#:
#:     조금 가라앉아 있네요.  |  오늘 무엇이 있었나요?
#:          비춰주기                  질문
#:
#: 관객의 사정을 우리가 알 수는 없지만, 무언가를 알아봐 줬다는 느낌이
#: 있어야 거기서부터 생각이 시작된다. 질문만 던지면 관객이 붙잡을 데가
#: 없어 추상적으로 겉돈다.
#:
#: 공감하되 진단하지 않기 위해 **감정에 이름을 붙이지 않고 물질의
#: 상태로만** 비춘다.
#:
#:     "불안해 보이네요"       ← 진단. 쓰지 않는다
#:     "조금 흔들리고 있네요"  ← 상태를 비춤. 이쪽
#:
#: 강도에 따라 비추는 세기도 다르다 — 저는 여지를 두고 조심스럽게,
#: 중은 분명하게, 고는 정면으로.
#:
#: 작가 확정본(위 AUTHOR_CONFIRMED_KO)은 비춤을 한 문장 안에 녹인 방식
#: 이고("그 무게", "그 뜨거움"), 나머지는 두 문장으로 나눈 방식이다.
#: 두 방식을 섞어 쓰기로 확정했다 (2026-09-07 작가 승인).
BASELINE_KO: dict[str, str | None] = {
    # ── 물 · 가라앉으며 고인다 ──────────────────────────────
    "water_low": "조금 가라앉아 있네요. 오늘 무엇이 있었나요?",
    "water_mid": "지금 당신을 가라앉게 하는 건 무엇인가요?",
    "water_high": "그 무게를 잠시 내려놓아도 될까요?",
    # ── 불 · 피어오르며 번진다 ──────────────────────────────
    "fire_joy_low": "작게 밝아지고 있네요. 무엇이 그렇게 만들었나요?",
    "fire_joy_mid": "안에서 무언가 피어오르고 있네요. 무엇 때문인가요?",
    "fire_joy_high": "그 뜨거움은 어디를 향해 있나요?",
    "fire_anger_low": "아직 식지 않은 열이 남아 있네요. 어디서 온 걸까요?",
    "fire_anger_mid": "뜨거운 것이 올라오고 있네요. 무엇이 그렇게 만들었나요?",
    "fire_anger_high": "그 뜨거움은 무엇을 지키려 하나요?",
    # ── 공기 · 경계 없이 흩어진다 ───────────────────────────
    "air_hope_low": "무언가를 조금 기다리고 있네요. 그게 무엇인가요?",
    "air_hope_mid": "당신이 기다리고 있는 건 무엇인가요?",
    "air_hope_high": "기다리는 마음이 크네요. 그것이 온다면 무엇이 달라질까요?",
    "air_anxiety_low": "조금 흔들리고 있네요. 무엇이 마음에 걸리나요?",
    "air_anxiety_mid": "아직 모르는 그것이, 당신에게 무엇일까요?",
    "air_anxiety_high": "흩어지는 것들 사이에 서 있네요. 무엇을 붙잡고 싶은가요?",
    # ── 흙 · 구조를 이루며 응집한다 ─────────────────────────
    "earth_low": "아주 고요하네요. 지금 이 순간 무엇이 남아 있나요?",
    "earth_mid": "지금 당신을 지탱해주는 건 무엇인가요?",
    # arousal을 표정과 독립시킨 이유가 바로 이 슬롯이다 —
    # "고요해 보이지만 속이 들끓는 사람". 판정을 그대로 말로 옮겼다.
    "earth_high": "겉은 잔잔한데 안이 분주하네요. 무엇이 움직이고 있나요?",
    # ── 혼합 · 두 원소가 비등할 때 ──────────────────────────
    "mixed_water_fire": "가라앉음과 뜨거움이 함께 있네요. 어느 쪽이 먼저였나요?",
    "mixed_water_air": "가라앉으면서 흩어지고 있네요. 어느 쪽에 머물고 싶은가요?",
    "mixed_water_earth": "가라앉은 자리에 그대로 머물러 있네요. 그곳은 어떤가요?",
    "mixed_fire_air": "뜨거움이 사방으로 흩어지고 있네요. 어디로 가고 싶은가요?",
    "mixed_fire_earth": "뜨거운 채로 자리를 지키고 있네요. 무엇을 위해서인가요?",
    "mixed_air_earth": "떠나려는 마음과 머무는 마음이 같이 있네요. 어느 쪽인가요?",
}

#: 1계층 기준 문구 — 영어 24개.
#:
#: 직역이 아니다. 다만 **완전히 다른 문장이어서도 안 된다** — 한글과
#: 영문이 화면에 나란히 뜨므로(2026-08-17 한영 병기 확정), 둘을 다 읽는
#: 관객에게 서로 다른 말로 보이면 어긋난다. 기준은 이렇게 좁혀졌다:
#:
#:     의미의 축은 같게, 문장의 리듬만 각 언어에 맞게 (2026-09-07)
#:
#: 영문은 장식이 아니라 **입력 트리거**다. 관객이 문장을 읽고 반응하는
#: 것이 8단계(반응 재캡처)의 입력값이므로, 문장을 읽지 못하는 관객에게는
#: 인터랙션의 절반이 작동하지 않는다. 외국인 관객에게는 이쪽이 본문이다.
#:
#: `Something in you is...` 구문을 축으로 삼았다 — 관객에게 감정을 붙이지
#: 않으면서 상태를 비추는 데 영어에서 가장 잘 작동한다.
BASELINE_EN: dict[str, str | None] = {
    # ── water ───────────────────────────────────────────────
    "water_low": "Something in you has settled low today. What was it?",
    "water_mid": "What is it that keeps pulling you down right now?",
    "water_high": "That weight — could you set it down for a moment?",
    # ── fire ────────────────────────────────────────────────
    "fire_joy_low": "Something in you is brightening, just a little. What did that?",
    "fire_joy_mid": "Something is rising in you. What lit it?",
    "fire_joy_high": "That heat in you — where is it heading?",
    "fire_anger_low": "A heat that hasn't cooled is still here. Where did it come from?",
    "fire_anger_mid": "Something hot is rising in you. What brought it up?",
    "fire_anger_high": "That heat in you — what is it protecting?",
    # ── air ─────────────────────────────────────────────────
    "air_hope_low": "You're waiting on something, quietly. What is it?",
    "air_hope_mid": "What is it that you keep waiting for?",
    "air_hope_high": "The waiting in you is large. If it arrived, what would change?",
    "air_anxiety_low": "Something in you is unsteady, slightly. What sits on your mind?",
    "air_anxiety_mid": "That thing you don't know yet — what is it to you?",
    "air_anxiety_high": "You're standing among things coming apart. What would you hold?",
    # ── earth ───────────────────────────────────────────────
    "earth_low": "It is very still here. What remains, in this moment?",
    "earth_mid": "What is holding you up right now?",
    "earth_high": "Still on the surface, busy underneath. What is moving in there?",
    # ── mixed ───────────────────────────────────────────────
    "mixed_water_fire": (
        "Something in you is sinking and burning at once. Which one came first?"
    ),
    "mixed_water_air": "Sinking and scattering at once. Which one would you stay with?",
    "mixed_water_earth": "Settled low, and staying there. What is that place like?",
    "mixed_fire_air": "The heat is scattering outward. Where does it want to go?",
    "mixed_fire_earth": "Hot, and holding its ground. What is it holding for?",
    "mixed_air_earth": "Part of you leaving, part of you staying. Which one is it?",
}

#: 영문에는 아직 작가 확정본이 없다 — 24개 전부 초안이다.
#: ⬜ **원어민 감수 예정** (2026-09-07 작가 메모). 24문장뿐이라 부담이
#: 크지 않고, 트리거로 실제 작동해야 하는 문장이므로 값어치가 있다.
#: 감수를 마친 슬롯은 이 목록으로 옮긴다.
AUTHOR_CONFIRMED_EN: frozenset[str] = frozenset()

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

#: 영문 감정 라벨 — 이 단어들을 관객에게 붙이는 것이 진단이다.
_EN_EMOTION_WORDS = (
    "sad|angry|anxious|depressed|happy|upset|stressed|afraid|scared"
    "|nervous|lonely|miserable|furious|joyful|calm"
)

#: 영문 금지 규칙 — 2026-09-07 완화.
#:
#: 이전에는 `you are` / `you're` 자체를 통째로 막았다. 그런데 영어에서
#: 이 구문 없이 관객에게 말을 걸기가 매우 어색해진다 — "You're waiting
#: on something"을 "There is a waiting in you"로 우회해야 했고, 그러면
#: 문어적으로 굳어 트리거로서의 즉각성이 떨어진다.
#:
#: 막아야 할 것은 구문이 아니라 **진단**이므로, `you are` 뒤에 감정
#: 라벨이 붙는 경우만 막는다. `you seem/look/feel + 감정`도 같은 진단이다.
#: (2026-09-07 작가 승인)
BANNED_EN_PATTERNS = (
    rf"\byou\s*(?:are|'re|were)\s+(?:\w+\s+){{0,2}}(?:{_EN_EMOTION_WORDS})\b",
    rf"\byou\s+(?:seem|look|feel|appear)\s+(?:\w+\s+){{0,2}}(?:{_EN_EMOTION_WORDS})\b",
    rf"\byou\s+(?:are|'re)\s+being\b",
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
    """집필 진행률. 남은 슬롯이 무엇인지 그대로 보여준다.

    `written`과 `author_confirmed`를 나눠 보고한다 — 칸이 채워진 것과
    작가가 확정한 것은 다르다. 초안으로 채워진 칸은 아직 검토 대기다.
    """
    table = BASELINE_KO if lang == "ko" else BASELINE_EN
    confirmed = AUTHOR_CONFIRMED_KO if lang == "ko" else AUTHOR_CONFIRMED_EN
    slots = all_slot_ids()
    missing = [s for s in slots if not table.get(s)]
    draft = [s for s in slots if table.get(s) and s not in confirmed]
    return {
        "lang": lang,
        "total": len(slots),
        "written": len(slots) - len(missing),
        "author_confirmed": len([s for s in slots if s in confirmed and table.get(s)]),
        "missing": missing,
        "draft": draft,
    }
