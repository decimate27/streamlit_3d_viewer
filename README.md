# 3D Model Viewer

Streamlit 기반 보안 3D 모델 뷰어 애플리케이션

## 기능
- OBJ, MTL, 텍스처 파일 업로드
- 인터랙티브 3D 뷰어 (회전, 확대/축소, 이동)
- 보안 제약: 와이어프레임 금지, 다운로드 불가

## 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

## 사용법
1. 사이드바에서 파일 업로드 (OBJ + MTL + 텍스처)
2. 3D 뷰어에서 모델 확인
3. 마우스로 조작

## 파일 형식
- 모델: .obj
- 재질: .mtl  
- 텍스처: .png, .jpg, .jpeg
