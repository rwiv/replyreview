# GUI Module

## 모듈 역할

`gui` 모듈은 **Presentation Layer**로서 PySide6를 기반한 사용자 인터페이스를 제공합니다.

이 모듈의 핵심 설계 원칙:
- **UI 렌더링과 이벤트 처리만 담당**: 위젯 생성, 레이아웃 배치, 사용자 입력 처리
- **비즈니스 로직 제외**: 데이터 파싱, 설정 파일 I/O, API 통신 등은 다른 계층에서 담당
- **의존성 주입(DI) 패턴**: 필요한 객체(예: `ConfigManager`)를 생성자에서 주입받아 테스트 용이성 확보

이를 통해 UI 로직과 비즈니스 로직을 명확히 분리하고, 각 계층을 독립적으로 테스트할 수 있습니다.

## 핵심 컴포넌트

### MainWindow

`MainWindow`는 애플리케이션의 루트 윈도우로, 현재 및 미래의 핵심 UI를 수용하는 컨테이너 역할을 합니다.

#### 구성 요소

- **윈도우 설정** (`_setup_window`):
  - 제목: "ReplyReview"
  - 크기: 900×600 픽셀

- **툴바** (`_setup_toolbar`):
  - "설정" 버튼: 클릭 시 SettingsDialog를 모달로 열기

- **중앙 영역** (`_setup_central_widget`):
  - 현재: 플레이스홀더 `QLabel` ("리뷰 데이터 파일을 불러와 주세요.")
  - 향후: Track 1.2에서 리뷰 카드 리스트 뷰로 교체 예정

#### 책임

- `ConfigManager` 인스턴스를 생성하여 보유
- 하위 다이얼로그(SettingsDialog)에 `ConfigManager`를 주입하여 설정 관리 기능 제공
- 앱 실행 시 메인 윈도우를 표시

#### 생성자

```python
def __init__(self) -> None:
    self._config_manager = ConfigManager()
    self._setup_window()
    self._setup_toolbar()
    self._setup_central_widget()
```

### SettingsDialog

`SettingsDialog`는 OpenAI API 키를 입력받고 저장하는 모달 다이얼로그입니다.

#### 책임

- API 키 입력 필드 제공 (마스킹 적용)
- 다이얼로그 열 시 기존 API 키 자동 로드
- 저장 버튼 클릭 시 입력값을 `ConfigManager`에 저장하고 다이얼로그 닫기

#### 생성자

```python
def __init__(self, config_manager: ConfigManager, parent=None) -> None:
    self._config_manager = config_manager
    self._setup_ui()
    self._load_api_key()
```

- `config_manager`: 설정 관리를 담당하는 객체 (의존성 주입)
- `parent`: Qt 부모 위젯 (모달 다이얼로그로 표시 시 필요)

#### UI 구성

- **레이블**: "OpenAI API 키"
- **입력 필드** (`QLineEdit`):
  - 에코 모드: `Password` (입력 마스킹)
  - 플레이스홀더: "sk-..."
- **저장 버튼** (`QPushButton`):
  - 클릭 시 `_save_api_key()` 호출

#### 주요 메서드

##### _load_api_key()

```python
def _load_api_key(self) -> None:
    self._api_key_input.setText(self._config_manager.get_api_key())
```

생성자에서 호출되어 기존 API 키를 입력 필드에 로드합니다.

##### _save_api_key()

```python
@Slot()
def _save_api_key(self) -> None:
    self._config_manager.set_api_key(self._api_key_input.text())
    self.accept()
```

저장 버튼 클릭 시 입력된 키를 `ConfigManager`에 저장하고 `accept()`를 호출하여 다이얼로그를 닫습니다.

## 시그널/슬롯 연결 구조

### 설정 다이얼로그 열기 흐름

```
MainWindow._setup_toolbar()
    ↓
[설정 버튼 생성]
    ↓
settings_button.clicked.connect(self._open_settings_dialog)
    ↓
MainWindow._open_settings_dialog()
    ↓
dialog = SettingsDialog(config_manager=self._config_manager, parent=self)
dialog.exec()  [모달 실행]
    ↓
SettingsDialog._load_api_key()  [기존 키 로드]
```

### API 키 저장 흐름

```
SettingsDialog._setup_ui()
    ↓
[저장 버튼 생성]
    ↓
save_button.clicked.connect(self._save_api_key)
    ↓
SettingsDialog._save_api_key()
    ↓
self._config_manager.set_api_key(...)  [키 저장]
self.accept()  [다이얼로그 닫기]
```

## 테스트

### 테스트 파일

테스트는 `tests/gui/test_settings_dialog.py`에 작성됩니다.

### 테스트 도구

- **`pytest-qt` (`qtbot`)**: PySide6 위젯의 인스턴스화, 이벤트 시뮬레이션, 위젯 상태 검증을 자동화합니다.

### 테스트 전략

- **임시 경로 사용**: `ConfigManager`를 `tmp_path`로 초기화하여 실제 `config.json` 파일과 격리
- **상호작용 시뮬레이션**:
  - 입력 필드에 텍스트 입력: `qtbot.keyClicks()`
  - 버튼 클릭: `qtbot.mouseClick()`
- **상태 검증**:
  - 저장 후 `ConfigManager`에 데이터가 반영되었는지 확인
  - 다이얼로그가 정상적으로 열렸는지 확인

### 예시

```python
def test_save_button_persists_api_key(
    qtbot: QtBot, dialog: SettingsDialog, config_manager: ConfigManager
) -> None:
    # 입력 필드에 키 입력
    qtbot.keyClicks(dialog._api_key_input, "sk-test-key")
    
    # 저장 버튼 클릭
    buttons = dialog.findChildren(QPushButton)
    save_button = next((btn for btn in buttons if btn.text() == "저장"), None)
    qtbot.mouseClick(save_button, 1)
    
    # ConfigManager에 저장 확인
    assert config_manager.get_api_key() == "sk-test-key"
```

### 테스트 실행

```bash
uv run pytest tests/gui/test_settings_dialog.py -v
```

## 의존성

- **`PySide6`**: GUI 프레임워크
- **`replyreview.config.ConfigManager`**: 설정 관리

## 관련 문서

- `docs/tech-spec.md` - 1절: 시스템 아키텍처 (Presentation Layer 설명)
- `replyreview/config/README.md` - ConfigManager 명세
- `replyreview/__main__.py` - 앱 엔트리포인트
