from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
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
        config_manager.set_api_key("sk-existing-key-123")
        dialog = SettingsDialog(config_manager=config_manager)
        qtbot.addWidget(dialog)
        assert dialog._api_key_input.text() == "sk-existing-key-123"

    def test_save_button_persists_api_key(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        키를 입력하고 저장 버튼을 클릭하면 ConfigManager에 키가 저장되는지 검증한다.
        """
        test_key = "sk-new-key-456"
        qtbot.keyClicks(dialog._api_key_input, test_key)
        buttons = dialog.findChildren(QPushButton)
        save_button = next((btn for btn in buttons if btn.text() == "저장"), None)
        assert save_button is not None
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert config_manager.get_api_key() == test_key

    def test_dialog_closes_after_save(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        다이얼로그가 저장 버튼 클릭 후 닫히는지 검증한다.
        """
        dialog.show()
        assert dialog.isVisible()
        qtbot.keyClicks(dialog._api_key_input, "sk-test-key")
        buttons = dialog.findChildren(QPushButton)
        save_button = next((btn for btn in buttons if btn.text() == "저장"), None)
        assert save_button is not None
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        assert not dialog.isVisible()

    def test_save_button_persists_empty_key(
        self, qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
    ) -> None:
        """
        빈 문자열 입력 후 저장 시 ConfigManager에 빈 문자열이 저장되는지 검증한다.
        """
        dialog._api_key_input.clear()
        buttons = dialog.findChildren(QPushButton)
        save_button = next((btn for btn in buttons if btn.text() == "저장"), None)
        assert save_button is not None
        qtbot.mouseClick(save_button, Qt.MouseButton.LeftButton)
        assert config_manager.get_api_key() == ""

    def test_input_field_empty_when_no_key_stored(
        self, qtbot: QtBot, config_manager: ConfigManager
    ) -> None:
        """
        저장된 API 키가 없을 때 다이얼로그를 열면 입력 필드가 비어있는지 검증한다.
        """
        dialog = SettingsDialog(config_manager=config_manager)
        qtbot.addWidget(dialog)
        assert dialog._api_key_input.text() == ""

    def test_api_key_input_uses_password_echo_mode(
        self, dialog: SettingsDialog
    ) -> None:
        """
        API 키 입력 필드에 EchoMode.Password 마스킹이 적용되어 있는지 검증한다.
        """
        from PySide6.QtWidgets import QLineEdit
        assert dialog._api_key_input.echoMode() == QLineEdit.EchoMode.Password
