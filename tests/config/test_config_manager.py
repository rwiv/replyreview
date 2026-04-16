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
        IS-01: API 키를 저장한 후 로드 시 동일한 값이 반환되는지 검증한다.
        """
        test_key = "sk-test-key-123"
        manager.set_api_key(test_key)
        loaded_key = manager.get_api_key()
        assert loaded_key == test_key

    def test_load_returns_default_when_file_not_found(
        self, manager: ConfigManager
    ) -> None:
        """
        IF-02: config.json 파일이 없을 때 빈 API 키를 포함한 기본값을 반환하는지 검증한다.
        """
        loaded = manager.load()
        assert loaded == {"openai_api_key": ""}

    def test_load_returns_default_on_invalid_json(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        IF-03: config.json의 JSON 형식이 잘못된 경우 기본값으로 복구하여 반환하는지 검증한다.
        """
        # Write invalid JSON to config file
        config_path.write_text("{ invalid json }", encoding="utf-8")

        loaded = manager.load()
        assert loaded == {"openai_api_key": ""}

    def test_save_creates_file(self, manager: ConfigManager, config_path: Path) -> None:
        """
        파일이 없을 때 save()를 호출하면 파일이 생성되는지 검증한다.
        """
        assert not config_path.exists()
        manager.save({"openai_api_key": "sk-test"})
        assert config_path.exists()

    def test_save_overwrites_existing_file(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        기존 파일을 덮어쓰는지 검증한다.
        """
        manager.save({"openai_api_key": "sk-old"})
        manager.save({"openai_api_key": "sk-new"})

        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["openai_api_key"] == "sk-new"

    def test_set_api_key_persists_to_file(
        self, manager: ConfigManager, config_path: Path
    ) -> None:
        """
        set_api_key()가 파일에 실제로 저장되는지 검증한다.
        """
        manager.set_api_key("sk-persist-test")

        # Read the file directly to verify persistence
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["openai_api_key"] == "sk-persist-test"

    def test_empty_api_key(self, manager: ConfigManager) -> None:
        """
        빈 API 키를 저장하고 로드하는지 검증한다.
        """
        manager.set_api_key("")
        assert manager.get_api_key() == ""
