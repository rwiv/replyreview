# ReplyReview

네이버 스마트스토어의 리뷰 데이터를 기반으로 OpenAI API를 활용하여 맞춤형 답글을 자동 생성하고 클립보드에 복사할 수 있는 데스크톱 애플리케이션입니다.

## 1. Overview

네이버 스마트스토어를 운영하는 셀러는 매일 다수의 고객 리뷰에 답글을 달아야 하지만, 반복적인 답글 작성은 시간과 노력이 상당히 소요됩니다. ReplyReview는 이 문제를 해결하기 위해 만들어진 데스크톱 자동화 도구입니다.

사용자는 스마트스토어에서 내보낸 리뷰 데이터(CSV/Excel)를 앱에 불러오기면, 각 리뷰의 별점·고객명·상품명·리뷰 내용을 OpenAI API가 종합 분석하여 친절하고 전문적인 쇼핑몰 고객센터 톤의 맞춤 답글을 자동 생성합니다. 생성된 답글은 카드 리스트 UI에서 즉시 확인하고 클립보드로 복사하여 바로 붙여넣기할 수 있습니다.

별도의 서버나 복잡한 설정 없이 로컬에서 동작하며, API 키는 앱 내 GUI를 통해 안전하게 관리됩니다. 반복 작업을 자동화하여 셀러가 핵심 비즈니스에 집중할 수 있도록 돕는 것이 본 프로젝트의 핵심 목적입니다.

## 2. Key Features

<img src="https://github.com/rwiv/replyreview/raw/main/assets/screenshot.png">

- **단일 파일 선택 지원**: 리뷰 데이터가 담긴 CSV 또는 Excel 파일을 선택하여 손쉽게 데이터를 로드할 수 있습니다.
- **카드 리스트 뷰 UI**: 일반적인 표 형태가 아닌, 모바일/웹 피드와 유사한 현대적이고 세련된 카드 리스트 형태로 리뷰 목록을 렌더링합니다.
- **AI 맞춤형 답글 생성**: 상품명, 고객명, 별점, 리뷰 내용을 종합적으로 분석하여 문맥에 맞는 자연스러운 답글을 생성합니다.
- **직관적인 로딩 및 에러 처리**: API 통신 중 비동기 로딩 상태("생성 중...")를 표시하며, 통신 실패 시 즉각적인 에러 메시지를 제공합니다.
- **수동 클립보드 복사**: 생성된 답글을 사용자가 직접 확인한 후 원할 때만 '클립보드 복사' 버튼을 눌러 안전하게 사용할 수 있습니다.
- **안전한 API 키 관리**: 앱 내 GUI를 통해 OpenAI API 키를 입력받아 로컬 JSON 파일(`config.json`)에 저장 및 관리합니다.

## 3. Tech Stack

- **언어**: Python 3
- **GUI 프레임워크**: PySide6 (Qt for Python)
- **AI 연동**: OpenAI API
- **빌드 도구**: PyInstaller
- **데이터 처리**: pandas (CSV 및 Excel 데이터 파싱)

## 4. Getting Started

### 4.1. 환경 설정 및 실행 방법

```bash
# 1. 저장소 클론
git clone [repository_url]
cd replyreview

# 2. 프로젝트 초기화
uv sync

# 3. 앱 실행
uv run replyreview
```

### 4.2. API 키 설정 방법

1. 앱을 처음 실행하면 상단 설정 영역 또는 설정 팝업을 통해 OpenAI API 키를 입력할 수 있습니다.
2. 입력된 키는 앱 실행 디렉토리의 `config.json`에 저장되며, 이후 실행 시 자동으로 불러옵니다.

## 5. Build (PyInstaller)

독립 실행형 애플리케이션으로 빌드하려면 아래 명령어를 사용합니다.

```bash
# macOS/Linux/Windows에서 단일 실행 파일로 빌드 (콘솔 창 숨김)
pyinstaller --noconfirm --onedir --windowed --name "ReplyReview" main.py
```

빌드가 완료되면 `dist/ReplyReview/` 디렉토리 내에 실행 파일이 생성됩니다.

## 6. Documentation

프로젝트의 상세 설계 및 기능 정의는 `docs/` 디렉토리에 위치해 있습니다.

- [명세 개요 문서 (프로젝트 개요 및 문서 인덱스)](docs/README.md)
- [기능 명세서 (기능 및 UI 요구사항)](docs/features.md)
- [기술 명세서 (아키텍처 및 시스템 요구사항)](docs/tech-spec.md)

