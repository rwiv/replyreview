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
        # Populate the input field with the currently saved API key on open
        self._api_key_input.setText(self._config_manager.get_api_key())

    @Slot()
    def _save_api_key(self) -> None:
        self._config_manager.set_api_key(self._api_key_input.text())
        self.accept()
