# GUI Module

## 1. 모듈 개요

`gui` 모듈은 **Presentation Layer**로서 PySide6를 기반한 사용자 인터페이스를 제공합니다.

이 모듈의 핵심 설계 원칙:
- **UI 렌더링과 이벤트 처리만 담당**: 위젯 생성, 레이아웃 배치, 사용자 입력 처리
- **비즈니스 로직 제외**: 데이터 파싱, 설정 파일 I/O, API 통신 등은 다른 계층에서 담당
- **의존성 주입(DI) 패턴**: 필요한 객체(예: `ConfigManager`)를 생성자에서 주입받아 테스트 용이성 확보

이를 통해 UI 로직과 비즈니스 로직을 명확히 분리하고, 각 계층을 독립적으로 테스트할 수 있습니다.

## 2. 관련 문서

- `docs/tech-spec.md` - 1절: 시스템 아키텍처 (Presentation Layer 설명)
- `replyreview/config/README.md` - ConfigManager 명세
- `replyreview/__main__.py` - 앱 엔트리포인트

## 3. 의존성

- **`PySide6`**: GUI 프레임워크
- **`replyreview.config.ConfigManager`**: 설정 관리

## 4. 핵심 컴포넌트

### MainWindow

`MainWindow`는 애플리케이션의 루트 윈도우로, 핵심 UI를 수용하는 컨테이너 역할을 합니다. (`replyreview/gui/main_window.py`)

- `ConfigManager`와 `ReviewParser` 인스턴스를 생성하여 보유하며, 앱 시작 시 `FileLoadView`를 중앙 위젯으로 표시합니다.
- 파일이 선택되면 `ReviewParser`로 파일을 파싱하고 `ReviewListView`로 뷰를 전환합니다.
- 툴바의 "설정" 버튼 클릭 시 `ConfigManager`를 주입한 `SettingsDialog`를 모달로 엽니다.

### FileLoadView

`FileLoadView`는 파일이 로드되지 않은 초기 상태에서 표시되는 위젯입니다. (`replyreview/gui/file_load_view.py`)

- 안내 문구와 파일 불러오기 버튼으로 구성되며, 파일 탐색기에서 `.csv`/`.xlsx` 파일을 선택하면 `file_selected(str)` 시그널로 경로를 emit합니다.
- 취소 시 아무 동작도 하지 않습니다.
- **시그널** `file_selected(str)`: 사용자가 선택한 파일 경로를 `MainWindow`로 전달

### ReviewCardWidget

`ReviewCardWidget`은 단일 `ReviewData`를 카드 형태로 렌더링하는 위젯입니다. (`replyreview/gui/review_card_widget.py`)

- 별점(★/☆), 고객명, 상품명을 헤더에 표시하고 리뷰 원문을 본문에 렌더링합니다.
- 하단에는 AI 답글 생성 버튼이 있으며, 클릭 시 `ReplyWorker`를 통해 비동기로 답글을 생성하고 결과를 화면에 표시합니다.

### ReviewListView

`ReviewListView`는 파싱된 `ReviewData` 목록을 스크롤 가능한 카드 목록으로 시각화하는 위젯입니다. (`replyreview/gui/review_list_view.py`)

- `list[ReviewData]`를 받아 각 항목을 `ReviewCardWidget`으로 렌더링하고, `QScrollArea`로 세로 스크롤을 제공합니다.

### SettingsDialog

`SettingsDialog`는 OpenAI API 키를 입력받고 저장하는 모달 다이얼로그입니다. (`replyreview/gui/settings_dialog.py`)

- `ConfigManager`를 주입받아 다이얼로그 열 시 기존 API 키를 입력 필드에 자동 로드하고, 저장 버튼 클릭 시 입력값을 `ConfigManager`에 저장하고 닫힙니다.
- 입력 필드는 Password 에코 모드로 마스킹을 적용합니다.

## 5. 시그널/슬롯 연결 구조

### 파일 선택 및 파싱 흐름

```
MainWindow._setup_central_widget()
    ↓
[FileLoadView 생성]
    ↓
file_load_view.file_selected.connect(self._on_file_selected)
    ↓
MainWindow.setCentralWidget(file_load_view)
```

### 파일 선택 후 뷰 전환 흐름

```
FileLoadView._open_file_dialog()
    ↓
[사용자가 파일 선택]
    ↓
file_selected.emit(file_path)
    ↓
MainWindow._on_file_selected(file_path)
    ↓
ReviewParser.parse(file_path)  [파일 파싱]
    ↓
success:  setCentralWidget(ReviewListView(reviews))  [뷰 전환]
error:    QMessageBox.warning(...)  [오류 안내]
```

### 파일 탐색기 열기 흐름

```
FileLoadView._load_button.clicked
    ↓
FileLoadView._open_file_dialog()
    ↓
QFileDialog.getOpenFileName()  [.csv, .xlsx 필터 적용]
    ↓
path = 사용자 선택 경로 (또는 빈 문자열)
    ↓
if path:  file_selected.emit(path)
```

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

## 6. 테스트

### 테스트 파일

테스트는 `tests/gui/` 디렉터리 내부에 작성됩니다.

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

