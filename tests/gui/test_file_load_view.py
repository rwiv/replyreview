from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from replyreview.gui.file_load_view import FileLoadView


@pytest.fixture
def view(qtbot: QtBot) -> FileLoadView:
    """테스트용 FileLoadView 인스턴스를 생성하고 qtbot에 등록하는 fixture."""
    widget = FileLoadView()
    qtbot.addWidget(widget)
    return widget


class TestFileLoadView:
    """FileLoadView의 렌더링 및 시그널 emit 동작을 검증하는 테스트 클래스."""

    def test_file_selected_emitted_with_path(
        self, qtbot: QtBot, view: FileLoadView
    ) -> None:
        """
        파일을 선택하면 file_selected 시그널에 선택된 경로가 emit되는지 검증한다.
        """
        fake_path = "/fake/reviews.csv"
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=(fake_path, ""),
        ):
            with qtbot.waitSignal(view.file_selected) as blocker:
                qtbot.mouseClick(view._load_button, Qt.MouseButton.LeftButton)

        assert blocker.args == [fake_path]

    def test_file_selected_not_emitted_on_cancel(
        self, qtbot: QtBot, view: FileLoadView
    ) -> None:
        """
        파일 탐색기를 취소하면(빈 문자열 반환) file_selected 시그널이 emit되지 않는지 검증한다.
        """
        with patch(
            "replyreview.gui.file_load_view.QFileDialog.getOpenFileName",
            return_value=("", ""),
        ):
            with qtbot.assertNotEmitted(view.file_selected):
                qtbot.mouseClick(view._load_button, Qt.MouseButton.LeftButton)

    def test_guide_label_text(self, view: FileLoadView) -> None:
        """
        안내 문구가 올바르게 표시되는지 검증한다.
        """
        labels = (
            view.findChildren(type(view.sender()))
            if hasattr(view.sender(), "__class__")
            else []
        )
        from PySide6.QtWidgets import QLabel

        labels = view.findChildren(QLabel)
        assert len(labels) > 0
        assert "리뷰 데이터 파일" in labels[0].text()

    def test_button_text(self, view: FileLoadView) -> None:
        """
        버튼 텍스트가 올바르게 표시되는지 검증한다.
        """
        assert view._load_button.text() == "파일 불러오기"
