# 빌드 및 배포 전략 (PyInstaller)

## 1. 빌드 시스템 개요

일반 사용자가 Python 환경 설정 없이 즉시 실행할 수 있는 독립 실행 파일로 패키징하기 위해 PyInstaller를 사용합니다. Python 인터프리터, PySide6, LangChain, pandas 등 모든 의존성을 단일 디렉토리 형태로 번들링합니다.

## 2. 빌드 파일 구조

```
replyreview/
├── replyreview.spec              # PyInstaller 빌드 명세 파일
├── build.sh                      # macOS/Linux 빌드 실행 스크립트
├── build.bat                     # Windows 빌드 실행 스크립트
└── ...
```

- **`replyreview.spec`**: PyInstaller 설정 파일로, 빌드 옵션을 선언적으로 관리합니다.
  - `Analysis` 섹션: 엔트리포인트 (`replyreview/__main__.py`), 의존성 분석, `tests` 모듈 제외
  - `EXE` 섹션: 콘솔 윈도우 비활성화 (`console=False`), UPX 압축 활성화
  - `COLLECT` 섹션: 모든 의존성을 단일 디렉토리에 번들링
  - `BUNDLE` 섹션: macOS에서 `.app` 번들 형태로 빌드

- **`build.sh`**: macOS/Linux 빌드 스크립트
  ```bash
  sh build.sh
  ```
  빌드 결과는 `dist/replyreview/` 디렉토리에 생성됩니다.

- **`build.bat`**: Windows 빌드 스크립트
  ```cmd
  build.bat
  ```

## 3. 빌드 옵션 설명

### `--onedir` vs `--onefile`

`--onedir` (단일 디렉토리) 방식을 선택하는 이유:
- PySide6 Qt 플러그인(platform, imageformats 등)을 직접 파일 시스템에서 로드해야 안정적으로 동작합니다.
- `--onefile` (단일 실행 파일)로 빌드하면, 런타임에 임시 디렉토리에 압축을 해제하는 오버헤드가 발생하고 Qt 플러그인 로드가 불안정할 수 있습니다.

### `--windowed` (콘솔 윈도우 제거)

GUI 애플리케이션이므로 백그라운드 콘솔 윈도우가 나타나지 않도록 설정합니다.

## 4. 의존성 관리

### `tests` 모듈 제외

`tests/` 디렉토리의 `FakeAIClient` 등 개발 전용 코드는 배포 패키지에 포함되지 않아야 합니다. 이를 위해 spec 파일의 `Analysis` 섹션에서 `excludes=['tests']`로 설정하여 자동으로 제외됩니다.

### 숨겨진 임포트 (Hidden Imports)

- PySide6는 PyInstaller 후킹(hook)이 잘 지원되므로 기본적으로 모든 모듈이 자동으로 포함됩니다.
- LangChain, pandas 등도 공식 PyInstaller 후킹을 통해 필요한 의존성이 자동으로 포함됩니다.
- 런타임에 `ModuleNotFoundError`가 발생하면 해당 모듈을 spec 파일의 `hiddenimports` 리스트에 수동으로 추가합니다.

### pandas 백엔드 모듈 제외

`pandas`는 다양한 선택적 백엔드 라이브러리(PyArrow, fastparquet, SQLAlchemy)를 import할 수 있으나, 이 프로젝트에서는 CSV/Excel 파싱에만 사용합니다. 번들 크기를 줄이기 위해 다음 모듈을 `excludes`에서 제외합니다:

```python
excludes=[
    'tests',
    'pyarrow',
    'fastparquet', 
    'sqlalchemy',
]
```

## 5. 아이콘 적용 및 macOS BUNDLE 설정

### 아이콘 파일

애플리케이션 고유 아이콘을 `assets/` 디렉토리에 준비합니다:
- **macOS**: `assets/icon.icns` (ICNS 형식, 128x128 이상 권장)
- **Windows**: `assets/icon.ico` (ICO 형식)

#### spec 파일에 아이콘 적용

`EXE` 섹션에서 플랫폼별 아이콘을 지정합니다:

```python
icon='assets/icon.icns' if sys.platform == 'darwin' else 'assets/icon.ico',
```

### macOS `.app` 번들 형태 빌드

macOS에서는 `.app` 번들 형태로 빌드하여 Dock 및 Finder 아이콘 통합을 지원합니다:

```python
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='ReplyReview.app',
        icon='assets/icon.icns',
        bundle_identifier='com.rwiv.replyreview',
    )
```

- `name`: 사용자에게 표시되는 앱 이름
- `icon`: 아이콘 파일 경로 (ICNS 형식)
- `bundle_identifier`: 역도메인 형식의 고유 ID (macOS에서 앱 식별 용도)

## 6. UPX 바이너리 압축 제외 패턴

Qt/PySide6 바이너리는 UPX 압축 시 런타임 크래시가 발생할 수 있으므로, COLLECT 섹션의 `upx_exclude`에 다음 패턴을 추가합니다:

```python
upx_exclude=['Qt6*', 'libQt6*', 'PySide6*', 'shiboken6*'],
```

이를 통해 Qt 관련 라이브러리는 압축되지 않으며, 다른 바이너리는 UPX로 압축되어 전체 번들 크기를 줄입니다.

## 7. 설정 파일 (`config.json`) 경로 처리

빌드된 애플리케이션은 `sys.frozen` 속성을 통해 PyInstaller로 패키징되었는지 감지할 수 있습니다.

```python
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller 임시 디렉토리
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
```

`ConfigManager`는 다음과 같이 설정 파일 경로를 결정합니다:
- **개발 환경**: 프로젝트 루트의 `config.json`
- **배포 환경**: 실행 파일 옆(예: `dist/replyreview/` 디렉토리) 또는 사용자 애플리케이션 디렉토리

## 8. 최적화 및 제한사항

### UPX 압축

spec 파일에서 `upx=True`로 설정하면 UPX(Ultimate Packer for eXecutables)가 설치된 경우 바이너리 압축을 자동으로 적용합니다. UPX가 설치되지 않은 경우 PyInstaller가 자동으로 무시하므로 에러가 발생하지 않습니다.

### macOS ad-hoc 코드 서명

macOS에서 배포하려면 코드 서명(Code Signing)이 필요합니다. `build.sh`에서 빌드 완료 후 다음과 같이 ad-hoc 서명을 자동으로 적용합니다:

```bash
if [[ "$OSTYPE" == "darwin"* ]]; then
    codesign --force --sign - dist/ReplyReview.app
    echo "Ad-hoc signing applied: dist/ReplyReview.app"
fi
```

이를 통해 동일 머신에서의 실행은 보장되며, 초기 실행 시 Gatekeeper 경고를 줄일 수 있습니다.

**한계 사항**: ad-hoc 서명은 Apple Notarization을 통과하지 않으므로, 처음 실행 시 macOS Gatekeeper 경고가 표시될 수 있습니다. 사용자는 시스템 환경설정 > 개인 정보 보호 및 보안 > "확인되지 않은 개발자" 허용을 통해 실행할 수 있습니다. 정식 공개 배포를 위해서는 Apple Developer ID 서명 및 Notarization이 필요합니다.

## 9. 최종 빌드 산출물

빌드 완료 후 생성되는 주요 산출물:

- **macOS**: `dist/ReplyReview.app/` — `.app` 번들 형태
  - 사용자는 Finder에서 `.app`을 더블클릭하여 실행 가능
  - Dock에 앱 아이콘 표시
  
- **기타 플랫폼**: `dist/replyreview/` — 단일 디렉토리 형태
  - `dist/replyreview/replyreview` 실행 파일로 앱 실행 가능
  - `config.json` 생성 위치: `dist/replyreview/` 디렉토리 옆

