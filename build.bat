@echo off
REM Builds the ReplyReview desktop application using PyInstaller.

uv run pyinstaller replyreview.spec --noconfirm
if %errorlevel% neq 0 exit /b %errorlevel%

echo Build complete: dist\
