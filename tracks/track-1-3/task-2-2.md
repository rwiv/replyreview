# Task 2.2: 클립보드 복사 + MainWindow AIClient 주입 + 명세 갱신

## Overview

AI 답글이 표시된 후 '클립보드 복사' 버튼을 노출하고, 클릭 시 시스템 클립보드에 텍스트를 복사하는 기능을 `ReviewCardWidget`에 추가합니다. `MainWindow._on_file_selected`에서 `OpenAIClient`를 생성하여 `ReviewListView`에 주입하는 연결 고리를 완성합니다. API 키가 비어있어도 파일 로드 단계에서 차단하지 않으며, 오류는 답글 생성 시 카드 레벨에서 처리합니다. `ReviewListView` 시그니처 변경으로 깨지는 `test_main_window.py`를 함께 수정합니다.

## Related Files

### Reference Files

- `replyreview/gui/review_card_widget.py`: 클립보드 복사 버튼 추가 위치 확인 (`_on_reply_finished`)
- `replyreview/gui/main_window.py`: `_on_file_selected` 슬롯 수정 위치 확인
- `replyreview/gui/review_list_view.py`: `ai_client` 파라미터 추가 여부 확인
- `replyreview/ai/openai_client.py`: `OpenAIClient` 생성자 시그니처 확인
- `tests/gui/test_main_window.py`: 기존 테스트 확인 및 수정 범위 파악
- `docs/features.md`: 3.4, 3.5절 현재 내용 확인
- `docs/tech-spec.md`: ai 모듈 관련 기술 항목 확인

### Target Files

- `replyreview/gui/review_card_widget.py`: 수정 — 클립보드 복사 버튼 추가
- `replyreview/gui/main_window.py`: 수정 — `OpenAIClient` 생성 및 주입
- `tests/gui/test_review_card_widget.py`: 수정 — 클립보드 복사 테스트 추가
- `tests/gui/test_main_window.py`: 수정 — `ReviewListView` 시그니처 변경 반영
- `docs/features.md`: 수정 — 3.4, 3.5절 구현 상세 추가
- `docs/tech-spec.md`: 수정 — ai 모듈 디렉터리 구조 반영

## Workflow

### Step 1: ReviewCardWidget에 클립보드 복사 기능 추가

`_setup_ui`에서 '클립보드 복사' 버튼을 생성하되 초기에는 숨겨두고, `_on_reply_finished`에서 노출합니다. 버튼 클릭 시 `QTimer.singleShot`으로 1.5초 후 텍스트를 원복합니다.

```python
# replyreview/gui/review_card_widget.py (추가 부분)
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

# 복사 완료 피드백을 보여주는 시간 (밀리초).
_COPY_FEEDBACK_DURATION_MS = 1500
_BUTTON_TEXT_COPY = "클립보드 복사"
_BUTTON_TEXT_COPIED = "복사 완료!"


class ReviewCardWidget(QFrame):
    # ... 기존 코드 유지

    def _setup_ui(self) -> None:
        # ... 기존 UI 설정 유지 (reply_area, error_label 이후에 추가)

        self._copy_button = QPushButton(_BUTTON_TEXT_COPY)
        self._copy_button.clicked.connect(self._on_copy_clicked)
        self._copy_button.hide()
        layout.addWidget(self._copy_button)

    @Slot(str)
    def _on_reply_finished(self, text: str) -> None:
        self._reply_area.setPlainText(text)
        self._reply_area.show()
        self._copy_button.show()
        self._restore_button()

    @Slot()
    def _on_copy_clicked(self) -> None:
        QApplication.clipboard().setText(self._reply_area.toPlainText())
        self._copy_button.setText(_BUTTON_TEXT_COPIED)
        QTimer.singleShot(
            _COPY_FEEDBACK_DURATION_MS,
            lambda: self._copy_button.setText(_BUTTON_TEXT_COPY),
        )
```

### Step 2: MainWindow에 OpenAIClient 생성 및 주입

`replyreview/gui/main_window.py`의 `_on_file_selected` 슬롯을 수정합니다.

API 키 공백 여부를 파일 로드 단계에서 사전 차단하지 않습니다. `features.md` 3.4절은 API 키 오류를 카드 텍스트 영역에 표시하도록 명세하고 있으며, 빈 키로 생성된 `OpenAIClient`는 답글 생성 시 `AIAuthError`를 발생시켜 카드에 표시됩니다.

```python
# replyreview/gui/main_window.py (수정 부분)
from replyreview.ai.openai_client import OpenAIClient


class MainWindow(QMainWindow):
    # ... 기존 코드 유지

    @Slot(str)
    def _on_file_selected(self, file_path: str) -> None:
        """
        파일 선택 후 파싱을 시도하고, 성공 시 OpenAIClient를 생성하여 ReviewListView로 전환한다.
        API 키 오류는 파일 로드 단계에서 차단하지 않고, 답글 생성 시 카드 레벨에서 처리한다.
        """
        try:
            reviews = self._parser.parse(file_path)
        except ParserError as e:
            QMessageBox.warning(self, "파일 오류", str(e))
            return

        api_key = self._config_manager.get_api_key()
        ai_client = OpenAIClient(api_key=api_key)
        self.setCentralWidget(ReviewListView(reviews=reviews, ai_client=ai_client))
```

### Step 3: 클립보드 복사 GUI 테스트 추가

`tests/gui/test_review_card_widget.py`의 `TestReviewCardWidget` 클래스에 클립보드 복사 관련 테스트를 추가합니다.

```python
# tests/gui/test_review_card_widget.py (추가 부분)
from PySide6.QtWidgets import QApplication


class TestReviewCardWidget:
    # ... 기존 테스트 유지

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
        qtbot.mouseClick(card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: card._copy_button.isVisible(), timeout=3000)

        qtbot.mouseClick(card._copy_button, Qt.MouseButton.LeftButton)

        expected = FakeAIClient.REPLY_TEMPLATE.format(customer_name=review.customer_name)
        assert QApplication.clipboard().text() == expected
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/gui/test_review_card_widget.py
```

### Step 4: tests/gui/test_main_window.py 갱신

`ReviewListView` 생성자 시그니처가 `(reviews)` → `(reviews, ai_client)`로 변경되므로, `_on_file_selected` 내부에서 `OpenAIClient`가 생성됩니다. 관련 테스트에서 `replyreview.gui.main_window.OpenAIClient`를 패치하여 `FakeAIClient`를 주입합니다.

수정 대상은 유효한 파일 선택 시 `ReviewListView`로 전환되는지 검증하는 테스트입니다. 파싱 오류 테스트는 `OpenAIClient`에 도달하지 않으므로 수정 불필요합니다.

```python
# tests/gui/test_main_window.py (수정 부분)
from unittest.mock import patch

from tests.fakes import FakeAIClient


class TestMainWindow:
    # ... 기존 테스트 유지

    def test_central_widget_switches_to_review_list_view_on_valid_file(
        self, qtbot: QtBot, window: MainWindow, valid_csv: str
    ) -> None:
        """
        유효한 파일이 선택되면 중앙 위젯이 ReviewListView로 전환되는지 검증한다.
        OpenAIClient는 FakeAIClient로 대체하여 실제 API 키 없이 테스트한다.
        """
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=(valid_csv, ""),
        ):
            with patch(
                "replyreview.gui.main_window.OpenAIClient",
                return_value=FakeAIClient(),
            ):
                central_widget = window.centralWidget()
                assert isinstance(central_widget, FileLoadView)
                qtbot.mouseClick(central_widget._load_button, Qt.MouseButton.LeftButton)

        assert isinstance(window.centralWidget(), ReviewListView)
```

테스트 실행 후 기존 테스트를 포함하여 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/gui/test_main_window.py
```

### Step 5: docs/features.md 갱신

`docs/features.md`의 3.4절 (AI 답글 생성) 및 3.5절 (결과물 클립보드 복사)에서 "미구현"으로 표기된 구현 상세 항목을 채웁니다. 아래 항목을 포함합니다.

- **3.4절 구현 상세**:
  - `replyreview/ai/client.py`: `AIClient` ABC, `AIAuthError`
  - `replyreview/ai/openai_client.py`: `OpenAIClient`
  - `replyreview/ai/worker.py`: `WorkerSignals`(`finished`, `auth_error`, `error`), `ReplyWorker`
  - `replyreview/gui/review_card_widget.py`: `_on_generate_clicked`, `_on_reply_finished`, `_on_reply_auth_error`, `_on_reply_error` 슬롯
  - 테스트: `tests/ai/test_fake_client.py`, `tests/gui/test_review_card_widget.py`
- **3.5절 구현 상세**:
  - `replyreview/gui/review_card_widget.py`: `_on_copy_clicked` 슬롯, `QTimer.singleShot` 피드백

### Step 6: docs/tech-spec.md 갱신

`docs/tech-spec.md`에 `replyreview/ai/` 모듈의 디렉터리 구조 및 각 파일의 역할을 반영합니다. 기존 섹션 구조를 유지하면서 ai 모듈 관련 내용을 추가합니다.

## Success Criteria

- [ ] `uv run pytest tests/gui/test_review_card_widget.py` 테스트가 모두 통과한다.
- [ ] `uv run pytest tests/gui/test_main_window.py` 테스트가 모두 통과한다.
- [ ] `uv run pytest` 전체 테스트가 통과한다.
- [ ] `uv run pyright` 타입 체크 오류가 없다.
- [ ] 답글 생성 완료 후 클립보드 복사 버튼이 노출된다.
- [ ] 클립보드 복사 버튼 클릭 시 텍스트가 복사되고 버튼 텍스트가 일시적으로 "복사 완료!"로 변경된다.
- [ ] `docs/features.md` 3.4, 3.5절 구현 상세가 갱신되었다.
- [ ] `docs/tech-spec.md` ai 모듈 디렉터리 구조가 반영되었다.
