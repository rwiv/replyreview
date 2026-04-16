# Task 3.1: MainWindow 뷰 전환 로직 연동

## Overview

`MainWindow`의 중앙 위젯을 `FileLoadView`로 교체하고, `file_selected` 시그널에 파싱 및 뷰 전환 슬롯을 연결합니다. 파싱 성공 시 `ReviewListView`로 화면이 전환되고, `ParserError` 발생 시 `QMessageBox`로 오류 내용을 안내합니다.

트랙 1.2의 모든 컴포넌트를 통합하는 마지막 Task이며, `gui` 모듈 명세 갱신과 `docs/features.md` 반영으로 마무리합니다.

## Related Files

### Reference Files

- `replyreview/gui/main_window.py`: 현재 `MainWindow` 구현 확인용
- `replyreview/gui/file_load_view.py`: `file_selected` 시그널 인터페이스 파악용
- `replyreview/gui/review_list_view.py`: `ReviewListView` 생성자 파악용
- `replyreview/parser/review_parser.py`: `ReviewParser.parse`, `ParserError` 파악용
- `docs/features.md`: 2.2, 2.3절 동작 요구사항 참조

### Target Files

- `replyreview/gui/main_window.py`: 수정 — 뷰 전환 로직 추가
- `replyreview/gui/README.md`: 수정 — 신규 컴포넌트 및 시그널/슬롯 구조 반영
- `tests/gui/test_main_window.py`: 신규 — `MainWindow` 통합 GUI 테스트
- `docs/features.md`: 수정 — 2.2, 2.3절 구현 완료 반영

## Workflow

### Step 1: MainWindow 뷰 전환 로직 구현

`replyreview/gui/main_window.py`를 수정합니다.

- `_setup_central_widget`에서 기존 placeholder `QLabel`을 제거하고 `FileLoadView`를 초기 중앙 위젯으로 설정합니다.
- `FileLoadView.file_selected` 시그널을 `_on_file_selected` 슬롯에 연결합니다.
- `_on_file_selected`는 `ReviewParser.parse`를 호출합니다. 성공 시 `setCentralWidget`으로 `ReviewListView`를 표시하고, `ParserError` 발생 시 `QMessageBox.warning`으로 오류를 안내합니다.
- `ReviewParser` 인스턴스는 `MainWindow` 생성자에서 초기화하여 보관합니다.

```python
# replyreview/gui/main_window.py (수정 부분)
from PySide6.QtWidgets import QMessageBox

from replyreview.gui.file_load_view import FileLoadView
from replyreview.gui.review_list_view import ReviewListView
from replyreview.parser.review_parser import ParserError, ReviewParser


class MainWindow(QMainWindow):
    # ... 기존 코드 유지

    def __init__(self) -> None:
        super().__init__()
        self._config_manager = ConfigManager()
        self._parser = ReviewParser()
        self._setup_window()
        self._setup_toolbar()
        self._setup_central_widget()

    def _setup_central_widget(self) -> None:
        file_load_view = FileLoadView()
        file_load_view.file_selected.connect(self._on_file_selected)
        self.setCentralWidget(file_load_view)

    @Slot(str)
    def _on_file_selected(self, file_path: str) -> None:
        """
        파일 선택 후 파싱을 시도하고 성공 시 ReviewListView로 화면을 전환한다.
        ParserError 발생 시 QMessageBox로 오류 내용을 안내한다.
        """
        try:
            reviews = self._parser.parse(file_path)
        except ParserError as e:
            QMessageBox.warning(self, "파일 오류", str(e))
            return

        self.setCentralWidget(ReviewListView(reviews))
```

### Step 2: MainWindow 통합 GUI 테스트 작성 및 수행

`tests/gui/test_main_window.py`에 테스트를 작성합니다. `QFileDialog.getOpenFileName`과 `QMessageBox.warning`을 패치하고, `tmp_path`로 임시 CSV 파일을 생성하여 실제 파싱 흐름과 뷰 전환을 검증합니다.

```python
# tests/gui/test_main_window.py
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from replyreview.gui.main_window import MainWindow
from replyreview.gui.review_list_view import ReviewListView


@pytest.fixture
def valid_csv(tmp_path: Path) -> str:
    """유효한 리뷰 데이터가 담긴 임시 CSV 파일 경로를 반환하는 fixture."""
    path = tmp_path / "reviews.csv"
    pd.DataFrame({
        "상품명": ["에어팟 프로 케이스"],
        "고객명": ["김땡땡"],
        "별점": [5],
        "리뷰 내용": ["배송이 빠르고 좋아요!"],
    }).to_csv(path, index=False)
    return str(path)


@pytest.fixture
def window(qtbot: QtBot) -> MainWindow:
    """테스트용 MainWindow 인스턴스를 생성하고 qtbot에 등록하는 fixture."""
    widget = MainWindow()
    qtbot.addWidget(widget)
    return widget


class TestMainWindow:
    """MainWindow의 뷰 전환 로직을 검증하는 통합 테스트 클래스."""

    def test_initial_central_widget_is_file_load_view(self, window: MainWindow) -> None:
        """
        앱 초기 화면의 중앙 위젯이 FileLoadView인지 검증한다.
        """
        # ...

    def test_central_widget_switches_to_review_list_view_on_valid_file(
        self, qtbot: QtBot, window: MainWindow, valid_csv: str
    ) -> None:
        """
        유효한 파일이 선택되면 중앙 위젯이 ReviewListView로 전환되는지 검증한다.
        """
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=(valid_csv, ""),
        ):
            qtbot.mouseClick(window.centralWidget()._load_button, Qt.MouseButton.LeftButton)

        assert isinstance(window.centralWidget(), ReviewListView)

    def test_shows_message_box_on_parser_error(
        self, qtbot: QtBot, window: MainWindow, tmp_path: Path
    ) -> None:
        """
        파싱 오류 발생 시 QMessageBox.warning이 호출되는지 검증한다.
        """
        # 필수 컬럼이 누락된 파일 생성 후 QFileDialog 패치
        # QMessageBox는 main_window.py에서 임포트되므로 패치 경로는
        # "replyreview.gui.main_window.QMessageBox.warning"이어야 한다.
        # ...
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/gui/test_main_window.py
```

### Step 3: `gui` 모듈 명세 갱신

`replyreview/gui/README.md`를 갱신합니다. 아래 항목을 추가해야 합니다.

- **핵심 컴포넌트** 섹션에 신규 컴포넌트 추가:
  - `FileLoadView`: 파일 미로드 상태의 초기 화면. `file_selected = Signal(str)` 시그널로 경로를 emit.
  - `ReviewCardWidget`: 단일 `ReviewData` 카드 렌더링. `_reply_button`은 Track 1.3에서 AI 답글 생성 기능과 연동 예정.
  - `ReviewListView`: `list[ReviewData]`를 받아 스크롤 가능한 카드 목록으로 시각화.
- **시그널/슬롯 연결 구조** 섹션 갱신:
  - `FileLoadView.file_selected` → `MainWindow._on_file_selected` → `ReviewParser.parse` → `setCentralWidget(ReviewListView)` 흐름 기술.

### Step 4: `docs/features.md` 갱신

`docs/features.md` 2.2절(파일 업로드)과 2.3절(리뷰 데이터 조회) 항목에 구현 완료 내용을 반영합니다. 구현 상세 섹션에 파일 경로와 클래스명을 명시합니다.

## Success Criteria

- [x] `uv run pytest tests/gui/test_main_window.py` 테스트가 모두 통과한다.
- [x] `uv run pytest` 전체 테스트가 통과한다.
- [x] `uv run pyright` 타입 체크 오류가 없다.
- [x] `replyreview/gui/README.md`에 `FileLoadView`, `ReviewCardWidget`, `ReviewListView` 컴포넌트와 시그널/슬롯 흐름이 반영되었다.
