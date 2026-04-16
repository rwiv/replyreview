from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewData:
    """파싱된 단일 리뷰를 나타내는 불변 데이터 클래스."""

    product_name: str
    customer_name: str
    rating: int
    content: str
