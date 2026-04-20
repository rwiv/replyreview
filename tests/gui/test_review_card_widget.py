import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from replyreview.ai.client import AIAuthError
from replyreview.gui.review_card_widget import (
    _BUTTON_TEXT_DEFAULT,
    _BUTTON_TEXT_LOADING,
    _ERROR_API_KEY,
    _ERROR_GENERAL,
    ReviewCardWidget,
)
from replyreview.models import ReviewData
from tests.fakes import FakeAIClient


@pytest.fixture
def review() -> ReviewData:
    """테스트용 ReviewData fixture."""
    return ReviewData(
        product_name="테스트 상품",
        customer_name="홍길동",
        rating=4,
        content="좋은 상품입니다.",
    )


@pytest.fixture
def card(qtbot: QtBot, review: ReviewData) -> ReviewCardWidget:
    """기본 FakeAIClient로 초기화된 ReviewCardWidget fixture."""
    widget = ReviewCardWidget(review=review, ai_client=FakeAIClient())
    qtbot.addWidget(widget)
    widget.show()
    return widget


class TestReviewCardWidget:
    """ReviewCardWidget의 비동기 답글 생성 흐름을 검증하는 테스트 클래스."""

    def test_reply_button_is_enabled_initially(self, card: ReviewCardWidget) -> None:
        """'답글 생성' 버튼이 초기에 활성화 상태인지 검증한다."""
        assert card._reply_button.isEnabled()
        assert card._reply_button.text() == _BUTTON_TEXT_DEFAULT

    def test_button_shows_loading_text_on_click(
        self, qtbot: QtBot, card: ReviewCardWidget
    ) -> None:
        """
        '답글 생성' 버튼 클릭 후 버튼 텍스트가 "생성 중..."으로 변경되고 비활성화되는지 검증한다.
        _on_generate_clicked가 동기적으로 실행되므로 클릭 직후 상태를 즉시 확인할 수 있다.
        """
        qtbot.mouseClick(card._reply_button, Qt.MouseButton.LeftButton)

        assert card._reply_button.text() == _BUTTON_TEXT_LOADING
        assert not card._reply_button.isEnabled()

        # 다음 테스트에 영향을 주지 않도록 워커 완료를 기다린다.
        qtbot.waitUntil(lambda: card._reply_button.isEnabled(), timeout=3000)

    def test_reply_area_shown_after_generation(
        self, qtbot: QtBot, card: ReviewCardWidget
    ) -> None:
        """답글 생성 완료 후 답글 텍스트 영역이 표시되는지 검증한다."""
        assert not card._reply_area.isVisible()

        qtbot.mouseClick(card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: card._reply_area.isVisible(), timeout=3000)

    def test_reply_area_contains_generated_text(
        self, qtbot: QtBot, card: ReviewCardWidget, review: ReviewData
    ) -> None:
        """생성된 답글 텍스트가 카드 내 텍스트 영역에 표시되는지 검증한다."""
        qtbot.mouseClick(card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: card._reply_area.isVisible(), timeout=3000)

        expected = FakeAIClient.REPLY_TEMPLATE.format(
            customer_name=review.customer_name
        )
        assert card._reply_area.toPlainText() == expected

    def test_button_restored_after_generation(
        self, qtbot: QtBot, card: ReviewCardWidget
    ) -> None:
        """답글 생성 완료 후 버튼 텍스트와 활성화 상태가 원래대로 복구되는지 검증한다."""
        qtbot.mouseClick(card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: card._reply_button.isEnabled(), timeout=3000)

        assert card._reply_button.text() == _BUTTON_TEXT_DEFAULT

    def test_error_label_shown_on_general_error(
        self, qtbot: QtBot, review: ReviewData
    ) -> None:
        """일반 오류 발생 시 오류 원인을 포함한 메시지 레이블이 표시되는지 검증한다."""
        error_msg = "network error"
        error_card = ReviewCardWidget(
            review=review,
            ai_client=FakeAIClient(raise_error=RuntimeError(error_msg)),
        )
        qtbot.addWidget(error_card)
        error_card.show()

        qtbot.mouseClick(error_card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: error_card._error_label.isVisible(), timeout=3000)

        label_text = error_card._error_label.text()
        assert _ERROR_GENERAL in label_text
        assert error_msg in label_text

    def test_error_label_shows_auth_message_on_auth_error(
        self, qtbot: QtBot, review: ReviewData
    ) -> None:
        """AIAuthError 발생 시 API 키 오류 메시지 레이블이 표시되는지 검증한다."""
        auth_card = ReviewCardWidget(
            review=review,
            ai_client=FakeAIClient(raise_error=AIAuthError("invalid key")),
        )
        qtbot.addWidget(auth_card)
        auth_card.show()

        qtbot.mouseClick(auth_card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: auth_card._error_label.isVisible(), timeout=3000)

        assert auth_card._error_label.text() == _ERROR_API_KEY

    def test_button_restored_after_error(
        self, qtbot: QtBot, review: ReviewData
    ) -> None:
        """오류 발생 후 버튼 텍스트와 활성화 상태가 원래대로 복구되는지 검증한다."""
        error_card = ReviewCardWidget(
            review=review,
            ai_client=FakeAIClient(raise_error=RuntimeError("error")),
        )
        qtbot.addWidget(error_card)
        error_card.show()

        qtbot.mouseClick(error_card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: error_card._reply_button.isEnabled(), timeout=3000)

        assert error_card._reply_button.text() == _BUTTON_TEXT_DEFAULT

    def test_copy_button_hidden_before_generation(self, card: ReviewCardWidget) -> None:
        """답글 생성 전에는 클립보드 복사 버튼이 숨겨져 있는지 검증한다."""
        assert not card._copy_button.isVisible()

    def test_copy_button_shown_after_generation(
        self, qtbot: QtBot, card: ReviewCardWidget
    ) -> None:
        """답글 생성 완료 후 클립보드 복사 버튼이 노출되는지 검증한다."""
        qtbot.mouseClick(card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: card._copy_button.isVisible(), timeout=3000)

    def test_copy_button_copies_reply_to_clipboard(
        self, qtbot: QtBot, card: ReviewCardWidget, review: ReviewData
    ) -> None:
        """클립보드 복사 버튼 클릭 시 시스템 클립보드에 답글 텍스트가 설정되는지 검증한다."""
        from PySide6.QtWidgets import QApplication

        qtbot.mouseClick(card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: card._copy_button.isVisible(), timeout=3000)

        qtbot.mouseClick(card._copy_button, Qt.MouseButton.LeftButton)

        expected = FakeAIClient.REPLY_TEMPLATE.format(
            customer_name=review.customer_name
        )
        assert QApplication.clipboard().text() == expected
