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
        test_key = "sk-test-key-123"
        manager.set_api_key(test_key)
        loaded_key = manager.get_api_key()
        assert loaded_key == test_key

    def test_load_returns_default_when_file_not_found(
        self, manager: ConfigManager
    ) -> None:
        """
        config.json 파일이 없을 때 빈 API 키를 포함한 기본값을 반환하는지 검증한다.
        """
        loaded = manager.load()
        assert loaded == {"openai_api_key": ""}

    def test_load_returns_default_on_invalid_json(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        config.json의 JSON 형식이 잘못된 경우 기본값으로 복구하여 반환하는지 검증한다.
        """
        config_path.write_text("{ invalid json }", encoding="utf-8")
        loaded = manager.load()
        assert loaded == {"openai_api_key": ""}

    def test_get_api_key_returns_empty_when_key_missing_from_valid_json(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        config.json이 유효한 JSON이지만 openai_api_key 필드가 없는 경우
        get_api_key()가 빈 문자열을 반환하는지 검증한다.
        """
        config_path.write_text('{"other_field": "value"}', encoding="utf-8")
        assert manager.get_api_key() == ""

    def test_set_api_key_preserves_other_fields(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        set_api_key() 호출 시 config.json에 존재하는 다른 필드가 덮어써지지 않고
        보존되는지 검증한다.
        """
        config_path.write_text('{"openai_api_key": "old-key", "other_field": "value"}', encoding="utf-8")
        manager.set_api_key("new-key")
        data = manager.load()
        assert data["openai_api_key"] == "new-key"
        assert data["other_field"] == "value"

    def test_save_and_load_full_dict(self, manager: ConfigManager) -> None:
        """
        save()로 저장한 전체 딕셔너리가 load()로 동일하게 복원되는지 검증한다.
        """
        test_data = {"openai_api_key": "sk-test", "other_field": "data"}
        manager.save(test_data)
        loaded = manager.load()
        assert loaded == test_data
