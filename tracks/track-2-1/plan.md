# Plan: 오류 처리 시스템 및 사용자 피드백 강화

## Phase 1: 예외 상황 감지 인프라 구축

### Task 1.1: ReviewParser 파일 읽기 예외 처리 강화

- [x] `ReviewParser.parse()`의 `pd.read_csv()` / `pd.read_excel()` 호출을 `try/except`로 감싸기
  - `FileNotFoundError`, `PermissionError`, `pd.errors.ParserError`, `pd.errors.EmptyDataError`, 기타 `Exception` 처리
  - 각 예외를 원인 메시지를 포함한 `ParserError`로 변환 (exception chaining 사용)
- [x] `tests/parser/test_review_parser.py`에 파일 읽기 예외 테스트 케이스 추가
  - `monkeypatch`로 `pd.read_csv`에 예외 주입하여 `ParserError`로 변환되는지 검증
  - 빈 파일(`pd.errors.EmptyDataError`) 케이스 검증
  - 기존 테스트 모두 계속 통과하는지 확인
- [x] `uv run pytest tests/parser/` 실행하여 전체 통과 확인

## Phase 2: 시각적 피드백 시스템 구현

### Task 2.1: AI 답글 오류 메시지 개선

- [x] `ReviewCardWidget._on_reply_error()`에서 `message` 파라미터를 활용하여 오류 원인 표시
  - 파라미터명을 `_message`에서 `message`로 변경
  - 레이블 텍스트를 `f"{_ERROR_GENERAL}\n오류: {message}"` 형식으로 변경
- [x] `tests/gui/test_review_card_widget.py`의 `test_error_label_shown_on_general_error` 업데이트
  - 오류 원인을 포함한 새 메시지 형식 검증으로 수정
- [x] `uv run pytest` 전체 테스트 실행하여 통과 확인
- [x] `uv run pyright` 타입 체크 오류 없음 확인
