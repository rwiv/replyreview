# Task 1.1: ReviewData 모델 및 ReviewParser 구현

## Overview

공유 데이터 모델인 `ReviewData` frozen dataclass와 CSV/Excel 파일을 파싱하는 `ReviewParser`를 구현합니다. `pandas`를 통해 파일을 읽고, 지원하지 않는 확장자나 필수 컬럼 누락 시 `ParserError`를 raise합니다.

이 Task는 실제 파일 I/O 기반 단위 테스트로 검증하고, `parser` 모듈 명세 문서를 작성합니다.

## Related Files

### Reference Files

- `docs/tech-spec.md`: 3절 데이터 모델 및 파싱 명세 참조
- `replyreview/config/config_manager.py`: 패키지·클래스 구조 스타일 참조용

### Target Files

- `replyreview/models.py`: 신규 — `ReviewData` frozen dataclass
- `replyreview/parser/__init__.py`: 신규 — `parser` 패키지 초기화
- `replyreview/parser/review_parser.py`: 신규 — `ReviewParser` 클래스, `ParserError`
- `replyreview/parser/README.md`: 신규 — `parser` 모듈 명세
- `tests/parser/__init__.py`: 신규 — 테스트 패키지 초기화
- `tests/parser/test_review_parser.py`: 신규 — `ReviewParser` 단위 테스트
- `docs/tech-spec.md`: 수정 — 데이터 모델 구현 경로 명시

## Workflow

### Step 1: ReviewData 모델 정의

`replyreview/models.py`에 `ReviewData` dataclass를 정의합니다.

- `frozen=True`로 불변성을 보장합니다. GUI와 파서 계층이 모두 참조하는 공유 도메인 모델입니다.
- `rating`은 1~5의 정수이며, 파서에서 `int` 변환을 담당합니다.

```python
# replyreview/models.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewData:
    """파싱된 단일 리뷰를 나타내는 불변 데이터 클래스."""

    product_name: str
    customer_name: str
    rating: int  # 1~5
    content: str
```

### Step 2: `parser/` 패키지 생성

`replyreview/parser/` 디렉터리를 생성하고 빈 `__init__.py`를 추가합니다. 테스트 패키지 `tests/parser/`도 동일하게 생성합니다.

### Step 3: ReviewParser 및 ParserError 구현

`replyreview/parser/review_parser.py`에 `ReviewParser` 클래스와 `ParserError` 예외를 구현합니다.

- `parse()`는 확장자를 먼저 확인하고, 지원하지 않으면 즉시 `ParserError`를 raise합니다 (early exit).
- 필수 컬럼 누락 검사는 `pandas` DataFrame을 읽은 직후 수행합니다.
- `rating`은 `int()` 변환 시 실패할 수 있으므로 각 행마다 안전하게 처리합니다.

```python
# replyreview/parser/review_parser.py
from pathlib import Path

import pandas as pd

from replyreview.models import ReviewData

# 파서가 지원하는 파일 확장자 목록
SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}

# CSV/Excel 컬럼명과 ReviewData 필드명의 매핑
COLUMN_MAP: dict[str, str] = {
    "상품명": "product_name",
    "고객명": "customer_name",
    "별점": "rating",
    "리뷰 내용": "content",
}


class ParserError(Exception):
    """지원하지 않는 파일 형식이거나 필수 컬럼이 누락된 경우 raise되는 커스텀 예외."""


class ReviewParser:
    """CSV/Excel 파일을 읽어 ReviewData 리스트로 변환하는 파서."""

    def parse(self, file_path: str) -> list[ReviewData]:
        """
        주어진 파일 경로의 CSV 또는 Excel 파일을 파싱하여 ReviewData 리스트를 반환한다.
        지원하지 않는 확장자 또는 필수 컬럼 누락 시 ParserError를 raise한다.
        """
        ext = Path(file_path).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise ParserError(f"지원하지 않는 파일 형식입니다: {ext}")

        df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)

        missing = [col for col in COLUMN_MAP if col not in df.columns]
        if missing:
            raise ParserError(f"필수 컬럼이 누락되었습니다: {missing}")

        # ... 각 행을 ReviewData로 변환하여 리스트 반환
        return [
            ReviewData(
                product_name=str(row["상품명"]),
                customer_name=str(row["고객명"]),
                rating=int(row["별점"]),
                content=str(row["리뷰 내용"]),
            )
            for _, row in df.iterrows()
        ]
```

### Step 4: ReviewParser 단위 테스트 작성 및 수행

`tests/parser/test_review_parser.py`에 테스트를 작성합니다. `tmp_path` fixture로 임시 파일을 생성하여 실제 파일 I/O를 수행하되 프로젝트 루트를 오염시키지 않습니다.

```python
# tests/parser/test_review_parser.py
from pathlib import Path

import pandas as pd
import pytest

from replyreview.models import ReviewData
from replyreview.parser.review_parser import ParserError, ReviewParser


@pytest.fixture
def parser() -> ReviewParser:
    """테스트용 ReviewParser 인스턴스를 반환하는 fixture."""
    return ReviewParser()


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """유효한 리뷰 데이터를 포함한 DataFrame fixture."""
    return pd.DataFrame({
        "상품명": ["에어팟 프로 케이스"],
        "고객명": ["김땡땡"],
        "별점": [5],
        "리뷰 내용": ["배송이 빠르고 좋아요!"],
    })


class TestReviewParser:
    def test_parse_csv_returns_review_list(self, parser: ReviewParser, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        """
        유효한 CSV 파일을 파싱하면 ReviewData 리스트가 반환되는지 검증한다.
        """
        # ...

    def test_parse_excel_returns_review_list(self, parser: ReviewParser, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        """
        유효한 Excel 파일을 파싱하면 ReviewData 리스트가 반환되는지 검증한다.
        """
        # ...

    def test_rating_is_converted_to_int(self, parser: ReviewParser, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        """
        파싱된 ReviewData의 rating 필드가 int 타입인지 검증한다.
        """
        # ...

    def test_parse_raises_on_unsupported_extension(self, parser: ReviewParser, tmp_path: Path) -> None:
        """
        지원하지 않는 확장자(.txt 등) 파일 입력 시 ParserError가 발생하는지 검증한다.
        """
        # ...

    def test_parse_raises_on_missing_column(self, parser: ReviewParser, tmp_path: Path) -> None:
        """
        필수 컬럼이 누락된 파일 입력 시 ParserError가 발생하는지 검증한다.
        """
        # ...
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/parser/
```

### Step 5: `parser` 모듈 명세 작성

`replyreview/parser/README.md`에 모듈 명세를 작성합니다. 아래 항목을 포함해야 합니다.

- **모듈 역할**: Business Logic Layer로서 CSV/Excel 파일 I/O와 도메인 모델 변환을 캡슐화하며, GUI 계층이 `pandas`에 직접 의존하지 않도록 추상화하는 역할 기술.
- **핵심 컴포넌트**:
  - `ReviewParser`: 공개 메서드 `parse(file_path: str) -> list[ReviewData]` 역할 기술.
  - `ParserError`: raise 조건(지원하지 않는 확장자, 필수 컬럼 누락) 기술.
- **지원 컬럼 매핑**: `COLUMN_MAP` 기반의 컬럼명 → 필드명 매핑 테이블 기술.
- **테스트**: `tests/parser/test_review_parser.py` 경로 및 `tmp_path` 기반 파일 I/O 테스트 전략 기술.

### Step 6: `docs/tech-spec.md` 갱신

`docs/tech-spec.md` 3절 데이터 모델 항목에 구현 파일 경로(`replyreview/models.py`, `replyreview/parser/review_parser.py`)를 추가하여 명세와 구현을 연결합니다.

## Success Criteria

- [x] `uv run pytest tests/parser/` 테스트가 모두 통과한다.
- [x] `uv run pyright` 타입 체크 오류가 없다.
- [x] 지원하지 않는 확장자 파일 경로 입력 시 `ParserError`가 raise된다.
- [x] 필수 컬럼이 누락된 파일 입력 시 `ParserError`가 raise된다.
- [x] `replyreview/parser/README.md`가 모듈 역할, 컴포넌트, 컬럼 매핑, 테스트 전략을 포함하여 작성되었다.
