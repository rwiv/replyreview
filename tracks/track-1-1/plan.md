# Plan: 로컬 애플리케이션 기반 구조 및 설정 시스템 구축

## Phase 1: 앱 엔트리포인트 및 메인 윈도우 구성

### Task 1.1: QApplication 엔트리포인트 및 MainWindow 구현

- [x] `replyreview/gui/` 패키지 생성 (`__init__.py` 포함)
- [x] `MainWindow` 클래스 구현 (`replyreview/gui/main_window.py`)
  - [x] `QMainWindow` 상속, 윈도우 제목·크기 설정
  - [x] 추후 리뷰 뷰어를 수용할 중앙 컨텐츠 영역(`QWidget` placeholder) 배치
  - [x] 설정 다이얼로그를 열기 위한 '설정' 버튼 배치 (툴바 또는 메뉴)
- [x] `__main__.py` 수정: `QApplication` 생성, `MainWindow` 인스턴스화 및 `show()` 호출
- [x] `uv run python -m replyreview` 실행으로 메인 윈도우 표시 확인

## Phase 2: 설정 관리 시스템 구현

### Task 2.1: ConfigManager 구현

- [x] `replyreview/config/` 패키지 생성 (`__init__.py` 포함)
- [x] `ConfigManager` 클래스 구현 (`replyreview/config/config_manager.py`)
  - [x] `load() -> dict`: `config.json` 파일 읽기; 파일 부재·JSON 오류 시 기본값 반환
  - [x] `save(data: dict) -> None`: `config.json` 파일 쓰기
  - [x] `get_api_key() -> str` / `set_api_key(key: str) -> None` 헬퍼 메서드
- [x] dev 의존성에 `pytest-qt` 추가 (`pyproject.toml`)
- [x] `ConfigManager` 유닛 테스트 작성 및 수행 (`tests/config/test_config_manager.py`)
  - [x] `tmp_path` fixture를 이용한 실제 파일 I/O 기반 검증
  - [x] 정상 저장/로드, 파일 부재 시 기본값 반환, 잘못된 JSON 복구 시나리오 포함
- [x] `config` 모듈 명세 작성 (`replyreview/config/README.md`)
  - [x] 모듈 역할, `ConfigManager` 클래스 책임, `config.json` 스키마, 오류 복구 정책 기술
- [x] 관련 문서 갱신 (`docs/tech-spec.md` — 설정 관리 섹션 구현 경로 명시)

### Task 2.2: API 키 설정 Dialog UI 구현

- [x] `SettingsDialog` 클래스 구현 (`replyreview/gui/settings_dialog.py`)
  - [x] `QDialog` 상속, API 키 입력 필드(`QLineEdit`, `EchoMode.Password`) 및 '저장' 버튼 배치
  - [x] 다이얼로그 열기 시 `ConfigManager.get_api_key()`로 저장된 키를 입력 필드에 자동 로드
  - [x] '저장' 클릭 시 `ConfigManager.set_api_key()`로 입력값 저장 후 다이얼로그 닫기
- [x] `MainWindow`에서 '설정' 버튼 클릭 시 `SettingsDialog`를 모달로 열도록 연동
- [x] `SettingsDialog` GUI 테스트 작성 및 수행 (`tests/gui/test_settings_dialog.py`)
  - [x] `qtbot`으로 입력 필드 텍스트 입력 및 저장 버튼 클릭 시뮬레이션
  - [x] 저장 후 `ConfigManager`에 키가 반영되는지 검증
  - [x] 다이얼로그 열기 시 기존 키가 자동 로드되는지 검증
- [x] `gui` 모듈 명세 작성 (`replyreview/gui/README.md`)
  - [x] 모듈 역할 및 설계 원칙(UI/비즈니스 로직 분리), `MainWindow`·`SettingsDialog` 컴포넌트 책임, 시그널/슬롯 연결 구조 기술
- [x] 관련 문서 갱신 (`docs/features.md` — 2.1절 설정 관리 구현 완료 여부 반영)
