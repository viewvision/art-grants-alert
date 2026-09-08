"""TouchDesigner 배관 — 엔진 출력을 TD가 바로 먹는 형태로.

왜 이렇게 단순한가
    `impression_engine`은 **외부 의존성이 하나도 없다**(표준 라이브러리만
    쓴다). TouchDesigner에는 파이썬이 내장돼 있으므로, 별도 프로세스도
    소켓도 없이 **TD 안에서 엔진을 직접 import**할 수 있다.

두 갈래

    개발·목업 단계        TD가 엔진을 직접 부른다
        슬라이더 → to_channels/to_table → 화면
        인식 모듈이 없어도 24슬롯을 전부 손으로 돌려볼 수 있다.

    운영 단계             py-feat는 TD 밖에서 돈다
        py-feat는 torch가 필요해 TD 내장 파이썬에 넣기 어렵다.
        바깥 프로세스가 `write_spec()`으로 JSON을 쓰고, TD의 File In
        DAT가 읽는다. 매 프레임이 아니라 **관객 한 명당 한 번**이므로
        파일로 충분하다.

TD가 실제로 원하는 형태
    TD는 색을 `#RRGGBB`가 아니라 **0~1 실수 RGB**로 쓴다. 그리고 숫자는
    CHOP, 문자열은 DAT로 나뉜다. 그래서 사양을 그대로 넘기지 않고
    `to_channels`(숫자)와 `to_table`(문자열)로 갈라 준다.

TD 쪽 최소 설정 (Text DAT 하나)

    import sys
    sys.path.append('C:/.../art-grants-alert')          # 저장소 경로
    from bridge.td_bridge import mock_spec, to_channels, to_table

    # 슬라이더 4개(비중) + arousal 하나로 목업
    spec = mock_spec(water=0.7, fire=0.3, air=0.0, earth=0.0, arousal=0.8)
    op('spec_chop').par...                              # to_channels(spec)
    op('spec_dat').clear(); op('spec_dat').appendRows(to_table(spec))
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from impression_engine import EmotionSignal, Profile, process  # noqa: E402

__all__ = [
    "hex_to_rgb",
    "to_channels",
    "to_table",
    "mock_spec",
    "write_spec",
    "read_spec",
]


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    """`#RRGGBB` → TD가 쓰는 0~1 실수 RGB.

    TD의 색 파라미터는 0~255가 아니라 0~1이다. 이 변환을 빼먹으면
    화면이 전부 흰색으로 뜬다.
    """
    h = value.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def to_channels(spec: dict[str, Any]) -> dict[str, float]:
    """숫자만 평면으로 — Constant CHOP / Script CHOP 용.

    색도 여기 들어간다(r/g/b로 갈라서). TD에서 색은 숫자이기 때문이다.
    """
    pal = spec["palette"]
    dom = pal["dominant"]
    sec = pal["second"]
    motion = spec["motion"]
    ratios = spec["ratios_percent"]

    out: dict[str, float] = {
        # 4방향 비중 — 색의 면적·농도가 되는 값
        "ratio_water": ratios["water"] / 100.0,
        "ratio_fire": ratios["fire"] / 100.0,
        "ratio_air": ratios["air"] / 100.0,
        "ratio_earth": ratios["earth"] / 100.0,
        "gap": spec["gap_pp"] / 100.0,
        # 강도 — 채도로 옮겨진다
        "arousal": spec["arousal"],
        "level": {"low": 0.0, "mid": 0.5, "high": 1.0}[pal["level"]],
        "is_mixed": 1.0 if spec["is_mixed"] else 0.0,
        # 1위
        "dom_weight": dom["weight"],
        # 2위 — 없으면 비중 0으로 넘긴다. 화면에 올리지 말라는 뜻이다.
        "sec_weight": sec["weight"] if sec else 0.0,
        "sec_visible": 1.0 if sec else 0.0,
        # 운동 — 톤을 단계가 아니라 정도로 쓴다
        "motion_bias": motion["bias"] if motion["bias"] is not None else 0.0,
        "motion_toned": 1.0 if motion["toned"] else 0.0,
    }

    for prefix, hexval in (
        ("dom", dom["color"]),
        ("sec", sec["color"] if sec else "#000000"),
        ("bg_from", pal["background"]["from"]),
        ("bg_to", pal["background"]["to"]),
    ):
        r, g, b = hex_to_rgb(hexval)
        out[f"{prefix}_r"], out[f"{prefix}_g"], out[f"{prefix}_b"] = r, g, b

    return out


def to_table(spec: dict[str, Any]) -> list[list[str]]:
    """문자열 — Table DAT 용. 첫 행이 헤더다."""
    motion = spec["motion"]
    return [
        ["key", "value"],
        ["slot", spec["slot"]],
        ["label", spec["label"]],
        ["direction", spec["palette"]["dominant"]["direction"]],
        ["tone", motion["tone"] or ""],
        ["motion_base", motion["base"]],
        ["motion_toned", motion["toned"] or motion["base"]],
        ["phrase_ko", spec["phrase"]["ko"] or ""],
        ["phrase_en", spec["phrase"]["en"] or ""],
        ["phrase_source", spec["phrase"]["source"]],
    ]


def mock_spec(
    water: float = 0.0,
    fire: float = 0.0,
    air: float = 0.0,
    earth: float = 0.0,
    arousal: float = 0.5,
    bias: float = 0.0,
    profile: Profile | None = None,
) -> dict[str, Any]:
    """슬라이더 값 → 렌더 사양. **인식 모듈 없이 24슬롯을 전부 돌려본다.**

    4방향 비중을 직접 주는 게 목적이므로, 그 비중이 나오도록 감정값을
    역산해 넣는다. 나중에 이 함수 자리에 py-feat 출력을 꽂으면 된다.

    bias
        불·공기의 톤을 미는 값(-1~1). 양수면 기쁨·희망, 음수면 분노·불안.
        물·흙은 톤 분기가 없어 무시된다.

    비중을 다 0으로 두면 흙이 잔여값으로 100%가 된다 — 무반응 상태다.
    """
    total = water + fire + air + earth
    if total > 0:
        # 활성 3방향의 합이 (1 - earth)가 되도록 맞춘다.
        # 흙은 잔여값이므로 직접 넣지 않고 나머지로 만들어진다.
        scale = (1.0 - earth / total) / (total - earth) if total > earth else 0.0
        water, fire, air = water * scale, fire * scale, air * scale

    # 각 방향은 배정된 감정 2개의 합이다. 톤은 bias로 가른다.
    bright = max(0.0, bias)
    dark = max(0.0, -bias)
    if bias == 0.0:
        bright = dark = 0.5

    return process(
        EmotionSignal(
            sadness=water,          # 물 = 슬픔 + 혐오
            disgust=0.0,
            joy=fire * bright,      # 불 = 기쁨 ↔ 분노
            anger=fire * dark,
            surprise=air,           # 공기 = 놀람 ↔ 공포
            fear=air * dark,
            smile_au=bright,
            arousal=arousal,
        ),
        profile=profile,
    ).to_render_spec()


def write_spec(path: str | Path, spec: dict[str, Any]) -> None:
    """사양을 JSON 파일로 — 외부 프로세스(py-feat)가 TD에 넘길 때.

    **원자적으로 쓴다.** 임시 파일에 다 쓴 뒤 이름을 바꾼다. 그냥 쓰면
    TD의 File In DAT가 반쯤 쓰인 파일을 읽어 JSON 파싱에 실패하는 일이
    생긴다 — 몇 초에 한 번이라 드물게 터지고, 그래서 원인을 찾기 어렵다.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(spec, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def read_spec(path: str | Path) -> dict[str, Any] | None:
    """TD 쪽에서 읽을 때. 파일이 없거나 깨졌으면 None."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
