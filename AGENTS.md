# 저장소 가이드라인

## 프로젝트 구조 및 모듈 구성
- 소스: `app.py`(메인 Streamlit 앱), `viewer.py`(토큰 기반 뷰어), 유틸: `viewer_utils.py`, `web_storage.py`, `database.py`, `texture_optimizer.py`, `mtl_generator.py`.
- 인증/API: `auth.py`, `annotations_api.py`.
- 서버 스크립트: `upload.php`, `delete.php`(원격 파일 작업).
- 구성/의존성: `pyproject.toml`, `requirements.txt`, `uv.lock`.
- 런타임 데이터(생성형): `data/models.db`, `data/models/{model_id}/`, `uploads/`.

## 빌드·테스트·개발 명령
- 설치(uv): `uv sync` — `pyproject.toml`/`uv.lock` 기준으로 의존성 동기화.
- 설치(pip): `pip install -r requirements.txt` — uv 미사용 시 대안.
- 실행: `uv run streamlit run app.py` 또는 `streamlit run app.py`.
- 뷰어만 실행: `streamlit run viewer.py` — `?token=...` 쿼리로 로드.
- 린트/포맷(선택): `ruff check .`, `black .`.

## 코딩 스타일 및 네이밍
- Python 3.11+, 스페이스 4칸, UTF-8.
- 공개 함수에는 타입 힌트와 간결한 docstring.
- 네이밍: 파일/함수 `snake_case`, 클래스 `CamelCase`, 상수 `UPPER_SNAKE`.
- UI는 `app.py`/`viewer.py`에, 순수 로직은 유틸 모듈로 분리(`database.py`, `web_storage.py` 등).

## 테스트 가이드
- 공식 테스트 스위트는 아직 없음. `pytest` 권장:
  - 디렉터리: `tests/`
  - 파일: `test_*.py` (예: `tests/test_database.py`)
  - 실행: `pytest -q`
- 우선 커버리지: DB 연산, 스토리지 폴백, MTL/텍스처 처리 루틴.

## 커밋·PR 가이드
- 커밋: 명확·작게·현재형. 예) `feat(viewer): add background color toggle`, `fix(db): prevent null author`.
- PR 필수: 목적/요약, 연결된 이슈, UI/동작 변경 시 스크린샷·로그, 테스트 노트(수동 절차 또는 자동 테스트).
- 작은 단위로 제출하여 리뷰 용이성 확보.

## 보안·설정 팁
- 비밀정보 커밋 금지. 서버 URL/토큰은 `.streamlit/secrets.toml` 또는 환경변수 사용.
- PHP 엔드포인트는 업로드/삭제를 수행하므로 서버 측에서 파일 형식 검증·입력 sanitization 필수. 클라이언트도 OBJ/MTL/PNG/JPG로 제한.
- 토큰 기반 접근 유지: 직접 파일 경로 노출 금지, DB의 `share_token` 플로우 활용.
- 백업/생성물: `data/`, `uploads/`는 쓰기 가능해야 하며, 생성 파일은 Git에 커밋하지 않음.
