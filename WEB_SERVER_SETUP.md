# 웹서버 SQLite DB 설정 가이드

## 📋 개요
로컬 Flask 서버 대신 웹서버의 SQLite 데이터베이스를 사용하여 더 안정적인 피드백 시스템을 구축합니다.

## 🌐 웹서버 업로드 파일들

### 1. 웹서버에 업로드할 PHP 스크립트들:
```
web_server_scripts/
├── init_database.php      # 데이터베이스 초기화
├── save_model.php         # 모델 저장 API
├── load_model.php         # 모델 로드 API
└── feedback_api.php       # 피드백 CRUD API
```

### 2. 웹서버 디렉토리 구조:
```
http://decimate27.dothome.co.kr/streamlit_data/
├── init_database.php
├── save_model.php  
├── load_model.php
├── feedback_api.php
├── upload.php             # 기존 파일 업로드
├── delete.php             # 기존 파일 삭제
├── files/                 # 파일 저장 디렉토리
│   └── [model_id]/        # 모델별 디렉토리
│       ├── model.obj
│       ├── model.mtl
│       └── *.jpg, *.png   # 텍스처 파일들
└── streamlit_3d.db        # SQLite 데이터베이스 (자동 생성)
```

## 🚀 설정 순서

### 1단계: PHP 파일 업로드
FTP 또는 웹 호스팅 파일 매니저를 통해 다음 파일들을 업로드:
- `web_server_scripts/init_database.php` → `streamlit_data/init_database.php`
- `web_server_scripts/save_model.php` → `streamlit_data/save_model.php`
- `web_server_scripts/load_model.php` → `streamlit_data/load_model.php`
- `web_server_scripts/feedback_api.php` → `streamlit_data/feedback_api.php`

### 2단계: 데이터베이스 초기화
웹 브라우저에서 다음 URL 접속:
```
http://decimate27.dothome.co.kr/streamlit_data/init_database.php
```

성공 응답 예시:
```json
{
  "status": "success",
  "message": "Database initialized successfully",
  "tables_created": ["models", "feedbacks"],
  "db_file": "streamlit_3d.db"
}
```

### 3단계: 권한 설정
웹서버에서 다음 디렉토리/파일이 쓰기 가능한지 확인:
- `streamlit_data/` 디렉토리
- `streamlit_data/files/` 디렉토리
- `streamlit_3d.db` 파일 (자동 생성됨)

## 🔧 API 엔드포인트들

### 1. 데이터베이스 초기화
```
GET /init_database.php
```

### 2. 모델 저장
```
POST /save_model.php
Content-Type: application/json

{
  "model_id": "uuid",
  "name": "모델명",
  "author": "작성자",
  "description": "설명",
  "share_token": "uuid",
  "obj_content": "OBJ 파일 내용",
  "mtl_content": "MTL 파일 내용",
  "texture_data": {
    "texture1.jpg": "base64_encoded_data",
    "texture2.png": "base64_encoded_data"
  }
}
```

### 3. 모델 로드
```
GET /load_model.php?token=share_token
```

### 4. 피드백 저장
```
POST /feedback_api.php?action=save
Content-Type: application/json

{
  "model_id": "uuid",
  "x": 0.123,
  "y": 0.456, 
  "z": 0.789,
  "screen_x": 100,
  "screen_y": 200,
  "comment": "피드백 내용",
  "feedback_type": "point"
}
```

### 5. 피드백 조회
```
GET /feedback_api.php?action=list&model_id=uuid
```

### 6. 피드백 상태 업데이트
```
PUT /feedback_api.php?action=update_status
Content-Type: application/json

{
  "id": 123,
  "status": "reviewed"  // pending, reviewed, resolved
}
```

### 7. 피드백 삭제
```
DELETE /feedback_api.php?id=123
```

## 🧪 테스트 방법

### 1. 데이터베이스 초기화 테스트
```bash
curl http://decimate27.dothome.co.kr/streamlit_data/init_database.php
```

### 2. 피드백 저장 테스트
```bash
curl -X POST \
  http://decimate27.dothome.co.kr/streamlit_data/feedback_api.php?action=save \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "test-model", 
    "x": 1.0, 
    "y": 2.0, 
    "z": 3.0,
    "screen_x": 100,
    "screen_y": 200,
    "comment": "테스트 피드백",
    "feedback_type": "point"
  }'
```

## 🔧 문제 해결

### PHP 오류 확인
웹서버에서 PHP 오류 로그 확인:
```
error_log 또는 웹 호스팅 제공업체의 로그 확인
```

### SQLite 권한 문제
```bash
chmod 666 streamlit_3d.db        # 파일 읽기/쓰기
chmod 777 streamlit_data/         # 디렉토리 쓰기
```

### CORS 문제
모든 PHP 파일에 CORS 헤더가 포함되어 있어야 합니다:
```php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
```

## 🎯 장점

1. **안정성**: 웹서버 환경에서 24/7 동작
2. **확장성**: SQLite에서 MySQL/PostgreSQL로 쉽게 확장 가능
3. **독립성**: 로컬 Flask 서버 불필요
4. **영속성**: 서버 재시작 시에도 데이터 유지
5. **성능**: 캐시와 인덱싱으로 빠른 조회

## 📝 주의사항

1. **보안**: 실제 운영 시 API 인증 추가 권장
2. **백업**: 정기적으로 streamlit_3d.db 백업
3. **용량**: 텍스처 파일 크기 제한 고려
4. **동시성**: 많은 사용자 접속 시 데이터베이스 락 주의

이제 웹서버 기반의 안정적인 3D 모델 뷰어와 피드백 시스템을 구축할 수 있습니다!
