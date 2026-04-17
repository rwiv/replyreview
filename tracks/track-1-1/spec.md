# Specification: 로컬 애플리케이션 기반 구조 및 설정 시스템 구축

## Overview

이 트랙은 ReplyReview 데스크톱 애플리케이션의 실행 가능한 뼈대를 구축합니다. PySide6 기반의 메인 윈도우를 구성하고, 사용자의 OpenAI API 키를 로컬 `config.json` 파일로 안전하게 관리하는 설정 인프라와 API 키 입력 UI를 완성합니다.

이 트랙이 완료되면 앱을 실행했을 때 메인 윈도우가 표시되고, 사용자가 설정 다이얼로그를 통해 API 키를 입력·저장·자동 로드할 수 있는 상태가 됩니다.

## Requirements

### 1. 앱 엔트리포인트 및 메인 윈도우

- `uv run python -m replyreview` 명령으로 앱을 실행하면 메인 윈도우(`QMainWindow`)가 표시된다.
- 메인 윈도우는 추후 리뷰 뷰어 UI를 수용할 수 있도록 중앙 컨텐츠 영역을 갖춘다.
- 메인 윈도우 상단 툴바 또는 메뉴에 '설정' 버튼을 배치하여 설정 다이얼로그를 열 수 있다.

### 2. 설정 관리 인프라 (`config.json`)

- 앱 실행 파일 기준 경로에 `config.json` 파일을 생성 및 관리한다.
- `config.json` 읽기/쓰기 책임은 `ConfigManager` 클래스 하나에 집중한다. 다른 모듈은 파일 경로나 JSON 포맷을 직접 다루지 않는다.
- 파일이 존재하지 않거나 JSON 형식이 올바르지 않은 경우, 앱 크래시 없이 기본값(`openai_api_key: ""`)으로 초기화한다.

### 3. API 키 설정 인터페이스

- `docs/features.md` 2.1절의 설정 관리 요구사항을 충족한다.
- 설정 다이얼로그(`SettingsDialog`)에 API 키 입력 필드(`QLineEdit`)와 '저장' 버튼을 제공한다.
- 보안을 위해 API 키 입력 필드는 비밀번호 마스킹(`EchoMode.Password`)이 적용된다.
- 앱 최초 실행 시 `config.json`에 키가 있다면 설정 다이얼로그 입력 필드에 자동으로 불러온다.
- '저장' 버튼 클릭 시 입력된 키가 `config.json`에 즉시 기록된다.

## Architecture

- **`__main__.py`**: `QApplication` 인스턴스를 생성하고 `MainWindow`를 표시하는 앱 진입점.
- **`gui/` (Presentation Layer)**: PySide6 위젯 클래스를 보관합니다. 비즈니스 로직 없이 UI 렌더링과 사용자 이벤트 처리만 담당합니다.
- **`config/` (Data & Config Layer)**: `config.json` 파일 I/O를 추상화하는 `ConfigManager`를 보관합니다.

## Directory Structure

트랙 완료 후 생성 또는 수정되는 파일 목록입니다.

```text
replyreview/
├── __main__.py                      # 수정: QApplication 및 MainWindow 실행 로직
├── config/
│   ├── __init__.py                  # 신규
│   ├── config_manager.py            # 신규: ConfigManager 클래스
│   └── README.md                    # 신규: config 모듈 명세
└── gui/
    ├── __init__.py                  # 신규
    ├── main_window.py               # 신규: MainWindow 클래스
    ├── settings_dialog.py           # 신규: SettingsDialog 클래스
    └── README.md                    # 신규: gui 모듈 명세

tests/
├── config/
│   ├── __init__.py                  # 신규
│   └── test_config_manager.py       # 신규: ConfigManager 유닛 테스트
└── gui/
    ├── __init__.py                  # 신규
    └── test_settings_dialog.py      # 신규: SettingsDialog GUI 테스트
```

## Core Components

- **ConfigManager**: `config.json`에 대한 읽기/쓰기를 전담하는 클래스. 파일 부재 또는 파싱 오류 시 기본값(`{"openai_api_key": ""}`)으로 자동 복구합니다.
- **MainWindow**: 앱의 루트 윈도우. 현 트랙에서는 빈 컨텐츠 영역과 설정 진입 버튼만 제공하며, 이후 트랙에서 리뷰 뷰어 등 핵심 UI를 수용하는 컨테이너 역할을 합니다.
- **SettingsDialog**: 사용자로부터 OpenAI API 키를 입력받아 `ConfigManager`를 통해 저장하는 모달 다이얼로그.

## Testing Strategy

- **`ConfigManager`**: `pytest`의 `tmp_path` fixture를 활용하여 실제 파일 I/O 기반으로 읽기, 쓰기, 오류 복구 시나리오를 검증합니다.
- **`SettingsDialog`**: `pytest-qt`(`qtbot`)를 사용하여 위젯 인스턴스화, 입력 이벤트 시뮬레이션, 저장 흐름을 검증합니다. 테스트 실행을 위해 dev 의존성에 `pytest-qt`를 추가합니다.

## Acceptance Criteria

- [ ] `uv run python -m replyreview` 실행 시 메인 윈도우가 정상적으로 표시된다.
- [ ] 메인 윈도우에서 설정 다이얼로그를 열 수 있다.
- [ ] 설정 다이얼로그에서 API 키 입력 후 '저장' 클릭 시 `config.json`에 키가 저장된다.
- [ ] 앱 재실행 시 `config.json`에 저장된 API 키가 설정 다이얼로그에 자동으로 로드된다.
- [ ] `config.json`이 없거나 형식이 잘못된 경우 앱이 크래시 없이 기본값으로 동작한다.
- [ ] 모든 테스트(`uv run pytest`)가 통과한다.
- [ ] 타입 체크(`uv run pyright`) 오류가 없다.

