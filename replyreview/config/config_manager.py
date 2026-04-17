import json
import sys
from pathlib import Path

# config.json이 없거나 형식이 잘못된 경우 적용되는 기본 설정값.
DEFAULT_CONFIG: dict[str, str] = {"openai_api_key": ""}


def find_project_root() -> Path:
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / ".git").exists():
            return parent
    return current_path.parent


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
            if getattr(sys, "frozen", False):
                # PyInstaller 번들 환경: 실행 파일이 위치한 디렉토리 기준
                base_path = Path(sys.executable).parent
            else:
                # 일반 Python 실행 환경: 프로젝트 루트 기준
                base_path = find_project_root()
            config_path = base_path / "config.json"
        self._config_path = config_path

    def load(self) -> dict[str, str]:
        """
        config.json 파일을 읽어 설정 딕셔너리를 반환한다.
        파일이 없거나 JSON 형식이 올바르지 않은 경우 기본값을 반환한다.
        """
        try:
            with open(self._config_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError, json.JSONDecodeError:
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
