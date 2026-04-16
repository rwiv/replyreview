# Task 2.2: API 키 설정 Dialog UI 구현

## Overview

OpenAI API 키를 입력받고 저장하는 `SettingsDialog`를 구현하고, `MainWindow`의 '설정' 버튼에 연동합니다. `SettingsDialog`는 열릴 때 `ConfigManager`에서 기존 키를 자동 로드하고, 저장 버튼 클릭 시 즉시 `config.json`에 기록합니다. `pytest-qt`를 사용하여 사용자 인터랙션 흐름을 자동화 테스트로 검증하고, `gui` 모듈 명세 문서를 완성합니다.

## Related Files

### Reference Files

- `replyreview/gui/main_window.py`: `_open_settings_dialog` 슬롯 연동 위치 확인용
- `replyreview/config/config_manager.py`: `ConfigManager` 인터페이스 파악용
- `replyreview/config/README.md`: config 모듈 역할 및 사용법 참조
- `docs/features.md`: 2.1절 설정 관리 UI/UX 요구사항 참조

### Target Files

- `replyreview/gui/settings_dialog.py`: 신규 — `SettingsDialog` 클래스
- `replyreview/gui/main_window.py`: 수정 — `_open_settings_dialog` 슬롯 구현, `ConfigManager` 주입
- `replyreview/gui/README.md`: 신규 — `gui` 모듈 명세
- `tests/gui/__init__.py`: 신규 — 테스트 패키지 초기화
- `tests/gui/test_settings_dialog.py`: 신규 — `SettingsDialog` GUI 테스트
- `docs/features.md`: 수정 — 2.1절 설정 관리 구현 완료 반영

## Workflow

### Step 1: `SettingsDialog` 클래스 구현

`replyreview/gui/settings_dialog.py` 파일에 `SettingsDialog` 클래스를 구현합니다.

- `QDialog`를 상속하며, 생성자에서 `ConfigManager` 인스턴스를 주입받습니다. 이는 테스트 시 임시 경로로 초기화된 `ConfigManager`를 주입할 수 있도록 하기 위함입니다.
- API 키 입력 필드(`QLineEdit`)는 `EchoMode.Password`를 적용하여 마스킹합니다.
- `_load_api_key()`는 생성자에서 호출되어 기존 키를 입력 필드에 채웁니다.
- '저장' 버튼 클릭 시 `_save_api_key()`를 호출하며, 저장 후 `self.accept()`로 다이얼로그를 닫습니다.

```python
# replyreview/gui/settings_dialog.py
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from replyreview.config.config_manager import ConfigManager


class SettingsDialog(QDialog):
    """
    OpenAI API 키를 입력받고 저장하는 설정 다이얼로그.
    열릴 때 ConfigManager에서 기존 API 키를 자동으로 로드한다.
    """

    MIN_WIDTH = 400

    def __init__(self, config_manager: ConfigManager, parent=None) -> None:
        """
        config_manager를 주입받아 API 키 로드·저장을 위임한다.
        테스트 시 임시 경로로 초기화된 ConfigManager를 주입하여 실제 파일과 격리할 수 있다.
        """
        super().__init__(parent)
        self._config_manager = config_manager
        self._setup_ui()
        self._load_api_key()

    def _setup_ui(self) -> None:
        self.setWindowTitle("설정")
        self.setMinimumWidth(self.MIN_WIDTH)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("OpenAI API 키"))

        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.setPlaceholderText("sk-...")
        layout.addWidget(self._api_key_input)

        button_layout = QHBoxLayout()
        save_button = QPushButton("저장")
        save_button.clicked.connect(self._save_api_key)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)

    def _load_api_key(self) -> None:
        self._api_key_input.setText(self._config_manager.get_api_key())

    @Slot()
    def _save_api_key(self) -> None:
        self._config_manager.set_api_key(self._api_key_input.text())
        self.accept()
```

### Step 2: `MainWindow`에 `SettingsDialog` 연동

`replyreview/gui/main_window.py`를 수정하여 `_open_settings_dialog` 슬롯을 구현합니다.

- `MainWindow` 생성자에서 `ConfigManager`를 초기화하고 인스턴스 변수로 보관합니다. `SettingsDialog`는 이 인스턴스를 재사용합니다.
- `_open_settings_dialog`는 `SettingsDialog`를 모달(`exec()`)로 실행합니다.

```python
# replyreview/gui/main_window.py (수정 부분)
from replyreview.config.config_manager import ConfigManager
from replyreview.gui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    # ... 기존 코드 유지

    def __init__(self) -> None:
        super().__init__()
        self._config_manager = ConfigManager()
        self._setup_window()
        self._setup_toolbar()
        self._setup_central_widget()

    @Slot()
    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(config_manager=self._config_manager, parent=self)
        dialog.exec()
```

### Step 3: `SettingsDialog` GUI 테스트 작성 및 수행

`tests/gui/test_settings_dialog.py` 파일에 `qtbot` fixture를 사용한 GUI 테스트를 작성합니다. `ConfigManager`는 `tmp_path`로 초기화하여 실제 `config.json`과 격리합니다.

```python
# tests/gui/test_settings_dialog.py
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from replyreview.config.config_manager import ConfigManager
from replyreview.gui.settings_dialog import SettingsDialog


@pytest.fixture
def config_manager(tmp_path: Path) -> ConfigManager:
    """테스트용 임시 경로로 초기화된 ConfigManager를 반환하는 fixture."""
    return ConfigManager(config_path=tmp_path / "config.json")


@pytest.fixture
def dialog(qtbot: QtBot, config_manager: ConfigManager) -> SettingsDialog:
    """테스트용 SettingsDialog 인스턴스를 생성하고 qtbot에 등록하는 fixture."""
    widget = SettingsDialog(config_manager=config_manager)
    qtbot.addWidget(widget)
    return widget


class TestSettingsDialog:
    """SettingsDialog의 UI 렌더링 및 사용자 인터랙션 흐름을 검증하는 테스트 클래스."""

    def test_loads_existing_api_key_on_open(
        self, qtbot: QtBot, config_manager: ConfigManager
    ) -> None:
        """
        다이얼로그가 열릴 때 ConfigManager에 저장된 기존 API 키가 입력 필드에 자동으로 로드되는지 검증한다.
        """
        # ...

    def test_save_button_persists_api_key(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        키를 입력하고 저장 버튼을 클릭하면 ConfigManager에 키가 저장되는지 검증한다.
        """
        # ...

    def test_dialog_closes_after_save(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        다이얼로그가 저장 버튼 클릭 후 닫히는지 검증한다.
        """
        # ...

    def test_save_button_persists_empty_key(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        빈 문자열 입력 후 저장 시 ConfigManager에 빈 문자열이 저장되는지 검증한다.
        """
        # ...

    def test_input_field_empty_when_no_key_stored(
        self, qtbot: QtBot, config_manager: ConfigManager
    ) -> None:
        """
        저장된 API 키가 없을 때 다이얼로그를 열면 입력 필드가 비어있는지 검증한다.
        """
        # ...

    def test_api_key_input_uses_password_echo_mode(
        self, dialog: SettingsDialog
    ) -> None:
        """
        API 키 입력 필드에 EchoMode.Password 마스킹이 적용되어 있는지 검증한다.
        """
        # ...
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/gui/
```

### Step 4: `gui` 모듈 명세 작성

`replyreview/gui/README.md` 파일에 모듈 명세를 작성합니다. 아래 항목을 포함해야 합니다.

- **모듈 역할**: Presentation Layer로서 UI 렌더링 및 사용자 이벤트 처리만 담당하며, 비즈니스 로직을 포함하지 않는 설계 원칙 기술.
- **핵심 컴포넌트**:
  - `MainWindow`: 앱 루트 윈도우 역할, 생성자에서 `ConfigManager`를 소유하여 하위 다이얼로그에 주입하는 구조 기술.
  - `SettingsDialog`: API 키 입력 UI 역할, 생성자 파라미터(`config_manager`, `parent`) 기술.
- **시그널/슬롯 연결 구조**: `MainWindow._setup_toolbar()` → `settings_button.clicked` → `_open_settings_dialog` → `SettingsDialog.exec()` 흐름 기술.
- **테스트**: `tests/gui/test_settings_dialog.py` 경로 및 `pytest-qt`(`qtbot`)를 활용한 GUI 테스트 전략 기술.

### Step 5: `docs/features.md` 갱신

`docs/features.md` 2.1절 설정 관리 항목에 구현 완료 내용을 반영합니다. 추가적으로 달라진 내용이 있다면 명세를 갱신합니다.

## Success Criteria

- [ ] `uv run pytest tests/gui/` 테스트가 모두 통과한다.
- [ ] `uv run pyright` 타입 체크 오류가 없다.
- [ ] 메인 윈도우에서 '설정' 버튼 클릭 시 설정 다이얼로그가 모달로 열린다.
- [ ] 설정 다이얼로그에서 API 키 입력 후 저장 시 `config.json`에 기록되고, 앱 재실행 시 동일한 키가 다이얼로그에 자동 로드된다.
- [ ] `replyreview/gui/README.md`가 모듈 역할, 핵심 컴포넌트, 시그널/슬롯 구조, 테스트 전략을 포함하여 작성되었다.

