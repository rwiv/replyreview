from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QToolBar

from replyreview.config.config_manager import ConfigManager
from replyreview.gui.settings_dialog import SettingsDialog


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
        self._config_manager = ConfigManager()
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
        # Placeholder: Task 1.2에서 리뷰 카드 리스트 뷰로 교체 예정
        placeholder = QLabel("리뷰 데이터 파일을 불러와 주세요.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)

    @Slot()
    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(config_manager=self._config_manager, parent=self)
        dialog.exec()
