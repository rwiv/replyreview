from pathlib import Path

import pytest
from PySide6.QtCore import Qt
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
    def test_loads_existing_api_key_on_open(
        self, qtbot: QtBot, config_manager: ConfigManager
    ) -> None:
        """
        다이얼로그가 열릴 때 ConfigManager에 저장된 기존 API 키가 입력 필드에 자동으로 로드되는지 검증한다.
        """
        # Pre-populate the config with an API key
        config_manager.set_api_key("sk-existing-key-123")

        # Create a new dialog and verify the key is loaded
        dialog = SettingsDialog(config_manager=config_manager)
        qtbot.addWidget(dialog)

        assert dialog._api_key_input.text() == "sk-existing-key-123"

    def test_save_button_persists_api_key(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        키를 입력하고 저장 버튼을 클릭하면 ConfigManager에 키가 저장되는지 검증한다.
        """
        # Type a new API key in the input field
        test_key = "sk-new-key-456"
        qtbot.keyClicks(dialog._api_key_input, test_key)

        # Find and click the save button
        save_button = None
        for widget in dialog.findChildren(type(dialog)):
            pass
        # Alternative: search by button text
        from PySide6.QtWidgets import QPushButton

        buttons = dialog.findChildren(QPushButton)
        save_button = next((btn for btn in buttons if btn.text() == "저장"), None)
        assert save_button is not None

        # Simulate button click
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # Verify the key was saved
        assert config_manager.get_api_key() == test_key

    def test_dialog_closes_after_save(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        다이얼로그가 저장 버튼 클릭 후 닫히는지 검증한다.
        """
        # Initially, the dialog should not be visible when created
        # (We need to show it first to test closing)
        dialog.show()
        assert dialog.isVisible()

        # Type a test key
        qtbot.keyClicks(dialog._api_key_input, "sk-test-key")

        # Find and click the save button
        from PySide6.QtWidgets import QPushButton

        buttons = dialog.findChildren(QPushButton)
        save_button = next((btn for btn in buttons if btn.text() == "저장"), None)
        assert save_button is not None

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # Use QTest.qWait to allow signals to be processed
        qtbot.wait(100)

        # Dialog should be hidden/closed (accepted)
        assert not dialog.isVisible()

    def test_save_button_persists_empty_key(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        빈 문자열 입력 후 저장 시 ConfigManager에 빈 문자열이 저장되는지 검증한다.
        """
        # Clear the input field
        dialog._api_key_input.clear()

        # Find and click the save button
        from PySide6.QtWidgets import QPushButton

        buttons = dialog.findChildren(QPushButton)
        save_button = next((btn for btn in buttons if btn.text() == "저장"), None)
        assert save_button is not None

        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)

        # Verify empty key was saved
        assert config_manager.get_api_key() == ""
