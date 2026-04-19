#!/bin/bash
# Builds the ReplyReview desktop application using PyInstaller.
set -e

export HOME=$TMPDIR

rm -rf build/ dist/

uv run --no-cache pyinstaller replyreview.spec --noconfirm --distpath dist --workpath build

if [[ "$OSTYPE" == "darwin"* ]]; then
    codesign --force --sign - dist/ReplyReview.app
    echo "Ad-hoc signing applied: dist/ReplyReview.app"
fi

echo "Build complete: dist/"
