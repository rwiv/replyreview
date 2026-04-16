import pytest
from pytestqt.qtbot import QtBot

from replyreview.gui.review_card_widget import ReviewCardWidget
from replyreview.gui.review_list_view import ReviewListView
from replyreview.models import ReviewData


@pytest.fixture
def sample_review() -> ReviewData:
    """테스트용 ReviewData fixture."""
    return ReviewData(
        product_name="에어팟 프로 케이스",
        customer_name="김땡땡",
        rating=5,
        content="배송이 빠르고 상품이 너무 예뻐요!",
    )


@pytest.fixture
def card_widget(qtbot: QtBot, sample_review: ReviewData) -> ReviewCardWidget:
    """테스트용 ReviewCardWidget 인스턴스를 생성하고 qtbot에 등록하는 fixture."""
    widget = ReviewCardWidget(review=sample_review)
    qtbot.addWidget(widget)
    return widget


class TestReviewCardWidget:
    """ReviewCardWidget의 렌더링 결과를 검증하는 테스트 클래스."""

    def test_header_displays_full_stars(
        self, card_widget: ReviewCardWidget, sample_review: ReviewData
    ) -> None:
        """
        rating=5일 때 헤더 라벨에 ★이 5개 표시되는지 검증한다.
        """
        header_text = card_widget._header_label.text()
        assert header_text.startswith("★★★★★")

    def test_header_displays_partial_stars(self, qtbot: QtBot) -> None:
        """
        rating=3일 때 헤더 라벨에 ★ 3개와 ☆ 2개가 표시되는지 검증한다.
        """
        review = ReviewData(
            product_name="상품",
            customer_name="고객",
            rating=3,
            content="내용",
        )
        card = ReviewCardWidget(review)
        qtbot.addWidget(card)

        header_text = card._header_label.text()
        assert header_text.startswith("★★★☆☆")

    def test_header_displays_customer_name(
        self, card_widget: ReviewCardWidget, sample_review: ReviewData
    ) -> None:
        """
        헤더 라벨에 고객명이 포함되는지 검증한다.
        """
        header_text = card_widget._header_label.text()
        assert sample_review.customer_name in header_text

    def test_header_displays_product_name(
        self, card_widget: ReviewCardWidget, sample_review: ReviewData
    ) -> None:
        """
        헤더 라벨에 상품명이 포함되는지 검증한다.
        """
        header_text = card_widget._header_label.text()
        assert sample_review.product_name in header_text

    def test_content_label_displays_review_text(
        self, card_widget: ReviewCardWidget, sample_review: ReviewData
    ) -> None:
        """
        본문 라벨에 리뷰 원문이 표시되는지 검증한다.
        """
        content_text = card_widget._content_label.text()
        assert content_text == sample_review.content

    def test_reply_button_is_disabled(self, card_widget: ReviewCardWidget) -> None:
        """
        답글 생성 버튼이 비활성화(disabled) 상태인지 검증한다.
        """
        assert card_widget._reply_button.isEnabled() is False

    def test_reply_button_text(self, card_widget: ReviewCardWidget) -> None:
        """
        답글 생성 버튼의 텍스트가 올바른지 검증한다.
        """
        assert card_widget._reply_button.text() == "답글 생성"


class TestReviewListView:
    """ReviewListView의 카드 렌더링 수를 검증하는 테스트 클래스."""

    def test_renders_all_cards(self, qtbot: QtBot) -> None:
        """
        전달된 ReviewData 수만큼 ReviewCardWidget이 렌더링되는지 검증한다.
        """
        reviews = [
            ReviewData("상품1", "고객1", 5, "좋아요"),
            ReviewData("상품2", "고객2", 4, "좋습니다"),
        ]
        list_view = ReviewListView(reviews)
        qtbot.addWidget(list_view)

        container = list_view.widget()
        assert container is not None
        layout = container.layout()
        assert layout is not None
        assert layout.count() == len(reviews)

    def test_card_widgets_are_review_card_widget_instances(self, qtbot: QtBot) -> None:
        """
        렌더링된 위젯이 ReviewCardWidget 인스턴스인지 검증한다.
        """
        reviews = [
            ReviewData("상품", "고객", 5, "내용"),
        ]
        list_view = ReviewListView(reviews)
        qtbot.addWidget(list_view)

        container = list_view.widget()
        assert container is not None
        layout = container.layout()
        assert layout is not None
        item = layout.itemAt(0)
        assert item is not None
        widget = item.widget()
        assert isinstance(widget, ReviewCardWidget)
