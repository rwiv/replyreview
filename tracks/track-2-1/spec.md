# Specification: 오류 처리 시스템 및 사용자 피드백 강화

## Overview

이 트랙은 ReplyReview 애플리케이션 전반에 걸쳐 발생할 수 있는 예외 상황을 체계적으로 감지하고, 모든 오류를 콘솔 에러가 아닌 사용자 친화적인 UI 피드백으로 전달하는 안정성 강화 작업을 수행합니다.

Phase 1 MVP 구현 시 누락되었거나 불완전하게 처리된 두 가지 핵심 갭을 해소합니다.

1. **파서 파일 읽기 예외 미처리**: `ReviewParser.parse()`가 pandas `read_csv`/`read_excel` 호출에서 발생하는 파일 I/O 예외를 잡지 않아, 손상된 파일이나 권한 오류 시 앱이 비정상 종료됩니다.
2. **오류 원인 미표시**: `ReviewCardWidget._on_reply_error()`가 워커에서 전달된 오류 메시지를 무시(`_message` 미사용)하고 범용 문자열만 표시하여, 기능 명세(`features.md` 3.4절 "원인과 함께" 요구사항)를 충족하지 못합니다.

## Requirements

### 1. ReviewParser 파일 읽기 예외 처리

- `pd.read_csv()` 및 `pd.read_excel()` 호출 시 발생하는 모든 예외는 `ParserError`로 감싸 상위로 전파한다.
- 처리 대상 예외: `FileNotFoundError`, `PermissionError`, `pd.errors.ParserError`, `pd.errors.EmptyDataError`, 그 외 xlsx 파싱 중 발생하는 `Exception`.
- 오류 메시지는 발생 원인을 식별할 수 있도록 원본 예외 정보를 포함한다.
- 기존의 확장자 검사 및 컬럼 누락 검사 로직은 변경하지 않는다.

### 2. AI 답글 오류 메시지 개선

- `ReviewCardWidget._on_reply_error(message: str)` 슬롯이 `message` 파라미터를 활용하여 오류 원인을 함께 표시한다.
- 화면에 표시되는 형식: `"답글 생성 실패. 다시 시도해 주세요.\n오류: {message}"`
- 기존 `_ERROR_GENERAL` 상수는 기본 메시지로 유지하고, 오류 원인을 덧붙이는 방식으로 조합한다.
- `_on_reply_auth_error()` 슬롯의 메시지(`_ERROR_API_KEY`) 및 동작은 변경하지 않는다.

## Gap Analysis

| 위치 | 현재 상태 | 목표 상태 |
| :--- | :--- | :--- |
| `ReviewParser.parse()` | pandas 읽기 예외 미처리 → 앱 크래시 | `ParserError`로 감싸 `QMessageBox`로 안내 |
| `ReviewCardWidget._on_reply_error()` | 오류 메시지 무시, 범용 텍스트만 표시 | 원본 오류 원인을 메시지에 포함하여 표시 |

## Architecture

이 트랙에서는 새로운 모듈이나 클래스를 추가하지 않습니다. 기존 컴포넌트의 예외 처리 로직만 보강합니다.

```
[ReviewParser.parse()]
  └── pd.read_csv() / pd.read_excel() 예외 → ParserError 변환
        └── MainWindow._on_file_selected() 에서 기존 QMessageBox.warning으로 표시

[ReplyWorker.run()] ─ (기존 그대로) ─▶ signals.error(str) 발행
  └── ReviewCardWidget._on_reply_error(message)
        └── 오류 원인 포함 문자열을 _error_label에 표시
```

## Directory Structure

이 트랙에서 수정되는 파일 목록입니다.

```text
replyreview/
└── parser/
    └── review_parser.py          # 수정: pd.read_csv/read_excel 예외 처리 추가
└── gui/
    └── review_card_widget.py     # 수정: _on_reply_error에서 message 파라미터 활용

tests/
└── parser/
    └── test_review_parser.py     # 수정: 파일 읽기 예외 테스트 케이스 추가
└── gui/
    └── test_review_card_widget.py # 수정: 일반 오류 메시지 검증 케이스 업데이트
```

## Testing Strategy

- **`ReviewParser`**: `pytest`의 `tmp_path` fixture와 `monkeypatch`를 활용하여 pandas 읽기 예외가 `ParserError`로 올바르게 변환되는지 검증합니다.
- **`ReviewCardWidget`**: 기존 `test_error_label_shown_on_general_error` 테스트를 업데이트하여 오류 원인 포함 메시지 형식을 검증합니다. `FakeAIClient(raise_error=...)` 패턴을 그대로 사용합니다.

## Acceptance Criteria

- [x] 손상된 CSV 파일(또는 읽기 불가 파일) 로드 시 앱이 크래시 없이 `QMessageBox`로 오류를 안내한다.
- [x] AI 답글 생성 실패 시 카드의 오류 레이블에 `"답글 생성 실패. 다시 시도해 주세요.\n오류: {원인}"` 형식의 메시지가 표시된다.
- [x] `uv run pytest` 전체 테스트가 통과한다.
- [x] `uv run pyright` 타입 체크 오류가 없다.
