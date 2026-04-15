# Model/View Architecture for Large Datasets

When dealing with thousands or millions of rows, `QTableWidget` and `QListWidget` consume too much memory and become sluggish. You must use the Model/View architecture (`QTableView` + `QAbstractTableModel`).

## 1. Implementing QAbstractTableModel

A custom model provides data to the view on-demand.

```python
from PySide6.QtCore import QAbstractTableModel, Qt, ModelIndex

class HugeDataTableModel(QAbstractTableModel):
    def __init__(self, data: list[list], headers: list[str]):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent=ModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=ModelIndex()) -> int:
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            # Provide data only when the view asks for it (e.g., when scrolling into view)
            return str(self._data[index.row()][index.column()])
            
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
            
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

# Usage
# table_view = QTableView()
# model = HugeDataTableModel(my_large_list, ["ID", "Name", "Value"])
# table_view.setModel(model)
```

## 2. Lazy Loading (Infinite Scroll) with fetchMore()

If fetching the entire dataset from a database is too slow, load data in chunks as the user scrolls.

```python
from PySide6.QtCore import QAbstractTableModel, ModelIndex

class LazyLoadedModel(QAbstractTableModel):
    def __init__(self, db_controller):
        super().__init__()
        self.db = db_controller
        self._data = []
        self._total_rows_in_db = self.db.get_total_count()

    def rowCount(self, parent=ModelIndex()) -> int:
        return len(self._data)

    def canFetchMore(self, parent=ModelIndex()) -> bool:
        return len(self._data) < self._total_rows_in_db

    def fetchMore(self, parent=ModelIndex()) -> None:
        batch_size = 100
        current_len = len(self._data)
        
        # Fetch next chunk from database
        new_data = self.db.get_rows(offset=current_len, limit=batch_size)
        
        # Notify the view that rows are about to be inserted
        self.beginInsertRows(ModelIndex(), current_len, current_len + len(new_data) - 1)
        self._data.extend(new_data)
        self.endInsertRows()
```

## 3. Custom Cell Rendering with QStyledItemDelegate

To display progress bars, buttons, or custom drawn graphics inside a cell, use a delegate.

```python
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionProgressBar, QApplication, QStyle
from PySide6.QtCore import Qt

class ProgressBarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 2:  # Assume column 2 holds progress percentage (0-100)
            progress = int(index.data())
            
            progressBarOption = QStyleOptionProgressBar()
            progressBarOption.rect = option.rect
            progressBarOption.minimum = 0
            progressBarOption.maximum = 100
            progressBarOption.progress = progress
            progressBarOption.text = f"{progress}%"
            progressBarOption.textVisible = True
            
            QApplication.style().drawControl(
                QStyle.CE_ProgressBar, progressBarOption, painter
            )
        else:
            super().paint(painter, option, index)

# Usage
# delegate = ProgressBarDelegate()
# table_view.setItemDelegateForColumn(2, delegate)
```

