# 3D Model Manager & Viewer

Streamlit 기반 3D 모델 관리 및 공유 시스템

## 주요 기능
- 다중 3D 모델 업로드 및 관리 (최대 10개)
- 공유 링크 생성으로 인터넷 접근 가능
- 보안 강화 (와이어프레임 차단, 다운로드 불가)
- SQLite 기반 모델 데이터베이스

## 설치 및 실행

```bash
# 의존성 설치
uv sync

# 앱 실행
uv run streamlit run app.py
```

## 사용법
1. **업로드**: OBJ + MTL + 텍스처 파일 업로드
2. **공유**: 생성된 링크로 외부 공유
3. **관리**: 저장된 모델 목록, 미리보기, 삭제

## 파일 구조
```
streamlit_3dviewer/
├── app.py          # 메인 애플리케이션
├── database.py     # 모델 데이터베이스
├── viewer.py       # 공유 뷰어 페이지
└── data/           # 모델 데이터 저장소
```

## 공유 URL 형식
```
http://localhost:8501/?token=<share_token>
```
