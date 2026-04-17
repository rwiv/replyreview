"""리뷰 카드 위젯."""

from typing import Any

from PySide6.QtCore import QThreadPool, QTimer, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from replyreview.ai.client import AIClient
from replyreview.ai.worker import ReplyWorker
from replyreview.models import ReviewData

MAX_RATING = 5
_BUTTON_TEXT_DEFAULT = "답글 생성"
_BUTTON_TEXT_LOADING = "생성 중..."
_ERROR_API_KEY = "API 키 설정에 문제가 있습니다."
_ERROR_GENERAL = "답글 생성 실패. 다시 시도해 주세요."
_COPY_FEEDBACK_DURATION_MS = 1500
_BUTTON_TEXT_COPY = "클립보드 복사"
_BUTTON_TEXT_COPIED = "복사 완료!"


class ReviewCardWidget(QFrame):
    """단일 ReviewData를 카드 형태로 렌더링하는 위젯."""

    def __init__(self, review: ReviewData, ai_client: AIClient, parent=None) -> None:
        super().__init__(parent)
        self._review = review
        self._ai_client = ai_client
        self._worker: Any = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        stars = "★" * self._review.rating + "☆" * (MAX_RATING - self._review.rating)
        self._header_label = QLabel(
            f"{stars} | {self._review.customer_name} | 상품: {self._review.product_name}"
        )
        layout.addWidget(self._header_label)

        self._content_label = QLabel(self._review.content)
        self._content_label.setWordWrap(True)
        layout.addWidget(self._content_label)

        button_row = QHBoxLayout()
        self._reply_button = QPushButton(_BUTTON_TEXT_DEFAULT)
        self._reply_button.clicked.connect(self._on_generate_clicked)
        button_row.addStretch()
        button_row.addWidget(self._reply_button)
        layout.addLayout(button_row)

        self._reply_area = QTextEdit()
        self._reply_area.setReadOnly(True)
        layout.addWidget(self._reply_area)
        self._reply_area.setVisible(False)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setWordWrap(True)
        layout.addWidget(self._error_label)
        self._error_label.setVisible(False)

        self._copy_button = QPushButton(_BUTTON_TEXT_COPY)
        self._copy_button.clicked.connect(self._on_copy_clicked)
        layout.addWidget(self._copy_button)
        self._copy_button.setVisible(False)

    @Slot()
    def _on_generate_clicked(self) -> None:
        self._reply_button.setEnabled(False)
        self._reply_button.setText(_BUTTON_TEXT_LOADING)
        self._error_label.setVisible(False)
        self._reply_area.setVisible(False)

        self._worker = ReplyWorker(client=self._ai_client, review=self._review)
        self._worker.signals.finished.connect(self._on_reply_finished)
        self._worker.signals.auth_error.connect(self._on_reply_auth_error)
        self._worker.signals.error.connect(self._on_reply_error)
        QThreadPool.globalInstance().start(self._worker)

    @Slot(str)
    def _on_reply_finished(self, text: str) -> None:
        self._reply_area.setPlainText(text)
        self._reply_area.setVisible(True)
        self._copy_button.setVisible(True)
        self._restore_button()

    @Slot()
    def _on_reply_auth_error(self) -> None:
        self._error_label.setText(_ERROR_API_KEY)
        self._error_label.show()
        self._restore_button()

    @Slot(str)
    def _on_reply_error(self, message: str) -> None:
        self._error_label.setText(_ERROR_GENERAL)
        self._error_label.show()
        self._restore_button()

    @Slot()
    def _on_copy_clicked(self) -> None:
        QApplication.clipboard().setText(self._reply_area.toPlainText())
        self._copy_button.setText(_BUTTON_TEXT_COPIED)
        QTimer.singleShot(
            _COPY_FEEDBACK_DURATION_MS,
            lambda: self._copy_button.setText(_BUTTON_TEXT_COPY),
        )

    def _restore_button(self) -> None:
        self._reply_button.setEnabled(True)
        self._reply_button.setText(_BUTTON_TEXT_DEFAULT)
