"""판정 엔진 검증.

pytest 없이도 `python3 tests/test_engine.py` 로 바로 실행된다.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from impression_engine import (  # noqa: E402
    DEFAULT_PROFILE,
    ArousalTracker,
    EmotionSignal,
    all_slot_ids,
    blend,
    coverage,
    filter_phrase,
    judge,
    motion_energy_from_joints,
    normalise,
    process,
    Profile,
    read_pyfeat,
    signal_from_pyfeat,
    to_directions,
)
from impression_engine.judgment import MIXED_THRESHOLD_PP  # noqa: E402

FAILURES: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        FAILURES.append(label)


def section(title: str) -> None:
    print(f"\n── {title}")


# ────────────────────────────── 1. 4방향 변환 ──────────────────────────────
section("4방향 변환 규칙")

v = to_directions(EmotionSignal(sadness=0.8, disgust=0.4, arousal=0.5))
check(abs(sum(v.ratios.values()) - 1.0) < 1e-9, "비율 합계가 정확히 1.0")
check(v.dominant == "water", "슬픔+혐오 → 물이 1위")

v = to_directions(EmotionSignal(anger=0.9, arousal=0.8))
check(v.dominant == "fire", "분노 → 불이 1위")

v = to_directions(EmotionSignal(fear=0.7, surprise=0.5, arousal=0.6))
check(v.dominant == "air", "공포+놀람 → 공기가 1위")

v = to_directions(EmotionSignal(arousal=0.1))
check(v.dominant == "earth", "감정 반응이 없으면 흙이 1위 (잔여값)")
check(v.ratios["earth"] == 1.0, "무반응 상태에서 흙 비중 100%")

weak = to_directions(EmotionSignal(joy=0.2, arousal=0.3))
strong = to_directions(EmotionSignal(joy=0.9, arousal=0.9))
check(
    weak.ratios["earth"] > strong.ratios["earth"],
    "감정이 약할수록 흙 비중이 커진다",
)

# ────────────────────────────── 2. valence ──────────────────────────────
section("방향별 valence 계산")

v = to_directions(EmotionSignal(joy=0.8, anger=0.1, arousal=0.7))
check(v.valences["fire"] > 0, "기쁨 > 분노 → 불 valence 양수")

v = to_directions(EmotionSignal(joy=0.1, anger=0.8, arousal=0.7))
check(v.valences["fire"] < 0, "분노 > 기쁨 → 불 valence 음수")

v = to_directions(EmotionSignal(sadness=0.5, disgust=0.5, arousal=0.5))
check(v.valences["water"] < 0, "물 valence는 음수 고정")

v = to_directions(EmotionSignal(arousal=0.2))
check(v.valences["earth"] == 0.0, "흙 valence는 중립 고정")

# 공기 — 놀람은 웃음근육이 동반될 때만 '희망' 재료가 된다
no_smile = to_directions(EmotionSignal(fear=0.3, surprise=0.7, arousal=0.6))
with_smile = to_directions(
    EmotionSignal(fear=0.3, surprise=0.7, smile_au=0.9, arousal=0.6)
)
check(no_smile.valences["air"] < 0, "웃음근육 없으면 공기는 불안 쪽")
check(with_smile.valences["air"] > 0, "웃음근육 동반 시 공기가 희망 쪽으로")

# ────────────────────────────── 3. 판정 알고리즘 ──────────────────────────────
section("문구 슬롯 판정 (4단계)")

j = judge(to_directions(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5)))
check(not j.is_mixed and j.dominant == "water", "물 단일 우세형 판정")
check(j.tone is None, "물은 톤 분기가 없다")
check(j.level == "mid", "arousal 0.5 → 강도 중")

j = judge(to_directions(EmotionSignal(anger=0.9, arousal=0.9)))
check(j.slot_id == "fire_anger_high", "불·분노·고 슬롯")

j = judge(to_directions(EmotionSignal(joy=0.9, arousal=0.2)))
check(j.slot_id == "fire_joy_low", "불·기쁨·저 슬롯")

j = judge(to_directions(EmotionSignal(fear=0.8, arousal=0.5)))
check(j.slot_id == "air_anxiety_mid", "공기·불안·중 슬롯")

# 강도 경계값
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.33))).level == "low", "arousal 0.33 → 저")
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.34))).level == "mid", "arousal 0.34 → 중")
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.66))).level == "mid", "arousal 0.66 → 중")
check(judge(to_directions(EmotionSignal(anger=0.9, arousal=0.67))).level == "high", "arousal 0.67 → 고")

# 혼합형
j = judge(to_directions(EmotionSignal(sadness=0.6, disgust=0.6, anger=0.6, joy=0.6, arousal=0.5)))
check(j.is_mixed, "1·2위 격차 10%p 미만 → 혼합형")
check(j.slot_id == "mixed_water_fire", "물+불 혼합 슬롯")
check(j.gap_pp < MIXED_THRESHOLD_PP, "혼합형 격차가 임계값 미만")

# 혼합형은 순서와 무관하게 같은 슬롯
a = judge(to_directions(EmotionSignal(sadness=0.61, disgust=0.61, anger=0.6, joy=0.6, arousal=0.5)))
b = judge(to_directions(EmotionSignal(sadness=0.6, disgust=0.6, anger=0.61, joy=0.61, arousal=0.5)))
check(a.slot_id == b.slot_id, "물+불 / 불+물은 같은 슬롯")

# ────────────────────────────── 4. 슬롯 총량 ──────────────────────────────
section("슬롯 구조")

slots = all_slot_ids()
check(len(slots) == 24, f"슬롯 총 24개 (실제 {len(slots)}개)")
check(len(set(slots)) == 24, "슬롯 ID 중복 없음")
single = [s for s in slots if not s.startswith("mixed_")]
mixed = [s for s in slots if s.startswith("mixed_")]
check(len(single) == 18, f"단일 우세형 18개 (실제 {len(single)}개)")
check(len(mixed) == 6, f"혼합형 6개 (실제 {len(mixed)}개)")

# ─────────────────────── 5. 입력 공간 전수 스윕 ───────────────────────
section("입력 공간 스윕 — 크래시·규칙 위반 없음")

produced: set[str] = set()
steps = (0.0, 0.25, 0.5, 0.75, 1.0)
count = 0
for joy, sadness, anger, fear, surprise in itertools.product(steps, repeat=5):
    for arousal in (0.1, 0.5, 0.9):
        for smile in (0.0, 1.0):
            sig = EmotionSignal(
                joy=joy,
                sadness=sadness,
                anger=anger,
                fear=fear,
                disgust=sadness * 0.5,
                surprise=surprise,
                smile_au=smile,
                arousal=arousal,
            )
            result = process(sig)
            produced.add(result.judgment.slot_id)
            count += 1

            assert abs(sum(result.judgment.ratios.values()) - 1.0) < 1e-9
            assert result.judgment.dominant != result.judgment.second
            assert result.palette.dominant_color.startswith("#")

check(True, f"{count}개 입력 조합 전부 예외 없이 처리")
check(produced <= set(slots), "생성된 슬롯이 전부 정의된 24개 안에 있음")
print(f"        도달한 슬롯 {len(produced)}/24 — 미도달 {sorted(set(slots) - produced)}")

# ────────────────────────────── 6. 배경색 규칙 ──────────────────────────────
section("배경색 — 1위 방향의 반대 온도")

warm_dominant = process(EmotionSignal(anger=0.9, arousal=0.8))
cool_dominant = process(EmotionSignal(sadness=0.9, disgust=0.8, arousal=0.5))
check(
    warm_dominant.palette.background[0] == "#BFE3F7",
    "불(따뜻) 1위 → 차가운 하늘색 배경",
)
check(
    cool_dominant.palette.background[0] == "#FFE0C4",
    "물(차가움) 1위 → 따뜻한 오렌지 배경",
)

# ────────────────────────────── 7. 문구 규칙 필터 ──────────────────────────────
section("3계층 작가 규칙 필터")

check(filter_phrase("지금 당신을 가라앉게 하는 건 무엇인가요?").passed, "정상 질문문 통과")
check(not filter_phrase("당신은 슬픕니다.").passed, "진단문 차단")
check(not filter_phrase("지금 기분이 어떤가요").passed, "물음표 없으면 차단")
check(not filter_phrase("가" * 50 + "?").passed, "길이 상한 초과 차단")
check(not filter_phrase("측정 결과는 무엇인가요?").passed, "'측정 결과' 금지어 차단")
check(not filter_phrase("You are sad?", lang="en").passed, "영문 진단문 차단")

# ────────────────────────────── 8. 폴백 동작 ──────────────────────────────
section("생성 실패 시 1계층 폴백")


def broken_generator(slot_id: str, lang: str, examples: list[str]) -> str:
    raise RuntimeError("모델 로드 실패")


def bad_generator(slot_id: str, lang: str, examples: list[str]) -> str:
    return "당신은 지금 불안합니다."


r = process(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5), generator=broken_generator)
check(r.phrase_source == "baseline", "생성 모델 예외 → 기준 문구로 폴백")

r = process(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5), generator=bad_generator)
check(r.phrase_source == "baseline", "필터 미통과 → 기준 문구로 폴백")


def good_generator(slot_id: str, lang: str, examples: list[str]) -> str:
    return "그 무거움은 어디서 왔을까요?"


r = process(EmotionSignal(sadness=0.9, disgust=0.7, arousal=0.5), generator=good_generator)
check(r.phrase_source == "generated", "필터 통과 → 생성 문구 사용")

# ────────────────────────── 9. arousal 산출 ──────────────────────────
section("arousal 산출 — 표정 강도 + 움직임 에너지 가중합")

check(normalise(6.0, 12.0) == 0.5, "정규화: 기준의 절반 → 0.5")
check(normalise(20.0, 12.0) == 1.0, "정규화: 기준 초과는 1.0으로 상한")
check(normalise(-1.0, 12.0) == 0.0, "정규화: 음수는 0.0")

check(abs(blend(1.0, 0.0) - 0.5) < 1e-9, "표정만 최대 → 0.5 (50:50 가중)")
check(abs(blend(0.0, 1.0) - 0.5) < 1e-9, "움직임만 최대 → 0.5")
check(abs(blend(1.0, 1.0) - 1.0) < 1e-9, "둘 다 최대 → 1.0")
check(abs(blend(0.8, 0.2, 0.75, 0.25) - 0.65) < 1e-9, "가중치 변경 반영")

try:
    blend(0.5, 0.5, 0.6, 0.6)
    check(False, "가중치 합이 1이 아니면 거부")
except ValueError:
    check(True, "가중치 합이 1이 아니면 거부")

# 움직임 — 관절 좌표에서 속도 산출
still = {"hand": (0.0, 0.0, 0.0), "head": (0.0, 1.5, 0.0)}
moved = {"hand": (0.3, 0.0, 0.0), "head": (0.0, 1.5, 0.0)}
speed = motion_energy_from_joints(still, moved, dt_seconds=1.0)
check(abs(speed - 0.15) < 1e-9, "관절 2개 중 하나만 0.3m 이동 → 평균 0.15m/s")
check(motion_energy_from_joints(still, still, 1.0) == 0.0, "정지 상태는 0")
check(
    motion_energy_from_joints({"a": (0, 0, 0)}, {"b": (1, 1, 1)}, 1.0) == 0.0,
    "공통 관절이 없으면 0 (가려짐을 움직임으로 세지 않음)",
)

# 트래커 — 평활과 초기화
t = ArousalTracker()
check(t.value == 0.0, "프레임 전에는 0.0")
first = t.update(au_intensity_sum=12.0, motion_speed=0.35)
check(abs(first - 1.0) < 1e-9, "첫 프레임은 평활 없이 그대로")
second = t.update(au_intensity_sum=0.0, motion_speed=0.0)
check(0.0 < second < 1.0, "급락한 프레임이 평활로 완충됨")
t.reset()
check(t.value == 0.0, "reset 후 이전 관객 값이 남지 않음")

# 흙·고 도달 — 이 결정의 핵심 근거.
# 감정 6개가 전부 약하게 잡힌 애매한 표정이면 흙이 1위가 된다.
# 감정에서 arousal을 유도했다면 이 상태는 강도 '저'로 고정돼 흙·고가
# 영구 미도달이었다. 별도 신호를 쓰기 때문에 도달한다.
AMBIGUOUS = dict(joy=0.1, sadness=0.1, anger=0.1, fear=0.1, disgust=0.1, surprise=0.1)

check(
    to_directions(EmotionSignal(**AMBIGUOUS)).dominant == "earth",
    "감정이 전부 약하면 흙이 1위",
)
check(
    judge(to_directions(EmotionSignal(**AMBIGUOUS, arousal=blend(0.5, 1.0)))).slot_id
    == "earth_high",
    "애매한 표정 + 큰 움직임 → 흙·고 도달",
)

# 한쪽 신호만으로는 '고'에 닿지 않는다 — 가중합의 의도된 성질이다.
# 확률합(soft OR)으로 바꾸면 격자 전체의 70%가 '고'로 쏠려 강도축이
# 무너진다. 가중합은 저/중/고를 24:52:24로 고르게 쓴다.
check(
    judge(to_directions(EmotionSignal(**AMBIGUOUS, arousal=blend(0.0, 1.0)))).level
    == "mid",
    "움직임만 최대 → 강도 '중'까지 (한 신호만으로는 '고' 불가)",
)
check(
    judge(to_directions(EmotionSignal(**AMBIGUOUS, arousal=blend(1.0, 0.0)))).level
    == "mid",
    "표정만 최대 → 강도 '중'까지",
)

# ────────────────────────── 10. py-feat 어댑터 ──────────────────────────
section("py-feat 어댑터 — 인식 출력 → 엔진 입력")

# v1 표기(소문자). 감정 7종 확률 합 = 1.
V1_ROW = {
    "anger": 0.05, "disgust": 0.03, "fear": 0.02, "happiness": 0.55,
    "sadness": 0.04, "surprise": 0.11, "neutral": 0.20,
    "AU06": 0.82, "AU12": 0.91, "AU25": 0.40, "AU01": 0.05,
}
r = read_pyfeat(V1_ROW)
check(r.emotions["joy"] == 0.55, "happiness → joy 사상")
check(r.emotions["sadness"] == 0.04, "sadness 그대로")
check("neutral" not in r.emotions, "Neutral은 넘기지 않는다")
check(
    abs(r.smile_au - min(1.0, 0.91 * (1 + 0.25 * 0.82))) < 1e-9,
    "웃음근육 = AU12 × (1 + 0.25×AU06)",
)
check(abs(r.earth_is_neutral - 0.20) < 1e-9, "흙 비중이 Neutral 확률과 일치")
check(r.native_arousal is None, "v1에는 네이티브 arousal이 없다")

# 흙 비중이 실제 판정에서도 Neutral과 같은지 — 설계와 모델의 대응 확인
sig = r.to_signal(arousal=0.8)
check(
    abs(to_directions(sig).ratios["earth"] - 0.20) < 1e-9,
    "엔진이 계산한 흙 비중 = py-feat Neutral (이중 계산 없음)",
)
check(judge(to_directions(sig)).slot_id == "fire_joy_high", "웃는 얼굴 → 불·기쁨·고")

# v2 표기(대문자) + 네이티브 arousal
V2_ROW = {
    "Anger": 0.02, "Disgust": 0.01, "Fear": 0.30, "Happy": 0.03,
    "Sad": 0.04, "Surprise": 0.45, "Neutral": 0.15,
    "AU06": 0.10, "AU12": 0.05, "AU04": 0.60,
    "arousal": 0.5,
}
r2 = read_pyfeat(V2_ROW)
check(r2.emotions["fear"] == 0.30, "대문자 표기도 인식")
check(r2.emotions["joy"] == 0.03, "Happy → joy 사상")
check(abs(r2.native_arousal - 0.75) < 1e-9, "arousal [-1,1] → [0,1] 변환")
check(
    r2.face_intensity() == r2.native_arousal,
    "네이티브 arousal이 있으면 AU 합 대신 그것을 쓴다",
)

# 웃음근육 — AU06은 웃음을 확인만 하고 만들어내지는 못한다.
# AU06은 py-feat 모델 카드가 밝힌 최약점(F1 0.526)이므로, 그 오류가
# 공기의 희망/불안 분기를 뒤집지 못하게 막는 것이 이 모델의 목적이다.
noisy_au06 = {"AU06": 0.9, "AU12": 0.1}   # AU06만 헛 반응
missed_au06 = {"AU06": 0.1, "AU12": 0.9}  # AU12는 켜졌는데 AU06이 놓침
duchenne = {"AU06": 0.9, "AU12": 0.8}     # 둘 다 켜진 진짜 웃음

check(
    read_pyfeat(noisy_au06).smile_au < 0.15,
    "AU06만 켜져도 웃음 신호를 만들지 못한다 (mean이었다면 0.5)",
)
check(
    read_pyfeat(missed_au06).smile_au > 0.9,
    "AU06이 놓쳐도 AU12가 켜졌으면 웃음이 유지된다 (mean이었다면 0.5)",
)
check(
    read_pyfeat(duchenne).smile_au > read_pyfeat({"AU06": 0.0, "AU12": 0.8}).smile_au,
    "AU06이 함께 켜지면 뒤셴 보너스로 신호가 커진다",
)
check(read_pyfeat({"AU06": 1.0, "AU12": 1.0}).smile_au == 1.0, "보너스가 1.0을 넘지 않는다")

check(abs(read_pyfeat(missed_au06, smile_mode="au12").smile_au - 0.9) < 1e-9, "au12 모드")
check(abs(read_pyfeat(missed_au06, smile_mode="weighted").smile_au - 0.7) < 1e-9, "weighted 모드")
check(abs(read_pyfeat(missed_au06, smile_mode="mean").smile_au - 0.5) < 1e-9, "mean 모드")
check(abs(read_pyfeat(missed_au06, smile_mode="strict").smile_au - 0.1) < 1e-9, "strict 모드")

# 통합 경로
s = signal_from_pyfeat(V1_ROW, motion_energy=0.6)
check(0.0 <= s.arousal <= 1.0, "통합 경로가 유효한 arousal 생성")
check(process(s).judgment.dominant == "fire", "통합 경로 판정까지 관통")

# 없는 컬럼은 0으로 — 모델 경로가 달라도 죽지 않는다
check(read_pyfeat({}).smile_au == 0.0, "빈 입력도 예외 없이 처리")
check(read_pyfeat({}).earth_is_neutral == 1.0, "감정이 없으면 흙 100%")

# ────────────────────────── 11. 캘리브레이션 프로필 ──────────────────────────
section("캘리브레이션 프로필 — 기계·현장 종속값 분리")

check(DEFAULT_PROFILE.is_provisional, "기본 프로필은 실측 전 표시")

# 저장소에 든 프로필이 전부 유효해야 한다
profiles = sorted(Path(__file__).resolve().parents[1].glob("calibration/*.json"))
check(len(profiles) >= 2, f"프로필 파일 {len(profiles)}개 확인")
for path in profiles:
    try:
        Profile.load(path)
        check(True, f"{path.name} 로드·검증 통과")
    except Exception as exc:  # noqa: BLE001
        check(False, f"{path.name} 로드 실패: {exc}")

# 프로필이 실제로 결과를 바꾸는가 — 배경색
tinted = Profile(background_cool=("#101820", "#203040"), background_warm=("#FFF0E0", "#FFD0A0"))
base = process(EmotionSignal(anger=0.9, arousal=0.8))
themed = process(EmotionSignal(anger=0.9, arousal=0.8), profile=tinted)
check(base.palette.background[0] == "#BFE3F7", "프로필 없으면 코드 기본 배경")
check(themed.palette.background[0] == "#101820", "프로필 배경색이 실제로 적용됨")

# 물 valence
deep = Profile(water_valence=-0.9)
check(
    to_directions(EmotionSignal(sadness=0.8, arousal=0.5), deep).valences["water"] == -0.9,
    "프로필 물 valence가 적용됨",
)

# 웃음근육 계수
strong = Profile(au06_bonus=1.0)
row = {"AU06": 1.0, "AU12": 0.5}
check(
    read_pyfeat(row, profile=strong).smile_au > read_pyfeat(row).smile_au,
    "프로필 au06_bonus가 웃음 신호를 바꾼다",
)
check(
    read_pyfeat(row, profile=Profile(smile_mode="au12")).smile_au == 0.5,
    "프로필 smile_mode가 적용됨",
)

# 프로필로 만든 트래커
t = Profile(au_reference=2.0, motion_reference=1.0).tracker()
check(abs(t.update(au_intensity_sum=2.0, motion_speed=1.0) - 1.0) < 1e-9, "프로필로 만든 트래커")

# 잘못된 값은 조용히 넘어가지 않는다
def rejects(label, **kwargs):
    try:
        Profile(**kwargs)
        check(False, f"거부해야 함: {label}")
    except ValueError:
        check(True, f"거부: {label}")

rejects("가중치 합이 1이 아님", face_weight=0.7, motion_weight=0.7)
rejects("smile_mode 오타", smile_mode="bonuss")
rejects("물 valence 양수", water_valence=0.5)
rejects("배경색 형식 오류", background_cool=("파랑", "#78C4F0"))
rejects("정규화 기준 0", au_reference=0.0)

# 오타 난 키를 조용히 무시하면 캘리브레이션했다고 착각하게 된다
import json as _json  # noqa: E402
import tempfile  # noqa: E402

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
    _json.dump({"arousal": {"au_referenc": 3.0}}, fh)  # 오타
    typo_path = fh.name
try:
    Profile.load(typo_path)
    check(False, "오타 난 키를 거부해야 함")
except ValueError:
    check(True, "오타 난 키를 거부한다")

# 왕복 — 저장했다 읽으면 같아야 한다
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fh:
    round_path = fh.name
original = Profile(name="왕복", measured="2026-09-07", au_reference=7.5, smile_mode="au12")
original.save(round_path)
check(Profile.load(round_path) == original, "저장 → 로드 왕복이 동일")
check(not original.is_provisional, "measured가 있으면 실측 완료로 표시")

# ────────────────────────────── 12. 집필 진행률 ──────────────────────────────
section("1계층 문구 집필 진행률")

ko = coverage("ko")
en = coverage("en")
print(f"        한국어 {ko['written']}/{ko['total']}   영어 {en['written']}/{en['total']}")
check(ko["written"] == 8, "한국어 확정 8개 반영됨")

# ────────────────────────────── 결과 ──────────────────────────────
print("\n" + "=" * 60)
if FAILURES:
    print(f"실패 {len(FAILURES)}건")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print("전체 통과")
