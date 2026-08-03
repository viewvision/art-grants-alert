# 감정의 지층 (Emotional Geology) — 프로젝트 검토 메모

마지막 업데이트: 2026-08-03

## 이 파일의 용도
VIEWVISION STUDIO가 2026 아트코리아랩 AI-예술 창제작 프로젝트(초기형)에 제출한
기획안 "감정의 지층(Emotional Geology)"을 검토하고, 실제 프로토타입 제작을 위한
기술 파이프라인/로드맵을 정리한 기록. `art-grants-alert` 저장소 자체(공모 알림 스크래퍼)와는
별개의 프로젝트이며, 세션이 바뀌어도 대화 맥락을 이어갈 수 있도록 이 파일에 저장해둔다.

**검토 결과 전체(디자인된 버전)**: https://claude.ai/code/artifact/bbd58b6d-cfdf-4108-a2a6-7b106f8e017e

## 프로젝트 개요
- 주관: VIEWVISION STUDIO (2015년 설립, 상주 2인 + 객원 2인)
- 공모: 2026 아트코리아랩 AI-예술 창제작 프로젝트(초기형)
- 시연/전시 장소: 울산 울주군 복합문화공간 미지의(MIGIUI)
- 시연 시점: 2026년 12월
- 예산: 42,000,000원
- 컨셉: 관객의 표정·정서 데이터를 지질학적 데이터로 재해석해 고유한 질감의
  '디지털 암석'으로 변환하고, 시간이 흐르며 공간 전체가 하나의 '디지털 지질층'으로
  축적되는 참여형 생성예술 프로젝트.
- 기획서상 6단계 파이프라인: SCAN → ANALYSE&SKETCH → ARTISTIC FILTERING → CREATING →
  SELF-REFINING → VISUALIZATION&ARCHIVING (A~E 5개 실행 그룹으로 세분화)

## 종합 검토

### 강점
- **일관된 은유 구조**: 개인의 감정 → 디지털 암석 → 공동체 지층이라는 서사가 캡처·
  시각화·아카이빙 전 단계에 끊김 없이 이어짐. 전시 공간 동선(진입로→전시홀→명상공간)도
  이 서사에 맞춰 설계됨.
- **초기형 단계치고 기술 스택이 구체적**: Hume AI, GPT/Gemini, TouchDesigner,
  Stable Diffusion, Houdini, CLIP 기반 검수까지 명시. 이미 "구글 안티그래비티"로
  UI/UX 목업까지 시각화한 상태.
- **거버넌스 선제 대응**: 창작자 60% / AI 40% 기여도 구분, 원본 이미지 실시간 파기,
  인포데스크 사전 동의(초상권) 등 심사에서 자주 지적되는 항목을 먼저 짚음.
- **장소 선정 논리가 탄탄함**: 미지의(MIGIUI)의 '자연·회복·미지의 나' 브랜드 철학과
  프로젝트의 정서적 자기성찰 메시지가 정확히 맞물림.

### 보완이 필요한 지점

**B. 개념 · 알고리즘 (실제 구현을 위해 지금 정의해야 함)**
1. **[핵심] 감정→지질학적 데이터 매핑 공식이 블랙박스** — valence/arousal/감정군이
   색상·질감·밀도·침식 패턴 중 무엇을 어떻게 결정하는지 문서화되어 있지 않음.
   → 매핑 스펙 시트(1장)부터 확정 필요: valence→색온도, arousal→노이즈/침식 스케일,
   감정군→암석 원형(결정질/퇴적/화산암 등) 대응표.
2. **[핵심] Hume 출력값(수십 차원) → 5개 감정 카테고리 축소 로직 미정의** — 데모 UI엔
   Serenity/Sadness/Joy/Anger/Anxiety 5종만 노출됨. 5종 분류 + valence/arousal
   연속값을 함께 쓰는 하이브리드 방식 권장.
3. **[권장] 입력 경로 이원화**(안면 캡처 vs 텍스트 입력) — 9p·24p는 Kinect Azure 안면
   캡처를, 13p 데모 UI는 텍스트 입력+감정 태그 선택을 보여줌. 데모가 엔진 개념증명용
   축약 버전인지, 실제 현장에서도 텍스트 입력을 병행하는지 명시 필요. (명상 공간은
   텍스트/음성 보조 입력, 진입로 캡처는 순수 안면 데이터로 공식화하는 안 제안)

**C. 기술 스택 정확성**
4. **[핵심] "Hume AI EVI" 표기 재확인 필요** — EVI(Empathic Voice Interface)는 음성
   대화형 API로 프로소디 기반 감정 추론에 특화됨. 카메라로 표정을 분석하는 용도라면
   Expression Measurement API(Face 모델) 쪽이 맞을 가능성이 높음. 기술 담당자와
   재확인 필요 — 두 제품은 지연시간·요금·출력 스키마가 다름.
5. **[권장] SD+Houdini+TouchDesigner 통합 방식 미확정** — 본문(17p)은 Houdini 프로시저럴
   3D 지오메트리를 말하지만, 데모(13~16p) 결과물은 평면 카드형 이미지. 프로토타입은
   2D 합성으로 먼저 검증하고, 예산·일정이 허락하면 2차에서 Houdini 3D를 얹는 단계적
   접근 권장.

**D. 실시간성 & 운영 리스크**
6. **[핵심] 전체 체인의 지연시간 예산이 없음** — 캡처→Hume→LLM→SD→CLIP검수→TD 합성까지
   클라우드 API가 최소 3번 이상 직렬로 이어짐. 관객 1인당 체감 대기시간 목표(예: 15초
   이내)를 먼저 정하고, SD는 로컬 GPU(LCM/Turbo류 경량 모델) 추론으로 전환 권장.
7. **[권장] 동시 다수 관람객/대기열 설계 없음** — 24p 다이어그램은 1인 캡처 볼륨만 보여줌.
8. **[권장] 외부 API 장애 시 폴백 없음** — 현장 네트워크 불안정/API 장애 시 전시가 멈출
   위험. 사전 생성된 "대체 암석 세트"를 로컬 캐싱해두고 자동 폴백하는 안전장치 필요.
9. **[참고] 예산·일정 타이트함** — AI 소프트웨어 구독비 100만원이 Hume+LLM+SD API
   누적 사용량 대비 낮아 보임. R&D~구축을 3개월(7~9월)에 몰아둔 일정도 5개 이상 이종
   기술 통합 프로젝트치고 여유가 적음. QR 링크 만료·데이터 보존 기간 정책도 미명시.

## 프로토타입 기술 파이프라인

기획서의 6단계(A~E) 서사 구조는 유지하되, 실제 구현 단위로 쪼갠 아키텍처.

| 단계 | 목적 | 핵심 기술 | 프로토타입에서 먼저 결정할 것 |
|---|---|---|---|
| Stage 0 · Capture | 표정/정서 원시 데이터 획득 | Kinect Azure, OpenCV, TouchDesigner | 안면 캡처 단독 vs 텍스트 입력 병행 여부 |
| Stage 1 · Emotion | 표정 → 정량 감정 지표 | Hume AI Expression API | EVI가 아닌 Expression Measurement API 사용 여부 확정 |
| Mapping · Translation | 감정 지표 → 시각 파라미터 | 자체 매핑 모듈 (Python) | valence/arousal/감정군 → 색·질감·밀도 대응표 확정 |
| Stage 2 · Narrative | 시적 문구 + 이미지 프롬프트 생성 | GPT-4급 / Gemini API | 작가 문체 고정용 시스템 프롬프트 + few-shot 예문 세트 |
| Stage 3 · Visual Gen | 암석 텍스처/지오메트리 생성 | Stable Diffusion, Houdini | 2D 합성 우선 vs 3D 프로시저럴 병행 시점 |
| Stage 4 · Self-Refining | 결과물 미학 기준 자동 검수 | CLIP similarity, VLM 평가 | 기준 임베딩(레퍼런스 이미지 세트), 통과 임계값, 최대 재시도 횟수 |
| Stage 5 · Render/Output | 실시간 합성 → LED 송출 + 개인 배포 | TouchDesigner, Spout/NDI, QR | 동시 다수 세션 처리, LED 상 지층 누적 규칙 |
| Stage 6 · Archive | 개인 데이터의 공동체 지층화 | DB(Postgres/Supabase 등) | 보존 기간, QR 링크 만료 정책, 원본 이미지 미저장 원칙 재확인 |

**오케스트레이션 레이어**: 세션 상태 관리, 타임아웃/재시도, 동시 요청 큐잉, API 장애
폴백을 담당하는 백엔드(예: FastAPI + Redis 큐)를 Kinect/TouchDesigner와 각 AI API
사이에 두는 것을 권장. TouchDesigner 자체 Python/WebSocket으로도 가능하지만, 로직이
커질수록 별도 서비스로 분리하는 편이 디버깅이 쉬움.

## 실행 로드맵

- **Phase 0 · 지금 결정**: Hume 제품(Expression API vs EVI) 확인, 감정→비주얼 매핑
  스펙 시트 1차 초안, 2D 합성 vs 3D 프로시저럴 최종 결과물 형식 확정.
- **Phase 1 · Vertical Slice**: Kinect·TouchDesigner·LED 없이 웹캠 → Hume → 매핑 →
  LLM 프롬프트 → 로컬 SD 이미지까지 관통하는 최소 경로 완성, 실제 지연시간 측정.
- **Phase 2 · Real-time Layer**: Phase 1 파이프라인을 TouchDesigner에 연결(OSC/
  WebSocket), 세로형 LED 목업에서 실시간 합성 확인, QR 배포 흐름 추가.
- **Phase 3 · Refine & Scale**: CLIP 자가검수 루프, Houdini 프로시저럴 지오메트리,
  동시 다수 관람객 큐잉, API 폴백 추가. Kinect Azure 안면 캡처가 웹캠 대체.
- **Phase 4 · Field Test**: 미지의(MIGIUI) 현장에서 실제 조명·네트워크 환경 안정성
  테스트, 아카이빙 시스템(Collective Strata) 검증, 관람 동선과 시스템 반응 속도 매칭.

## 확인이 필요한 질문
1. Hume AI는 정확히 어떤 제품/엔드포인트를 쓰나? (EVI vs Expression Measurement API)
2. 최종 결과물은 2D 합성 이미지인가, 3D 프로시저럴 지오메트리인가?
3. 관객 1인당 허용 가능한 체감 대기시간은 몇 초인가?
4. 진입로 캡처와 명상 공간 텍스트 입력을 모두 쓸 것인가?
5. 감정 데이터·시적 문구·QR 링크의 보존 기간은 얼마로 정할까?
6. 오프닝처럼 관객이 몰리는 시간대엔 어떻게 대응할까? (대기열 UX, 병렬 세션)
