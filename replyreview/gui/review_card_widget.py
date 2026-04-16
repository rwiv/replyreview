from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from replyreview.models import ReviewData

MAX_RATING = 5


class ReviewCardWidget(QFrame):
    """단일 ReviewData를 카드 형태로 렌더링하는 위젯."""

    def __init__(self, review: ReviewData, parent=None) -> None:
        super().__init__(parent)
        self._review = review
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
        self._reply_button = QPushButton("답글 생성")
        self._reply_button.setEnabled(False)
        button_row.addStretch()
        button_row.addWidget(self._reply_button)
        layout.addLayout(button_row)
