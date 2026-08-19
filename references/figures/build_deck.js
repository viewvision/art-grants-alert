const pptxgen = require('pptxgenjs');

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';          // 13.3 x 7.5
const W = 13.3, H = 7.5;

const NAVY  = '1E2761';
const INK   = '1C2230';
const SUB   = '8A919E';
const FAINT = 'B9BFC9';
const GRAY  = 'C4C8D0';
const ACC   = 'D6603C';
const KR    = '맑은 고딕';

function title(slide, t) {
  slide.addText(t, {
    x: 0.75, y: 0.45, w: 3.2, h: 0.6,
    fontFace: KR, fontSize: 30, bold: true, color: NAVY, margin: 0,
    align: 'left', valign: 'middle',
  });
}

/* ─────────────────────────── 1. 4방향 색 ─────────────────────────── */
const s1 = pres.addSlide();
s1.background = { color: 'FFFFFF' };
title(s1, '감정 판정 결과 = 색');

const ELEMENTS = [
  { name: '물',   sw: ['AADBDF', '55BCC7', '009EB0'] },
  { name: '불',   sw: ['F6CAB8', 'F29977', 'EE6836'] },
  { name: '공기', sw: ['D6D1E7', 'B1A6D7', '8C7CC8'] },
  { name: '흙',   sw: ['E5D4B6', 'CFAD73', 'BA8630'] },
];

const COL_W = 2.6, COL_GAP = 0.55;
const TOTAL = ELEMENTS.length * COL_W + (ELEMENTS.length - 1) * COL_GAP;
const X0 = (W - TOTAL) / 2;
const SW_H = 1.05, SW_GAP = 0.13, Y0 = 1.75;

ELEMENTS.forEach((el, i) => {
  const x = X0 + i * (COL_W + COL_GAP);
  el.sw.forEach((c, j) => {
    s1.addShape(pres.ShapeType.roundRect, {
      x, y: Y0 + j * (SW_H + SW_GAP), w: COL_W, h: SW_H,
      fill: { color: c }, line: { color: c, width: 0 }, rectRadius: 0.08,
    });
  });
  s1.addText(el.name, {
    x, y: Y0 + 3 * (SW_H + SW_GAP) + 0.18, w: COL_W, h: 0.6,
    fontFace: KR, fontSize: 26, bold: true, color: INK, align: 'center', margin: 0,
  });
});

s1.addText('위 → 아래 : 강도 저 → 고', {
  x: W - 4.05, y: H - 0.95, w: 3.3, h: 0.35,
  fontFace: KR, fontSize: 12, color: FAINT, align: 'right', margin: 0,
});
s1.addNotes('4가지 방향(물·불·공기·흙)의 기준색과 강도 3단계. 강도는 채도로 옮겨진다.');

/* ─────────────────────── 2. 출력 스케일 ─────────────────────── */
const s2 = pres.addSlide();
s2.background = { color: 'FFFFFF' };
title(s2, '출력 스케일');

const PH = 4.15;                       // 패널 높이 (in) = 2.20 m
const PW = PH * 2.93 / 2.20;           // = 5.53
const PX = (W - PW) / 2;
const PY = 2.05;
const IN_PER_M = PH / 2.20;

s2.addShape(pres.ShapeType.rect, {
  x: PX, y: PY, w: PW, h: PH,
  fill: { color: 'E8F0F6' }, line: { color: 'C3CBD4', width: 1 },
});

// 실루엣 169cm
const figH = 1.69 * IN_PER_M;
const baseY = PY + PH;
const topY  = baseY - figH;
const cx    = PX + PW / 2;
const SIL   = '96A2B0';
const noLine = { width: 0, color: SIL };

const headR = figH * 0.055;
s2.addShape(pres.ShapeType.ellipse, {
  x: cx - headR, y: topY, w: headR * 2, h: headR * 2,
  fill: { color: SIL }, line: noLine,
});
const tw = figH * 0.105, ty0 = topY + headR * 2 + figH * 0.018, ty1 = topY + figH * 0.55;
s2.addShape(pres.ShapeType.roundRect, {
  x: cx - tw, y: ty0, w: tw * 2, h: ty1 - ty0,
  fill: { color: SIL }, line: noLine, rectRadius: 0.18,
});
const aw = figH * 0.030;
[-1, 1].forEach(sgn => {
  s2.addShape(pres.ShapeType.roundRect, {
    x: sgn < 0 ? cx - tw - aw * 2 : cx + tw,
    y: ty0 + figH * 0.012, w: aw * 2, h: (ty1 - ty0) - figH * 0.04,
    fill: { color: SIL }, line: noLine, rectRadius: 0.1,
  });
});
const lw = figH * 0.040;
[-1, 1].forEach(sgn => {
  s2.addShape(pres.ShapeType.roundRect, {
    x: sgn < 0 ? cx - tw + 0.03 : cx + tw - lw * 2 - 0.03,
    y: ty1 - figH * 0.02, w: lw * 2, h: baseY - (ty1 - figH * 0.02),
    fill: { color: SIL }, line: noLine, rectRadius: 0.1,
  });
});

// 상지 도달 높이 2.10m
const reachY = baseY - 2.10 * IN_PER_M;
s2.addShape(pres.ShapeType.line, {
  x: PX - 0.2, y: reachY, w: PW + 0.4, h: 0,
  line: { color: ACC, width: 1.5 },
});
s2.addText('2.10 m', {
  x: PX + PW + 0.3, y: reachY - 0.2, w: 1.5, h: 0.4,
  fontFace: KR, fontSize: 14, color: ACC, margin: 0, valign: 'middle',
});

// 치수 — 가로
s2.addShape(pres.ShapeType.line, {
  x: PX, y: PY - 0.42, w: PW, h: 0, line: { color: INK, width: 1.25 },
});
[PX, PX + PW].forEach(xx => {
  s2.addShape(pres.ShapeType.line, {
    x: xx, y: PY - 0.55, w: 0, h: 0.26, line: { color: INK, width: 1.25 },
  });
});
s2.addText('2.93 m', {
  x: PX, y: PY - 1.02, w: PW, h: 0.4,
  fontFace: KR, fontSize: 18, bold: true, color: INK, align: 'center', margin: 0,
});

// 치수 — 세로
s2.addShape(pres.ShapeType.line, {
  x: PX - 0.62, y: PY, w: 0, h: PH, line: { color: INK, width: 1.25 },
});
[PY, PY + PH].forEach(yy => {
  s2.addShape(pres.ShapeType.line, {
    x: PX - 0.75, y: yy, w: 0.26, h: 0, line: { color: INK, width: 1.25 },
  });
});
s2.addText('2.20 m', {
  x: PX - 2.5, y: PY + PH / 2 - 0.22, w: 1.75, h: 0.44,
  fontFace: KR, fontSize: 18, bold: true, color: INK, align: 'right', margin: 0, valign: 'middle',
});

// 인물 키
s2.addText('169 cm', {
  x: cx + tw + 0.35, y: baseY - figH * 0.42, w: 1.4, h: 0.35,
  fontFace: KR, fontSize: 13, color: SUB, margin: 0,
});
s2.addNotes('LED 2.2m(H) x 2.93m(W), 4:3. 20대 평균 신장 169cm 기준 상지 도달 높이 약 2.10m에서 역산.');

/* ─────────────────────── 3. 파이프라인 ─────────────────────── */
const s3 = pres.addSlide();
s3.background = { color: 'FFFFFF' };
title(s3, '파이프라인');

const STEPS = [
  { n: '1', t: '감지',   dev: false },
  { n: '2', t: '캡처',   dev: false },
  { n: '3', t: '분석',   dev: true  },
  { n: '4', t: '변환',   dev: true  },
  { n: '5', t: '판정',   dev: true  },
  { n: '6', t: '문구',   dev: true  },
  { n: '7', t: '렌더',   dev: false },
  { n: '8', t: '재캡처', dev: true  },
  { n: '9', t: '저장',   dev: true  },
];

const MARG = 0.75;
const BGAP = 0.14;
const BW = (W - MARG * 2 - BGAP * (STEPS.length - 1)) / STEPS.length;
const BH = 1.55;
const BY = 2.75;

STEPS.forEach((st, i) => {
  const x = MARG + i * (BW + BGAP);
  const fillC = st.dev ? NAVY : GRAY;
  s3.addShape(pres.ShapeType.roundRect, {
    x, y: BY, w: BW, h: BH,
    fill: { color: fillC }, line: { color: fillC, width: 0 }, rectRadius: 0.12,
  });
  s3.addText(st.n, {
    x: x + 0.12, y: BY + 0.12, w: 0.5, h: 0.3,
    fontFace: KR, fontSize: 11, color: st.dev ? '9BAAC8' : '6E7684', margin: 0,
  });
  s3.addText(st.t, {
    x, y: BY + BH / 2 - 0.28, w: BW, h: 0.56,
    fontFace: KR, fontSize: 17, bold: true,
    color: st.dev ? 'FFFFFF' : '363E4C', align: 'center', valign: 'middle', margin: 0,
  });
  if (i < STEPS.length - 1) {
    s3.addShape(pres.ShapeType.triangle, {
      x: x + BW + 0.028, y: BY + BH / 2 - 0.07, w: BGAP - 0.056, h: 0.14,
      fill: { color: 'CBD0D8' }, line: { width: 0, color: 'CBD0D8' }, rotate: 90,
    });
  }
});

// 1~7 브래킷
const bx0 = MARG;
const bx1 = MARG + 6 * (BW + BGAP) + BW;
const by  = BY + BH + 0.34;
s3.addShape(pres.ShapeType.line, { x: bx0, y: by, w: bx1 - bx0, h: 0, line: { color: ACC, width: 1.5 } });
[bx0, bx1].forEach(xx => {
  s3.addShape(pres.ShapeType.line, { x: xx, y: by - 0.16, w: 0, h: 0.16, line: { color: ACC, width: 1.5 } });
});
s3.addText('연산 3초', {
  x: bx0, y: by + 0.1, w: bx1 - bx0, h: 0.45,
  fontFace: KR, fontSize: 18, bold: true, color: ACC, align: 'center', margin: 0,
});

// 범례
const ly = H - 0.95;
s3.addShape(pres.ShapeType.roundRect, {
  x: MARG, y: ly, w: 0.26, h: 0.26,
  fill: { color: NAVY }, line: { width: 0, color: NAVY }, rectRadius: 0.05,
});
s3.addText('개발', {
  x: MARG + 0.38, y: ly - 0.05, w: 1.2, h: 0.36,
  fontFace: KR, fontSize: 13, color: INK, margin: 0, valign: 'middle',
});
s3.addShape(pres.ShapeType.roundRect, {
  x: MARG + 1.5, y: ly, w: 0.26, h: 0.26,
  fill: { color: GRAY }, line: { width: 0, color: GRAY }, rectRadius: 0.05,
});
s3.addText('보유', {
  x: MARG + 1.88, y: ly - 0.05, w: 1.2, h: 0.36,
  fontFace: KR, fontSize: 13, color: INK, margin: 0, valign: 'middle',
});
s3.addNotes('캡처부터 표시까지 9단계. 1~7단계 연산이 3초 이내. 네이비 = 본 사업 개발분, 회색 = 기보유 기술.');

pres.writeFile({ fileName: '/home/user/art-grants-alert/references/figures/감정의인상_도해.pptx' })
   .then(f => console.log('saved', f));
