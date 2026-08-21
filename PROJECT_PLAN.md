# 공모/지원사업 알림 시스템 — 기획 메모

마지막 업데이트: 2026-07-31

## 현재 상태: 구현 완료, 운영 중 (2026-07-31 이메일 발송/대시보드 실제 테스트 완료)
- 대시보드 URL: https://viewvision.github.io/art-grants-alert/
- 매일 07:00 KST GitHub Actions 자동 실행, 새 글 있을 때만 mojok2200@gmail.com으로 이메일 발송

11개 사이트 스크래퍼 + 필터링 + 이메일 + 대시보드 + GitHub Actions 자동화까지 전부 구현되어 저장소에 커밋/푸시됨.
그 중 7개 사이트는 GitHub Actions(해외 서버)에서 정상 작동 확인, 4개는 해외 IP 차단으로 실패 중 (아래 "알려진 제약사항" 참고).
코드 구조: `main.py`(오케스트레이션) → `scraper/sites/*.py`(사이트별 수집) → `scraper/filters.py`(키워드+지역 필터) →
`scraper/state.py`(신규글 diff) → `scraper/email_sender.py` / `scraper/dashboard.py`.

## 알려진 제약사항
- **해외 IP 차단**: GitHub Actions(미국 등 해외 리전)에서 실행 시 아래 사이트들이 실패함 (로컬 한국 IP에서는 정상 동작 확인됨)
  - 아트누리, 국가문화예술지원시스템: Connection refused (해외 IP 차단 확실 — 코드로 해결 불가, 한국 IP 우회 인프라 필요)
  - 가상융합기술 Campus: SSL 인증서 검증 오류 — **원인 확인 완료(2026-08-21)**: 서버가 체인에서 중간 인증서(RapidSSL TLS RSA CA G1)를 빠뜨리고 보냄(IP 차단 아님). `.github/workflows/daily.yml`에 GitHub Actions 실행 시 이 중간 인증서를 받아와 CA 번들에 추가하는 단계 추가 — 다음 실행에서 해결 여부 확인 필요
  - 위비티: 403 Forbidden — 브라우저 User-Agent/Accept-Language/Referer 헤더 보강 + 세션 쿠키 확보 시도(2026-08-21)했으나 여전히 차단됨. 단순 헤더 체크가 아니라 더 강한 봇 차단(WAF/IP 평판 등)으로 추정, 추가 조치 불명
  - 2026-07-31 사용자 결정: 일단 나머지 7개 사이트만 자동화하고 이 4개는 보류. 각 사이트 실패해도 나머지는 정상 진행됨(try/except 처리됨).
- 매일 실행 시 새 글이 없으면 이메일 발송 안 함(스팸 방지 의도적 설계)

## 목표
아래 사이트(공모/지원사업/예술 관련 플랫폼)를 매일 일일이 방문하지 않고,
새 공고가 올라오면 이메일로 알림을 받고, 어디서든 웹페이지로 모아서 볼 수 있게 만든다.

## 대상 사이트 (확정 — 사용자가 "일단 이게 전부"라고 확인함, 2026-07-31)
1. 아르코 통합플랫폼 — 공모·소식 — https://thearts.arko.or.kr/thearts/news/contest
2. 한국문화예술위원회 — 전시·행사·공연·교육 > 교육 — https://arko.or.kr/infra/exevshedBoard/list?category=education
3. e나라도움 — https://www.bojo.go.kr/bojo.do
4. 아트누리 — https://artnuri.or.kr/
5. 아트코리아랩 — https://www.artskorealab.kr/bbs/list.do?key=2303300002
6. 국가문화예술지원시스템 — https://www.ncas.or.kr/
7. 가상융합기술 Campus — https://www.metaverse-campus.kr/index.do
8. 아트스푼 — 공모전 지원 — https://artspoon.io/ko/contest
9. 아트모아 — https://www.artmore.kr/main/main.do
10. 아트센터 나비미술관 — https://www.nabi.or.kr/page/academy/academy.php
11. 위비티(Wevity) — https://www.wevity.com/
12. 예술경영지원센터 — https://www.gokams.or.kr/01_news/notice_list.aspx (2026-07-31 추가)
13. 가상융합기술 Campus (제작역량강화 교육과정) — https://www.metaverse-campus.kr/lecture/listAll.do?menu_idx=50&lecIdx=17 (2026-07-31 추가, 같은 사이트의 다른 메뉴 3개: 기업수요 프로젝트/해외선진기술/생성형AI 교육도 있으나 미추가)
14. 위비티 (영상/UCC/사진 카테고리) — https://www.wevity.com/?c=find&s=1&gub=1&cidx=10 (2026-07-31 추가)
15. 국립아시아문화전당재단(ACCF) — 공연 및 행사 > 기획 행사 — https://www.accf.or.kr/main/event/other (2026-08-11 추가, 백엔드 API `main/api/v1/product/list?category=16&status=진행중` 직접 호출)
16. 광주미디어아트플랫폼(G.MAP) — 공지사항 — https://gmap.gwangju.go.kr/bbs/board.php?bo_table=notice (2026-08-11 추가, 그누보드5 정적 HTML)

### 보류(URL 미제공, 이번 범위에서 제외 — 나중에 URL 주시면 추가 가능)
- 예술인경력정보시스템
- 예술인패스
- 예술경영지원센터
- 아트스푼 — 작가에게 새로운 기회가 열리는 아트스푼 (8번과 동일 사이트일 가능성 높음, 별도 URL 없으면 생략)
- 기업마당
- 2026년 혁신 소상공인 AI 활용 지원사업 모집공고
- 소상공인24 메인

### 사이트별 기술 조사 메모 (구현 완료, `scraper/sites/*.py` 참고)
- 대부분 정적 HTML을 requests+BeautifulSoup으로 파싱
- **아트스푼**: Next.js SPA지만 리스트가 백엔드 API(`api-rakama.artra.gallery:8882/contest/public`)를 직접 호출해서 가져옴 — Playwright 불필요
- **e나라도움(bojo.go.kr)**: 홈페이지 위젯 데이터 API(`/aa/getAA001000DataSet.do`)를 POST로 직접 호출 — Playwright 불필요
- **나비미술관**: `/proc/board_list.php` JSON API 사용
- **국립아시아문화전당재단(ACCF)**: Vue/JS로 목록을 렌더링하지만 `/main/api/v1/product/list` JSON API를 직접 호출해서 가져옴 — Playwright 불필요. 이 환경에서는 accf.or.kr 도메인이 네트워크 정책상 차단돼 있어 직접 테스트는 못 했고, 사용자가 브라우저 개발자도구로 캡처해준 API 응답으로 파싱 로직만 검증함(GitHub Actions 실행 시 실제 동작 확인 필요)
- 최종적으로 15개 사이트 전부 Playwright 없이(requests만으로) 구현됨

## 확정된 설계 결정

### 1. 수집 (Scraper)
- 사이트별로 목록 페이지를 긁어 제목/링크/날짜 추출
- 정적 HTML은 requests/BeautifulSoup(또는 Node 동급), JS 렌더링 사이트는 Playwright 필요할 수 있음
- 이전 스크래핑 결과와 비교해 "새 글"만 추출 (diff 방식)

### 2. 스케줄링
- **GitHub Actions cron**으로 매일 1회 자동 실행 (서버 상시 구동 불필요, 무료)
- 확인 주기: 하루 1회

### 3. 알림
- **이메일 발송** (Gmail 앱 비밀번호 방식 사용, mojok2200@gmail.com)
- 외부 이메일 API(Resend 등)는 사용하지 않기로 함 — Gmail 앱 비밀번호가 더 간단해서 선택
- **이메일 형식**: HTML 메일. 제목/링크/날짜는 항상 표시. 사이트에 포스터·썸네일 이미지가 있으면 함께 표시, 없으면 텍스트만 (사이트별로 혼합 형태가 됨 — 예: 아트스푼/위비티는 이미지 가능성 높음, 아트코리아랩/e나라도움 등은 보통 텍스트만)

### 4. 웹 대시보드
- **무료 정적 웹사이트** (GitHub Pages)로 배포
- 실행할 때마다 최신 데이터로 자동 갱신
- 대화나 특정 컴퓨터와 무관하게 어디서든 URL로 접속 가능

### 5. 필터링
- **키워드 포함/제외 방식** 채택 (AI 판단 방식 대신)
- 설정 파일(JSON 등)로 관리 → 사용자가 언제든 직접 키워드 추가/삭제 가능
- **관심 유형(카테고리)** — 알림 받고 싶은 정보의 종류: 공모전, 지원사업, 교육프로그램, 세미나, 워크샵 (이 자체는 텍스트 매칭용 키워드가 아니라, "어떤 종류의 글을 원하는지"를 나타내는 카테고리)
- **주제 키워드(포함, 텍스트 매칭용)**: 예술, 미디어아트, 디지털아트, 비디오아트, ai생성예술, ai, 영화제, 공모전, 지원사업 (2026-08-03 추가), 프로젝션 맵핑, 예술기술 융합, ai예술, 창제작, 인터렉티브, 프롬프트 (2026-08-04 추가)
- **알려진 데이터 갭**: 아트코리아랩 "2026 아트코리아랩 AI 프로젝트 지원" 공지(2026-06-02)가 `data/state.json`에 없음 — 키워드 필터 문제가 아니라 스크래퍼 수집 범위(페이지네이션 등) 밖에 있었던 것으로 추정. 원인 조사 필요 (2026-08-04 발견)
- 제외 키워드: 아직 미정
- **지역 필터**: 서울/경기 지역 공고만 포함
  - 규칙: 제목/본문에 "서울" 또는 "경기"가 언급되면 포함. 지역 언급이 전혀 없는 "전국 대상" 공고는 포함(제외하지 않음). 다른 특정 지역(부산, 대구 등)만 명시적으로 언급된 공고는 제외
  - 즉, "전국 대상 또는 서울/경기 포함"이 포함 조건, "다른 지역 단독 명시"가 제외 조건

### 6. GitHub 설정
- 사용자는 기존 GitHub 계정 보유
- 리포지토리 이름: 미정 (예시: `art-grants-alert`)
- 공개/비공개 여부: 미정 — public이면 GitHub Pages 무료 배포가 더 간단, private도 가능하나 설정 다름

## 다음에 필요한 입력 (사용자가 전달 예정)
- [x] 사이트 URL 11개 확정 (2026-07-31)
- [ ] 필터링에 쓸 포함/제외 키워드 및 관심 분야 (포함 키워드 1차 수집됨, 논의 진행 중)
- [x] GitHub 리포지토리 이름 확정 (`art-grants-alert`)
- [x] 리포지토리 공개/비공개 여부 확정 (public)

## 참고: 이 파일의 용도
이 메모는 Claude Code와의 대화가 로컬 세션이라 다른 컴퓨터로 자동 이어지지 않는 문제를 보완하기 위해 작성됨.
이 프로젝트 폴더를 GitHub에 올리면, 다른 컴퓨터에서 리포지토리를 열거나 클론해서
이 파일만 봐도(또는 Claude Code에게 "PROJECT_PLAN.md 읽고 이어서 진행해줘"라고 하면)
지금까지의 맥락을 그대로 이어갈 수 있음.
