# Threading and Asynchronous Patterns

PySide applications run on an event loop in the main GUI thread. Blocking this thread freezes the application.

## 1. Fire-and-Forget Tasks (QRunnable + QThreadPool)

For simple background tasks that execute once and return a result.

```python
from PySide6.QtCore import QRunnable, QThreadPool, QObject, Signal, Slot

class WorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(str)

class Worker(QRunnable):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            # Simulate heavy work (e.g., file processing, network request)
            import time
            time.sleep(2)
            self.signals.finished.emit(f"Processed: {self.data}")
        except Exception as e:
            self.signals.error.emit(str(e))

# Usage in Main Thread
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool.globalInstance()

    def start_work(self):
        worker = Worker("Test Data")
        worker.signals.finished.connect(self.on_finished)
        self.threadpool.start(worker)

    @Slot(str)
    def on_finished(self, result):
        self.label.setText(result)
```

## 2. Long-Running Workers (QObject.moveToThread)

For services that need their own event loop or need to maintain state and respond to multiple signals over time.

```python
from PySide6.QtCore import QObject, QThread, Signal, Slot

class Worker(QObject):
    progress = Signal(int)
    finished = Signal()

    @Slot()
    def process(self):
        for i in range(100):
            import time
            time.sleep(0.1)
            self.progress.emit(i)
        self.finished.emit()

# Usage
class MainWindow(QMainWindow):
    def start_service(self):
        self.thread = QThread()
        self.worker = Worker()
        
        self.worker.moveToThread(self.thread)
        
        # Connect signals for startup and cleanup
        self.thread.started.connect(self.worker.process)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.progress.connect(self.update_progress)
        
        self.thread.start()
```

## 3. Asyncio Integration (qasync)

When heavily using modern Python `async/await` (e.g., `aiohttp`, `websockets`), integrate the asyncio event loop with Qt's event loop using `qasync`.

```python
import asyncio
from qasync import QEventLoop, asyncSlot
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.button = QPushButton("Fetch Data")
        self.button.clicked.connect(self.fetch_data)
        self.setCentralWidget(self.button)

    @asyncSlot()
    async def fetch_data(self):
        self.button.setEnabled(False)
        self.button.setText("Fetching...")
        
        # Async non-blocking call
        await asyncio.sleep(2) 
        
        self.button.setText("Done")
        self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = MainWindow()
    window.show()
    
    with loop:
        loop.run_forever()
```

