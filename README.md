# 🎮 (주)에어바이블 3D 모델 뷰어

Streamlit 기반의 엔터프라이즈급 3D 모델 관리 및 공유 시스템으로, 웹 브라우저에서 직접 3D 모델을 업로드하고 관리하며 공유할 수 있는 통합 플랫폼입니다.

## 📋 목차
- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [설치 가이드](#설치-가이드)
- [사용 방법](#사용-방법)
- [UI/UX 특징](#uiux-특징)
- [외부 저장소](#외부-저장소)
- [기술 스택](#기술-스택)
- [파일 구조](#파일-구조)
- [API 문서](#api-문서)
- [보안 기능](#보안-기능)
- [문제 해결](#문제-해결)

## 🌟 주요 기능

### 📤 모델 업로드 및 관리
- **다중 모델 지원**: 최대 20개의 3D 모델 동시 관리
- **자동 MTL 생성**: 텍스처 기반 재질 파일 자동 생성
- **텍스처 최적화**: 대용량 텍스처 자동 압축 (2MB/1024px 임계값)
- **작성자 정보**: 모델별 작성자 및 설명 기록
- **조회수 추적**: 각 모델의 접근 횟수 자동 기록

### 🌐 공유 및 배포
- **고유 공유 링크**: UUID 기반 보안 토큰 생성
- **즉시 공유**: 링크만으로 누구나 3D 모델 접근 가능
- **클라우드 배포**: Streamlit Cloud 통합 지원
- **반응형 디자인**: 모바일/태블릿/데스크톱 최적화

### 🎨 3D 뷰어 기능
- **Three.js 렌더링**: WebGL 기반 고성능 3D 렌더링
- **인터랙티브 컨트롤**:
  - 마우스 드래그: 모델 회전
  - 마우스 휠: 확대/축소
  - 우클릭 드래그: 모델 이동
- **배경색 변경**: 실시간 배경색 전환 (흰색/회색/검은색)
- **매트 렌더링**: 반사 제거로 선명한 모델 표현
- **자동 크기 조정**: 모델 크기 자동 정규화

### 🔒 보안 기능
- **와이어프레임 차단**: 모델 구조 보호
- **다운로드 방지**: 파일 직접 다운로드 차단
- **텍스처 필수**: 텍스처 없는 모델 로드 불가
- **토큰 기반 접근**: UUID v4 기반 보안 토큰

## 🏗️ 시스템 아키텍처

### 데이터베이스 구조
```sql
models 테이블:
- id: TEXT PRIMARY KEY (UUID)
- name: TEXT NOT NULL (모델명)
- author: TEXT (작성자)
- description: TEXT (설명)
- file_paths: TEXT (파일 경로 JSON)
- backup_paths: TEXT (백업 경로 JSON)
- storage_type: TEXT DEFAULT 'web' (저장 타입)
- share_token: TEXT UNIQUE (공유 토큰)
- created_at: TIMESTAMP (생성일)
- last_accessed: TIMESTAMP (최근 접근)
- access_count: INTEGER DEFAULT 0 (조회수)
```

### 저장소 아키텍처
```
┌─────────────────────────────────────┐
│         Streamlit Frontend          │
│   (app.py, viewer.py, viewer_utils) │
└────────────┬────────────────────────┘
             │
     ┌───────▼───────┐
     │  Database.py  │
     │   (SQLite)    │
     └───┬───────┬───┘
         │       │
    ┌────▼──┐ ┌─▼──────────┐
    │  Web  │ │   Local    │
    │Storage│ │  Backup    │
    └───────┘ └────────────┘
         │
    ┌────▼──────────────┐
    │ Dothome.co.kr    │
    │  Web Server      │
    │ (PHP Backend)    │
    └──────────────────┘
```

## 📥 설치 가이드

### 필수 요구사항
- Python 3.8 이상
- uv 패키지 매니저 (또는 pip)
- 1GB 이상의 여유 공간

### 설치 방법

#### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/streamlit_3dviewer.git
cd streamlit_3dviewer
```

#### 2. 의존성 설치
```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install -r requirements.txt
```

#### 3. 애플리케이션 실행
```bash
# uv 사용
uv run streamlit run app.py

# 또는 직접 실행
streamlit run app.py
```

## 📖 사용 방법

### 1. 모델 업로드
1. **업로드 탭** 선택
2. **모델 정보 입력**:
   - 모델 이름 (필수)
   - 작성자 이름 (필수)
   - 설명 (선택사항)
3. **파일 선택**:
   - OBJ 파일 (필수): 3D 모델 메시
   - 텍스처 이미지 (필수): PNG/JPG/JPEG
   - MTL 파일 (선택): 업로드해도 자동 재생성
4. **"모델 저장 및 공유 링크 생성"** 클릭

### 2. 모델 관리
- **관리 탭**에서 저장된 모델 목록 확인
- 각 모델별 정보 표시:
  - 제목, 조회수, 작성자, 날짜, 설명
  - 저장 위치 (웹서버/로컬)
- **미리보기**: 배경색 선택 가능한 3D 뷰어
- **공유 링크**: 복사하여 외부 공유
- **삭제**: 모델 완전 제거

### 3. 모델 공유
1. 생성된 공유 링크 복사
2. 링크 형식: `https://airbible-3d-viewer.streamlit.app?token=xxxxx`
3. 링크 접속 시 전체 화면 3D 뷰어 자동 로드

## 🎨 UI/UX 특징

### 메인 인터페이스
```
┌──────────────────────────────────────┐
│  🎮 (주)에어바이블 3D 모델 뷰어 관리  │
├──────────────────────────────────────┤
│ ┌─────┬─────┬──────┐                 │
│ │업로드│관리│사용법│                  │
│ └─────┴─────┴──────┘                 │
│                                      │
│  [현재 저장된 모델: 5/20]           │
│                                      │
│  모델 이름: [___________]           │
│  작성자:    [___________]           │
│  설명:      [___________]           │
│                                      │
│  [파일 선택 영역]                   │
│                                      │
│  [모델 저장 및 공유 링크 생성]      │
└──────────────────────────────────────┘
```

### 3D 뷰어 인터페이스
```
┌──────────────────────────────────────┐
│  ┌─────────┐                        │
│  │ ⚪ 흰색 │  [3D 모델 렌더링 영역] │
│  │ 🔘 회색 │                        │
│  │ ⚫ 검은색│                        │
│  └─────────┘                        │
│                                      │
│      마우스 컨트롤:                  │
│      - 드래그: 회전                  │
│      - 휠: 확대/축소                 │
│      - 우클릭: 이동                  │
└──────────────────────────────────────┘
```

### 모바일 최적화
- **반응형 버튼**: 화면 크기에 따른 버튼 크기 조정
- **터치 제스처**: 모바일 터치 컨트롤 지원
- **간소화 UI**: 작은 화면에서 아이콘만 표시

## 🌐 외부 저장소

### Dothome 웹서버 통합
본 시스템은 Dothome.co.kr 웹서버와 통합되어 영구적인 파일 저장을 지원합니다.

#### 서버 구조
```
http://decimate27.dothome.co.kr/
└── streamlit_data/
    ├── upload.php    # 파일 업로드 API
    ├── delete.php    # 파일 삭제 API
    └── files/        # 모델 파일 저장소
        └── {model_id}/
            ├── model.obj
            ├── model.mtl
            └── *.png/jpg
```

#### PHP Backend API

##### upload.php
```php
엔드포인트: POST /streamlit_data/upload.php
파라미터:
- file: 업로드할 파일 (multipart/form-data)
- model_id: 모델 고유 ID
- action: 'upload'

응답:
{
  "status": "success",
  "file_path": "{model_id}/filename",
  "message": "File uploaded successfully"
}
```

##### delete.php
```php
엔드포인트: POST /streamlit_data/delete.php
파라미터:
- model_id: 삭제할 모델 ID
- action: 'delete' 또는 'list'

응답 (delete):
{
  "status": "success",
  "message": "Model deleted successfully"
}

응답 (list):
{
  "status": "success",
  "models": [
    {
      "model_id": "xxx",
      "files": [...]
    }
  ]
}
```

### 저장소 폴백 메커니즘
1. **1차 시도**: Dothome 웹서버 업로드
2. **실패 시**: 로컬 백업 저장 (data/models/)
3. **로드 시**: 웹서버 → 로컬 백업 순서로 시도

## 🛠️ 기술 스택

### Frontend
- **Streamlit**: 웹 애플리케이션 프레임워크
- **Three.js**: 3D 그래픽 렌더링
- **JavaScript**: 인터랙티브 기능 구현

### Backend
- **Python 3.8+**: 핵심 애플리케이션 로직
- **SQLite**: 모델 메타데이터 관리
- **PHP**: 웹서버 파일 관리 API

### 주요 라이브러리
```python
streamlit==1.31.0      # 웹 프레임워크
trimesh==3.9.43        # 3D 모델 처리
Pillow==10.2.0        # 이미지 처리
requests==2.31.0      # HTTP 통신
```

## 📁 파일 구조

```
streamlit_3dviewer/
├── app.py                 # 메인 애플리케이션 진입점
├── database.py            # 데이터베이스 관리 및 모델 CRUD
├── viewer.py              # 공유 링크 뷰어 페이지
├── viewer_utils.py        # 3D 뷰어 HTML/JS 생성
├── web_storage.py         # 웹서버 스토리지 통합
├── texture_optimizer.py   # 텍스처 자동 최적화
├── mtl_generator.py       # MTL 파일 자동 생성
│
├── data/                  # 로컬 데이터 저장소
│   ├── models.db          # SQLite 데이터베이스
│   └── models/            # 로컬 백업 파일
│       └── {model_id}/
│           ├── model.obj
│           ├── model.mtl
│           └── *.png
│
├── uploads/               # 임시 업로드 디렉토리
├── requirements.txt       # Python 의존성
├── pyproject.toml        # 프로젝트 설정
├── uv.lock               # uv 패키지 락 파일
│
├── upload.php            # 웹서버 업로드 스크립트
├── delete.php            # 웹서버 삭제 스크립트
│
└── test_*.py             # 테스트 스크립트들
```

## 📚 API 문서

### ModelDatabase 클래스

```python
class ModelDatabase:
    def save_model(name, author, description, obj_content, mtl_content, texture_data)
        """모델 저장 (웹서버 + 로컬 백업)"""
        Returns: (model_id, share_token)
    
    def get_model_by_token(share_token)
        """공유 토큰으로 모델 조회"""
        Returns: model_data dict
    
    def get_all_models()
        """모든 모델 목록 조회"""
        Returns: list of model dicts
    
    def delete_model(model_id)
        """모델 삭제 (웹서버 + 로컬)"""
        Returns: bool
```

### WebServerStorage 클래스

```python
class WebServerStorage:
    def save_model_to_server(model_id, obj_content, mtl_content, texture_data)
        """웹서버에 모델 저장"""
        Returns: file_paths dict or None
    
    def load_model_from_server(file_paths)
        """웹서버에서 모델 로드"""
        Returns: (obj_content, mtl_content, texture_data)
    
    def delete_model(model_id)
        """웹서버에서 모델 삭제"""
        Returns: bool
```

## 🔐 보안 기능

### 모델 보호
- **와이어프레임 모드 비활성화**: 모델 구조 보호
- **텍스처 필수 적용**: 텍스처 없는 렌더링 차단
- **다운로드 방지**: 브라우저 다운로드 기능 차단

### 접근 제어
- **UUID v4 토큰**: 예측 불가능한 고유 토큰
- **토큰 기반 접근**: 토큰 없이 모델 접근 불가
- **접근 기록**: 모든 접근 시간 및 횟수 기록

### 데이터 보안
- **이중 백업**: 웹서버 + 로컬 백업
- **자동 정리**: 삭제 시 모든 저장소에서 제거
- **SSL 통신**: HTTPS 통한 안전한 데이터 전송

## 🔧 문제 해결

### 데이터베이스 초기화
관리 탭 → 문제 해결 → "데이터베이스 초기화" 클릭
- 기존 DB 백업 후 새로 생성
- 파일은 보존, 메타데이터만 초기화

### 웹서버 연결 테스트
1. 관리 탭 → 문제 해결 열기
2. 서버 URL 입력 (기본값 제공)
3. "서버 연결 테스트" 클릭
4. 연결 상태 및 응답 확인

### 텍스처 최적화 테스트
1. 문제 해결 섹션에서 이미지 업로드
2. "최적화 테스트" 클릭
3. 원본 vs 최적화 크기 비교
4. 최적화된 파일 다운로드 가능

### 일반적인 문제
- **모델이 표시되지 않음**: 텍스처 파일 확인
- **업로드 실패**: 파일 크기 및 형식 확인
- **공유 링크 작동 안 함**: 토큰 유효성 확인

## 📞 지원 및 문의

- **회사**: (주)에어바이블
- **이메일**: airbible@naver.com
- **웹사이트**: https://airbible.com
- **라이선스**: MIT License
