# Task 2.1: FileLoadView 구현

## Overview

파일이 로드되지 않은 초기 상태에서 표시되는 `FileLoadView` 위젯을 구현합니다. 사용자가 '파일 불러오기' 버튼을 클릭하면 `.csv`/`.xlsx` 필터가 적용된 시스템 파일 탐색기를 열고, 파일 선택 시 경로를 `file_selected` 시그널로 emit합니다.

`QFileDialog.getOpenFileName`은 정적 메서드이므로 `unittest.mock.patch`로 교체하여 자동화 테스트로 검증합니다.

## Related Files

### Reference Files

- `docs/features.md`: 2.2절 파일 업로드 UI/UX 요구사항 참조
- `replyreview/gui/main_window.py`: `MainWindow` 구조 및 `setCentralWidget` 패턴 파악용

### Target Files

- `replyreview/gui/file_load_view.py`: 신규 — `FileLoadView` 위젯
- `tests/gui/test_file_load_view.py`: 신규 — `FileLoadView` GUI 테스트

## Workflow

### Step 1: FileLoadView 구현

`replyreview/gui/file_load_view.py`에 `FileLoadView` 클래스를 구현합니다.

- `file_selected = Signal(str)` 시그널을 정의합니다. 이 시그널은 Task 3.1에서 `MainWindow`가 구독하여 파싱 및 뷰 전환을 처리합니다.
- 안내 문구(`QLabel`)와 '파일 불러오기' 버튼(`QPushButton`)을 중앙 정렬로 배치합니다.
- `_open_file_dialog`에서 `QFileDialog.getOpenFileName`을 사용합니다. 사용자가 다이얼로그를 취소하면 반환된 경로가 빈 문자열이므로, 이 경우 시그널을 emit하지 않습니다.

```python
# replyreview/gui/file_load_view.py
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget

# 파일 탐색기에 표시되는 필터 문자열
FILE_FILTER = "데이터 파일 (*.csv *.xlsx)"


class FileLoadView(QWidget):
    """
    파일 미로드 상태의 초기 진입 화면.
    사용자가 파일을 선택하면 file_selected 시그널에 파일 경로를 emit한다.
    """

    file_selected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        guide_label = QLabel("리뷰 데이터 파일(CSV/Excel)을 선택하세요")
        guide_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(guide_label)

        self._load_button = QPushButton("파일 불러오기")
        self._load_button.clicked.connect(self._open_file_dialog)
        layout.addWidget(self._load_button, alignment=Qt.AlignmentFlag.AlignCenter)

    @Slot()
    def _open_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "리뷰 데이터 파일 선택",
            "",
            FILE_FILTER,
        )
        # 사용자가 취소하면 path가 빈 문자열이므로 시그널을 emit하지 않음
        if path:
            self.file_selected.emit(path)
```

### Step 2: FileLoadView GUI 테스트 작성 및 수행

`tests/gui/test_file_load_view.py`에 테스트를 작성합니다. `QFileDialog.getOpenFileName`을 패치하여 실제 다이얼로그 없이 시그널 emit 동작을 검증합니다.

```python
# tests/gui/test_file_load_view.py
from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from replyreview.gui.file_load_view import FileLoadView


@pytest.fixture
def view(qtbot: QtBot) -> FileLoadView:
    """테스트용 FileLoadView 인스턴스를 생성하고 qtbot에 등록하는 fixture."""
    widget = FileLoadView()
    qtbot.addWidget(widget)
    return widget


class TestFileLoadView:
    """FileLoadView의 렌더링 및 시그널 emit 동작을 검증하는 테스트 클래스."""

    def test_file_selected_emitted_with_path(self, qtbot: QtBot, view: FileLoadView) -> None:
        """
        파일을 선택하면 file_selected 시그널에 선택된 경로가 emit되는지 검증한다.
        """
        fake_path = "/fake/reviews.csv"
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=(fake_path, ""),
        ):
            with qtbot.waitSignal(view.file_selected) as blocker:
                qtbot.mouseClick(view._load_button, Qt.MouseButton.LeftButton)

        assert blocker.args == [fake_path]

    def test_file_selected_not_emitted_on_cancel(self, qtbot: QtBot, view: FileLoadView) -> None:
        """
        파일 탐색기를 취소하면(빈 문자열 반환) file_selected 시그널이 emit되지 않는지 검증한다.
        """
        # qtbot.assertNotEmitted 컨텍스트 매니저로 시그널 미emit를 검증한다.
        # ...

    def test_guide_label_text(self, view: FileLoadView) -> None:
        """
        안내 문구가 올바르게 표시되는지 검증한다.
        """
        # ...
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/gui/test_file_load_view.py
```

## Success Criteria

- [x] `uv run pytest tests/gui/test_file_load_view.py` 테스트가 모두 통과한다.
- [x] 파일 선택 시 `file_selected` 시그널에 올바른 경로가 emit된다.
- [x] 취소 시 `file_selected` 시그널이 emit되지 않는다.
- [x] `uv run pyright` 타입 체크 오류가 없다.
