# Specification: 리뷰 데이터 입력 및 시각화 파이프라인 개발

## Overview

이 트랙은 사용자가 CSV/Excel 형식으로 제공한 네이버 스마트스토어 리뷰 데이터를 앱으로 가져오고, 각 리뷰를 읽기 쉬운 카드 형태로 시각화하는 파이프라인을 완성합니다.

트랙이 완료되면 사용자는 파일을 선택하는 즉시 리뷰 카드 목록으로 화면이 전환됩니다. 각 카드에는 별점·고객명·상품명·리뷰 내용이 표시되며, Track 1.3에서 구현할 AI 답글 생성 버튼의 자리가 마련됩니다.

## Requirements

### 1. 파일 업로드 UI

- `docs/features.md` 2.2절의 파일 업로드 요구사항을 충족한다.
- 데이터가 로드되지 않은 초기 화면 중앙에 안내 문구와 '파일 불러오기' 버튼을 배치한다.
- '파일 불러오기' 클릭 시 `.csv`, `.xlsx` 파일만 선택 가능한 시스템 파일 탐색기를 열고, 선택된 경로를 `file_selected` 시그널로 `MainWindow`에 전달한다.

### 2. 데이터 파싱 시스템

- 선택된 파일을 `ReviewParser`가 파싱하여 `ReviewData` 리스트로 변환한다.
- `ReviewData`는 `product_name`, `customer_name`, `rating`, `content` 4개 필드를 갖는 불변 데이터 클래스(`frozen=True`)이다.
- 파일 확장자에 따라 파싱 방식을 분기한다.
  - `.csv` → `pd.read_csv`
  - `.xlsx` → `pd.read_excel`
- 파싱 대상 컬럼명은 다음과 같이 매핑한다.

  | CSV/Excel 컬럼 | ReviewData 필드 | 타입 |
  | :--- | :--- | :--- |
  | 상품명 | `product_name` | `str` |
  | 고객명 | `customer_name` | `str` |
  | 별점 | `rating` | `int` (정수 변환) |
  | 리뷰 내용 | `content` | `str` |

- 지원하지 않는 파일 확장자 또는 필수 컬럼 누락 시 `ParserError`를 raise한다.

### 3. 리뷰 뷰어 UI (카드 리스트)

- `docs/features.md` 2.3절의 카드 리스트 뷰 요구사항을 충족한다.
- 파싱된 `ReviewData` 리스트를 받아 각 항목을 `ReviewCardWidget`으로 렌더링하는 `ReviewListView`를 구현한다.
- `ReviewCardWidget` 레이아웃:
  - [상단] 별점(★ 문자열), 고객명, 상품명 (예: `★★★★★ | 김땡땡 | 상품: 에어팟 프로 케이스`)
  - [중단] 리뷰 원문 (자동 줄바꿈 처리)
  - [하단] '답글 생성' 버튼 — Track 1.3에서 기능 연동 예정이므로 **비활성화(disabled)** 상태로 배치
- 리뷰 목록은 세로 스크롤이 가능한 `QScrollArea` 내에 표시된다.

### 4. MainWindow 뷰 전환

- 앱 초기 화면은 `FileLoadView`이다.
- 파일 파싱 성공 시 `MainWindow`가 중앙 위젯을 `FileLoadView` → `ReviewListView`로 교체한다.
- `ParserError` 발생 시 `QMessageBox.warning`으로 사용자에게 오류 내용을 안내한다.

## Architecture

```text
replyreview/
├── models.py          # ReviewData frozen dataclass
├── parser/            # 파일 파싱 로직 (Business Logic Layer)
│   └── review_parser.py  # ReviewParser, ParserError
└── gui/               # Presentation Layer
    ├── file_load_view.py     # 파일 선택 초기 화면
    ├── review_card_widget.py # 개별 리뷰 카드 위젯
    ├── review_list_view.py   # 리뷰 카드 목록 컨테이너
    └── main_window.py        # 뷰 전환 로직 추가
```

- **`models.py`**: `ReviewData` frozen dataclass 정의. `gui/`와 `parser/` 양측에서 참조하는 공유 데이터 모델.
- **`parser/ReviewParser`**: pandas를 통해 파일을 읽고 `ReviewData` 리스트를 반환. 파싱 실패 시 `ParserError`를 raise.
- **`gui/FileLoadView`**: 파일 미로드 상태의 초기 화면. `file_selected = Signal(str)` 시그널로 경로를 `MainWindow`에 전달.
- **`gui/ReviewCardWidget`**: 단일 `ReviewData`를 카드 형태로 렌더링. 별점 문자열 변환(`rating → ★` 반복) 포함.
- **`gui/ReviewListView`**: `list[ReviewData]`를 받아 `ReviewCardWidget` 인스턴스를 동적으로 생성하고 `QScrollArea`에 배치.
- **`gui/MainWindow`**: `FileLoadView.file_selected` 시그널에 파싱 및 뷰 전환 슬롯을 연결.

## Directory Structure

트랙 완료 후 생성 또는 수정되는 파일 목록입니다.

```text
replyreview/
├── models.py                        # 신규: ReviewData dataclass
├── parser/
│   ├── __init__.py                  # 신규
│   ├── review_parser.py             # 신규: ReviewParser 클래스, ParserError
│   └── README.md                    # 신규: parser 모듈 명세
└── gui/
    ├── file_load_view.py            # 신규: 파일 선택 초기 화면
    ├── review_card_widget.py        # 신규: 리뷰 카드 위젯
    ├── review_list_view.py          # 신규: 리뷰 리스트 뷰
    ├── main_window.py               # 수정: 뷰 전환 로직 추가
    └── README.md                    # 수정: 신규 컴포넌트 반영

tests/
├── parser/
│   ├── __init__.py                  # 신규
│   └── test_review_parser.py        # 신규: ReviewParser 단위 테스트
└── gui/
    ├── test_file_load_view.py        # 신규: FileLoadView GUI 테스트
    ├── test_review_card_widget.py    # 신규: ReviewCardWidget GUI 테스트
    └── test_main_window.py          # 신규: MainWindow 통합 GUI 테스트
```

## Domain Concepts

- **ReviewData**: 파싱된 단일 리뷰를 나타내는 불변 데이터 클래스. GUI와 파서 계층 모두에서 사용하는 공유 도메인 모델.
- **ReviewParser**: CSV/Excel 파일을 읽어 `ReviewData` 리스트를 반환하는 파서 클래스.
- **ParserError**: 지원하지 않는 파일 형식이거나 필수 컬럼이 누락된 경우 raise되는 커스텀 예외.
- **FileLoadView**: 파일 미로드 상태의 진입 화면. 사용자가 파일을 선택하면 경로를 시그널로 emit.
- **ReviewListView**: 파싱된 `ReviewData` 목록을 스크롤 가능한 카드 뷰로 시각화하는 컨테이너 위젯.
- **ReviewCardWidget**: 단일 `ReviewData`를 카드 형태로 렌더링하는 위젯. Track 1.3에서 답글 생성 기능이 연동되는 확장 지점.

## Testing Strategy

- **ReviewParser**: `pytest`의 `tmp_path` fixture로 임시 CSV/Excel 파일을 생성하여 실제 파일 I/O 기반으로 검증. 정상 파싱, 컬럼 누락, 지원하지 않는 확장자 등 케이스를 포함.
- **FileLoadView**: `unittest.mock.patch`로 `QFileDialog.getOpenFileName`을 교체하여 `file_selected` 시그널 emit 여부를 `qtbot.waitSignal`로 검증. 취소 시(빈 문자열 반환) 시그널이 emit되지 않는 케이스도 검증.
- **ReviewCardWidget**: `pytest-qt`(`qtbot`)로 위젯 인스턴스화 후 별점·고객명·상품명·리뷰 내용 라벨 텍스트와 버튼 비활성화 상태를 검증.
- **MainWindow (통합)**: `QFileDialog.getOpenFileName`과 `QMessageBox.warning`을 패치하고 `tmp_path`로 임시 CSV를 생성하여 뷰 전환 및 오류 안내 흐름을 검증.

## Acceptance Criteria

- [ ] '파일 불러오기' 버튼 클릭 시 `.csv`, `.xlsx` 필터가 적용된 파일 탐색기가 열린다.
- [ ] 유효한 CSV/Excel 파일 선택 시 리뷰 카드 목록으로 화면이 전환된다.
- [ ] 각 카드에 별점(★), 고객명, 상품명, 리뷰 내용이 올바르게 표시된다.
- [ ] 필수 컬럼이 누락된 파일 또는 지원하지 않는 확장자 선택 시 `QMessageBox`로 오류가 안내된다.
- [ ] 모든 테스트(`uv run pytest`)가 통과한다.
- [ ] 타입 체크(`uv run pyright`) 오류가 없다.
