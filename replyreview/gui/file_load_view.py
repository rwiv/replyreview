from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget

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
        if path:
            self.file_selected.emit(path)
