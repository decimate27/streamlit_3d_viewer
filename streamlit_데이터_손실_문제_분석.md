# Streamlit 3D Viewer 데이터 손실 문제 분석

## 문제 상황
- **증상**: Streamlit 애플리케이션 재부팅 후 업로드했던 모든 3D 모델이 사라짐
- **FTP 상태**: Dothome 웹서버에는 모든 파일이 그대로 남아있음
- **DB 상태**: SQLite 데이터베이스에 1개의 레코드만 남아있음 (8월 12일 생성된 'aaa' 모델)

## 문제 원인 분석

### 1. 주요 원인: Streamlit Cloud의 컨테이너 특성
Streamlit Cloud는 다음과 같은 특성을 가집니다:
- **일시적 파일시스템**: 애플리케이션이 재시작될 때마다 컨테이너가 재생성됨
- **로컬 파일 손실**: `/data/models.db`와 같은 로컬 파일은 재부팅 시 초기화됨
- **외부 저장소 필요성**: 영구 데이터는 반드시 외부 저장소에 보관해야 함

### 2. 현재 시스템의 문제점

#### 데이터베이스 구조
```python
# database.py의 init_db() 메서드
def init_db(self):
    """데이터베이스 초기화"""
    conn = sqlite3.connect(self.db_path)  # 로컬 파일시스템에 저장
    cursor = conn.cursor()
    
    # 테이블이 없으면 새로 생성
    if not columns:
        cursor.execute('''CREATE TABLE models (...)''')
        st.write("🆕 새 데이터베이스 테이블 생성")
```

**문제점**:
- SQLite DB가 로컬 파일시스템(`data/models.db`)에 저장됨
- Streamlit Cloud 재시작 시 DB 파일이 삭제되고 재생성됨
- init_db()가 매번 새 테이블을 생성하여 기존 데이터가 소실됨

#### 파일 저장 시스템
```python
# 현재 구조
1차 저장소: Dothome 웹서버 (영구 보존) ✅
2차 백업: 로컬 파일시스템 (재부팅 시 삭제) ❌
DB 메타데이터: SQLite 로컬 DB (재부팅 시 삭제) ❌
```

### 3. 데이터 손실 과정

1. **초기 상태**: 사용자가 모델 업로드
   - 파일 → Dothome 웹서버 (성공적으로 저장)
   - 메타데이터 → SQLite DB (로컬에 저장)

2. **Streamlit 재부팅**: 
   - 컨테이너 재생성
   - 로컬 파일시스템 초기화
   - `data/models.db` 파일 삭제

3. **애플리케이션 재시작**:
   - `ModelDatabase.__init__()` 실행
   - `init_db()` 메서드가 새 DB 테이블 생성
   - 기존 데이터 모두 손실

4. **결과**:
   - FTP 서버에는 파일 존재
   - DB에는 메타데이터 없음
   - 모델 목록이 비어있게 표시

## 해결 방안

### 1. 단기 해결책: 데이터 복구
```python
# 수동 복구 스크립트
def recover_models_from_ftp():
    """FTP 서버의 파일을 스캔하여 DB 재구성"""
    web_storage = WebServerStorage()
    db = ModelDatabase()
    
    # FTP 디렉토리 스캔
    model_dirs = web_storage.list_directories()
    
    for dir_id in model_dirs:
        # 파일 목록 확인
        files = web_storage.list_files(dir_id)
        
        # DB에 레코드 재생성
        db.recover_model(dir_id, files)
```

### 2. 중기 해결책: 외부 데이터베이스 사용

#### 옵션 A: PostgreSQL (Supabase/Neon)
```python
# PostgreSQL 연결
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')
url = urlparse(DATABASE_URL)

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
```

#### 옵션 B: Firebase Firestore
```python
# Firestore 사용
import firebase_admin
from firebase_admin import firestore

db = firestore.client()
models_ref = db.collection('models')
```

#### 옵션 C: Dothome MySQL 활용
```python
# 기존 Dothome 서버의 MySQL 사용
import pymysql

connection = pymysql.connect(
    host='localhost',
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    database='streamlit_3d',
    charset='utf8mb4'
)
```

### 3. 장기 해결책: 완전한 클라우드 아키텍처

```
┌─────────────────────────────────────┐
│     Streamlit Cloud (Frontend)      │
│         - UI/UX 처리만 담당          │
│         - 상태없는(Stateless) 설계   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        Cloud Database               │
│   (PostgreSQL/MySQL/Firestore)      │
│      - 모든 메타데이터 저장          │
│      - 영구 보존 보장                │
└─────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Object Storage (Dothome)       │
│        - 3D 파일 저장                │
│        - CDN 통합 가능               │
└─────────────────────────────────────┘
```

## 즉시 실행 가능한 조치

### 1. 임시 복구 기능 추가
```python
# app.py에 추가
if st.button("🔄 FTP에서 모델 복구"):
    recover_models_from_ftp()
    st.success("복구 완료!")
    st.rerun()
```

### 2. 환경 변수로 DB 위치 지정
```python
# Streamlit Cloud secrets에 추가
DB_TYPE = "external"  # local 또는 external
DB_CONNECTION_STRING = "postgresql://..."
```

### 3. 데이터베이스 추상화 레이어
```python
class DatabaseInterface:
    def __init__(self):
        if os.environ.get('DB_TYPE') == 'external':
            self.db = ExternalDatabase()
        else:
            self.db = LocalDatabase()
    
    def save_model(self, model_data):
        return self.db.save_model(model_data)
```

## 권장 우선순위

1. **즉시 (오늘)**: FTP 파일 스캔하여 DB 복구 기능 구현
2. **단기 (1주일 내)**: 외부 데이터베이스 연동 (Supabase 추천)
3. **중기 (1개월 내)**: 완전한 클라우드 아키텍처로 마이그레이션
4. **장기**: 자동 백업/복구 시스템 구축

## 예방 조치

1. **데이터베이스 백업**:
   - 주기적으로 DB를 외부 저장소에 백업
   - JSON 형태로 export하여 Git에 저장

2. **헬스체크 시스템**:
   - DB와 FTP 동기화 상태 확인
   - 불일치 발견 시 자동 복구

3. **모니터링**:
   - 모델 수 변화 추적
   - 비정상적인 데이터 손실 알림

## 결론

현재 문제는 Streamlit Cloud의 일시적 파일시스템 특성과 로컬 SQLite 데이터베이스 사용의 조합으로 발생했습니다. 파일은 Dothome 서버에 안전하게 보관되어 있으므로 데이터 자체는 손실되지 않았으며, DB 메타데이터만 재구성하면 됩니다.

**즉각적인 해결**: FTP 스캔을 통한 DB 복구  
**근본적인 해결**: 외부 데이터베이스 서비스 도입