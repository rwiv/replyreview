# Task 2.1: AI 답글 오류 메시지 개선

## Overview

`ReviewCardWidget._on_reply_error()`가 현재 `message` 파라미터를 무시(`_message`로 선언)하고 범용 텍스트만 표시합니다. `features.md` 3.4절에서 "원인과 함께" 표시하도록 정의되어 있으므로, 오류 원인을 포함한 메시지 형식으로 수정합니다. 기존 테스트도 새 형식에 맞게 업데이트합니다.

## Related Files

### Reference Files

- `replyreview/gui/review_card_widget.py`: 수정 대상. `_on_reply_error` 및 관련 상수 확인
- `replyreview/ai/worker.py`: `error(str)` 시그널로 전달되는 메시지의 출처 파악
- `docs/features.md`: 3.4절 예외 처리 정책 — "원인과 함께" 요구사항 확인
- `tests/gui/test_review_card_widget.py`: 수정 대상. 기존 `test_error_label_shown_on_general_error` 케이스 확인

### Target Files

- `replyreview/gui/review_card_widget.py`: 수정 — `_on_reply_error` 파라미터명 및 레이블 텍스트 변경
- `tests/gui/test_review_card_widget.py`: 수정 — 일반 오류 메시지 검증 케이스 업데이트

## Workflow

### Step 1: `_on_reply_error` 수정

`review_card_widget.py`에서 두 가지를 변경합니다.

1. `_on_reply_error`의 파라미터명을 `_message`에서 `message`로 변경합니다.
2. 레이블 텍스트를 `_ERROR_GENERAL` 단독 대신 오류 원인을 포함한 형식으로 변경합니다.

```python
# replyreview/gui/review_card_widget.py

@Slot(str)
def _on_reply_error(self, message: str) -> None:
    cause = f"\n오류: {message}" if message else ""
    self._error_label.setText(f"{_ERROR_GENERAL}{cause}")
    self._error_label.show()
    self._restore_button()
```

`_ERROR_GENERAL` 상수(`"답글 생성 실패. 다시 시도해 주세요."`)는 그대로 유지합니다. `message`가 비어 있으면 오류 원인 줄을 추가하지 않아 레이블에 불완전한 `"\n오류: "` 문자열이 노출되는 것을 방지합니다.

`_on_reply_auth_error()`는 고정 메시지를 유지하며 변경하지 않습니다.

### Step 2: 테스트 업데이트

`test_error_label_shown_on_general_error` 테스트가 현재 `_ERROR_GENERAL` 상수와의 완전 일치를 검증하고 있어 Step 1 변경 후 실패합니다. 새 메시지 형식에 맞게 검증 방식을 수정합니다.

```python
# tests/gui/test_review_card_widget.py

class TestReviewCardWidget:
    # ...

    def test_error_label_shown_on_general_error(
        self, qtbot: QtBot, review: ReviewData
    ) -> None:
        """
        일반 오류 발생 시 오류 원인을 포함한 메시지 레이블이 표시되는지 검증한다.
        """
        error_msg = "network error"
        error_card = ReviewCardWidget(
            review=review,
            ai_client=FakeAIClient(raise_error=RuntimeError(error_msg)),
        )
        qtbot.addWidget(error_card)
        error_card.show()

        qtbot.mouseClick(error_card._reply_button, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: error_card._error_label.isVisible(), timeout=3000)

        label_text = error_card._error_label.text()
        assert _ERROR_GENERAL in label_text
        assert error_msg in label_text
```

완전 일치(`==`) 대신 부분 포함(`in`) 검증으로 전환하여, 메시지 형식이 향후 미세하게 변경되더라도 테스트가 의도를 명확히 표현하도록 합니다.

### Step 3: 전체 테스트 실행

```bash
uv run pytest
uv run pyright
```

기존 테스트 모두 통과하고, 타입 체크 오류가 없는지 확인합니다.

## Success Criteria

- [x] 일반 오류 발생 시 카드 오류 레이블에 `_ERROR_GENERAL` 텍스트와 오류 원인이 함께 표시된다.
- [x] `_on_reply_auth_error()`의 동작은 변경되지 않았다.
- [x] `uv run pytest` 전체 테스트가 통과한다.
- [x] `uv run pyright` 타입 체크 오류가 없다.
