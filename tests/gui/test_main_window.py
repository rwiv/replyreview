from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from replyreview.gui.file_load_view import FileLoadView
from replyreview.gui.main_window import MainWindow
from replyreview.gui.review_list_view import ReviewListView
from tests.fakes import FakeAIClient


@pytest.fixture
def valid_csv(tmp_path: Path) -> str:
    """유효한 리뷰 데이터가 담긴 임시 CSV 파일 경로를 반환하는 fixture."""
    path = tmp_path / "reviews.csv"
    pd.DataFrame(
        {
            "상품명": ["에어팟 프로 케이스"],
            "고객명": ["김땡땡"],
            "별점": [5],
            "리뷰 내용": ["배송이 빠르고 좋아요!"],
        }
    ).to_csv(path, index=False)
    return str(path)


@pytest.fixture
def invalid_csv(tmp_path: Path) -> str:
    """필수 컬럼이 누락된 CSV 파일 경로를 반환하는 fixture."""
    path = tmp_path / "invalid.csv"
    pd.DataFrame(
        {
            "상품명": ["상품"],
            "고객명": ["고객"],
        }
    ).to_csv(path, index=False)
    return str(path)


@pytest.fixture
def window(qtbot: QtBot) -> MainWindow:
    """테스트용 MainWindow 인스턴스를 생성하고 qtbot에 등록하는 fixture."""
    widget = MainWindow()
    qtbot.addWidget(widget)
    return widget


class TestMainWindow:
    """MainWindow의 뷰 전환 로직을 검증하는 통합 테스트 클래스."""

    def test_initial_central_widget_is_file_load_view(self, window: MainWindow) -> None:
        """
        앱 초기 화면의 중앙 위젯이 FileLoadView인지 검증한다.
        """
        assert isinstance(window.centralWidget(), FileLoadView)

    def test_central_widget_switches_to_review_list_view_on_valid_file(
        self, qtbot: QtBot, window: MainWindow, valid_csv: str
    ) -> None:
        """
        유효한 파일이 선택되면 중앙 위젯이 ReviewListView로 전환되는지 검증한다.
        OpenAIClient는 FakeAIClient로 대체하여 실제 API 키 없이 테스트한다.
        """
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=(valid_csv, ""),
        ):
            with patch(
                "replyreview.gui.main_window.OpenAIClient",
                return_value=FakeAIClient(),
            ):
                central_widget = window.centralWidget()
                assert isinstance(central_widget, FileLoadView)
                qtbot.mouseClick(central_widget._load_button, Qt.MouseButton.LeftButton)

        assert isinstance(window.centralWidget(), ReviewListView)

    def test_shows_message_box_on_parser_error(
        self, qtbot: QtBot, window: MainWindow, invalid_csv: str
    ) -> None:
        """
        파싱 오류 발생 시 QMessageBox.warning이 호출되는지 검증한다.
        """
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=(invalid_csv, ""),
        ):
            with patch(
                "replyreview.gui.main_window.QMessageBox.warning"
            ) as mock_warning:
                central_widget = window.centralWidget()
                assert isinstance(central_widget, FileLoadView)
                qtbot.mouseClick(central_widget._load_button, Qt.MouseButton.LeftButton)

                mock_warning.assert_called_once()
                # Check that the error message contains expected text
                call_args = mock_warning.call_args
                assert "파일 오류" in str(call_args)

    def test_central_widget_remains_file_load_view_on_parser_error(
        self, qtbot: QtBot, window: MainWindow, invalid_csv: str
    ) -> None:
        """
        파싱 오류 발생 시 중앙 위젯이 FileLoadView로 유지되는지 검증한다.
        """
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=(invalid_csv, ""),
        ):
            with patch("replyreview.gui.main_window.QMessageBox.warning"):
                central_widget = window.centralWidget()
                assert isinstance(central_widget, FileLoadView)
                qtbot.mouseClick(central_widget._load_button, Qt.MouseButton.LeftButton)

                assert isinstance(window.centralWidget(), FileLoadView)
