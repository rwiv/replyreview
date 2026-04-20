from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from replyreview.ai.client import AIClient
from replyreview.gui.review_card_widget import ReviewCardWidget
from replyreview.models import ReviewData


class ReviewListView(QScrollArea):
    """파싱된 ReviewData 목록을 스크롤 가능한 카드 목록으로 시각화하는 위젯."""

    def __init__(
        self, reviews: list[ReviewData], ai_client: AIClient, parent=None
    ) -> None:
        super().__init__(parent)
        self._reviews = reviews
        self._ai_client = ai_client
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for review in self._reviews:
            layout.addWidget(ReviewCardWidget(review=review, ai_client=self._ai_client))

        self.setWidget(container)
