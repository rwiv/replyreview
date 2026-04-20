from abc import ABC, abstractmethod

from replyreview.models import ReviewData


class AIAuthError(Exception):
    """OpenAI API 키 인증 실패 오류."""

    pass


class AIClient(ABC):
    """AI 답글 생성 클라이언트 인터페이스."""

    @abstractmethod
    def generate_reply(self, review: ReviewData) -> str:
        """리뷰 데이터를 받아 생성된 답글 텍스트를 반환한다."""
        ...
