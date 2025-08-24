# Hugging Face 배포용 최소 수정 파일
# web_storage.py 의 일부만 수정

import os

class WebServerStorage:
    def __init__(self):
        # Hugging Face Spaces에서는 로컬 저장소 사용
        self.use_local = True  # 또는 환경변수로 제어
        
        if os.environ.get('SPACE_ID'):  # HF Spaces 환경 감지
            self.use_local = True
            self.storage_path = './data/models'
            os.makedirs(self.storage_path, exist_ok=True)
        else:
            # 기존 웹서버 코드
            self.use_local = False
            self.web_url = "http://decimate27.dothome.co.kr/streamlit_data/"
    
    # 나머지 코드는 그대로...
