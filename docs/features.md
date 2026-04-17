# 기능 명세서 (Functional Specification)

본 문서는 '네이버 스마트스토어 리뷰 AI 답글 생성기(ReplyReview)' 애플리케이션의 핵심 기능, 워크플로우, 사용자 스토리 및 UI/UX 요구사항을 정의합니다.

## 1. 주요 기능 개요

본 애플리케이션은 사용자가 엑셀/CSV 형식의 리뷰 데이터를 불러오면, 각 리뷰 내역을 리스트업하고 선택한 리뷰에 대해 AI가 적절한 답글을 생성해주는 기능을 수행합니다. 주요 기능은 다음과 같습니다.

1.  **설정 관리 (API 키 등록)**
2.  **파일 업로드 (단일 파일 선택)**
3.  **리뷰 데이터 조회 (카드 리스트 뷰)**
4.  **AI 답글 생성 (비동기 처리)**
5.  **결과물 클립보드 복사**

## 2. 제약 사항 및 고려 대상

- 디자인의 톤앤매너는 모던하고 깔끔해야 하며, 여백(Padding, Margin)을 적절히 주어 답답하지 않도록 구성해야 합니다.
- 고정된 프롬프트를 사용하되, 답글은 반드시 '친절하고 전문적인 쇼핑몰 고객센터 직원 톤'으로 설정되어야 합니다.

## 3. 기능별 상세 명세

### 3.1. 설정 관리 (OpenAI API 키 설정)

#### 기능 상세

- **UI 요구사항**:
  - 메인 화면 상단 또는 별도의 설정 팝업(Dialog) 창에 API 키를 입력할 수 있는 텍스트 필드(`QLineEdit`)와 '저장' 버튼 제공.
  - 보안을 위해 API 키 입력 시 텍스트가 마스킹(비밀번호 형태, `echoMode: Password`)되어야 함.
- **기능 동작**:
  - 앱 최초 실행 시 로컬의 `config.json`을 검사하여 키가 있다면 자동으로 불러옴.
  - 키가 없거나 잘못된 키로 인해 API 통신 실패 시, 사용자에게 키 설정이 필요함을 UI에 안내.
  - 사용자가 키를 입력하고 '저장'을 누르면 `config.json` 파일에 즉시 기록 및 갱신.

#### 구현 상세

- **메인 윈도우**: `replyreview/gui/main_window.py`의 `MainWindow` 클래스 상단 툴바에 '설정' 버튼 배치
- **설정 다이얼로그**: `replyreview/gui/settings_dialog.py`의 `SettingsDialog` 클래스로 API 키 입력 UI 제공
- **설정 관리**: `replyreview/config/config_manager.py`의 `ConfigManager` 클래스가 `config.json` 읽기/쓰기 담당
- **테스트**:
  - `tests/config/test_config_manager.py`: ConfigManager 통합 테스트
  - `tests/gui/test_settings_dialog.py`: SettingsDialog GUI 테스트 (pytest-qt 사용)

### 3.2. 파일 업로드 (단일 파일 선택)

#### 기능 상세

- **UI 요구사항**:
  - 데이터가 로드되지 않은 초기 화면 중앙에 "리뷰 데이터 파일(CSV/Excel)을 선택하세요" 라는 안내 문구와 함께 눈에 띄는 '파일 불러오기' 버튼(`QPushButton`) 배치.
- **기능 동작**:
  - '파일 불러오기' 버튼 클릭 시 시스템 파일 탐색기(`QFileDialog`) 오픈.
  - 확장자 필터를 통해 `.csv`, `.xlsx` 파일만 선택 가능하도록 제한.
  - 한 번에 하나의 파일만 선택 및 로드 가능 (단일 파일 처리).
  - 파일 로드 성공 시 파싱 로직을 거쳐 메인 리스트 뷰로 화면 전환.

#### 구현 상세

- **파일 선택 UI**: `replyreview/gui/file_load_view.py`의 `FileLoadView` 클래스
  - `file_selected = Signal(str)` 시그널로 선택된 파일 경로를 `MainWindow`에 전달
  - `QFileDialog.getOpenFileName`으로 `.csv`, `.xlsx` 필터 적용
  - 취소 시 아무 동작 없음
- **메인 윈도우 통합**: `replyreview/gui/main_window.py`의 `MainWindow._on_file_selected`
  - `ReviewParser.parse`로 파일 파싱
  - 성공 시 `ReviewListView`로 뷰 전환
  - `ParserError` 발생 시 `QMessageBox.warning`으로 오류 안내
- **테스트**: `tests/gui/test_file_load_view.py`, `tests/gui/test_main_window.py`

### 3.3. 리뷰 데이터 조회 (카드 리스트 뷰)

#### 기능 상세

- **UI 요구사항**:
  - 각 리뷰 데이터는 세로로 스크롤 가능한 `QListWidget`(또는 `QScrollArea`) 내에 **커스텀 카드 위젯**으로 렌더링됨.
  - **카드 레이아웃**:
    - [상단]: 별점(★ 개수로 표시) 및 고객명, 상품명 (예: `★★★★★ | 김땡땡 | 상품: 에어팟 프로 케이스`)
    - [중단]: 리뷰 원문 텍스트 (텍스트가 길 경우 자동 줄바꿈 처리)
    - [하단]: '답글 생성' 버튼 (버튼 우측 또는 하단에 답글 표시 영역 확보)
- **기능 동작**:
  - 파싱된 데이터 행(Row) 개수만큼 카드를 동적으로 생성하여 리스트에 추가.

#### 구현 상세

- **리뷰 카드 위젯**: `replyreview/gui/review_card_widget.py`의 `ReviewCardWidget` 클래스
  - `QFrame` 상속으로 카드 경계 시각화
  - 별점: `rating` 값만큼 ★을 표시하고 나머지를 ☆으로 채움 (예: rating=3 → `★★★☆☆`)
  - 고객명, 상품명, 리뷰 원문 렌더링
  - '답글 생성' 버튼 현재 비활성화 상태 (Track 1.3에서 활성화 예정)
- **리뷰 리스트 뷰**: `replyreview/gui/review_list_view.py`의 `ReviewListView` 클래스
  - `QScrollArea` 기반으로 세로 스크롤 기능 제공
  - `list[ReviewData]`를 받아 각 항목을 `ReviewCardWidget`으로 동적 생성
  - 내부 컨테이너의 `QVBoxLayout`으로 카드를 순서대로 배치
- **테스트**: `tests/gui/test_review_card_widget.py`

### 3.4. AI 답글 생성

#### 기능 상세

- **UI 요구사항**:
  - 사용자가 카드의 '답글 생성' 버튼을 클릭하면 버튼 텍스트가 "생성 중..."으로 변경.
  - 로딩 중에는 해당 버튼이 비활성화(Disabled)되어 중복 클릭 방지.
  - 답글 생성이 완료되면 버튼 아래(또는 지정된 영역)에 생성된 텍스트 출력 영역(`QTextEdit` 또는 `QLabel`)이 나타남.
- **기능 동작**:
  - 백그라운드 스레드(비동기)에서 LangChain을 호출하여 답글 요청.
  - 성공 시 텍스트 영역에 결과를 출력하고, "생성 중..." 버튼을 원래 텍스트로 복구하며 비활성화 해제.
  - **예외 처리 정책**:
    - API 키 미설정/유효하지 않음: 텍스트 영역에 빨간색 글씨로 "API 키 설정에 문제가 있습니다." 표시.
    - 네트워크 오류/Rate Limit 등: 텍스트 영역에 원인과 함께 "답글 생성 실패. 다시 시도해 주세요." 표시.

#### 구현 상세

- **AI 클라이언트 추상화**: `replyreview/ai/client.py`의 `AIClient` ABC와 `AIAuthError` 정의
  - `AIClient`는 `generate_reply(review: ReviewData) -> str` 추상 메서드 정의
  - `AIAuthError`는 OpenAI 인증 실패를 나타내는 커스텀 예외
- **OpenAI 클라이언트**: `replyreview/ai/openai_client.py`의 `OpenAIClient`
  - LangChain `ChatOpenAI` 사용, `ChatPromptTemplate`으로 프롬프트 구성
  - `docs/tech-spec.md` 4.3절의 System Message / Human Message 템플릿 적용
  - `openai.AuthenticationError` 발생 시 `AIAuthError`로 변환
- **비동기 워커**: `replyreview/ai/worker.py`의 `ReplyWorker` 및 `WorkerSignals`
  - `QRunnable` 기반으로 백그라운드 스레드에서 `AIClient.generate_reply` 호출
  - `WorkerSignals`는 `finished(str)`, `auth_error()`, `error(str)` 세 신호 제공
  - `AIAuthError` 발생 시 `auth_error` 신호, 기타 예외 시 `error` 신호 발행
- **리뷰 카드 위젯 개선**: `replyreview/gui/review_card_widget.py`의 `ReviewCardWidget`
  - 생성자에 `ai_client: AIClient` 파라미터 추가
  - `_on_generate_clicked`: 버튼 비활성화/"생성 중..." 텍스트로 변경, `ReplyWorker` 생성 후 `QThreadPool.globalInstance()`에 제출
  - `_on_reply_finished`: 생성된 텍스트를 `QTextEdit` 영역에 표시, 버튼 복구, 클립보드 복사 버튼 노출
  - `_on_reply_auth_error`: API 키 오류 메시지를 빨간색으로 표시, 버튼 복구
  - `_on_reply_error`: 일반 오류 메시지를 빨간색으로 표시, 버튼 복구
- **리뷰 리스트 뷰**: `replyreview/gui/review_list_view.py`의 `ReviewListView`
  - `ai_client: AIClient` 파라미터 추가, 각 `ReviewCardWidget` 생성 시 전달
- **메인 윈도우**: `replyreview/gui/main_window.py`의 `MainWindow`
  - `_on_file_selected`에서 `ConfigManager.get_api_key()`로 API 키 읽음
  - `OpenAIClient` 생성 후 `ReviewListView`에 주입
  - API 키 공백은 파일 로드 단계에서 차단하지 않으며, 답글 생성 시 카드 레벨에서 처리
- **테스트**:
  - `tests/ai/test_fake_client.py`: `FakeAIClient` 동작 검증
  - `tests/ai/test_openai_client.py`: `OpenAIClient` 수동 통합 테스트 (자동 실행 제외)
  - `tests/gui/test_review_card_widget.py`: 버튼 상태 전환, 답글 표시, 오류 처리 검증
  - `tests/gui/test_main_window.py`: `OpenAIClient` 의존성 패치로 `ReviewListView` 전환 검증

### 3.5. 결과물 클립보드 복사

#### 기능 상세

- **UI 요구사항**:
  - AI 답글이 화면에 표시된 후, 텍스트 영역 우측 하단이나 근처에 '클립보드 복사' 버튼 노출.
- **기능 동작**:
  - 해당 버튼 클릭 시, 시스템 클립보드에 생성된 텍스트 전체를 복사.
  - 복사가 완료되면 버튼 텍스트가 일시적으로 "복사 완료!" 등으로 변경되거나, 간단한 토스트 메시지/상태바(StatusBar) 알림을 통해 시각적 피드백 제공.

#### 구현 상세

- **클립보드 복사 버튼**: `replyreview/gui/review_card_widget.py`의 `ReviewCardWidget`
  - `_copy_button` (`QPushButton`)은 초기에 숨겨짐 (`setVisible(False)`)
  - 답글 생성 완료 시 `_on_reply_finished`에서 버튼 노출 (`setVisible(True)`)
  - 버튼 클릭 시 `_on_copy_clicked` 슬롯 실행
- **복사 동작**: `_on_copy_clicked` 슬롯
  - `QApplication.clipboard().setText()`으로 텍스트를 시스템 클립보드에 복사
  - 버튼 텍스트를 "복사 완료!"로 변경
  - `QTimer.singleShot(_COPY_FEEDBACK_DURATION_MS)`로 1.5초 후 원래 텍스트 복구
- **테스트**:
  - `tests/gui/test_review_card_widget.py`: 클립보드 복사 버튼 표시 여부, 복사 동작, 클립보드 내용 검증

