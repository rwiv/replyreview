# PySide API Quick Reference & Cheatsheet

This reference organizes the most frequently used core APIs and patterns by category for PySide6 (PyQt6) development.

## 1. Signals and Slots

The core mechanism for communication between objects.

- **`@Slot()`, `@Slot(type)`**: Explicitly declares a slot method. Provides a slight performance improvement and better code readability through C++ signature matching.
- **`Signal()`, `Signal(type)`**: Defines custom signals at the class level. (Not at the instance level.)
- **`.connect(slot, type=Qt.AutoConnection)`**: Connects a callback (slot) to be executed when the signal is emitted. In a multi-threaded environment, the execution mode can be explicitly controlled by specifying `Qt.QueuedConnection` or `Qt.BlockingQueuedConnection`.
- **`.disconnect(slot)`**: Disconnects a connected slot. You can disconnect a specific slot or all connected slots.
- **`.emit(*args)`**: Emits the signal and passes data to the connected slots.
- **`.blockSignals(bool)`**: Temporarily blocks or unblocks signal emission for a specific widget. (Useful for preventing infinite loops.)

## 2. Event Loop & Object Lifecycle

APIs for managing event queue processing and preventing memory leaks and crashes.

- **`QTimer.singleShot(ms, func)`**: Asynchronously executes a function after a specified delay (ms), or when the event loop is idle (0ms).
- **`.deleteLater()`**: Schedules the object to be safely released from memory after the event loop has processed all of its pending events, rather than deleting it immediately.
- **`sender()`**: When called within a slot, returns the sender object of the signal that invoked it. (Use with caution as it increases coupling; it is recommended to explicitly pass sender information as a slot argument using `functools.partial` or `lambda` instead.)
- **`QCoreApplication.processEvents()`**: Forces immediate processing of pending events. (Often used to prevent UI freezing, but separating tasks into threads is the fundamental solution.)

## 3. Widget Hierarchy & Layouts

APIs used for dynamic UI manipulation and navigating the object tree.

- **`.setParent(parent)`**: Sets or changes the parent of a widget. (If `None` is specified, it becomes an independent window.)
- **`.findChild(type, name)`**: Searches for a single child widget matching a specific type and `objectName`.
- **`.findChildren(type, name)`**: Returns a list of all child widgets matching the given conditions.
- **`.layout()` / `.setLayout(layout)`**: Gets the layout currently assigned to the widget, or sets a new layout.

## 4. Dialogs & Windows

APIs for controlling modal and modeless windows.

- **`.show()`**: Shows the window and returns immediately. (Non-blocking, modeless) - Beware of Python's garbage collection.
- **`.exec()`**: Shows the window modally, blocking the main thread's execution until the user closes the window. It runs its own internal event loop.
- **`QDialog.Accepted` / `QDialog.Rejected`**: Integer values returned after `.exec()` is called. Used to determine whether the user clicked OK or Cancel.
- **`.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)`**: Automatically frees the underlying C++ object's memory when the window is closed.

## 5. UI State & Thread Safety

- **`.setEnabled(bool)`**: Toggles the enabled/disabled state of a widget. (When disabled, it cannot be clicked and appears grayed out.)
- **`QMetaObject.invokeMethod(...)`**: Used to request the safe execution of a specific slot or function on the main GUI thread from another thread. (An alternative to signals and slots.)

