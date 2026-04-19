# Config Module

## 1. 모듈 개요

`config` 모듈은 **Data & Config Layer**로서 ReplyReview 애플리케이션의 로컬 설정 파일(`config.json`) I/O를 캡슐화합니다.

이 모듈의 핵심 책임은:
- `config.json` 파일에 대한 읽기/쓰기를 전담
- 파일 부재 또는 JSON 파싱 오류 발생 시 기본값으로 자동 복구
- 다른 모듈이 파일 경로나 JSON 포맷을 직접 다루지 않도록 추상화

이를 통해 설정 관리의 복잡성을 한곳(`ConfigManager`)에 집중시키고, GUI 및 기타 모듈들은 `ConfigManager` 인터페이스만 의존하도록 설계합니다.

## 2. 관련 문서

- `docs/tech-spec.md` - 4.3절: 설정 관리 시스템 명세
- `replyreview/gui/README.md` - GUI 모듈에서 ConfigManager 사용 방식

## 3. 핵심 컴포넌트

### ConfigManager

`ConfigManager`는 `config.json` 파일 I/O의 유일한 진입점입니다. (`replyreview/config/config_manager.py`)

- 설정 파일 경로를 생성자에서 주입받아 테스트 환경에서 실제 파일과 격리할 수 있습니다.
- `load`로 설정 딕셔너리를 읽고 `save`로 저장하며, `get_api_key` / `set_api_key`로 OpenAI API 키를 직접 조회·저장하는 편의 메서드를 제공합니다.
- 파일 부재나 JSON 파싱 오류 발생 시 예외를 전파하지 않고 기본값(`DEFAULT_CONFIG`)으로 자동 복구하는 것이 핵심 설계 원칙입니다.

## 4. config.json 스키마

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

## 5. 오류 복구 정책

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

## 6. 테스트

### 테스트 파일

- `tests/config/test_config_manager.py`: `ConfigManager` 동작 검증

### 테스트 전략

- **실제 파일 I/O 기반**: `pytest`의 `tmp_path` fixture를 사용하여 임시 경로에서 실제 파일 I/O를 수행합니다.
- **외부 의존성 없음**: 실제 `config.json` 파일이나 다른 모듈에 의존하지 않고 독립적으로 실행됩니다.
- **예외 시나리오 포함**:
  - 파일 부재 시 기본값 반환 검증
  - 잘못된 JSON 형식 시 복구 검증
  - 저장/로드 순환 검증

