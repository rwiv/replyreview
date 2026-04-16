# Parser Module

## 모듈 역할

`parser` 모듈은 **Business Logic Layer**로서 CSV/Excel 파일 I/O와 도메인 모델 변환을 캡슐화합니다. 이 모듈의 핵심 설계 원칙:

- **파일 포맷 추상화**: GUI 계층이 `pandas`에 직접 의존하지 않도록 파일 파싱 로직을 분리
- **도메인 모델 변환**: 스프레드시트의 행(Row)을 `ReviewData` 도메인 객체로 변환
- **오류 처리**: 지원하지 않는 확장자나 필수 컬럼 누락 시 명확한 `ParserError`를 raise

이를 통해 파싱 로직을 한곳에 집중시키고, GUI와 데이터 처리를 명확히 분리합니다.

## 핵심 컴포넌트

### ReviewParser

`ReviewParser` 클래스는 CSV/Excel 파일 파싱의 유일한 진입점입니다.

#### 공개 메서드

##### parse(file_path: str) -> list[ReviewData]

```python
def parse(self, file_path: str) -> list[ReviewData]:
    """
    주어진 파일 경로의 CSV 또는 Excel 파일을 파싱하여 ReviewData 리스트를 반환한다.
    지원하지 않는 확장자 또는 필수 컬럼 누락 시 ParserError를 raise한다.
    """
```

- 파일 확장자를 검사하여 지원하지 않으면 즉시 `ParserError`를 raise합니다 (early exit).
- `.csv` 파일은 `pd.read_csv`, `.xlsx` 파일은 `pd.read_excel`로 읽습니다.
- 필수 컬럼(`상품명`, `고객명`, `별점`, `리뷰 내용`) 누락 시 `ParserError`를 raise합니다.
- 각 행을 `ReviewData` 도메인 객체로 변환합니다.

**예시:**

```python
parser = ReviewParser()
reviews = parser.parse("/path/to/reviews.csv")
for review in reviews:
    print(review.product_name, review.rating)
```

### ParserError

`ParserError`는 파싱 실패 시 raise되는 커스텀 예외입니다.

#### Raise 조건

- **지원하지 않는 확장자**: `.csv`, `.xlsx` 이외의 파일 확장자
  - 예: "지원하지 않는 파일 형식입니다: .txt"
- **필수 컬럼 누락**: 요구되는 컬럼 중 하나 이상이 DataFrame에 없음
  - 예: "필수 컬럼이 누락되었습니다: ['별점', '리뷰 내용']"

**예시:**

```python
try:
    reviews = parser.parse("/path/to/invalid.txt")
except ParserError as e:
    print(f"파싱 오류: {e}")
```

## 지원 컬럼 매핑

CSV/Excel 파일의 컬럼명과 `ReviewData` 필드명의 매핑입니다.

| CSV/Excel 컬럼 | ReviewData 필드 | 타입 | 설명 |
| :--- | :--- | :--- | :--- |
| 상품명 | `product_name` | `str` | 구매한 상품의 이름 |
| 고객명 | `customer_name` | `str` | 리뷰를 작성한 고객명 |
| 별점 | `rating` | `int` | 별점 (1~5) |
| 리뷰 내용 | `content` | `str` | 리뷰의 본문 내용 |

### 예시 CSV

```csv
상품명,고객명,별점,리뷰 내용
에어팟 프로 케이스,김땡땡,5,배송이 빠르고 상품이 너무 예뻐요!
맨투맨,이순신,4,사이즈가 딱 맞고 편해요.
```

## 테스트

### 테스트 파일

테스트는 `tests/parser/test_review_parser.py`에 작성됩니다.

### 테스트 전략

- **실제 파일 I/O 기반**: `pytest`의 `tmp_path` fixture를 사용하여 임시 CSV/Excel 파일을 생성하고 실제 파일 I/O를 수행합니다.
- **외부 의존성 없음**: 실제 파일 시스템에 테스트 데이터를 쓰지만, 테스트 완료 후 자동으로 정리됩니다.
- **주요 케이스**:
  - CSV 파일 정상 파싱
  - Excel 파일 정상 파싱
  - rating이 int로 변환됨
  - 지원하지 않는 확장자 시 `ParserError` 발생
  - 필수 컬럼 누락 시 `ParserError` 발생
  - 여러 행 파싱

### 실행

```bash
uv run pytest tests/parser/test_review_parser.py -v
```

## 의존성

- **`pandas`**: CSV/Excel 파일 읽기 및 DataFrame 처리
- **`openpyxl`**: Excel 파일 처리 (pandas가 내부적으로 사용)
- **`replyreview.models.ReviewData`**: 도메인 모델

## 관련 문서

- `docs/tech-spec.md` - 3절: 데이터 모델 및 파싱 명세
- `replyreview/models.py` - `ReviewData` 도메인 모델 정의
