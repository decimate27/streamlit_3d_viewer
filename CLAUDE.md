# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요
Streamlit 기반 3D 모델 뷰어 및 관리 시스템. 웹브라우저에서 3D 모델(OBJ/MTL/텍스처)을 업로드, 관리, 공유할 수 있는 플랫폼.

## 개발 명령어

### 애플리케이션 실행
```bash
# uv 사용 (권장)
uv run streamlit run app.py

# pip 환경
streamlit run app.py
```

### 의존성 설치
```bash
# uv 사용
uv sync

# pip 사용
pip install -r requirements.txt
```

### 데이터베이스 관리
```bash
# DB 초기화 (문제 해결용)
python force_reset_db.py

# DB 테스트
python test_db.py
```

### 텍스처 최적화 테스트
```bash
python optimize_texture.py [이미지파일경로]
```

## 핵심 아키텍처

### 1. 파일 저장 시스템 (이중화)
- **1차 저장소**: Dothome 웹서버 (`http://decimate27.dothome.co.kr/streamlit_data/`)
  - `web_storage.py`: WebServerStorage 클래스
  - PHP 백엔드: `upload.php`, `delete.php`
- **2차 백업**: 로컬 파일시스템 (`data/models/`)
  - `web_storage.py`: LocalBackupStorage 클래스
- **폴백 메커니즘**: 웹서버 실패시 자동으로 로컬 백업 사용

### 2. 데이터베이스 구조
- SQLite 기반 (`data/models.db`)
- `database.py`: ModelDatabase 클래스
- 모델 메타데이터: ID, 이름, 작성자, 설명, 파일경로, 공유토큰, 조회수 등

### 3. 3D 뷰어 렌더링
- `viewer_utils.py`: Three.js 기반 HTML/JS 생성
  - OBJLoader, MTLLoader 사용
  - 텍스처 base64 인코딩 및 동적 로딩
  - 카메라/조명/컨트롤 설정
- `viewer.py`: 공유 링크 뷰어 페이지

### 4. 인증 시스템
- `auth.py`: 세션 기반 인증
  - 환경변수 또는 기본 비밀번호 사용
  - 30분 타임아웃
  - 쿠키 기반 자동 로그인

### 5. 자동 처리 기능
- `mtl_generator.py`: MTL 파일 자동 생성
- `texture_optimizer.py`: 대용량 텍스처 자동 압축 (2MB/1024px 임계값)

## 주요 모듈 역할

- **app.py**: 메인 Streamlit 앱 (업로드/관리 UI)
- **database.py**: 모델 CRUD 및 DB 관리
- **viewer.py**: 공유 링크 전용 뷰어
- **viewer_utils.py**: 3D 렌더링 HTML/JS 생성
- **web_storage.py**: 웹서버/로컬 파일 저장 관리
- **auth.py**: 인증 및 세션 관리

## 보안 고려사항
- UUID v4 기반 공유 토큰
- 와이어프레임 모드 비활성화
- 텍스처 필수 적용 (텍스처 없는 렌더링 차단)
- 관리자 페이지 인증 필수

## 외부 연동
- Dothome 웹서버: PHP 백엔드 API (upload.php, delete.php)
- Streamlit Cloud: 클라우드 배포 지원