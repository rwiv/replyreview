# Task 2.1: 아이콘 적용 및 spec 파일 고도화

## Overview

앱 고유 아이콘 파일을 `assets/` 디렉토리에 준비하고 `replyreview.spec`에 적용합니다. macOS에서는 `BUNDLE` 섹션을 추가하여 `.app` 번들 형태로 빌드합니다. 불필요한 대형 모듈을 `excludes`에 추가하여 빌드 결과물의 크기와 안정성을 최적화한 후 최종 빌드를 검증합니다.

## Related Files

### Reference Files

- `replyreview.spec`: Task 1.1에서 작성한 기본 spec 파일
- `assets/icon.icns`: 기존 — macOS용 앱 아이콘
- `assets/icon.ico`: 기존 — Windows용 앱 아이콘
- `docs/tech-spec.md`: 5절 빌드 전략 — 아이콘 및 windowed 요건 참조

### Target Files

- `replyreview.spec`: 수정 — 아이콘, BUNDLE 섹션, excludes/upx_exclude 고도화
- `build.sh`: 수정 — macOS ad-hoc 코드 사이닝 단계 추가
- `docs/tech-spec.md`: 수정 — 5절 최종 배포 설정 반영

## Workflow

### Step 1: 아이콘 파일 사전 확인

`assets/icon.icns`(macOS)와 `assets/icon.ico`(Windows) 파일이 이미 준비되어 있습니다.

### Step 2: spec 파일에 아이콘 적용 및 BUNDLE 섹션 추가

`EXE` 섹션에 `icon` 파라미터를 추가하고, macOS `.app` 번들 형태를 위한 `BUNDLE` 섹션을 추가합니다.

```python
# replyreview.spec
# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['replyreview/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 플랫폼별 아이콘 파일 경로를 지정한다.
    icon='assets/icon.icns' if sys.platform == 'darwin' else 'assets/icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    # Qt/PySide6 바이너리는 UPX 압축 시 런타임 크래시가 발생할 수 있으므로 제외한다.
    upx_exclude=['Qt6*', 'libQt6*', 'PySide6*', 'shiboken6*'],
    name='replyreview',
)

# macOS에서만 .app 번들을 생성한다.
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='ReplyReview.app',
        icon='assets/icon.icns',
        bundle_identifier='com.rwiv.replyreview',
    )
```

- `argv_emulation=False`: macOS `.app` 번들에서 `argv_emulation=True`는 Apple Event 처리 시 부작용이 있으므로 비활성화합니다.
- `bundle_identifier`: 역도메인 형식의 고유 ID. macOS에서 앱을 식별하는 데 사용됩니다.

### Step 3: excludes 고도화

`pandas`는 다양한 백엔드 라이브러리(PyArrow 등)를 선택적으로 import하는데, 이 프로젝트에서는 CSV/Excel 파싱에만 사용합니다. 런타임에 사용하지 않는 모듈을 `excludes`에 추가하여 빌드 크기를 줄입니다.

```python
a = Analysis(
    ...
    excludes=[
        'tests',
        # pandas가 선택적으로 사용하는 백엔드 중 이 프로젝트에서 사용하지 않는 모듈들
        'pyarrow',
        'fastparquet',
        'sqlalchemy',
    ],
    ...
)
```

제외 전후 빌드 크기를 비교하여 실제 효과를 확인하고, 제외로 인해 런타임 오류가 발생하는 경우 해당 모듈을 다시 포함시킵니다.

```bash
du -sh dist/ReplyReview.app
```

### Step 4: macOS ad-hoc 코드 사이닝 적용

코드 사이닝 없이 배포하면 macOS Gatekeeper가 앱 실행을 차단합니다. Apple Developer ID가 없는 환경에서는 ad-hoc 서명을 적용하여 동일 머신 또는 신뢰된 환경에서의 실행 문제를 줄입니다.

`build.sh`에 빌드 완료 후 서명 단계를 추가합니다.

```bash
#!/bin/bash
set -e

uv run pyinstaller replyreview.spec --noconfirm

if [[ "$OSTYPE" == "darwin"* ]]; then
    codesign --force --sign - dist/ReplyReview.app
    echo "Ad-hoc signing applied: dist/ReplyReview.app"
fi

echo "Build complete: dist/"
```

> **한계 사항**: ad-hoc 서명은 Apple Notarization을 통과하지 않으므로, 처음 실행 시 Gatekeeper 경고가 표시될 수 있습니다. 사용자는 시스템 환경설정 > 개인 정보 보호 및 보안 > "확인되지 않은 개발자" 허용을 통해 실행할 수 있습니다. 정식 공개 배포를 위해서는 Apple Developer ID 서명 및 Notarization이 필요하며 이는 별도 트랙에서 다룹니다.

### Step 5: 최종 빌드 실행 및 검증

```bash
sh build.sh
```

빌드 완료 후 다음 항목을 검증합니다.

- macOS에서 `dist/ReplyReview.app`이 생성되는지 확인
- `.app`을 더블클릭으로 실행하고 Dock에 아이콘이 표시되는지 확인
- 메인 윈도우 표시, CSV 로드, AI 답글 생성 전체 플로우 동작 확인
- 콘솔 창이 표시되지 않는지 확인

### Step 6: `docs/tech-spec.md` 최종 반영

`docs/tech-spec.md` 5절에 다음 내용을 최종 반영합니다.

- 아이콘 파일 경로 및 플랫폼별 적용 방식
- macOS `BUNDLE` 섹션 및 `bundle_identifier`
- `excludes` 목록 및 제외 이유
- `upx_exclude` Qt 바이너리 패턴 및 이유
- macOS ad-hoc 코드 사이닝 적용 방법 및 한계 사항
- 최종 빌드 산출물 경로 (`dist/ReplyReview.app`)

## Success Criteria

- [ ] `sh build.sh` 실행 시 오류 없이 빌드가 완료된다.
- [ ] macOS에서 `dist/ReplyReview.app` 번들이 생성된다.
- [ ] `.app` 실행 시 Dock 및 파인더에 설정한 아이콘이 표시된다.
- [ ] 빌드된 앱에서 CSV 파일 로드 및 AI 답글 생성 기능이 정상 동작한다.
- [ ] `assets/icon.icns` 및 `assets/icon.ico` 파일이 프로젝트에 포함되어 있다.
- [ ] `build.sh`에서 ad-hoc 서명이 적용되고 한계 사항이 `docs/tech-spec.md`에 문서화된다.
