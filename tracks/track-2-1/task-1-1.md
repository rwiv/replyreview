# Task 1.1: ReviewParser 파일 읽기 예외 처리 강화

## Overview

`ReviewParser.parse()`의 pandas 파일 읽기 호출(`pd.read_csv`, `pd.read_excel`)을 `try/except`로 감싸, 파일 읽기 중 발생하는 모든 예외를 `ParserError`로 변환합니다. 기존에는 손상된 파일, 권한 오류, 빈 파일 등의 상황에서 예외가 상위로 전파되어 앱이 비정상 종료되었습니다. 이 Task 완료 후에는 모든 파서 오류가 `MainWindow._on_file_selected()`의 기존 `QMessageBox.warning` 처리 흐름으로 안전하게 전달됩니다.

## Related Files

### Reference Files

- `replyreview/parser/review_parser.py`: 수정 대상. 현재 `pd.read_csv`/`pd.read_excel` 예외 미처리 상태 확인
- `replyreview/gui/main_window.py`: `ParserError`를 소비하는 호출 측 — 기존 `QMessageBox.warning` 처리 흐름 파악용
- `tests/parser/test_review_parser.py`: 기존 테스트 케이스 확인 후 신규 케이스 추가

### Target Files

- `replyreview/parser/review_parser.py`: 수정 — pandas 읽기 예외 처리 추가
- `tests/parser/test_review_parser.py`: 수정 — 파일 읽기 예외 테스트 케이스 추가

## Workflow

### Step 1: pandas 읽기 호출을 `try/except`로 감싸기

`parse()` 메서드에서 확장자 검사 후 수행되는 `pd.read_csv` / `pd.read_excel` 호출을 `try/except`로 감쌉니다. 원본 예외가 디버깅에 활용될 수 있도록 exception chaining(`from e`)을 사용합니다.

```python
# replyreview/parser/review_parser.py

class ReviewParser:
    def parse(self, file_path: str) -> list[ReviewData]:
        ext = Path(file_path).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ParserError(f"지원하지 않는 파일 형식입니다: {ext}")

        try:
            df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)
        except Exception as e:
            raise ParserError(f"파일을 읽는 중 오류가 발생했습니다: {e}") from e

        # ... 이후 컬럼 누락 검사 및 ReviewData 변환 로직은 기존과 동일
```

`Exception`으로 광범위하게 처리하는 이유는 pandas와 openpyxl이 파일 형식에 따라 다양한 예외 타입(`pd.errors.ParserError`, `pd.errors.EmptyDataError`, `PermissionError`, `FileNotFoundError`, openpyxl 내부 예외 등)을 발생시키기 때문입니다. 어떤 예외든 사용자에게는 동일하게 "파일 읽기 실패"로 안내하는 것이 적절합니다.

### Step 2: 테스트 케이스 추가

`tests/parser/test_review_parser.py`의 `TestReviewParser` 클래스에 다음 테스트를 추가합니다. `monkeypatch`로 pandas 읽기 함수에 예외를 주입하여 네트워크나 실제 파일 시스템 의존 없이 검증합니다.

```python
# tests/parser/test_review_parser.py (추가 케이스)

class TestReviewParser:
    # ... 기존 테스트 유지 ...

    def test_parse_raises_parser_error_on_csv_read_failure(
        self, parser: ReviewParser, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        pd.read_csv 호출 시 예외가 발생하면 ParserError가 raise되는지 검증한다.
        """
        # ...

    def test_parse_raises_parser_error_on_completely_empty_csv(
        self, parser: ReviewParser, tmp_path: Path
    ) -> None:
        """
        바이트 내용이 전혀 없는 빈 파일(write_text(""))을 입력했을 때
        pd.errors.EmptyDataError가 ParserError로 변환되는지 검증한다.
        헤더만 있고 데이터 행이 없는 CSV는 정상 파싱되어 이 케이스에 해당하지 않는다.
        """
        # ...

    def test_parse_raises_parser_error_on_excel_read_failure(
        self, parser: ReviewParser, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        pd.read_excel 호출 시 예외가 발생하면 ParserError가 raise되는지 검증한다.
        """
        # ...

    def test_parse_error_chains_original_exception(
        self, parser: ReviewParser, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        ParserError가 원본 예외를 __cause__로 보존하는지(exception chaining) 검증한다.
        """
        # ...
```

테스트 구현 시 유의사항:
- `monkeypatch.setattr(pd, "read_csv", ...)` 패턴으로 pandas 함수를 교체합니다.
- 빈 파일 테스트는 `tmp_path / "empty.csv"`에 `write_text("")`으로 바이트가 없는 파일을 생성합니다. 헤더만 있는 파일(`write_text("상품명,고객명,별점,리뷰 내용\n")`)은 pandas가 정상 파싱하므로 `EmptyDataError`가 발생하지 않아 이 케이스에 해당하지 않습니다.
- exception chaining 검증: `pytest.raises(ParserError) as exc_info` 후 `assert exc_info.value.__cause__ is not None`으로 확인합니다.

### Step 3: 테스트 실행 확인

```bash
uv run pytest tests/parser/ -v
```

기존 테스트와 신규 테스트 모두 통과하는지 확인합니다.

## Success Criteria

- [x] `pd.read_csv` 또는 `pd.read_excel`에서 예외가 발생할 때 `ParserError`가 raise된다.
- [x] raise된 `ParserError`의 `__cause__`에 원본 예외가 보존된다 (exception chaining).
- [x] `uv run pytest tests/parser/` 전체 테스트가 통과한다.
- [x] `uv run pyright` 타입 체크 오류가 없다.
