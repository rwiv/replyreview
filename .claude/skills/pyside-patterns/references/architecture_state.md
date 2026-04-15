# UI Architecture and State Management

As desktop applications grow, managing UI layout and data state efficiently becomes crucial.

## 1. Widget Composition

Avoid writing massive `QMainWindow` classes containing hundreds of lines of UI setup. Break the UI down into modular, reusable custom widgets.

```python
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

# Good: Composition
class SidebarWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Sidebar specific setup...

class ContentWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Content specific setup...

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sidebar = SidebarWidget()
        self.content = ContentWidget()
        
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content)
        
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
```

## 2. Separation of Styles (QSS)

Do not hardcode styles via `.setStyleSheet()` in your Python files. Extract them into a `.qss` file to separate logic from presentation.

```python
# style.qss
/* 
  QPushButton {
      background-color: #2c3e50;
      color: white;
      border-radius: 4px;
      padding: 8px;
  }
  QPushButton:hover {
      background-color: #34495e;
  }
*/

# main.py
from PySide6.QtWidgets import QApplication
import sys

def load_stylesheet(app, path):
    with open(path, "r") as f:
        app.setStyleSheet(f.read())

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     load_stylesheet(app, "style.qss")
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())
```

## 3. Event Bus Pattern for Global State

When deeply nested widgets need to communicate or update based on global data changes, passing signals up and down the hierarchy becomes messy ("Signal hell"). Use a Singleton Event Bus.

```python
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QLabel

# 1. Define the Global Event Bus
class EventBus(QObject):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            QObject.__init__(cls._instance)
        return cls._instance

    # Global Signals
    user_logged_in = Signal(dict)
    theme_changed = Signal(str)
    
bus = EventBus()

# 2. Emitting an event from anywhere
class LoginWidget(QWidget):
    def perform_login(self):
        user_data = {"name": "John Doe"}
        bus.user_logged_in.emit(user_data)

# 3. Listening to an event from anywhere
class ProfileWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Not logged in")
        bus.user_logged_in.connect(self.update_profile)
        
    def update_profile(self, user_data):
        self.label.setText(f"Welcome, {user_data['name']}")
```

