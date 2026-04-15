---
name: python-style-guide
description: This skill provides Python coding standards and style guidelines. Use this skill when you need to handle code, such as writing Python code, refactoring, or performing code reviews.
---

# Python Style Guide

This document defines the style guide and coding standards to adhere to when writing Python code.

## Type Hinting

- Use the latest syntax (Python 3.10+).
- Use `list`, `dict`, etc., instead of `List`, `Dict`.
- Use the `|` operator instead of `Optional`, `Union`.
- Always specify types in function signatures.
- Type variables explicitly only when type inference is impossible or ambiguous.

## Imports

- Use absolute paths.
- Default to using `from x import y`.
- You may use `import x` for code clarity.
  - Example: For the `auth` module, using `import auth` and calling `auth.verify_token()` can make the code clearer than using `from auth import verify`.

## Exceptions

- Do not use empty `except:` clauses.

## Variables

- Avoid `global` variables whenever possible.

## Data Class

- Implement classes that represent data/state using `pydantic` by default.
- However, use the built-in `dataclasses` in the following cases:
  - When the `pydantic` package is not installed in the project.
  - When used within simple utility (util) functions that do not require data validation.

## Control Flow

- **Comprehensions:** Decide on usage considering readability. Use them for simple logic, but use loops like `for` if the logic becomes complex.
- **Default Argument Values:** Do not use mutable objects (like `[]` or `{}`) as default values.

## Formatting

- **Line Length:** Configure based on the line length value of the formatter (ruff, black, etc.), and use a maximum of 88 characters if there is no separate configuration.
- **Indentation:** Use 4 spaces per indentation level. Never use tabs.
- **Blank Lines:** Place two blank lines between top-level definitions (classes, functions). Place one blank line between method definitions.
- **Strings:** Use f-strings for formatting unless there is a specific reason not to.

## Documentation

- Write docstrings for all modules, classes, and public functions and methods.
- Write docstrings in the Google style.

## Naming Conventions

- **General:** Use `snake_case` for modules, functions, methods, and variables.
- **Classes:** Use `PascalCase`.
- **Constants:** Use `ALL_CAPS_WITH_UNDERSCORES`.
- **Internal Use:** Use a single leading underscore (`_internal_variable`) for internal module/class members.

## Application Structure

- Every executable file must have a `main()` function containing the main logic, and it must be called within an `if __name__ == '__main__':` block.

