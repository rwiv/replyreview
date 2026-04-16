# Task 2.1: ConfigManager 구현

## Overview

`config.json` 파일에 대한 읽기/쓰기를 전담하는 `ConfigManager` 클래스를 구현합니다. 이 클래스는 앱 전역에서 설정에 접근하는 유일한 통로로, 파일 부재·JSON 오류 등 예외 상황 시 기본값으로 자동 복구합니다. 실제 파일 I/O 기반의 통합 테스트로 검증하고, `config` 모듈 명세 문서를 작성합니다.

## Related Files

### Reference Files

- `docs/tech-spec.md`: 4.3절 설정 관리 — `config.json` 스키마 및 예외 처리 정책 참조
- `replyreview/gui/main_window.py`: ConfigManager를 소비하는 호출 측 인터페이스 파악용

### Target Files

- `replyreview/config/__init__.py`: 신규 — `config` 패키지 초기화
- `replyreview/config/config_manager.py`: 신규 — `ConfigManager` 클래스
- `replyreview/config/README.md`: 신규 — `config` 모듈 명세
- `tests/config/__init__.py`: 신규 — 테스트 패키지 초기화
- `tests/config/test_config_manager.py`: 신규 — `ConfigManager` 통합 테스트
- `pyproject.toml`: 수정 — `pytest-qt` dev 의존성 추가
- `docs/tech-spec.md`: 수정 — 설정 관리 섹션에 구현 파일 경로 명시

## Workflow

### Step 1: `config/` 패키지 생성

`replyreview/config/` 디렉터리를 생성하고 빈 `__init__.py`를 추가합니다. 테스트 패키지 `tests/config/`도 동일하게 생성합니다.

### Step 2: `ConfigManager` 클래스 구현

`replyreview/config/config_manager.py` 파일에 `ConfigManager` 클래스를 구현합니다.

- 생성자에서 `config_path`를 주입받아 테스트 시 임시 경로로 교체 가능하도록 설계합니다.
- `load()`는 파일 읽기 실패(`FileNotFoundError`) 및 파싱 실패(`json.JSONDecodeError`) 시 기본값 딕셔너리를 반환합니다. 오류를 삼키지 않고 기본값으로 명확히 복구하는 것이 핵심입니다.
- `save()`는 `json.dump`로 파일을 덮어씁니다.

```python
# replyreview/config/config_manager.py
import json
from pathlib import Path

# config.json이 없거나 형식이 잘못된 경우 적용되는 기본 설정값.
DEFAULT_CONFIG: dict[str, str] = {"openai_api_key": ""}


class ConfigManager:
    """
    로컬 config.json 파일에 대한 읽기/쓰기를 전담하는 클래스.
    파일 부재 또는 JSON 파싱 오류 발생 시 기본값으로 자동 복구한다.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """
        config_path가 주어지지 않으면 런타임에 프로젝트 루트 기준으로 경로를 결정한다.
        테스트 시 tmp_path로 초기화된 경로를 주입하여 실제 파일과 격리할 수 있다.
        """
        if config_path is None:
            # 런타임에 프로젝트 루트 기준으로 config.json 경로를 결정한다.
            config_path = Path(__file__).parent.parent.parent / "config.json"
        self._config_path = config_path

    def load(self) -> dict[str, str]:
        """
        config.json 파일을 읽어 설정 딕셔너리를 반환한다.
        파일이 없거나 JSON 형식이 올바르지 않은 경우 기본값을 반환한다.
        """
        try:
            with open(self._config_path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return DEFAULT_CONFIG.copy()

    def save(self, data: dict[str, str]) -> None:
        """설정 딕셔너리를 config.json 파일에 저장한다."""
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_api_key(self) -> str:
        """저장된 OpenAI API 키를 반환한다. 키가 없으면 빈 문자열을 반환한다."""
        return self.load().get("openai_api_key", "")

    def set_api_key(self, key: str) -> None:
        # 기존 필드를 덮어쓰지 않도록 전체 설정을 먼저 읽은 뒤 키만 교체한다.
        data = self.load()
        data["openai_api_key"] = key
        self.save(data)
```

### Step 3: `pytest-qt` dev 의존성 추가

`pyproject.toml`의 `[dependency-groups] dev` 섹션에 `pytest-qt`를 추가하고, `uv sync`로 설치합니다. `pytest-qt`는 Task 2.2의 GUI 테스트에서 사용됩니다.

```toml
[dependency-groups]
dev = [
    ...
    "pytest-qt>=4.4.0",
]
```

### Step 4: `ConfigManager` 통합 테스트 작성 및 수행

`tests/config/test_config_manager.py` 파일에 테스트를 작성합니다. `tmp_path` fixture를 사용하여 실제 파일 I/O를 수행하되 프로젝트 루트를 오염시키지 않습니다.

```python
# tests/config/test_config_manager.py
import json
from pathlib import Path

import pytest

from replyreview.config.config_manager import ConfigManager


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    """테스트용 임시 config.json 경로를 반환하는 fixture."""
    return tmp_path / "config.json"


@pytest.fixture
def manager(config_path: Path) -> ConfigManager:
    """임시 경로로 초기화된 ConfigManager 인스턴스를 반환하는 fixture."""
    return ConfigManager(config_path=config_path)


class TestConfigManager:
    def test_save_and_load_api_key(self, manager: ConfigManager) -> None:
        """
        API 키를 저장한 후 로드 시 동일한 값이 반환되는지 검증한다.
        """
        # ...

    def test_load_returns_default_when_file_not_found(self, manager: ConfigManager) -> None:
        """
        config.json 파일이 없을 때 빈 API 키를 포함한 기본값을 반환하는지 검증한다.
        """
        # ...

    def test_load_returns_default_on_invalid_json(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        config.json의 JSON 형식이 잘못된 경우 기본값으로 복구하여 반환하는지 검증한다.
        """
        # ...

    def test_get_api_key_returns_empty_when_key_missing_from_valid_json(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        config.json이 유효한 JSON이지만 openai_api_key 필드가 없는 경우
        get_api_key()가 빈 문자열을 반환하는지 검증한다.
        """
        # ...

    def test_set_api_key_preserves_other_fields(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        set_api_key() 호출 시 config.json에 존재하는 다른 필드가 덮어써지지 않고
        보존되는지 검증한다.
        """
        # ...

    def test_save_and_load_full_dict(
        self, manager: ConfigManager
    ) -> None:
        """
        save()로 저장한 전체 딕셔너리가 load()로 동일하게 복원되는지 검증한다.
        """
        # ...
```

테스트 실행 후 모두 통과하는지 확인합니다.

```bash
uv run pytest tests/config/
```

### Step 5: `config` 모듈 명세 작성

`replyreview/config/README.md` 파일에 모듈 명세를 작성합니다. 아래 항목을 포함해야 합니다.

- **모듈 역할**: Data & Config Layer로서 `config.json` 파일 I/O를 캡슐화하며, 다른 모듈이 파일 경로나 JSON 포맷을 직접 다루지 않도록 추상화하는 역할 기술.
- **핵심 컴포넌트**: `ConfigManager` 클래스의 책임, 생성자 파라미터(`config_path`), 공개 메서드(`load`, `save`, `get_api_key`, `set_api_key`) 목록 및 역할 기술.
- **`config.json` 스키마**: `docs/tech-spec.md` 4.3절 기준의 JSON 구조 명시.
- **오류 복구 정책**: `FileNotFoundError` 및 `json.JSONDecodeError` 발생 시 `DEFAULT_CONFIG`로 복구하는 동작 기술.
- **테스트**: `tests/config/test_config_manager.py` 경로 및 `tmp_path` 기반 통합 테스트 전략 기술.

### Step 6: `docs/tech-spec.md` 갱신

`docs/tech-spec.md`의 4.3절 설정 관리 항목에 구현 파일 경로(`replyreview/config/config_manager.py`)를 추가하여 명세와 구현을 연결합니다.

## Success Criteria

- [ ] `uv run pytest tests/config/` 테스트가 모두 통과한다.
- [ ] `uv run pyright` 타입 체크 오류가 없다.
- [ ] `config.json`이 없는 상태에서 `ConfigManager().get_api_key()`를 호출해도 예외가 발생하지 않는다.
- [ ] `replyreview/config/README.md`가 모듈 역할, 컴포넌트, 스키마, 오류 복구 정책을 포함하여 작성되었다.

