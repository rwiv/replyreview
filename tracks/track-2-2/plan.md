# Plan: 독립 실행 파일 패키징 및 배포 체계 확립

## Phase 1: 기본 빌드 파이프라인 구축

### Task 1.1: spec 파일 생성 및 기본 빌드 파이프라인 구축

- [ ] `pyi-makespec` 명령으로 초기 spec 파일 생성
  - 엔트리포인트: `replyreview/__main__.py`
  - `--windowed`, `--onedir`, `--name replyreview` 옵션 적용
- [ ] spec 파일 수정: `excludes`, `hiddenimports` 조정
  - `tests` 모듈 제외
  - PySide6 관련 hidden import 필요 여부 검증
- [ ] 초기 빌드 실행 및 결과물 동작 검증
  - `pyinstaller replyreview.spec` 실행
  - `dist/` 결과물에서 앱 정상 실행 확인
  - 콘솔 창 미표시 확인
  - `config.json`이 실행 파일 옆에 생성되는지 확인
- [ ] `build.sh` 빌드 스크립트 작성
- [ ] `build.bat` Windows 빌드 스크립트 작성
- [ ] `docs/tech-spec.md` 5절 빌드 전략 세부사항 갱신

## Phase 2: 배포 설정 최적화

### Task 2.1: 아이콘 적용 및 spec 파일 고도화

- [ ] spec 파일에 아이콘 및 macOS BUNDLE 섹션 적용
  - `EXE` 섹션의 `icon` 파라미터 설정
  - `BUNDLE` 섹션 추가로 macOS `.app` 번들 형태 빌드
  - `bundle_identifier` 및 앱 표시 이름 설정
- [ ] spec 파일 `excludes` 고도화
  - 불필요한 대형 모듈(예: `pandas` 백엔드 미사용 엔진) 제외 처리
  - `upx_exclude`에 Qt/PySide6 바이너리 패턴 추가
- [ ] `build.sh`에 macOS ad-hoc 코드 사이닝 적용
- [ ] 최종 빌드 실행 및 아이콘 적용 확인
- [ ] `docs/tech-spec.md` 5절 최종 반영 (ad-hoc 서명 한계 사항 포함)
