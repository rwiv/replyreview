# Task 1.1: QApplication 엔트리포인트 및 MainWindow 구현

## Overview

PySide6 기반의 앱 실행 진입점을 재구성하고, 향후 핵심 UI를 수용할 메인 윈도우(`MainWindow`) 뼈대를 구현합니다. 현재 `__main__.py`의 `print` 스텁을 `QApplication` 생성 및 `MainWindow` 표시 로직으로 교체합니다.

이 Task는 별도의 자동화 테스트 없이 앱 실행 확인으로 검증합니다.

## Related Files

### Reference Files

- `replyreview/__main__.py`: 현재 스텁 구현 확인용
- `docs/tech-spec.md`: 시스템 아키텍처(Presentation Layer 역할) 및 3계층 분리 원칙 참조

### Target Files

- `replyreview/__main__.py`: 수정 — `QApplication` 생성 및 `MainWindow` 실행 로직
- `replyreview/gui/__init__.py`: 신규 — `gui` 패키지 초기화
- `replyreview/gui/main_window.py`: 신규 — `MainWindow` 클래스

## Workflow

### Step 1: `gui/` 패키지 생성

`replyreview/gui/` 디렉터리를 생성하고 빈 `__init__.py`를 추가합니다.

### Step 2: `MainWindow` 클래스 구현

`replyreview/gui/main_window.py` 파일에 `MainWindow` 클래스를 구현합니다.

- `QMainWindow`를 상속하며, 윈도우 제목과 기본 크기를 설정합니다.
- 중앙 컨텐츠 영역(`setCentralWidget`)에 플레이스홀더 `QLabel`을 배치합니다. 이 영역은 Track 1.2에서 리뷰 카드 리스트 뷰로 교체됩니다.
- 상단 툴바에 '설정' 버튼을 배치합니다. 클릭 시 호출할 `_open_settings_dialog` 슬롯은 Task 2.2에서 구현되므로 현재는 빈 메서드로 유지합니다.

```python
# replyreview/gui/main_window.py
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QToolBar


class MainWindow(QMainWindow):
    """
    ReplyReview 앱의 루트 윈도우.
    핵심 기능 UI를 수용하는 컨테이너 역할을 하며, 상단 툴바를 통해 설정 다이얼로그에 진입할 수 있다.
    """

    WINDOW_TITLE = "ReplyReview"
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600

    def __init__(self) -> None:
        super().__init__()
        self._setup_window()
        self._setup_toolbar()
        self._setup_central_widget()

    def _setup_window(self) -> None:
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("메인 툴바")
        self.addToolBar(toolbar)

        settings_button = QPushButton("설정")
        settings_button.clicked.connect(self._open_settings_dialog)
        toolbar.addWidget(settings_button)

    def _setup_central_widget(self) -> None:
        # TODO: 리뷰 카드 리스트 뷰로 교체 예정
        placeholder = QLabel("리뷰 데이터 파일을 불러와 주세요.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)

    @Slot()
    def _open_settings_dialog(self) -> None:
        # TODO: SettingsDialog 연동 로직으로 교체 예정
        pass
```

### Step 3: `__main__.py` 수정

기존 `print` 스텁을 제거하고 `QApplication` 및 `MainWindow` 실행 로직으로 교체합니다.

```python
# replyreview/__main__.py
import sys

from PySide6.QtWidgets import QApplication

from replyreview.gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### Step 4: 앱 실행 확인

아래 명령으로 앱을 실행하여 메인 윈도우가 정상 표시되는지 직접 확인합니다.

```bash
uv run python -m replyreview
```

확인 항목:
- 윈도우 제목이 "ReplyReview"로 표시된다.
- 중앙에 "리뷰 데이터 파일을 불러와 주세요." 텍스트가 표시된다.
- 상단 툴바에 '설정' 버튼이 표시된다. (클릭 시 아무 동작 없음은 정상)

## Success Criteria

- [ ] `uv run python -m replyreview` 실행 시 메인 윈도우가 정상적으로 표시된다.
- [ ] `uv run pyright` 타입 체크 오류가 없다.

