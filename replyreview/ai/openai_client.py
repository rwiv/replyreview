"""LangChain 기반 OpenAI 클라이언트 구현."""

import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from replyreview.ai.client import AIAuthError, AIClient
from replyreview.models import ReviewData

_SYSTEM_MESSAGE = (
    "당신은 친절하고 전문적인 쇼핑몰 고객센터 직원입니다. "
    "고객의 리뷰에 공감하며 예의 바르게 답변해야 합니다. "
    "모든 답변은 반드시 한국어로만 작성하십시오."
)

_HUMAN_TEMPLATE = (
    "고객명: {customer_name}\n"
    "구매상품: {product_name}\n"
    "별점: {rating}/5\n"
    "리뷰 내용: {content}\n\n"
    "위 리뷰에 대한 적절한 답글을 작성해 주세요."
)


class OpenAIClient(AIClient):
    """LangChain ChatOpenAI를 사용하는 AIClient 구현체."""

    def __init__(self, api_key: str) -> None:
        prompt = ChatPromptTemplate.from_messages(
            [("system", _SYSTEM_MESSAGE), ("human", _HUMAN_TEMPLATE)]
        )
        self._chain = (
            prompt
            | ChatOpenAI(model="gpt-4o-mini", api_key=SecretStr(api_key))
            | StrOutputParser()
        )

    def generate_reply(self, review: ReviewData) -> str:
        try:
            return self._chain.invoke(
                {
                    "customer_name": review.customer_name,
                    "product_name": review.product_name,
                    "rating": review.rating,
                    "content": review.content,
                }
            )
        except openai.AuthenticationError as e:
            raise AIAuthError(str(e)) from e
