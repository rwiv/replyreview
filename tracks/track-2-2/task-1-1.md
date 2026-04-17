# Task 1.1: spec 파일 생성 및 기본 빌드 파이프라인 구축

## Overview

`pyi-makespec` 명령으로 초기 spec 파일을 생성하고, `tests` 모듈 제외·windowed 모드 등 필수 빌드 옵션을 반영하도록 spec 파일을 수정합니다. 초기 빌드를 실행하여 `dist/` 결과물이 정상 동작하는지 검증하고, 반복 빌드를 위한 `build.sh` 스크립트를 작성합니다.

## Related Files

### Reference Files

- `docs/tech-spec.md`: 5절 빌드 및 배포 전략 — `--windowed`, `onedir` 방침 참조
- `replyreview/__main__.py`: 빌드 엔트리포인트 확인
- `pyproject.toml`: 의존성 목록 확인 (번들 대상 파악)

### Target Files

- `replyreview.spec`: 신규 — PyInstaller 빌드 명세 파일
- `build.sh`: 신규 — macOS/Linux 빌드 실행 스크립트
- `build.bat`: 신규 — Windows 빌드 실행 스크립트
- `docs/tech-spec.md`: 수정 — 5절 구현 세부사항 반영

## Workflow

### Step 1: 초기 spec 파일 생성

`pyi-makespec`으로 spec 파일 초안을 생성합니다. 실제 빌드 없이 설정 파일만 생성하므로 편집 전 기준점으로 활용합니다.

```bash
uv run pyi-makespec \
    --windowed \
    --onedir \
    --name replyreview \
    replyreview/__main__.py
```

생성된 `replyreview.spec`를 열고 다음 단계에서 내용을 수정합니다.

### Step 2: spec 파일 수정

`Analysis` 섹션의 `excludes`에 `tests` 모듈을 추가하여 `tests/fakes.py`의 `FakeAIClient` 등 개발 전용 코드가 번들에 포함되지 않도록 합니다.

```python
# replyreview.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['replyreview/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # tests 모듈은 개발 전용이므로 번들에서 제외한다.
    excludes=['tests'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='replyreview',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # console=False: GUI 앱이므로 콘솔 창을 표시하지 않는다.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='replyreview',
)
```

- `hiddenimports`: PySide6는 PyInstaller hook이 잘 지원되므로 기본값으로 시작합니다. 빌드 후 런타임 오류가 발생하는 경우 해당 모듈을 추가합니다.
- `upx=True`: UPX가 설치된 경우 바이너리 압축을 적용합니다. 설치되지 않은 경우 PyInstaller가 자동으로 무시합니다.

### Step 3: 초기 빌드 실행 및 결과물 검증

spec 파일 기반으로 빌드를 실행합니다.

```bash
uv run pyinstaller replyreview.spec --noconfirm
```

빌드 성공 후 다음 항목을 직접 확인합니다.

- `dist/replyreview/replyreview` 실행 파일이 생성되었는지 확인
- 실행 시 메인 윈도우가 정상 표시되는지 확인
- 콘솔(터미널) 창이 별도로 열리지 않는지 확인
- CSV 파일 로드 및 기본 UI 동작 확인
- OpenAI API 키 저장 후 앱 재실행 시 `config.json`이 실행 파일 옆 디렉토리에 생성되는지 확인

빌드 중 `ModuleNotFoundError` 또는 런타임 ImportError가 발생하는 경우, 해당 모듈을 spec의 `hiddenimports`에 추가합니다.

### Step 4: 빌드 스크립트 작성

반복 빌드를 위한 스크립트를 프로젝트 루트에 작성합니다. `--noconfirm`으로 기존 `dist/` 결과물을 자동 덮어씁니다.

**macOS/Linux (`build.sh`)**

```bash
#!/bin/bash
# Builds the ReplyReview desktop application using PyInstaller.
set -e

rm -rf build/ dist/

uv run pyinstaller replyreview.spec --noconfirm

echo "Build complete: dist/"
```

실행 권한을 부여합니다.

```bash
chmod +x build.sh
```

**Windows (`build.bat`)**

```bat
@echo off
REM Builds the ReplyReview desktop application using PyInstaller.

uv run pyinstaller replyreview.spec --noconfirm
if %errorlevel% neq 0 exit /b %errorlevel%

echo Build complete: dist\
```

### Step 5: `docs/tech-spec.md` 갱신

`docs/tech-spec.md` 5절 "빌드 및 배포 전략" 항목에 다음 내용을 추가합니다.

- `replyreview.spec` 파일 경로 및 역할 명시
- `build.sh` / `build.bat` 실행 방법
- `--onedir` 선택 이유 (PySide6 플러그인 안정성)
- `tests` 모듈 제외 이유
- `ConfigManager`의 `sys.frozen` 분기 처리 설명

## Success Criteria

- [ ] `sh build.sh` 실행 시 오류 없이 빌드가 완료된다.
- [ ] `dist/replyreview/` 디렉토리 내 실행 파일이 생성된다.
- [ ] 빌드된 앱 실행 시 메인 윈도우가 표시되고 콘솔 창이 나타나지 않는다.
- [ ] `replyreview.spec` 파일이 프로젝트 루트에 존재한다.
- [ ] `dist/replyreview/` 결과물에 `tests` 관련 파일이 포함되지 않는다.
- [ ] 빌드된 앱에서 API 키 저장 시 `config.json`이 실행 파일 옆에 생성된다.
- [ ] `build.bat` 파일이 프로젝트 루트에 존재한다.
