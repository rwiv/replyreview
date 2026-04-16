# Config Module

## 모듈 역할

`config` 모듈은 **Data & Config Layer**로서 ReplyReview 애플리케이션의 로컬 설정 파일(`config.json`) I/O를 캡슐화합니다.

이 모듈의 핵심 책임은:
- `config.json` 파일에 대한 읽기/쓰기를 전담
- 파일 부재 또는 JSON 파싱 오류 발생 시 기본값으로 자동 복구
- 다른 모듈이 파일 경로나 JSON 포맷을 직접 다루지 않도록 추상화

이를 통해 설정 관리의 복잡성을 한곳(`ConfigManager`)에 집중시키고, GUI 및 기타 모듈들은 `ConfigManager` 인터페이스만 의존하도록 설계합니다.

## 핵심 컴포넌트

### ConfigManager

`ConfigManager` 클래스는 `config.json` 파일 I/O의 유일한 진입점입니다.

#### 생성자

```python
def __init__(self, config_path: Path | None = None) -> None:
    """
    ConfigManager를 초기화합니다.

    @param config_path: config.json 파일의 경로. None인 경우 프로젝트 루트 기준의 기본 경로로 설정됩니다.
    """
```

- `config_path=None`일 경우 프로젝트 루트에 있는 `config.json`을 사용합니다.
- 테스트 시에는 `config_path`에 임시 경로(`tmp_path`)를 주입하여 실제 파일과 격리할 수 있습니다.

#### 공개 메서드

##### load() -> dict[str, str]

```python
def load(self) -> dict[str, str]:
    """config.json 파일을 읽어 설정 딕셔너리를 반환합니다."""
```

- 파일이 존재하면 JSON을 파싱하여 반환합니다.
- `FileNotFoundError` 발생 시 기본값(`DEFAULT_CONFIG`)을 반환합니다.
- `json.JSONDecodeError` 발생 시 기본값을 반환합니다.
- **오류를 무시하지 않고 명확한 기본값으로 복구**하는 것이 설계 원칙입니다.

##### save(data: dict[str, str]) -> None

```python
def save(self, data: dict[str, str]) -> None:
    """설정 딕셔너리를 config.json 파일에 저장합니다."""
```

- 주어진 딕셔너리를 `config.json`으로 덮어씁니다.
- JSON 직렬화 시 들여쓰기(indent=2)와 한글 인코딩(`ensure_ascii=False`)을 적용합니다.

##### get_api_key() -> str

```python
def get_api_key(self) -> str:
    """저장된 OpenAI API 키를 반환합니다."""
```

- `load().get("openai_api_key", "")`로 구현됩니다.
- 키가 없으면 빈 문자열을 반환합니다.

##### set_api_key(key: str) -> None

```python
def set_api_key(self, key: str) -> None:
    """OpenAI API 키를 저장합니다."""
```

- 현재 설정을 로드하고 `openai_api_key` 필드를 업데이트한 후 저장합니다.
- 기존 다른 설정값은 유지됩니다.

## config.json 스키마

### 파일 위치

프로젝트 루트에 위치합니다:
```
replyreview/
├── __main__.py
├── config.json    <-- 여기
├── config/
│   └── config_manager.py
└── gui/
```

### JSON 구조

```json
{
  "openai_api_key": ""
}
```

| 필드 | 타입 | 설명 | 기본값 |
|------|------|------|--------|
| `openai_api_key` | `str` | OpenAI API 키 | `""` (빈 문자열) |

### 예시

```json
{
  "openai_api_key": "sk-proj-1234567890abcdef"
}
```

## 오류 복구 정책

### FileNotFoundError

**시나리오**: `config.json` 파일이 존재하지 않음

**복구 방식**: `DEFAULT_CONFIG`를 반환
```python
DEFAULT_CONFIG = {"openai_api_key": ""}
```

**결과**: 앱이 기본값으로 정상 동작하며, 사용자가 나중에 설정 다이얼로그를 통해 API 키를 입력할 수 있습니다.

### json.JSONDecodeError

**시나리오**: `config.json`의 JSON 형식이 올바르지 않음

**복구 방식**: `DEFAULT_CONFIG`를 반환

**결과**: 마찬가지로 앱이 기본값으로 동작하며, 잘못된 파일은 다음 저장 시 올바른 형식으로 덮어씌워집니다.

## 사용 예시

### MainWindow에서 사용

```python
from replyreview.config.config_manager import ConfigManager

class MainWindow:
    def __init__(self):
        self._config_manager = ConfigManager()
        # API 키 로드 (앱 시작 시)
        api_key = self._config_manager.get_api_key()
```

### SettingsDialog에서 사용

```python
class SettingsDialog:
    def __init__(self, config_manager: ConfigManager):
        self._config_manager = config_manager
        # 기존 API 키 로드
        existing_key = self._config_manager.get_api_key()
        
    def _save_api_key(self):
        # 사용자 입력 저장
        self._config_manager.set_api_key(user_input)
```

## 테스트

### 테스트 파일

테스트는 `tests/config/test_config_manager.py`에 작성됩니다.

### 테스트 전략

- **실제 파일 I/O 기반**: `pytest`의 `tmp_path` fixture를 사용하여 임시 경로에서 실제 파일 I/O를 수행합니다.
- **외부 의존성 없음**: 실제 `config.json` 파일이나 다른 모듈에 의존하지 않고 독립적으로 실행됩니다.
- **예외 시나리오 포함**:
  - 파일 부재 시 기본값 반환 검증
  - 잘못된 JSON 형식 시 복구 검증
  - 저장/로드 순환 검증

### 실행

```bash
uv run pytest tests/config/test_config_manager.py -v
```

## 관련 문서

- `docs/tech-spec.md` - 4.3절: 설정 관리 시스템 명세
- `replyreview/gui/README.md` - GUI 모듈에서 ConfigManager 사용 방식
