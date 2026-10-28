# 원 모어 / 카운팅 — 프로젝트 컨텍스트 (Claude Code가 매 세션 자동으로 읽는 파일)

나는 박선호. 폰 카메라로 운동 횟수를 세는 웹앱을 Claude와 함께 만들어 왔고, 이제부터 이 저장소 작업을 여기서 이어간다. 아래는 지금까지의 전체 맥락이다.

## 0. 작업 규칙 (항상 지킬 것)
- 배포되는 앱을 수정한 뒤에는 **항상** 접속 링크를 답변에 포함한다.
- 수정이 끝나면 **실제로 완료됐는지 확인한 뒤** 답한다: (1) 테스트 통과, (2) 커밋이 origin에 올라갔는지 (`git ls-remote`), (3) GitHub Pages 배포가 success인지 (`gh run list --limit 1`).
- 배포 루틴: `cp index.html 404.html && cp counting/index.html counting/404.html` → 커밋 → `git push origin main && git push -f origin main:gh-pages` (gh-pages는 main을 강제 푸시한 복사본).
- 커밋 전에 `APP_VERSION` 문자열을 올린다 (예: `2026-10-14a`, `counting-2026-10-14a`, `review-2026-10-28a`). 리뷰는 `cp review/index.html review/404.html`도 배포 루틴에 포함. 설정 화면 하단에 표시되어 폰에서 최신 여부를 확인한다.
- 답변은 한국어, 짧고 결론부터.

## 1. 저장소 · 배포
- GitHub: `tjsgh03123-lgtm/spot-checkers` (main = 소스, gh-pages = 배포, `assets` 브랜치 = MediaPipe 모델 사본, `ci-logs` 브랜치 = 안드로이드 빌드 로그, `wip/person-lock` = 미배포 작업).
- 웹 (GitHub Pages):
  - 원 모어 (풀 버전): https://tjsgh03123-lgtm.github.io/spot-checkers/
  - 카운팅 (단순 버전): https://tjsgh03123-lgtm.github.io/spot-checkers/counting/
  - 리뷰 (운동 후 영상 분석, 2026-10-28 신설): https://tjsgh03123-lgtm.github.io/spot-checkers/review/
- 둘 다 **HTML 한 파일짜리 PWA** (`index.html`, `counting/index.html`), 서버 없음, 모든 처리·저장은 폰 로컬(localStorage). `manifest.json`, `sw.js`(네트워크 우선 셸, 모델·wasm은 캐시 우선), `icons/`, `404.html`(index 복사본, SPA 라우팅용), `.nojekyll`, `privacy.html`.
- 안드로이드: Bubblewrap TWA를 GitHub Actions(`.github/workflows/android.yml`, matrix onemore/counting, max-parallel 1)로 빌드. 릴리스 태그 `android-latest`(패키지 `app.onemore.counter`), `android-counting-latest`(`app.onemore.counting`). 키스토어 `android.keystore`는 저장소에 커밋됨(비밀번호 `onemore-keystore`). `.well-known/assetlinks.json`은 워크플로가 두 패키지 모두 자동 생성. `twa-manifest.json`, `twa-manifest-counting.json`의 `appVersionCode`는 스토어 업데이트마다 올려야 함. `STORE_LISTING.md`에 플레이스토어 등록 문구·데이터 안전 답변 정리됨.

## 2. 두 앱의 역할
### 원 모어 (One More) — `index.html`
- 풀 기능: 근육/관절 칩 선택, 촬영 방향(정면/후면/측면), 등 운동 상대 지표(BACK_THR), 측면 지표(허리 기울기·상체 말림·상체-허벅지 각, SIDE_THR), 실시간 게이지, 무게 입력, "실패까지" 토글, 노력도(속도 저하 VL → RIR 추정) 타일, 동선 재생(영상 위 관절·궤적, 렙 단위 이동), 진단 JSON 내보내기, 설정(카메라, 음성, 모델 정밀/빠름, 화면 맞춤, 박수).
- `const LITE = false;` 플래그로 고급 UI를 가릴 수 있음.
- 노력도: VL = 1 − v/v_best (v = ROM/구심 시간; 구심 = 컬·풀다운·로우는 down 구간, 나머지 up). 밴드 `EFFORT.bands lower [15,25,40] / upper [20,30,45]`, 라벨 여유/중간/높음/실패 근접, 개인 보정 `cal_<exercise>` (실패까지 한 세트로 RIR~VL 선형회귀).
### 카운팅 — `counting/index.html` (플레이스토어 1차 출시 대상)
- **횟수만** 센다. 설정 = 운동 이름(선택), 무게(선택), 쉬는 시간, 목표 횟수, 목표 세트. 운동 시작 → 카메라 → **동작 자동 인식** → 카운트 → 목표 도달 시 휴식 카운트다운 → 다음 세트 → 요약/기록(횟수만, 궤적·강도·시간 없음).
- 슈퍼세트 기능은 넣었다가 **삭제함**(2026-10-14). 운동 하나만.
- 운동 이름은 관절 힌트로만 사용: 스쿼트·런지·레그·데드·힙… → 무릎/엉덩이 체인만, 컬·프레스·푸시·로우·풀·레이즈·플라이·딥… → 팔꿈치/어깨만 (`HINT` 정규식). 비우면 전체 후보.
- localStorage 키는 `ct_` 접두사. 설정 화면에서 전신 스켈레톤을 항상 그리되 잘린 관절은 빼고 보이는 부분만.

### 리뷰 — `review/index.html` (트래킹 원리 전환의 주 무대)
- 실시간이 아니라 **운동 후 영상**에 관절을 직접 찍어 추적. 흐름: 영상 선택 → 프레임 추출(시킹, 15/30 fps, MediaPipe IMAGE 모드 프레임별 사람 검출 + 384px 그레이 프레임 메모리 보관 ≤150 MB) → 관절 찍기(자동 랜드마크 탭 선택 / 빈 곳 탭 → 이름 붙인 수동 점, 프리셋 체인 칩, 점 3개로 각도) → 추적 → 결과(횟수·렙당 시간·ROM, 각도 그래프, 영상 위 점·궤적 재생, 신뢰도 타임라인) → 점 끌어 고치면 키프레임 → 구간 재추적 → IndexedDB 저장(`rv` DB, 영상 blob 포함) / 진단 JSON.
- 엔진: 자동 점 = 프레임별 MediaPipe(가시성 <0.5 구간 보간). 수동 점 = 피라미드 Lucas-Kanade(3단, 창 15×15, 전후 검사) + 몸통(어깨·골반 4점) 유사변환 앵커로 드리프트 억제, 키프레임 사이 양방향 추적을 신뢰도 가중 보간. 스무딩은 zero-phase(median3 + gaussian). 렙은 `RepCounter`(카운팅과 동일 규칙)에 각도 시계열 전체 입력, 임계값 = 5~95% 범위에서 up = hi−0.15·range, down = lo+0.3·range.
- 테스트 훅: `window.__RV_CFG = { delegate:"CPU", vision:"/mp/wasm", models:{...} }`(샌드박스 GPU가 느려서), `window.__rv`(S, flowStep, trackAll…), `window.__rv_setS`. 합성 이동 프레임에서 LK 오차 <0.1 px 확인. 번들 크로미움은 h264 미지원 → 테스트 클립은 webm.
- 아직 실제 운동 영상으로 검증 전(사용자 영상 대기).

## 3. 트래킹 엔진 (두 앱 공통 개념, 수치는 각 파일 상단 상수)
- MediaPipe Tasks Vision 0.10.14 Pose Landmarker (Lite/Full 선택, 기본 Full, GPU→CPU 폴백). VIDEO 모드 numPoses 2 + IMAGE 모드 폴백 랜드마커로 사람 재탐지. 얼굴 관절은 쓰지 않음.
- 사람 잠금(`pickPerson`): 헬스장에 여러 명 있을 때 가장 큰 사람에 잠금 후 중심점 근접 추적 (카운팅엔 적용됨, 원 모어는 `wip/person-lock` 브랜치에만 있고 미배포 — 검증 전까지 보류하라는 지시).
- 관절 스무딩: One-Euro 필터 `SMOOTH = { minCutoff 0.6, beta 25, dCutoff 3, deadband 0.002, holdMs 500, predictMs 90, jumpRate 4, jumpFrames 2 }` + 뼈 길이 가드 `BONE = { minFrac 0.5, maxFrac 1.6, learn 0.05, seedFrames 10, holdMaxMs 250 }` (중앙값 시드, 0.7–1.3 범위에서만 학습). 표시 시 속도×90 ms 예측.
- 렙 상태머신 `RepCounter`: 히스테리시스 up/down, 시간 기반 디바운스(원 모어 65 ms/3프레임, 카운팅 40 ms/2프레임), 꼭대기 턴어라운드 `TURN = { frac 0.6, drop 12 }`, 각도 슬루 제한 1500°/s, 부분 렙은 깊은 구간 ≥300 ms, 속도 기반 구간 분리, 렙당 ROM.
- 카운팅의 동작 인식 `detectMovement`: 후보 체인 = 팔꿈치(11-13-15 / 12-14-16), 무릎(23-25-27 / 24-26-28), 엉덩이(11-23-25 / 12-24-26), 어깨(23-11-13 / 24-12-14). `DETECT = { windowMs 8000, minSwing 60, minVis 0.6, edge 0.03, bandFrac 0.3, upFrac 0.1, downFrac 0.3, edgeFrac 0.15, dipMs 120 }`. 세 관절이 모두 프레임 안쪽(가장자리 3% 제외)이고 가시성 ≥0.6, 창이 꼭대기에서 시작·끝나고(완전한 1회), 내려감/올라감 구간이 각각 ≥120 ms(순간 튐 배제). 잠금 후엔 렙마다 `adapt()`로 범위를 갱신. 잘못 잠근 경우(4초간 0회) 다른 체인에서 2회가 분명하면 교체. 2세트부터는 1세트의 관절·임계값 재사용. 휴식 중 동작 1회면 다음 세트 조기 시작.
- 원 모어 시작 로직: 선택 관절이 3초 보이면 시작(`START_DELAY_MS`), 카운트다운·준비자세 없음.
- 카메라: 4:3 960×1280 요청, 줌 최소, object-fit contain 기본. 재생은 영상을 캔버스에 같은 변환으로 그림(`cam {w,h}` 저장, 방향 바뀌면 회전).

## 4. 검증 도구 (이전 세션의 스크래치패드에 있었음 — 저장소엔 없으니 필요하면 다시 만들 것)
- 진단 JSON(원 모어 내보내기): frames = `[t, angle, xy×TRACK, side, angle_raw, min_vis, state]`, TRACK v2 = 19관절. 실제 덤벨컬 세트 5개(d1–d5, 정답 10/7/12/11/14 — d2는 파일상 6이나 실제 7, d5는 파일상 17이나 실제 14)로 카운터를 회귀 테스트했음. 현재 통과값 **10/7/12/11/14**. 이 값이 바뀌면 회귀.
- Node 시뮬레이터: `index.html`의 `<script type="module">`에서 `function jointAngle` ~ `// ---------- workout ----------` 구간을 `new Function`으로 떼어 `RepCounter`, `detectMovement`를 꺼내 쓰는 방식.
- Playwright(크로미움)로 설정/기록 화면 스크린샷, 가짜 포즈 33점으로 `beginWorkout/step`을 돌리는 상태머신 테스트(window.__t로 노출한 복사본 사용).
- 사용자가 보낸 폰 화면 녹화(mp4)는 ffmpeg로 1–2 fps 타일 이미지로 만들어 확인.

## 5. 우선순위와 결정 사항 (사용자 지시)
1. 횟수 카운트 + 렙당 시간이 핵심 소구점. 트래킹 정확도가 최우선, 단관절 팔운동(덤벨컬)을 먼저 완벽히 한 뒤 다른 관절로 확장.
2. 얼굴 관절 불필요. 척추 굴곡·골반·견갑 움직임 추적은 원하지만 MediaPipe 33점으로는 불가 → 메시 모델 또는 본인 영상으로 라벨링한 보조 모델 학습이 필요(사용자 영상 대기: 몸에 붙는 옷, 후면/측면 45°, 혼자).
3. 피드백·경고·기준 랩·10초 대기 기능은 삭제됨. 운동 전 무게 입력 가능.
4. 라이선스: MediaPipe·MMPose(Apache) OK, YOLO(AGPL) 제외, SMPL은 비상업.
5. 샌드박스 제약: raw.githubusercontent, storage.googleapis, YouTube 접근 불가였음 → 모델은 Actions로 `assets` 브랜치에 저장. YouTube 다운로드는 약관 때문에 거절.

## 6. 미해결 · 다음 할 일
- 카운팅: 카메라가 가까워 무릎·골반이 화면 가장자리에 걸릴 때 오인식하던 문제를 2026-10-14에 수정(이름 힌트 + 엄격한 인식). 실제 헬스장 재검증 필요. 폰을 1 m쯤 더 뒤로 두는 게 권장.
- 원 모어 `wip/person-lock` 브랜치를 검증 후 main에 합칠지 결정.
- 플레이스토어: 개발자 계정 만들고 `counting.aab` 업로드, `STORE_LISTING.md` 사용, 업데이트 때마다 `appVersionCode` 증가.
- 소개 슬라이드(11장) 아티팩트 있음: https://claude.ai/artifact/V9Qmpa1KkTBBAjovcZzQRv

## 7. 세션 시작 시
1. `index.html`과 `counting/index.html`의 `APP_VERSION`과 상단 상수를 확인하고 현재 버전을 한 줄로 알려줄 것.
2. 그 다음 사용자가 지시하는 수정부터 진행.
