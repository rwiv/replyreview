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
    return pd.DataFrame(
        {
            "상품명": ["에어팟 프로 케이스"],
            "고객명": ["김땡땡"],
            "별점": [5],
            "리뷰 내용": ["배송이 빠르고 좋아요!"],
        }
    )


class TestReviewParser:
    def test_parse_csv_returns_review_list(
        self, parser: ReviewParser, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """유효한 CSV 파일을 파싱하면 ReviewData 리스트가 반환되는지 검증한다."""
        csv_path = tmp_path / "reviews.csv"
        sample_df.to_csv(csv_path, index=False)

        result = parser.parse(str(csv_path))

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ReviewData)
        assert result[0].product_name == "에어팟 프로 케이스"
        assert result[0].customer_name == "김땡땡"
        assert result[0].rating == 5
        assert result[0].content == "배송이 빠르고 좋아요!"

    def test_parse_excel_returns_review_list(
        self, parser: ReviewParser, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """유효한 Excel 파일을 파싱하면 ReviewData 리스트가 반환되는지 검증한다."""
        excel_path = tmp_path / "reviews.xlsx"
        sample_df.to_excel(excel_path, index=False)

        result = parser.parse(str(excel_path))

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ReviewData)

    def test_rating_is_converted_to_int(
        self, parser: ReviewParser, sample_df: pd.DataFrame, tmp_path: Path
    ) -> None:
        """파싱된 ReviewData의 rating 필드가 int 타입인지 검증한다."""
        csv_path = tmp_path / "reviews.csv"
        sample_df.to_csv(csv_path, index=False)

        result = parser.parse(str(csv_path))

        assert isinstance(result[0].rating, int)
        assert result[0].rating == 5

    def test_parse_raises_on_unsupported_extension(
        self, parser: ReviewParser, tmp_path: Path
    ) -> None:
        """지원하지 않는 확장자(.txt 등) 파일 입력 시 ParserError가 발생하는지 검증한다."""
        txt_path = tmp_path / "reviews.txt"
        txt_path.write_text("dummy content")

        with pytest.raises(ParserError, match="지원하지 않는 파일 형식"):
            parser.parse(str(txt_path))

    def test_parse_raises_on_missing_column(
        self, parser: ReviewParser, tmp_path: Path
    ) -> None:
        """필수 컬럼이 누락된 파일 입력 시 ParserError가 발생하는지 검증한다."""
        csv_path = tmp_path / "reviews.csv"
        incomplete_df = pd.DataFrame(
            {
                "상품명": ["에어팟 프로 케이스"],
                "고객명": ["김땡땡"],
            }
        )
        incomplete_df.to_csv(csv_path, index=False)

        with pytest.raises(ParserError, match="필수 컬럼이 누락"):
            parser.parse(str(csv_path))

    def test_parse_multiple_rows(self, parser: ReviewParser, tmp_path: Path) -> None:
        """여러 행의 리뷰 데이터를 파싱하면 모두 ReviewData로 변환되는지 검증한다."""
        csv_path = tmp_path / "reviews.csv"
        multi_df = pd.DataFrame(
            {
                "상품명": ["상품1", "상품2"],
                "고객명": ["고객1", "고객2"],
                "별점": [4, 3],
                "리뷰 내용": ["좋아요", "괜찮아요"],
            }
        )
        multi_df.to_csv(csv_path, index=False)

        result = parser.parse(str(csv_path))

        assert len(result) == 2
        assert result[0].product_name == "상품1"
        assert result[1].product_name == "상품2"

    def test_parse_raises_parser_error_on_csv_read_failure(
        self, parser: ReviewParser, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        pd.read_csv 호출 시 예외가 발생하면 ParserError가 raise되는지 검증한다.
        """
        csv_path = tmp_path / "reviews.csv"
        csv_path.write_text("dummy")

        def mock_read_csv(*args, **kwargs):
            raise ValueError("CSV parsing failed")

        monkeypatch.setattr(pd, "read_csv", mock_read_csv)

        with pytest.raises(ParserError, match="파일을 읽는 중 오류가 발생했습니다"):
            parser.parse(str(csv_path))

    def test_parse_raises_parser_error_on_completely_empty_csv(
        self, parser: ReviewParser, tmp_path: Path
    ) -> None:
        """
        바이트 내용이 전혀 없는 빈 파일(write_text(""))을 입력했을 때
        pd.errors.EmptyDataError가 ParserError로 변환되는지 검증한다.
        """
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("")

        with pytest.raises(ParserError, match="파일을 읽는 중 오류가 발생했습니다"):
            parser.parse(str(csv_path))

    def test_parse_raises_parser_error_on_excel_read_failure(
        self, parser: ReviewParser, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        pd.read_excel 호출 시 예외가 발생하면 ParserError가 raise되는지 검증한다.
        """
        excel_path = tmp_path / "reviews.xlsx"
        excel_path.write_bytes(b"invalid xlsx content")

        def mock_read_excel(*args, **kwargs):
            raise ValueError("Excel parsing failed")

        monkeypatch.setattr(pd, "read_excel", mock_read_excel)

        with pytest.raises(ParserError, match="파일을 읽는 중 오류가 발생했습니다"):
            parser.parse(str(excel_path))

    def test_parse_error_chains_original_exception(
        self, parser: ReviewParser, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        ParserError가 원본 예외를 __cause__로 보존하는지(exception chaining) 검증한다.
        """
        csv_path = tmp_path / "reviews.csv"
        csv_path.write_text("dummy")

        original_error = RuntimeError("original error message")

        def mock_read_csv(*args, **kwargs):
            raise original_error

        monkeypatch.setattr(pd, "read_csv", mock_read_csv)

        with pytest.raises(ParserError) as exc_info:
            parser.parse(str(csv_path))

        assert exc_info.value.__cause__ is original_error
