from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPushButton, QToolBar

from replyreview.ai.openai_client import OpenAIClient
from replyreview.config.config_manager import ConfigManager
from replyreview.gui.file_load_view import FileLoadView
from replyreview.gui.review_list_view import ReviewListView
from replyreview.gui.settings_dialog import SettingsDialog
from replyreview.parser.review_parser import ParserError, ReviewParser


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
        self._parser = ReviewParser()
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
        file_load_view = FileLoadView()
        file_load_view.file_selected.connect(self._on_file_selected)
        self.setCentralWidget(file_load_view)

    @Slot(str)
    def _on_file_selected(self, file_path: str) -> None:
        """
        파일 선택 후 파싱을 시도하고 성공 시 ReviewListView로 화면을 전환한다.
        ParserError 발생 시 QMessageBox로 오류 내용을 안내한다.
        API 키 오류는 파일 로드 단계에서 차단하지 않고, 답글 생성 시 카드 레벨에서 처리한다.
        """
        try:
            reviews = self._parser.parse(file_path)
        except ParserError as e:
            QMessageBox.warning(self, "파일 오류", str(e))
            return

        api_key = self._config_manager.get_api_key()
        ai_client = OpenAIClient(api_key=api_key)
        self.setCentralWidget(ReviewListView(reviews=reviews, ai_client=ai_client))

    @Slot()
    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(config_manager=self._config_manager, parent=self)
        dialog.exec()
