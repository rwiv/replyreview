# Plan: 리뷰 데이터 입력 및 시각화 파이프라인 개발

## Phase 1: 데이터 모델 및 파싱 시스템 구현

### Task 1.1: ReviewData 모델 및 ReviewParser 구현

- [x] `replyreview/models.py` 생성: `ReviewData` frozen dataclass 정의
  - 필드: `product_name: str`, `customer_name: str`, `rating: int`, `content: str`
- [x] `replyreview/parser/` 패키지 생성 (`__init__.py` 포함)
- [x] `ReviewParser` 클래스 및 `ParserError` 구현 (`replyreview/parser/review_parser.py`)
  - `parse(file_path: str) -> list[ReviewData]`: 확장자 분기 후 pandas로 파싱
  - `.csv` → `pd.read_csv`, `.xlsx` → `pd.read_excel`
  - 지원하지 않는 확장자 또는 필수 컬럼(상품명, 고객명, 별점, 리뷰 내용) 누락 시 `ParserError` raise
  - `rating` 컬럼을 `int`로 변환
- [x] `tests/parser/` 패키지 생성 (`__init__.py` 포함)
- [x] `ReviewParser` 테스트 작성 및 수행 (`tests/parser/test_review_parser.py`)
  - `tmp_path` fixture로 임시 CSV 파일 생성 후 정상 파싱 검증
  - `tmp_path` fixture로 임시 Excel 파일 생성 후 정상 파싱 검증
  - 지원하지 않는 확장자(`.txt` 등) 입력 시 `ParserError` 발생 검증
  - 필수 컬럼 누락 파일 입력 시 `ParserError` 발생 검증
  - `rating` 필드가 `int` 타입으로 반환되는지 검증
- [x] `parser` 모듈 명세 작성 (`replyreview/parser/README.md`)
  - 모듈 역할, `ReviewParser` 책임, `ParserError` 정책, 지원 컬럼 매핑 기술
- [x] 관련 문서 갱신 (`docs/tech-spec.md` — 데이터 모델 구현 경로 명시)

## Phase 2: 리뷰 뷰어 UI 구현

### Task 2.1: FileLoadView 구현

- [x] `FileLoadView` 위젯 구현 (`replyreview/gui/file_load_view.py`)
  - `QWidget` 상속, 안내 문구(`QLabel`)와 '파일 불러오기' 버튼(`QPushButton`) 중앙 배치
  - `file_selected = Signal(str)` 시그널 정의
  - '파일 불러오기' 클릭 시 `QFileDialog.getOpenFileName`으로 `.csv`, `.xlsx` 필터 적용
  - 파일 선택 시 `file_selected` 시그널에 경로 emit; 취소 시 아무 동작 없음
- [x] `FileLoadView` GUI 테스트 작성 및 수행 (`tests/gui/test_file_load_view.py`)
  - `QFileDialog.getOpenFileName` 패치 후 버튼 클릭 시 `file_selected` 시그널 emit 검증
  - 취소(빈 문자열 반환) 시 시그널 미emit 검증

### Task 2.2: ReviewCardWidget 및 ReviewListView 구현

- [x] `ReviewCardWidget` 구현 (`replyreview/gui/review_card_widget.py`)
  - `QFrame` 상속, `ReviewData`를 생성자 인자로 받아 렌더링
  - [상단] 별점(`rating` → `★` 반복 문자열), 고객명, 상품명 라벨
  - [중단] 리뷰 원문 라벨 (자동 줄바꿈: `setWordWrap(True)`)
  - [하단] '답글 생성' 버튼 (`setEnabled(False)` — Track 1.3 연동 예정)
- [x] `ReviewListView` 구현 (`replyreview/gui/review_list_view.py`)
  - `QScrollArea` 기반, `list[ReviewData]`를 받아 `ReviewCardWidget` 목록을 동적 생성
  - 내부 컨테이너 위젯에 `QVBoxLayout`으로 카드 순서대로 배치
- [x] `ReviewCardWidget` GUI 테스트 작성 및 수행 (`tests/gui/test_review_card_widget.py`)
  - `qtbot`으로 위젯 인스턴스화 후 각 라벨 텍스트 렌더링 결과 검증
  - 별점 `★` 문자열, 고객명, 상품명 표시 검증
  - 리뷰 원문 텍스트 표시 검증
  - '답글 생성' 버튼이 `isEnabled() == False`인지 검증

## Phase 3: MainWindow 연동

### Task 3.1: MainWindow 뷰 전환 로직 연동

- [x] `MainWindow._setup_central_widget()` 수정: placeholder `QLabel` → `FileLoadView`로 교체
- [x] `FileLoadView.file_selected` 시그널에 `_on_file_selected(path: str)` 슬롯 연결
  - 파싱 성공: `setCentralWidget(ReviewListView(reviews))`
  - `ParserError` 발생: `QMessageBox.warning`으로 오류 메시지 표시
- [x] `MainWindow` 통합 GUI 테스트 작성 및 수행 (`tests/gui/test_main_window.py`)
  - 초기 중앙 위젯이 `FileLoadView`인지 검증
  - 유효한 파일 선택 시 중앙 위젯이 `ReviewListView`로 전환되는지 검증
  - `ParserError` 발생 시 `QMessageBox.warning` 호출 검증
- [x] `gui` 모듈 명세 갱신 (`replyreview/gui/README.md`)
  - `FileLoadView`, `ReviewCardWidget`, `ReviewListView` 컴포넌트 책임 및 시그널/슬롯 연결 구조 추가
- [x] 관련 문서 갱신 (`docs/features.md` — 2.2, 2.3절 구현 완료 여부 반영)
