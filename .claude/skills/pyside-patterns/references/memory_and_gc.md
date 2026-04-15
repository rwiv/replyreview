# Memory and Garbage Collection in PySide

Understanding the interplay between Python's Garbage Collector (GC) and C++ Qt object lifecycles is critical to preventing crashes (segmentation faults) and disappearing windows.

## 1. Window/Dialog Object Lifetime

**Problem:** A common mistake is assigning a new window to a local variable. When the function ends, Python garbage-collects the variable, which destroys the C++ window object immediately.

```python
# Bad: Window disappears immediately
def show_settings():
    window = SettingsWindow()
    window.show()
    # End of function -> 'window' is garbage collected!

# Good: Keep a reference using 'self'
class MainWindow(QMainWindow):
    def show_settings(self):
        self.settings_window = SettingsWindow()  # Persists as instance variable
        self.settings_window.show()
```

## 2. Parent-Child Relationship

Setting a parent for a widget automatically manages its memory. When the parent is destroyed, all its children are automatically destroyed.

```python
# Good: Automatic memory management
class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Passing 'self' as parent ensures the button is destroyed when MyWidget is destroyed
        self.button = QPushButton("Click Me", self)
        
        # Layouts automatically reparent widgets added to them
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
```

## 3. Safe Deletion with deleteLater()

Never use `del obj` or directly delete Qt objects that might still have pending events in the event loop.

```python
# Good: Using deleteLater()
def close_and_cleanup(self):
    self.close()
    self.deleteLater()  # Safely schedules deletion for the next event loop iteration

# Good: Auto-delete on close for independent windows
class TemporaryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)  # Deletes the object when closed
```

