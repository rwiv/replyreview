# 네이버 스마트스토어 리뷰 AI 답글 생성기 (ReplyReview)

네이버 스마트스토어의 리뷰 데이터를 기반으로 OpenAI API를 활용하여 맞춤형 답글을 자동 생성하고 클립보드에 복사할 수 있는 데스크톱 애플리케이션입니다.

## 1. 프로젝트 개요 및 목적

파일 드래그 앤 드롭을 통한 간편한 데이터 입력과, 수려한 카드 리스트 뷰 UI를 통해 직관적인 사용자 경험(UX)을 제공합니다.

## 2. 주요 기능

*   **파일 드래그 앤 드롭 지원**: 리뷰 데이터가 담긴 CSV 또는 Excel 파일을 앱 화면에 끌어다 놓아 손쉽게 데이터를 로드할 수 있습니다.
*   **카드 리스트 뷰 UI**: 일반적인 표 형태가 아닌, 모바일/웹 피드와 유사한 현대적이고 세련된 카드 리스트 형태로 리뷰 목록을 렌더링합니다.
*   **AI 맞춤형 답글 생성**: 상품명, 고객명, 별점, 리뷰 내용을 종합적으로 분석하여 문맥에 맞는 자연스러운 답글을 생성합니다.
*   **직관적인 로딩 및 에러 처리**: API 통신 중 비동기 로딩 상태("생성 중...")를 표시하며, 통신 실패 시 즉각적인 에러 메시지를 제공합니다.
*   **수동 클립보드 복사**: 생성된 답글을 사용자가 직접 확인한 후 원할 때만 '클립보드 복사' 버튼을 눌러 안전하게 사용할 수 있습니다.
*   **안전한 API 키 관리**: 앱 내 GUI를 통해 OpenAI API 키를 입력받아 로컬 JSON 파일(`config.json`)에 저장 및 관리합니다.

## 3. 기술 스택

*   **언어**: Python 3
*   **GUI 프레임워크**: PySide6 (Qt for Python)
*   **AI 연동**: OpenAI API
*   **빌드 도구**: PyInstaller
*   **데이터 처리**: `pandas` (CSV 및 Excel 데이터 파싱)

## 4. 시작하기 (Getting Started)

### 4.1. 환경 설정 및 실행 방법

```bash
# 1. 저장소 클론
git clone [repository_url]
cd replyreview

# 2. 가상환경 생성 및 활성화 (선택 사항)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. 의존성 설치 (uv 또는 pip 사용)
pip install -r requirements.txt # 또는 uv 활용

# 4. 앱 실행
python main.py
```

### 4.2. API 키 설정 방법

1.  앱을 처음 실행하면 상단 설정 영역 또는 설정 팝업을 통해 OpenAI API 키를 입력할 수 있습니다.
2.  입력된 키는 앱 실행 디렉토리의 `config.json`에 저장되며, 이후 실행 시 자동으로 불러옵니다.

## 5. 앱 빌드 (PyInstaller)

독립 실행형 애플리케이션으로 빌드하려면 아래 명령어를 사용합니다.

```bash
# macOS/Linux/Windows에서 단일 실행 파일로 빌드 (콘솔 창 숨김)
pyinstaller --noconfirm --onedir --windowed --name "ReplyReview" main.py
```

빌드가 완료되면 `dist/ReplyReview/` 디렉토리 내에 실행 파일이 생성됩니다.

## 6. 명세서 문서 목록

프로젝트의 상세 설계 및 기능 정의는 `docs/` 디렉토리에 위치해 있습니다.

*   [문서 구조 개요 (Index)](docs/README.md)
*   [기능 명세서 (기능 및 UI 요구사항)](docs/features.md)
*   [기술 명세서 (아키텍처 및 시스템 요구사항)](docs/tech-spec.md)
