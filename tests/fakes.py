"""테스트 전용 페이크 구현. 프로덕션 패키지에 포함되지 않음."""

from replyreview.ai.client import AIClient
from replyreview.models import ReviewData


class FakeAIClient(AIClient):
    """
    테스트 전용 AIClient 구현체.
    네트워크 호출 없이 고정 텍스트를 반환하며, raise_error를 지정하면 해당 예외를 발생시킨다.
    """

    REPLY_TEMPLATE = "안녕하세요, {customer_name}님. 소중한 리뷰 감사합니다."

    def __init__(self, raise_error: Exception | None = None) -> None:
        self._raise_error = raise_error

    def generate_reply(self, review: ReviewData) -> str:
        if self._raise_error is not None:
            raise self._raise_error
        return self.REPLY_TEMPLATE.format(customer_name=review.customer_name)
