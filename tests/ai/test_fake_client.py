"""FakeAIClient의 동작을 검증하는 테스트."""

import pytest

from replyreview.ai.client import AIAuthError
from replyreview.models import ReviewData
from tests.fakes import FakeAIClient


@pytest.fixture
def review() -> ReviewData:
    """테스트용 ReviewData fixture."""
    return ReviewData(
        product_name="테스트 상품",
        customer_name="홍길동",
        rating=5,
        content="정말 좋은 상품입니다.",
    )


class TestFakeAIClient:
    """FakeAIClient의 동작을 검증하는 테스트 클래스."""

    @pytest.fixture
    def client(self) -> FakeAIClient:
        """기본 FakeAIClient 인스턴스를 반환하는 fixture."""
        return FakeAIClient()

    def test_generate_reply_returns_string(
        self, client: FakeAIClient, review: ReviewData
    ) -> None:
        """generate_reply가 문자열을 반환하는지 검증한다."""
        result = client.generate_reply(review)
        assert isinstance(result, str)

    def test_generate_reply_is_non_empty(
        self, client: FakeAIClient, review: ReviewData
    ) -> None:
        """generate_reply가 비어있지 않은 문자열을 반환하는지 검증한다."""
        result = client.generate_reply(review)
        assert len(result) > 0

    def test_generate_reply_includes_customer_name(
        self, client: FakeAIClient, review: ReviewData
    ) -> None:
        """generate_reply 결과에 고객명이 포함되는지 검증한다."""
        result = client.generate_reply(review)
        assert review.customer_name in result

    def test_raises_specified_error(self, review: ReviewData) -> None:
        """raise_error가 설정된 경우 generate_reply 호출 시 해당 예외가 발생하는지 검증한다."""
        error = ValueError("테스트 오류")
        client = FakeAIClient(raise_error=error)
        with pytest.raises(ValueError, match="테스트 오류"):
            client.generate_reply(review)

    def test_raises_ai_auth_error(self, review: ReviewData) -> None:
        """raise_error로 AIAuthError를 설정하면 AIAuthError가 발생하는지 검증한다."""
        client = FakeAIClient(raise_error=AIAuthError("invalid key"))
        with pytest.raises(AIAuthError):
            client.generate_reply(review)
