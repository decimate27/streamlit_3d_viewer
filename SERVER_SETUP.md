# 웹서버 설정 가이드

## 🚨 현재 문제
`https://airbible.kr/streamlit_data/upload.php` 파일이 존재하지 않아 웹서버 저장이 불가능합니다.

## 🔧 해결 방법

### 1. 서버에 디렉토리 구조 생성
```bash
/path/to/webroot/streamlit_data/
├── upload.php          # 업로드 처리 스크립트
└── files/              # 업로드된 파일 저장소
    └── [model_id]/     # 각 모델별 폴더
        ├── model.obj
        ├── model.mtl
        └── texture.jpg
```

### 2. upload.php 파일 업로드
현재 프로젝트의 `upload.php` 파일을 웹서버의 다음 경로에 업로드:
- **경로**: `/path/to/webroot/streamlit_data/upload.php`
- **권한**: 644 (읽기/쓰기)

### 3. 디렉토리 권한 설정
```bash
# files 디렉토리에 쓰기 권한 부여
chmod 755 /path/to/webroot/streamlit_data/
chmod 777 /path/to/webroot/streamlit_data/files/
```

### 4. PHP 설정 확인
```ini
; php.ini 설정
file_uploads = On
upload_max_filesize = 100M
post_max_size = 100M
max_execution_time = 300
```

### 5. 테스트 방법
서버 설정 후 다음 명령으로 테스트:
```bash
cd /Users/bag-wonseog/temp/streamlit_3dviewer
source .venv/bin/activate
python test_server_upload.py
```

## 🔍 현재 상태
- ❌ **웹서버 저장**: 불가능 (upload.php 없음)
- ✅ **로컬 저장**: 정상 작동
- ✅ **공유 기능**: 로컬 파일로 작동

## ⚠️ 임시 대응
서버 설정이 완료될 때까지 모든 파일은 Streamlit Cloud의 로컬 저장소에 저장됩니다.
공유 링크는 정상적으로 작동하지만 파일은 세션이 종료되면 삭제될 수 있습니다.

## 📞 서버 관리자 연락사항
웹서버에 upload.php 설치 및 권한 설정이 필요합니다.
