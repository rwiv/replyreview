---
name: pyside-patterns
description: PySide6/PyQt6 GUI development patterns for thread management, memory optimization, architecture, and testing.
---

# PySide Development Patterns

Idiomatic PySide6 (and PyQt6) patterns and best practices for building robust, responsive, and maintainable desktop GUI applications.

## Core Principles

### 1. Never Block the Main (GUI) Thread

The main thread is responsible for the event loop and UI updates. **Never** run heavy computations, `time.sleep()`, or blocking I/O on the main thread. Always move them to background threads.

### 2. Separation of UI and Business Logic

Keep your widget classes focused on display and user interaction. Do not mix database queries, network requests, or complex algorithms inside UI classes.

### 3. Safe Cross-Thread Communication

Always use **Signals and Slots** to communicate between worker threads and the main GUI thread. Never update a UI element directly from a background thread.

### 4. Understand C++ vs Python Lifecycles

PySide objects are wrappers around C++ Qt objects. If a Python reference (like a local variable) is garbage collected, the underlying C++ object is destroyed, causing windows to close instantly or segfaults. Always manage object ownership carefully.

## Anti-Patterns

- **Direct UI Modification from Worker:** Calling `label.setText()` from a thread other than the main thread (causes crashes).
- **Infinite Loops in UI Thread:** Using `while True:` inside a button click slot (freezes the app).
- **Circular Signal Emission:** `spinbox1.valueChanged` connecting to `spinbox2.setValue`, which connects back to `spinbox1.setValue` (infinite recursion). Use `.blockSignals(True)` to break the loop.

## References

When solving specific problems, refer to the following in-depth guides located in the `references/` directory:

1. **[API Quick Reference](references/api_quick_reference.md)**
    Read this for a categorized cheatsheet of the most frequently used PySide/PyQt APIs, including Signals/Slots, object lifecycles, and window management.
2. **[Memory & Garbage Collection](references/memory_and_gc.md)**
   Read this when dealing with random crashes, segmentation faults, or dialog windows that disappear immediately after opening.
3. **[Threading & Concurrency](references/threading_async.md)**
   Read this when the UI freezes during background tasks, network requests, or when you need to use `QRunnable`, `QThread`, or `asyncio`.
4. **[Model/View Architecture](references/model_view.md)**
   Read this when `QTableWidget` or `QListWidget` becomes slow with thousands of rows. Covers `QAbstractTableModel` and `fetchMore()`.
5. **[GUI Testing](references/gui_testing.md)**
    Read this when writing automated tests for PySide applications using `pytest-qt` and `qtbot`.
6. **[Architecture & State Management](references/architecture_state.md)**
    Read this for organizing complex UIs using Widget Composition, separating QSS styles, and managing global state using the Event Bus pattern.

