# Plan: AI 답글 생성 엔진 및 비동기 처리 로직 연동

## Phase 1: AI 클라이언트 추상화 계층 구축

### Task 1.1: AIClient ABC 및 구현체 구현

- [ ] `replyreview/ai/` 패키지 생성 (`__init__.py` 포함)
- [ ] `AIClient` ABC 및 `AIAuthError` 구현 (`replyreview/ai/client.py`)
  - `AIAuthError(Exception)`: 인증 실패를 나타내는 커스텀 예외 정의
  - `AIClient` ABC: `generate_reply(review: ReviewData) -> str` 추상 메서드 정의
- [ ] `FakeAIClient` 구현 (`tests/fakes.py`, 테스트 전용)
  - 고정 더미 텍스트 반환, `raise_error: Exception | None` 옵션으로 오류 시나리오 지원
- [ ] `OpenAIClient` 구현 (`replyreview/ai/openai_client.py`)
  - `api_key: str` 주입받아 LangChain `ChatOpenAI` + `ChatPromptTemplate` 체인 초기화
  - `docs/tech-spec.md` 4.3절 프롬프트 템플릿 적용
  - `openai.AuthenticationError` 발생 시 `AIAuthError`로 변환하여 재발생
- [ ] `tests/ai/` 패키지 생성 (`__init__.py` 포함)
- [ ] `FakeAIClient` 테스트 작성 및 수행 (`tests/ai/test_fake_client.py`)
  - 반환 타입, 고객명 포함 여부, 오류 발생 옵션 검증 (전체 로직 구현)
- [ ] `OpenAIClient` 수동 통합 테스트 작성 (`tests/ai/test_openai_client.py`)
  - `pytest.mark.skip` 적용, 자동 실행 제외 명시
  - 정상 응답 및 인증 오류 발생 시나리오 검증 (전체 로직 구현)

## Phase 2: 비동기 답글 생성 UI 통합

### Task 2.1: ReplyWorker 구현 및 ReviewCardWidget 비동기 연동

- [ ] `ReplyWorker` 구현 (`replyreview/ai/worker.py`)
  - `WorkerSignals(QObject)`: `finished = Signal(str)`, `auth_error = Signal()`, `error = Signal(str)`
  - `ReplyWorker(QRunnable)`: `AIClient`와 `ReviewData`를 받아 백그라운드에서 `generate_reply` 호출
  - `AIAuthError` 발생 시 `auth_error` 시그널, 그 외 예외 시 `error` 시그널 발행
- [ ] `ReviewCardWidget` 개선 (`replyreview/gui/review_card_widget.py`)
  - 생성자에 `ai_client: AIClient` 파라미터 추가 (`self._threadpool` 인스턴스 변수 없이 `QThreadPool.globalInstance()` 직접 호출)
  - `_reply_button` 활성화 및 클릭 시 `_on_generate_clicked` 슬롯 연결
  - `_on_generate_clicked`: 버튼 비활성화/"생성 중...", `ReplyWorker` 생성 후 `QThreadPool.globalInstance()`에 제출
  - `_on_reply_finished(text: str)`: 답글 텍스트 영역 표시 및 버튼 복구
  - `_on_reply_auth_error()`: 빨간색 API 키 오류 메시지 표시 및 버튼 복구
  - `_on_reply_error(message: str)`: 빨간색 일반 오류 메시지 표시 및 버튼 복구
- [ ] `ReviewListView` 수정 (`replyreview/gui/review_list_view.py`)
  - `ai_client: AIClient` 파라미터 추가, 각 `ReviewCardWidget` 생성 시 전달
- [ ] `ReviewCardWidget` 비동기 GUI 테스트 작성 및 수행 (`tests/gui/test_review_card_widget.py`)
  - `FakeAIClient`와 `qtbot.waitUntil`을 사용하여 버튼 상태 전환 및 답글 표시 검증
  - `raise_error` 옵션으로 인증 오류, 일반 오류 시나리오 검증 (전체 로직 구현)

### Task 2.2: 클립보드 복사 + MainWindow AIClient 주입 + 명세 갱신

- [ ] `ReviewCardWidget`에 클립보드 복사 기능 추가 (`replyreview/gui/review_card_widget.py`)
  - 답글 표시 시 '클립보드 복사' 버튼 노출
  - 클릭 시 `QApplication.clipboard().setText()`로 복사
  - `QTimer.singleShot`으로 1.5초 후 버튼 텍스트를 원복
- [ ] `MainWindow` 수정 (`replyreview/gui/main_window.py`)
  - `_on_file_selected`에서 `ConfigManager.get_api_key()`로 키를 읽어 `OpenAIClient` 생성
  - `ReviewListView` 생성 시 `ai_client` 주입 (빈 키 사전 차단 없이, 오류는 카드 레벨에서 처리)
- [ ] 클립보드 복사 GUI 테스트 추가 (`tests/gui/test_review_card_widget.py`)
  - 답글 생성 전 복사 버튼 숨김 여부, 생성 후 노출 여부, 클릭 시 클립보드 내용 검증 (전체 로직 구현)
- [ ] `tests/gui/test_main_window.py` 갱신
  - `ReviewListView` 생성자 시그니처 변경(`ai_client` 추가) 반영
  - `FakeAIClient`를 주입하도록 관련 테스트 수정
- [ ] `docs/features.md` 갱신 (3.4, 3.5절 구현 상세 추가)
- [ ] `docs/tech-spec.md` 갱신 (ai 모듈 디렉터리 구조 반영)
