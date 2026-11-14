// Editable PowerPoint templates for the contest winner pack (no images: shapes + text only)
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/ce2abee9-91b1-4046-b0dd-d56cb1afdeb1_7f9cef30-0a1d-4d02-a274-fc7146dac682/pptx/scripts/apply_theme.js");

const THEME = {
  name: "SIRA Short-form Contest",
  headFontFace: "맑은 고딕", bodyFontFace: "맑은 고딕",
  colors: { dk1: "224098", lt1: "FFFFFF", dk2: "1A1A1A", lt2: "E8E8E6",
            accent1: "224098", accent2: "E12D2D", accent3: "8A8A8A", accent4: "B8B8B8", accent5: "4A64B0", accent6: "D9DEEC",
            hlink: "224098", folHlink: "4A64B0" },
};
const W = { award: "대상", contest: "2026 숏폼 영상 공모전", title: "건축사의 진심:\nInside the building",
            maker: "구앤건 (구재영, 고건)" };
const SLOGAN = "건축엔 건축사가 있습니다";
const HOST = "주관 | 서울특별시건축사회 홍보위원회";
const LINKS = "www.sira.or.kr  ·  Instagram @kiro_seoul";

function crossObjs(cx, cy, s, color, w) {
  return [
    { line: { x: cx - s, y: cy, w: 2 * s, h: 0, line: { color, width: w } } },
    { line: { x: cx, y: cy - s, w: 0, h: 2 * s, line: { color, width: w } } },
  ];
}
function corners(SW, SH, m, s, color, w = 1.25) {
  return [[m, m], [SW - m, m], [m, SH - m], [SW - m, SH - m]].flatMap(([x, y]) => crossObjs(x, y, s, color, w));
}
function logoSlot(x, y, size, color, fs) {
  return [
    { rect: { x, y, w: size, h: size, fill: { type: "none" }, line: { color, width: 1.5 } } },
    { text: { text: "LOGO", options: { x, y, w: size, h: size, align: "center", valign: "middle", fontSize: fs * 0.4, bold: true, color, margin: 0 } } },
    { text: { text: "서울특별시건축사회", options: { x: x + size + 0.12, y, w: 3.2, h: size, valign: "middle", fontSize: fs, bold: true, color, margin: 0 } } },
  ];
}
function badge(slide, x, y, text, fs, fill, color, name) {
  const w = 0.32 + text.length * fs / 72 * 1.05, h = fs / 72 * 1.55;
  slide.addText(text, { x, y, w, h, fontSize: fs, bold: true, color, fill: { color: fill }, align: "center", valign: "middle",
                        margin: 0, isTextBox: true, objectName: name });
  return x + w;
}

// ---------- 16:9 thumbnail ----------
async function build169() {
  const pres = new pptxgen();
  pres.defineLayout({ name: "THUMB_16x9", width: 13.333, height: 7.5 });
  pres.layout = "THUMB_16x9";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "2026 숏폼 영상 공모전 — 썸네일 템플릿";
  const C = pres.SchemeColor;
  pres.defineSlideMaster({
    title: "썸네일 16x9",
    background: { color: "E8E8E6" },
    objects: [
      ...corners(13.333, 7.5, 0.36, 0.15, "224098"),
      { text: { text: "SHORT FORM VIDEO CONTEST", options: { x: 0.73, y: 0.6, w: 5, h: 0.3, fontSize: 13, bold: true, color: "224098", margin: 0 } } },
      // video still frame: put the scene behind/inside this box
      { rect: { x: 6.67, y: 0.73, w: 6.04, h: 6.04, fill: { color: "B8B8B8" }, line: { color: "224098", width: 3 } } },
      { text: { text: "FRAME 01", options: { x: 6.85, y: 0.85, w: 2, h: 0.3, fontSize: 13, bold: true, color: "FFFFFF", margin: 0 } } },
      { text: { text: "영상 대표 장면 넣기", options: { x: 6.67, y: 3.5, w: 6.04, h: 0.5, fontSize: 16, color: "FFFFFF", align: "center", margin: 0 } } },
      ...logoSlot(0.73, 6.33, 0.36, "224098", 19),
    ],
  });
  const s = pres.addSlide({ masterName: "썸네일 16x9" });
  const x = badge(s, 0.73, 1.33, W.award, 34, "224098", "FFFFFF", "수상 등급");
  s.addText(W.contest, { x: x + 0.2, y: 1.33, w: 4, h: 0.73, fontSize: 21, bold: true, color: C.accent1, valign: "middle", margin: 0, isTextBox: true, objectName: "공모전명" });
  s.addText(W.title, { x: 0.73, y: 2.45, w: 5.7, h: 2.6, fontSize: 46, bold: true, color: C.accent1, valign: "top", margin: 0, lineSpacingMultiple: 1.05, fit: "shrink", isTextBox: true, objectName: "작품명" });
  s.addText(W.maker, { x: 0.73, y: 5.25, w: 5.7, h: 0.5, fontSize: 21, bold: true, color: C.accent1, margin: 0, isTextBox: true, objectName: "제작자" });
  s.addNotes("수상 등급, 작품명, 제작자 텍스트만 바꾸면 됩니다. 회색 FRAME 01 상자에 영상 대표 장면을 넣으세요(그림 삽입 후 상자 크기에 맞춰 자르기).");
  await pres.writeFile({ fileName: "공모전_썸네일_16x9.pptx" });
  await applyTheme("공모전_썸네일_16x9.pptx", THEME);
}

// ---------- 9:16 intro + ending ----------
async function build916() {
  const pres = new pptxgen();
  const SW = 7.5, SH = 13.333;
  pres.defineLayout({ name: "SHORTS_9x16", width: SW, height: SH });
  pres.layout = "SHORTS_9x16";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "2026 숏폼 영상 공모전 — 인트로·엔딩 템플릿";
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "인트로 9x16",
    background: { color: "6E6E6E" },   // stands in for the video; delete/replace when compositing
    objects: [
      ...corners(SW, SH, 0.49, 0.18, "FFFFFF", 1.75),
      { text: { text: "REC", options: { x: 5.9, y: 0.68, w: 0.65, h: 0.3, fontSize: 13, bold: true, color: "FFFFFF", align: "right", margin: 0 } } },
      { rect: { x: 0.49, y: 1.25, w: 6.52, h: 3.6, fill: { color: "224098", transparency: 12 }, line: { color: "224098", width: 0 } } },
      ...logoSlot(0.76, 12.1, 0.3, "FFFFFF", 15),
    ],
  });
  pres.defineSlideMaster({
    title: "엔딩 9x16",
    background: { color: "E8E8E6" },
    objects: [
      ...corners(SW, SH, 0.49, 0.18, "224098"),
      { text: { text: "SHORT FORM\nVIDEO CONTEST", options: { x: 0.76, y: 0.76, w: 3, h: 0.6, fontSize: 13, bold: true, color: "224098", margin: 0 } } },
      { text: { text: "ARCHITECTURE\n& ARCHITECT", options: { x: 3.74, y: 0.76, w: 3, h: 0.6, fontSize: 13, bold: true, color: "224098", align: "right", margin: 0 } } },
      { text: { text: "REC", options: { x: 5.9, y: 1.45, w: 0.65, h: 0.3, fontSize: 12, bold: true, color: "224098", align: "right", margin: 0 } } },
      { rect: { x: 0.76, y: 8.6, w: 5.98, h: 1.3, fill: { color: "224098" }, line: { color: "224098", width: 0 } } },
      { text: { text: SLOGAN, options: { x: 0.76, y: 8.6, w: 5.98, h: 1.3, fontSize: 30, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 } } },
      { text: { text: HOST + "\n" + LINKS, options: { x: 0.76, y: 10.95, w: 5.98, h: 0.8, fontSize: 14, color: "224098", margin: 0, lineSpacingMultiple: 1.3 } } },
      ...logoSlot(0.76, 12.0, 0.34, "224098", 17),
    ],
  });

  const a = pres.addSlide({ masterName: "인트로 9x16" });
  a.addShape(pres.shapes.OVAL, { x: 6.62, y: 0.77, w: 0.12, h: 0.12, fill: { color: "E12D2D" }, line: { color: "E12D2D", width: 0 }, objectName: "REC 점" });
  let x = badge(a, 0.76, 1.55, W.award, 24, "FFFFFF", "224098", "수상 등급");
  a.addText(W.contest, { x: x + 0.15, y: 1.55, w: 4, h: 0.52, fontSize: 18, bold: true, color: "FFFFFF", valign: "middle", margin: 0, isTextBox: true, objectName: "공모전명" });
  a.addText(W.title, { x: 0.76, y: 2.3, w: 5.98, h: 1.85, fontSize: 40, bold: true, color: "FFFFFF", valign: "top", margin: 0, lineSpacingMultiple: 1.05, fit: "shrink", isTextBox: true, objectName: "작품명" });
  a.addText(W.maker, { x: 0.76, y: 4.2, w: 5.98, h: 0.45, fontSize: 18, color: "FFFFFF", margin: 0, isTextBox: true, objectName: "제작자" });
  a.addNotes("영상 첫 1~2초에 겹치는 인트로입니다. 회색 배경은 영상 자리 표시이므로, 에펙에서는 배경 없이 위쪽 패널·텍스트·모서리 표시만 사용하세요.");

  const e = pres.addSlide({ masterName: "엔딩 9x16" });
  e.addShape(pres.shapes.OVAL, { x: 6.62, y: 1.54, w: 0.11, h: 0.11, fill: { color: "E12D2D" }, line: { color: "E12D2D", width: 0 }, objectName: "REC 점" });
  x = badge(e, 0.76, 3.25, W.award, 28, "224098", "FFFFFF", "수상 등급");
  e.addText(W.contest, { x: x + 0.18, y: 3.25, w: 4, h: 0.6, fontSize: 20, bold: true, color: C.accent1, valign: "middle", margin: 0, isTextBox: true, objectName: "공모전명" });
  e.addText(W.title, { x: 0.76, y: 4.25, w: 5.98, h: 2.3, fontSize: 44, bold: true, color: C.accent1, valign: "top", margin: 0, lineSpacingMultiple: 1.05, fit: "shrink", isTextBox: true, objectName: "작품명" });
  e.addShape(pres.shapes.LINE, { x: 0.76, y: 6.75, w: 5.98, h: 0, line: { color: "224098", width: 1 }, objectName: "구분선" });
  e.addText([{ text: "제작   ", options: { bold: false } }, { text: W.maker, options: { bold: true } }],
            { x: 0.76, y: 6.95, w: 5.98, h: 0.5, fontSize: 19, color: C.accent1, margin: 0, isTextBox: true, objectName: "제작자" });
  e.addNotes("수상 등급, 작품명, 제작자 텍스트만 바꾸면 됩니다. 슬로건·주관·링크·로고는 레이아웃에 고정돼 있습니다.");

  await pres.writeFile({ fileName: "공모전_인트로_엔딩_9x16.pptx" });
  await applyTheme("공모전_인트로_엔딩_9x16.pptx", THEME);
}

(async () => { await build169(); await build916(); console.log("ok"); })();
