import os

import pytest

from replyreview.ai.client import AIAuthError
from replyreview.ai.openai_client import OpenAIClient
from replyreview.models import ReviewData

# 이 모듈의 모든 테스트를 자동 실행에서 제외한다.
pytestmark = pytest.mark.skip(
    reason=(
        "실제 OpenAI API를 호출하는 수동 1회성 통합 테스트. "
        "uv run pytest 자동 실행 대상이 아님. "
        "수동 실행: OPENAI_API_KEY=sk-... uv run pytest tests/ai/test_openai_client.py -v"
    )
)


@pytest.fixture
def api_key() -> str:
    """환경 변수에서 OpenAI API 키를 읽어 반환하는 fixture."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        pytest.skip("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    return key


@pytest.fixture
def review() -> ReviewData:
    """통합 테스트용 ReviewData fixture."""
    return ReviewData(
        product_name="무선 이어폰",
        customer_name="김철수",
        rating=5,
        content="음질이 정말 좋고 배송도 빨랐어요. 재구매 의사 있습니다.",
    )


class TestOpenAIClient:
    """OpenAIClient의 실제 API 호출 동작을 검증하는 통합 테스트 클래스."""

    def test_generate_reply_returns_non_empty_string(
        self, api_key: str, review: ReviewData
    ) -> None:
        """유효한 API 키로 generate_reply를 호출하면 비어있지 않은 문자열을 반환하는지 검증한다."""
        client = OpenAIClient(api_key=api_key)
        result = client.generate_reply(review)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_reply_raises_auth_error_on_invalid_key(
        self, review: ReviewData
    ) -> None:
        """잘못된 API 키로 generate_reply를 호출하면 AIAuthError가 발생하는지 검증한다."""
        client = OpenAIClient(api_key="sk-invalid-key-for-testing-only")
        with pytest.raises(AIAuthError):
            client.generate_reply(review)
