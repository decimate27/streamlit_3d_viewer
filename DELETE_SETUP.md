# 서버 삭제 기능 설치 가이드

## 📁 업로드할 파일
`delete.php` 파일을 웹서버에 업로드해야 합니다.

### FTP 업로드 경로
```
FTP: ftp://decimate27@decimate27.dothome.co.kr/html/streamlit_data/delete.php
웹 URL: http://decimate27.dothome.co.kr/streamlit_data/delete.php
```

### 파일 위치
```
/html/streamlit_data/
├── upload.php    (기존)
├── delete.php    (신규 업로드)
└── files/        (모델 저장 폴더)
    └── [model_id]/
        ├── model.obj
        ├── model.mtl
        └── texture.jpg
```

## 🔧 테스트 방법

### 1. delete.php 업로드 후 테스트
```bash
cd /Users/bag-wonseog/temp/streamlit_3dviewer
source .venv/bin/activate
python test_delete.py
```

### 2. 웹 앱에서 테스트
- 브라우저에서 앱의 "문제 해결" 섹션 접속
- "서버 모델 목록 조회" 버튼 클릭
- 서버의 모델들이 표시되는지 확인

### 3. 실제 삭제 테스트
- 웹 앱에서 모델 삭제 버튼 클릭
- 로그에 "웹서버에서 삭제 성공" 메시지 확인

## ⚠️ 주의사항
- delete.php가 없으면 웹서버 삭제는 실패하고 로컬만 삭제됩니다
- 실제 파일이 서버에서 완전히 삭제되므로 주의해서 사용하세요

## 🔒 보안 기능
- Model ID 유효성 검사 (영숫자만 허용)
- 경로 조작 공격 방지
- 재귀적 디렉토리 삭제로 완전 제거
