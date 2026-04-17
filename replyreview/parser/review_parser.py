from pathlib import Path

import pandas as pd

from replyreview.models import ReviewData

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}

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

        try:
            df = pd.read_csv(file_path) if ext == ".csv" else pd.read_excel(file_path)
        except Exception as e:
            raise ParserError(f"파일을 읽는 중 오류가 발생했습니다: {e}") from e

        missing = [col for col in COLUMN_MAP if col not in df.columns]
        if missing:
            raise ParserError(f"필수 컬럼이 누락되었습니다: {missing}")

        reviews = []
        for row_dict in df.to_dict("records"):
            reviews.append(
                ReviewData(
                    product_name=str(row_dict["상품명"]),
                    customer_name=str(row_dict["고객명"]),
                    rating=int(row_dict["별점"]),
                    content=str(row_dict["리뷰 내용"]),
                )
            )
        return reviews
