# Windows 빌드 검증 가이드

이 문서는 Windows 환경에서 ReplyReview 애플리케이션을 직접 빌드하고 검증하는 절차를 기술합니다.

## 사전 조건

- Windows 10 이상
- Python 3.9 이상 설치
- [uv](https://github.com/astral-sh/uv) 설치
- 프로젝트 루트에 `replyreview.spec` 파일이 존재해야 합니다 (Track 2-2 Task 1.1 완료 후).

## 빌드 실행

프로젝트 루트에서 명령 프롬프트(cmd) 또는 PowerShell을 열고 실행합니다.

```bat
build.bat
```

빌드가 완료되면 `dist\replyreview\` 디렉토리에 결과물이 생성됩니다.

## 검증 절차

### 1. 빌드 결과물 확인

```bat
dir dist\replyreview\replyreview.exe
```

`replyreview.exe` 파일이 존재하는지 확인합니다.

### 2. 실행 파일 실행

`dist\replyreview\replyreview.exe`를 더블클릭하거나 다음 명령으로 실행합니다.

```bat
dist\replyreview\replyreview.exe
```

### 3. 체크리스트

- [ ] 메인 윈도우가 정상 표시된다.
- [ ] 별도의 콘솔(cmd) 창이 열리지 않는다.
- [ ] 작업 표시줄에 아이콘이 표시된다.
- [ ] CSV 파일 로드 기능이 동작한다.
- [ ] OpenAI API 키 저장 후 `dist\replyreview\config.json`이 생성된다.
- [ ] AI 답글 생성 기능이 정상 동작한다.
- [ ] `dist\replyreview\` 내에 `tests` 관련 파일이 없다.

### 4. 빌드 크기 확인

```bat
powershell -Command "Get-ChildItem -Recurse dist\replyreview | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum | ForEach-Object { '{0:N0} bytes' -f $_ }"
```

## 자주 발생하는 문제

### `ModuleNotFoundError` 또는 `ImportError`

런타임에서 모듈을 찾지 못하는 경우 `replyreview.spec`의 `hiddenimports`에 해당 모듈을 추가한 후 재빌드합니다.

```python
hiddenimports=['missing.module.name'],
```

### 아이콘이 표시되지 않음

`assets\icon.ico` 파일이 존재하는지 확인합니다. 없는 경우 유효한 `.ico` 파일을 해당 경로에 배치한 후 재빌드합니다.

### Antivirus 경고

일부 바이러스 백신 소프트웨어가 PyInstaller 빌드 결과물을 오탐할 수 있습니다. 이는 PyInstaller 부트로더의 특성으로, 코드 서명 없이 배포 시 발생할 수 있는 알려진 현상입니다. 정식 배포 시에는 코드 서명 인증서 적용을 고려하십시오.
