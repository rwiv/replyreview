# Task 1.1: AIClient ABC 및 구현체 구현

## Overview

`AIClient` ABC와 `AIAuthError` 커스텀 예외를 `replyreview/ai/client.py`에 정의하여 외부 AI 서비스 의존성을 추상화합니다. 실제 LangChain 기반 `OpenAIClient`를 구현하고, 테스트 전용 `FakeAIClient`는 프로덕션 패키지와 분리하여 `tests/fakes.py`에 정의합니다. 이 계층 덕분에 GUI 및 워커 코드는 구체적인 AI 서비스에 의존하지 않아 테스트가 용이해집니다.

## Related Files

### Reference Files

- `replyreview/models.py`: `ReviewData` 데이터클래스 필드 확인
- `docs/tech-spec.md`: 4.2절 AI 클라이언트 추상화 전략, 4.3절 LangChain 프롬프트 명세

### Target Files

- `replyreview/ai/__init__.py`: 신규 — ai 패키지 초기화
- `replyreview/ai/client.py`: 신규 — `AIClient` ABC, `AIAuthError`
- `replyreview/ai/openai_client.py`: 신규 — `OpenAIClient`
- `tests/fakes.py`: 신규 — `FakeAIClient` (테스트 전용, 프로덕션 패키지 미포함)
- `tests/ai/__init__.py`: 신규 — 테스트 패키지 초기화
- `tests/ai/test_fake_client.py`: 신규 — `FakeAIClient` 동작 테스트 (자동 실행)
- `tests/ai/test_openai_client.py`: 신규 — `OpenAIClient` 수동 통합 테스트 (자동 실행 제외)

## Workflow

### Step 1: AIClient ABC 및 AIAuthError 구현

`replyreview/ai/client.py`에 인터페이스와 예외 타입만 정의합니다. `FakeAIClient`는 테스트 전용이므로 이 파일에 포함하지 않습니다.

- `AIAuthError`는 `WorkerSignals.auth_error` 시그널과 연동하여 API 키 오류를 일반 네트워크 오류와 구별합니다.
- `AIClient`는 `generate_reply` 추상 메서드 하나만 정의합니다.

```python
# replyreview/ai/client.py
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
```

### Step 2: FakeAIClient 구현 (테스트 전용)

`tests/fakes.py`에 `FakeAIClient`를 구현합니다. 프로덕션 `replyreview/` 패키지와 분리함으로써 PyInstaller 빌드에 포함되지 않습니다.

- `raise_error` 옵션으로 성공 케이스와 오류 케이스(일반 오류, `AIAuthError`)를 모두 시뮬레이션할 수 있어 별도의 Mock 클래스 없이 다양한 테스트 케이스를 커버합니다.
- `REPLY_TEMPLATE`을 클래스 상수로 노출하여 테스트에서 예상 결과를 쉽게 참조할 수 있습니다.

```python
# tests/fakes.py
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
```

### Step 3: OpenAIClient 구현

`replyreview/ai/openai_client.py`에 `OpenAIClient`를 구현합니다.

- 생성자에서 `api_key`를 받아 LangChain 체인을 초기화합니다. 체인은 `ChatPromptTemplate` → `ChatOpenAI` → `StrOutputParser` 순서로 구성합니다.
- `generate_reply` 호출 시 `openai.AuthenticationError`가 발생하면 `AIAuthError`로 변환하여 재발생시킵니다. 이를 통해 워커가 인증 오류와 일반 오류를 구별하여 적절한 시그널을 발행할 수 있습니다.
- `docs/tech-spec.md` 4.3절의 System Message와 Human Message 템플릿을 그대로 적용합니다.

```python
# replyreview/ai/openai_client.py
import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

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
        self._chain = prompt | ChatOpenAI(api_key=api_key) | StrOutputParser()

    def generate_reply(self, review: ReviewData) -> str:
        try:
            return self._chain.invoke({
                "customer_name": review.customer_name,
                "product_name": review.product_name,
                "rating": review.rating,
                "content": review.content,
            })
        except openai.AuthenticationError as e:
            raise AIAuthError(str(e)) from e
```

### Step 4: FakeAIClient 테스트 작성 및 수행

`tests/ai/test_fake_client.py`에 `FakeAIClient` 동작을 검증하는 테스트를 작성합니다. 이 파일은 `uv run pytest`에 자동으로 포함됩니다.

```python
# tests/ai/test_fake_client.py
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
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/ai/test_fake_client.py
```

### Step 5: OpenAIClient 수동 통합 테스트 작성

`tests/ai/test_openai_client.py`에 실제 OpenAI API를 호출하는 통합 테스트를 작성합니다.

**주의**: 이 파일은 `pytestmark = pytest.mark.skip`이 적용되어 `uv run pytest` 자동 실행에서 제외됩니다. API 키 변경, `OpenAIClient` 로직 수정, 프롬프트 변경 후 아래 명령으로 수동으로만 실행합니다.

```bash
OPENAI_API_KEY=sk-... uv run pytest tests/ai/test_openai_client.py -v --no-header
```

```python
# tests/ai/test_openai_client.py
"""
OpenAIClient 수동 통합 테스트.

이 테스트는 실제 OpenAI API를 호출하므로 pytest 자동 실행 대상이 아닙니다.
pytestmark = pytest.mark.skip 이 적용되어 uv run pytest 실행 시 자동으로 건너뜁니다.

수동 실행이 필요한 경우:
    OPENAI_API_KEY=sk-... uv run pytest tests/ai/test_openai_client.py -v --no-header
"""
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
```

## Success Criteria

- [ ] `uv run pytest tests/ai/test_fake_client.py` 테스트가 모두 통과한다.
- [ ] `uv run pytest tests/ai/test_openai_client.py`는 skip으로 건너뜀이 확인된다.
- [ ] `uv run pyright` 타입 체크 오류가 없다.
- [ ] `AIClient` ABC는 `generate_reply` 추상 메서드만 정의하며, `FakeAIClient`를 포함하지 않는다.
- [ ] `FakeAIClient`는 `tests/fakes.py`에 위치하며 `replyreview/` 패키지에 없다.
- [ ] `OpenAIClient`는 `openai.AuthenticationError` 발생 시 `AIAuthError`로 변환한다.
