# Task 2.2: ReviewCardWidget 및 ReviewListView 구현

## Overview

`ReviewData`를 카드 형태로 렌더링하는 `ReviewCardWidget`과, 카드 목록을 세로 스크롤로 표시하는 `ReviewListView`를 구현합니다.

`ReviewCardWidget`은 Track 1.3에서 AI 답글 생성 기능이 연동되는 확장 지점입니다. 이 Task에서는 '답글 생성' 버튼을 비활성화 상태로 배치하고, `pytest-qt`로 렌더링 결과를 검증합니다.

## Related Files

### Reference Files

- `docs/features.md`: 2.3절 카드 리스트 뷰 레이아웃 요구사항 참조
- `replyreview/models.py`: `ReviewData` 필드 구조 파악용
- `replyreview/gui/settings_dialog.py`: `QVBoxLayout` / `QHBoxLayout` 구성 패턴 참조용

### Target Files

- `replyreview/gui/review_card_widget.py`: 신규 — `ReviewCardWidget` 클래스
- `replyreview/gui/review_list_view.py`: 신규 — `ReviewListView` 클래스
- `tests/gui/test_review_card_widget.py`: 신규 — `ReviewCardWidget` / `ReviewListView` GUI 테스트

## Workflow

### Step 1: ReviewCardWidget 구현

`replyreview/gui/review_card_widget.py`에 `ReviewCardWidget` 클래스를 구현합니다.

- `QFrame`을 상속하여 카드 경계를 시각적으로 구분합니다.
- 테스트에서 라벨 텍스트를 직접 검증할 수 있도록 `_header_label`, `_content_label`, `_reply_button`을 인스턴스 변수로 보관합니다.
- 별점은 `rating`만큼 `★`을 반복하고 나머지를 `☆`으로 채워 표현합니다. (예: rating=4 → `★★★★☆`)
- '답글 생성' 버튼은 `setEnabled(False)`로 비활성화합니다. Track 1.3에서 이 버튼에 AI 답글 생성 로직이 연결됩니다.

```python
# replyreview/gui/review_card_widget.py
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from replyreview.models import ReviewData

MAX_RATING = 5


class ReviewCardWidget(QFrame):
    """단일 ReviewData를 카드 형태로 렌더링하는 위젯."""

    def __init__(self, review: ReviewData, parent=None) -> None:
        super().__init__(parent)
        self._review = review
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # [상단] 별점·고객명·상품명
        stars = "★" * self._review.rating + "☆" * (MAX_RATING - self._review.rating)
        self._header_label = QLabel(
            f"{stars} | {self._review.customer_name} | 상품: {self._review.product_name}"
        )
        layout.addWidget(self._header_label)

        # [중단] 리뷰 원문
        self._content_label = QLabel(self._review.content)
        self._content_label.setWordWrap(True)
        layout.addWidget(self._content_label)

        # [하단] 답글 생성 버튼 (Track 1.3에서 기능 연동 예정)
        button_row = QHBoxLayout()
        self._reply_button = QPushButton("답글 생성")
        self._reply_button.setEnabled(False)
        button_row.addStretch()
        button_row.addWidget(self._reply_button)
        layout.addLayout(button_row)
```

### Step 2: ReviewListView 구현

`replyreview/gui/review_list_view.py`에 `ReviewListView` 클래스를 구현합니다.

- `QScrollArea`를 상속합니다. `setWidgetResizable(True)`로 내부 컨테이너가 뷰 크기에 맞게 늘어나도록 설정합니다.
- 내부 컨테이너 `QWidget`에 `QVBoxLayout`을 붙이고, `list[ReviewData]`를 순회하며 `ReviewCardWidget`을 동적으로 생성하여 추가합니다.
- 카드가 아래쪽부터 쌓이지 않도록 레이아웃에 `AlignTop`을 설정합니다.

```python
# replyreview/gui/review_list_view.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from replyreview.gui.review_card_widget import ReviewCardWidget
from replyreview.models import ReviewData


class ReviewListView(QScrollArea):
    """파싱된 ReviewData 목록을 스크롤 가능한 카드 목록으로 시각화하는 위젯."""

    def __init__(self, reviews: list[ReviewData], parent=None) -> None:
        super().__init__(parent)
        self._reviews = reviews
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for review in self._reviews:
            layout.addWidget(ReviewCardWidget(review))

        self.setWidget(container)
```

### Step 3: ReviewCardWidget GUI 테스트 작성 및 수행

`tests/gui/test_review_card_widget.py`에 `qtbot` fixture를 사용한 GUI 테스트를 작성합니다.

```python
# tests/gui/test_review_card_widget.py
import pytest
from pytestqt.qtbot import QtBot

from replyreview.gui.review_card_widget import ReviewCardWidget
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

    def test_header_displays_full_stars(self, card_widget: ReviewCardWidget, sample_review: ReviewData) -> None:
        """
        rating=5일 때 헤더 라벨에 ★이 5개 표시되는지 검증한다.
        """
        # ...

    def test_header_displays_partial_stars(self, qtbot: QtBot) -> None:
        """
        rating=3일 때 헤더 라벨에 ★ 3개와 ☆ 2개가 표시되는지 검증한다.
        """
        # card_widget fixture는 rating=5이므로, 이 테스트에서는 rating=3인 위젯을 직접 생성한다.
        # ...

    def test_header_displays_customer_name(self, card_widget: ReviewCardWidget, sample_review: ReviewData) -> None:
        """
        헤더 라벨에 고객명이 포함되는지 검증한다.
        """
        # ...

    def test_header_displays_product_name(self, card_widget: ReviewCardWidget, sample_review: ReviewData) -> None:
        """
        헤더 라벨에 상품명이 포함되는지 검증한다.
        """
        # ...

    def test_content_label_displays_review_text(self, card_widget: ReviewCardWidget, sample_review: ReviewData) -> None:
        """
        본문 라벨에 리뷰 원문이 표시되는지 검증한다.
        """
        # ...

    def test_reply_button_is_disabled(self, card_widget: ReviewCardWidget) -> None:
        """
        답글 생성 버튼이 비활성화(disabled) 상태인지 검증한다.
        """
        # ...
```

테스트 파일 하단에 `ReviewListView` 렌더링 테스트도 함께 작성합니다.

```python
class TestReviewListView:
    """ReviewListView의 카드 렌더링 수를 검증하는 테스트 클래스."""

    def test_renders_all_cards(self, qtbot: QtBot) -> None:
        """
        전달된 ReviewData 수만큼 ReviewCardWidget이 렌더링되는지 검증한다.
        """
        # ReviewData 2개를 생성하여 ReviewListView에 전달하고,
        # 내부 컨테이너 레이아웃의 아이템 수가 2인지 검증한다.
        # ...
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/gui/test_review_card_widget.py
```

## Success Criteria

- [x] `uv run pytest tests/gui/test_review_card_widget.py` 테스트가 모두 통과한다.
- [x] `uv run pyright` 타입 체크 오류가 없다.
- [x] `ReviewCardWidget`에 별점(★/☆), 고객명, 상품명, 리뷰 원문이 올바르게 렌더링된다.
- [x] `ReviewCardWidget`의 '답글 생성' 버튼이 비활성화 상태이다.
- [x] `ReviewListView`가 여러 `ReviewData`를 받아 각각 카드로 렌더링한다.
