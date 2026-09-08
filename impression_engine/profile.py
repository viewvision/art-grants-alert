"""캘리브레이션 프로필 — 기계·현장마다 달라지는 값을 코드 밖으로.

왜 필요한가
    엔진의 상수 중 일부는 **설계 확정값**이고 일부는 **그 기계, 그 공간
    에서 재봐야 아는 값**이다. 둘이 코드에 섞여 있으면 현장에서 조명이
    바뀔 때마다 파이썬 소스를 편집해야 하고, 그건 전시 중에 사고가
    나는 길이다.

    이 모듈은 후자만 JSON으로 빼낸다.

        같은 코드 + calibration/작업실.json    ← 작업실 PC
        같은 코드 + calibration/현장.json      ← 현장 PC

    현장 PC 설치가 "코드 복사 + 프로필 하나"로 끝나고, 값이 바뀐 이력은
    git에 남는다.

무엇이 프로필로 나오고 무엇이 코드에 남는가

    프로필 (여기)          기계·공간 종속. 실측으로 정한다
      · arousal 재료의 가중치와 정규화 기준
      · 프레임 평활 계수
      · 웃음근육 결합 방식과 계수
      · 아직 미확정인 작가 판단값 (물 valence, 배경색)

    코드에 유지            작품 설계 확정값. 함부로 바뀌면 안 된다
      · 24개 슬롯 구조, 혼합 임계 10%p, 강도 구간 33/66
      · 4방향 원소색 HEX, 감정→방향 배정
      · 2위 가시성 하한

프로필을 주지 않으면 `DEFAULT_PROFILE`이 쓰인다 — 즉 프로필 없이도 돈다.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

SMILE_MODES = ("bonus", "au12", "weighted", "mean", "strict")


@dataclass(frozen=True)
class Profile:
    """한 기계·한 공간의 캘리브레이션 한 벌."""

    name: str = "default"
    note: str = ""
    #: 실측한 날짜(YYYY-MM-DD). 비어 있으면 아직 잠정값이라는 뜻이다.
    measured: str = ""

    # ── arousal 산출 ─────────────────────────────────────────
    face_weight: float = 0.5
    motion_weight: float = 0.5
    #: 표정 강도 정규화 기준. py-feat는 AU가 0~1 확률이라 5.0,
    #: OpenFace 계열(0~5 intensity)이라면 12.0 근처다.
    au_reference: float = 5.0
    #: 움직임 정규화 기준 — 상체 관절 평균 이동 속도(m/s).
    #: **공간마다 다르다.** 관객 체류가 짧고 정적인 공간에서는 낮춘다.
    motion_reference: float = 0.35
    #: 프레임 간 평활(EMA). 작을수록 둔하게 반응한다.
    smoothing: float = 0.4

    # ── 웃음근육 결합 ────────────────────────────────────────
    smile_mode: str = "bonus"
    au06_bonus: float = 0.25

    # ── 미확정 (작가 판단 대기) ──────────────────────────────
    #: 물의 고정 valence. 설계 문서 범위 -0.3 ~ -0.6의 중앙값.
    water_valence: float = -0.45
    #: 배경 그라데이션. 1위 방향의 반대 온도가 배정된다.
    background_cool: tuple[str, str] = ("#BFE3F7", "#78C4F0")
    background_warm: tuple[str, str] = ("#FFE0C4", "#FFB37A")

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """잘못된 값으로 조용히 도는 것보다 즉시 멈추는 편이 낫다."""
        if abs(self.face_weight + self.motion_weight - 1.0) > 1e-9:
            raise ValueError(
                "face_weight + motion_weight 는 1.0이어야 합니다: "
                f"{self.face_weight} + {self.motion_weight}"
            )
        for name in ("face_weight", "motion_weight", "au06_bonus"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} 는 0.0~1.0 범위여야 합니다: {value}")
        if not 0.0 < self.smoothing <= 1.0:
            raise ValueError(f"smoothing 은 0 초과 1.0 이하여야 합니다: {self.smoothing}")
        for name in ("au_reference", "motion_reference"):
            value = getattr(self, name)
            if value <= 0:
                raise ValueError(f"{name} 는 양수여야 합니다: {value}")
        if self.smile_mode not in SMILE_MODES:
            raise ValueError(
                f"smile_mode 는 {'/'.join(SMILE_MODES)} 중 하나여야 합니다: "
                f"{self.smile_mode!r}"
            )
        if not -1.0 <= self.water_valence <= 0.0:
            raise ValueError(
                "water_valence 는 -1.0~0.0 이어야 합니다(물은 음수 고정): "
                f"{self.water_valence}"
            )
        for name in ("background_cool", "background_warm"):
            pair = getattr(self, name)
            if len(pair) != 2:
                raise ValueError(f"{name} 은 색 2개여야 합니다: {pair}")
            for hex_value in pair:
                if not HEX_RE.match(hex_value):
                    raise ValueError(f"{name} 의 색이 #RRGGBB 형식이 아닙니다: {hex_value}")

    @property
    def is_provisional(self) -> bool:
        """아직 실측 전인가."""
        return not self.measured

    @classmethod
    def load(cls, path: str | Path) -> Profile:
        """JSON 프로필을 읽는다.

        모르는 키는 무시하지 않고 거부한다 — 오타 난 키가 조용히
        기본값으로 돌아가면 캘리브레이션을 했다고 착각하게 된다.
        """
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        flat = _flatten(raw)

        known = {f.name for f in cls.__dataclass_fields__.values()}
        unknown = set(flat) - known
        if unknown:
            raise ValueError(
                f"{path.name}: 모르는 항목이 있습니다: {sorted(unknown)}\n"
                f"  쓸 수 있는 항목: {sorted(known)}"
            )

        for key in ("background_cool", "background_warm"):
            if key in flat:
                flat[key] = tuple(flat[key])

        return cls(**flat)

    def save(self, path: str | Path) -> None:
        """사람이 읽고 고칠 수 있는 형태로 쓴다."""
        Path(path).write_text(
            json.dumps(_nest(asdict(self)), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def tracker(self):
        """이 프로필로 설정된 ArousalTracker를 만든다."""
        from .arousal import ArousalTracker

        return ArousalTracker(
            face_weight=self.face_weight,
            motion_weight=self.motion_weight,
            au_reference=self.au_reference,
            motion_reference=self.motion_reference,
            smoothing=self.smoothing,
        )

    def summary(self) -> str:
        mark = "잠정값 (실측 전)" if self.is_provisional else f"실측 {self.measured}"
        return (
            f"[{self.name}] {mark}\n"
            f"  arousal  표정 {self.face_weight:.2f} : 움직임 {self.motion_weight:.2f}"
            f"  · 기준 AU합 {self.au_reference} / {self.motion_reference}m/s"
            f"  · 평활 {self.smoothing}\n"
            f"  웃음     {self.smile_mode}"
            + (f" (보너스 {self.au06_bonus})" if self.smile_mode == "bonus" else "")
            + f"\n  미확정   물 valence {self.water_valence}"
            f"  · 배경 {self.background_cool[0]}↔{self.background_warm[0]}"
            + (f"\n  비고     {self.note}" if self.note else "")
        )


#: 프로필을 주지 않았을 때 쓰이는 값. 현재 코드 상수와 같다.
DEFAULT_PROFILE = Profile()


# ── JSON 중첩 ↔ 평면 변환 ─────────────────────────────────────
# 사람이 읽기 좋게 섹션으로 묶어 두되, 코드에서는 평면으로 쓴다.
_SECTIONS = {
    "arousal": ("face_weight", "motion_weight", "au_reference", "motion_reference", "smoothing"),
    "smile": ("smile_mode", "au06_bonus"),
    "pending": ("water_valence", "background_cool", "background_warm"),
}


def _flatten(raw: dict) -> dict:
    flat: dict = {}
    for key, value in raw.items():
        if key.startswith("_"):
            continue  # 사람이 적어 둔 메모
        if key in _SECTIONS and isinstance(value, dict):
            flat.update({k: v for k, v in value.items() if not k.startswith("_")})
        else:
            flat[key] = value
    return flat


def _nest(flat: dict) -> dict:
    out: dict = {k: flat[k] for k in ("name", "note", "measured") if k in flat}
    for section, keys in _SECTIONS.items():
        out[section] = {k: _listify(flat[k]) for k in keys if k in flat}
    return out


def _listify(value):
    return list(value) if isinstance(value, tuple) else value
