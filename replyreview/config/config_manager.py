import json
from pathlib import Path

# Default value applied when config.json is absent or malformed
DEFAULT_CONFIG: dict[str, str] = {"openai_api_key": ""}


class ConfigManager:
    """
    로컬 config.json 파일에 대한 읽기/쓰기를 전담하는 클래스.
    파일 부재 또는 JSON 파싱 오류 발생 시 기본값으로 자동 복구한다.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        if config_path is None:
            # Resolve config.json relative to the project root at runtime
            config_path = Path(__file__).parent.parent.parent / "config.json"
        self._config_path = config_path

    def load(self) -> dict[str, str]:
        """
        config.json 파일을 읽어 설정 딕셔너리를 반환한다.
        파일이 없거나 JSON 형식이 올바르지 않은 경우 기본값을 반환한다.

        @returns 설정 딕셔너리를 반환.
        """
        try:
            with open(self._config_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError, json.JSONDecodeError:
            return DEFAULT_CONFIG.copy()

    def save(self, data: dict[str, str]) -> None:
        """
        설정 딕셔너리를 config.json 파일에 저장한다.

        @param data 저장할 설정 딕셔너리.
        """
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_api_key(self) -> str:
        """
        저장된 OpenAI API 키를 반환한다.

        @returns OpenAI API 키 문자열. 설정되지 않은 경우 빈 문자열을 반환.
        """
        return self.load().get("openai_api_key", "")

    def set_api_key(self, key: str) -> None:
        """
        OpenAI API 키를 저장한다.

        @param key 저장할 OpenAI API 키 문자열.
        """
        data = self.load()
        data["openai_api_key"] = key
        self.save(data)
