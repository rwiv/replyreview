# Task 2.1: ReplyWorker 구현 및 ReviewCardWidget 비동기 연동

## Overview

백그라운드 스레드에서 AI 답글을 생성하는 `ReplyWorker`를 구현하고, `ReviewCardWidget`을 개선하여 비동기 답글 생성 흐름을 완성합니다. `WorkerSignals`는 오류 유형에 따라 `auth_error`와 `error` 두 개의 시그널을 분리하여 `ReviewCardWidget`이 타입 안전하게 처리합니다. `ReviewListView`에 `ai_client` 파라미터를 추가하여 각 카드에 전달하는 연결도 완성합니다.

## Related Files

### Reference Files

- `replyreview/ai/client.py`: `AIClient`, `AIAuthError` 인터페이스 확인
- `replyreview/gui/review_card_widget.py`: 현재 구현 상태 확인 (버튼 비활성화 구조)
- `replyreview/gui/review_list_view.py`: `ReviewCardWidget` 생성 위치 확인
- `tests/fakes.py`: `FakeAIClient` 인터페이스 확인
- `docs/features.md`: 3.4절 AI 답글 생성 UI/UX 요구사항
- `.claude/skills/pyside-patterns/references/threading_async.md`: QRunnable + QThreadPool 패턴
- `.claude/skills/pyside-patterns/references/gui_testing.md`: `qtbot.waitUntil` 사용법

### Target Files

- `replyreview/ai/worker.py`: 신규 — `WorkerSignals`, `ReplyWorker`
- `replyreview/gui/review_card_widget.py`: 수정 — 비동기 답글 생성 UI 통합
- `replyreview/gui/review_list_view.py`: 수정 — `ai_client` 파라미터 추가
- `tests/gui/test_review_card_widget.py`: 신규 — 비동기 GUI 테스트

## Workflow

### Step 1: ReplyWorker 구현

`replyreview/ai/worker.py`에 `WorkerSignals`와 `ReplyWorker`를 구현합니다.

- `QRunnable`은 `QObject`를 상속하지 않으므로 시그널을 별도 `QObject`인 `WorkerSignals`에 선언합니다.
- `AIAuthError`와 일반 예외를 별도 시그널(`auth_error`, `error`)로 분리합니다. 이를 통해 `ReviewCardWidget`이 문자열 비교 없이 타입 수준에서 오류를 구별할 수 있습니다.

```python
# replyreview/ai/worker.py
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from replyreview.ai.client import AIAuthError, AIClient
from replyreview.models import ReviewData


class WorkerSignals(QObject):
    """ReplyWorker가 발행하는 시그널 컨테이너."""

    finished = Signal(str)
    # API 키 인증 실패 시 발행. 파라미터 없음.
    auth_error = Signal()
    # 네트워크 오류 등 일반 예외 발생 시 발행.
    error = Signal(str)


class ReplyWorker(QRunnable):
    """백그라운드 스레드에서 AIClient.generate_reply를 호출하는 워커."""

    def __init__(self, client: AIClient, review: ReviewData) -> None:
        super().__init__()
        self._client = client
        self._review = review
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            reply = self._client.generate_reply(self._review)
            self.signals.finished.emit(reply)
        except AIAuthError:
            self.signals.auth_error.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
```

### Step 2: ReviewCardWidget 개선

`replyreview/gui/review_card_widget.py`를 수정하여 비동기 답글 생성 흐름을 통합합니다.

- 생성자에 `ai_client: AIClient` 파라미터를 추가합니다. `self._threadpool` 인스턴스 변수는 불필요하므로 `QThreadPool.globalInstance()`를 `_on_generate_clicked` 내에서 직접 호출합니다.
- 기존에 비활성화 상태였던 `_reply_button`을 활성화하고 `_on_generate_clicked` 슬롯에 연결합니다.
- 답글 표시 영역(`QTextEdit`)과 오류 레이블은 초기에 숨겨두고, 각 이벤트 시 `show()`로 노출합니다.
- `auth_error`와 `error` 시그널을 각각 별도 슬롯에 연결합니다.

```python
# replyreview/gui/review_card_widget.py
from PySide6.QtCore import QThreadPool, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from replyreview.ai.client import AIClient
from replyreview.ai.worker import ReplyWorker
from replyreview.models import ReviewData

MAX_RATING = 5
_BUTTON_TEXT_DEFAULT = "답글 생성"
_BUTTON_TEXT_LOADING = "생성 중..."
_ERROR_API_KEY = "API 키 설정에 문제가 있습니다."
_ERROR_GENERAL = "답글 생성 실패. 다시 시도해 주세요."


class ReviewCardWidget(QFrame):
    """단일 ReviewData를 카드 형태로 렌더링하는 위젯."""

    def __init__(self, review: ReviewData, ai_client: AIClient, parent=None) -> None:
        super().__init__(parent)
        self._review = review
        self._ai_client = ai_client
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
        self._reply_button = QPushButton(_BUTTON_TEXT_DEFAULT)
        self._reply_button.clicked.connect(self._on_generate_clicked)
        button_row.addStretch()
        button_row.addWidget(self._reply_button)
        layout.addLayout(button_row)

        self._reply_area = QTextEdit()
        self._reply_area.setReadOnly(True)
        self._reply_area.hide()
        layout.addWidget(self._reply_area)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

    @Slot()
    def _on_generate_clicked(self) -> None:
        self._reply_button.setEnabled(False)
        self._reply_button.setText(_BUTTON_TEXT_LOADING)
        self._error_label.hide()
        self._reply_area.hide()

        worker = ReplyWorker(client=self._ai_client, review=self._review)
        worker.signals.finished.connect(self._on_reply_finished)
        worker.signals.auth_error.connect(self._on_reply_auth_error)
        worker.signals.error.connect(self._on_reply_error)
        QThreadPool.globalInstance().start(worker)

    @Slot(str)
    def _on_reply_finished(self, text: str) -> None:
        self._reply_area.setPlainText(text)
        self._reply_area.show()
        self._restore_button()

    @Slot()
    def _on_reply_auth_error(self) -> None:
        self._error_label.setText(_ERROR_API_KEY)
        self._error_label.show()
        self._restore_button()

    @Slot(str)
    def _on_reply_error(self, message: str) -> None:
        self._error_label.setText(_ERROR_GENERAL)
        self._error_label.show()
        self._restore_button()

    def _restore_button(self) -> None:
        self._reply_button.setEnabled(True)
        self._reply_button.setText(_BUTTON_TEXT_DEFAULT)
```

### Step 3: ReviewListView에 ai_client 파라미터 추가

`replyreview/gui/review_list_view.py`에 `ai_client: AIClient` 파라미터를 추가하여 각 `ReviewCardWidget` 생성 시 전달합니다.

```python
# replyreview/gui/review_list_view.py
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
```

### Step 4: ReviewCardWidget 비동기 GUI 테스트 작성 및 수행

`tests/gui/test_review_card_widget.py`에 `qtbot`과 `FakeAIClient`를 결합한 테스트를 작성합니다.

비동기 워커는 QThreadPool에서 실행되고 결과를 큐 연결(queued connection)으로 메인 스레드에 전달합니다. `qtbot.waitUntil`을 사용하여 UI 상태 변화를 기다립니다. `worker` 객체는 `_on_generate_clicked` 내부에서 생성되므로 테스트에서 직접 접근할 수 없으며, UI 상태 변화로 완료 여부를 판단합니다.

```python
# tests/gui/test_review_card_widget.py
import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from replyreview.ai.client import AIAuthError
from replyreview.gui.review_card_widget import (
    ReviewCardWidget,
    _BUTTON_TEXT_DEFAULT,
    _BUTTON_TEXT_LOADING,
    _ERROR_API_KEY,
    _ERROR_GENERAL,
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

        expected = FakeAIClient.REPLY_TEMPLATE.format(customer_name=review.customer_name)
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
        """일반 오류 발생 시 일반 오류 메시지 레이블이 표시되는지 검증한다."""
        error_card = ReviewCardWidget(
            review=review,
            ai_client=FakeAIClient(raise_error=RuntimeError("network error")),
        )
        qtbot.addWidget(error_card)

        qtbot.mouseClick(error_card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: error_card._error_label.isVisible(), timeout=3000)

        assert error_card._error_label.text() == _ERROR_GENERAL

    def test_error_label_shows_auth_message_on_auth_error(
        self, qtbot: QtBot, review: ReviewData
    ) -> None:
        """AIAuthError 발생 시 API 키 오류 메시지 레이블이 표시되는지 검증한다."""
        auth_card = ReviewCardWidget(
            review=review,
            ai_client=FakeAIClient(raise_error=AIAuthError("invalid key")),
        )
        qtbot.addWidget(auth_card)

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

        qtbot.mouseClick(error_card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: error_card._reply_button.isEnabled(), timeout=3000)

        assert error_card._reply_button.text() == _BUTTON_TEXT_DEFAULT
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/gui/test_review_card_widget.py
```

## Success Criteria

- [ ] `uv run pytest tests/gui/test_review_card_widget.py` 테스트가 모두 통과한다.
- [ ] `uv run pyright` 타입 체크 오류가 없다.
- [ ] '답글 생성' 버튼 클릭 시 버튼이 비활성화되고 "생성 중..." 텍스트로 변경된다.
- [ ] 답글 생성 완료 시 카드에 답글 텍스트 영역이 표시되고 버튼이 원래 상태로 복구된다.
- [ ] `AIAuthError` 발생 시 "API 키 설정에 문제가 있습니다." 메시지가 표시된다.
- [ ] 일반 오류 발생 시 "답글 생성 실패. 다시 시도해 주세요." 메시지가 표시된다.
- [ ] 오류 발생 후에도 버튼이 복구되어 재시도가 가능하다.
