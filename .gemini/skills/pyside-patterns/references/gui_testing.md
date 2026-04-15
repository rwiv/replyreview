# GUI Testing Automation

Testing PySide applications requires specific tools because GUI events are asynchronous and rely on the Qt Event Loop. Use `pytest` combined with the `pytest-qt` plugin.

## 1. Setup and qtbot Fixture

`pytest-qt` provides the `qtbot` fixture, which allows you to simulate user interaction and wait for signals.

```python
# test_app.py
import pytest
from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.button = QPushButton("Click Me")
        self.button.clicked.connect(self.change_text)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        
    def change_text(self):
        self.button.setText("Clicked!")

def test_button_click(qtbot):
    # 1. Instantiate the widget
    widget = MyWidget()
    
    # 2. Register widget with qtbot so it gets properly closed/destroyed after the test
    qtbot.addWidget(widget)
    
    # 3. Simulate a mouse click on the button
    qtbot.mouseClick(widget.button, Qt.LeftButton)
    
    # 4. Assert the expected outcome
    assert widget.button.text() == "Clicked!"
```

## 2. Waiting for Asynchronous Signals

When a user action triggers a background thread that eventually emits a signal, you cannot assert immediately. You must wait for the signal.

```python
def test_async_worker(qtbot):
    # Assuming MyAsyncWidget has a worker thread and a start_button
    widget = MyAsyncWidget()
    qtbot.addWidget(widget)
    
    # Block execution until the specific signal is emitted
    with qtbot.waitSignal(widget.worker.finished, timeout=5000) as blocker:
        qtbot.mouseClick(widget.start_button, Qt.LeftButton)
        
    # Assertions after the signal was received
    assert widget.status_label.text() == "Task Complete"
```

## 3. Waiting for UI State Changes

Sometimes you just need to wait until a specific condition becomes true in the UI.

```python
def test_ui_state_change(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    widget.start_animation()
    
    # Repeatedly evaluates the function until it doesn't raise an AssertionError
    def check_progress():
        assert widget.progress_bar.value() == 100
        
    qtbot.waitUntil(check_progress, timeout=3000)
```

