import requests
import urllib3
import os

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TestWebStorage:
    def __init__(self):
        self.base_url = "http://airbible.kr/streamlit_data"
        self.download_url = f"{self.base_url}/files"
        
    def download_file(self, file_path):
        """웹서버에서 파일 다운로드"""
        try:
            url = f"{self.download_url}/{file_path}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            print(f"다운로드 시도: {url}")
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            
            print(f"응답 상태: {response.status_code}")
            if response.status_code == 200:
                print(f"다운로드 성공: {len(response.content)} bytes")
                return response.content
            else:
                print(f"다운로드 실패: {response.status_code}")
                print(f"응답 내용: {response.text[:100]}")
                return None
        except Exception as e:
            print(f"다운로드 오류: {str(e)}")
            return None
    
    def load_model_from_server(self, file_paths):
        """웹서버에서 모델 로드"""
        try:
            print("=== 모델 로드 시작 ===")
            
            # OBJ 파일 다운로드
            print("1. OBJ 파일 다운로드...")
            obj_content = self.download_file(file_paths['obj_path'])
            if obj_content:
                obj_content = obj_content.decode('utf-8')
                print(f"OBJ 디코딩 성공: {len(obj_content)} chars")
            else:
                print("OBJ 다운로드 실패")
                return None, None, None
            
            # MTL 파일 다운로드
            print("\n2. MTL 파일 다운로드...")
            mtl_content = self.download_file(file_paths['mtl_path'])
            if mtl_content:
                mtl_content = mtl_content.decode('utf-8')
                print(f"MTL 디코딩 성공: {len(mtl_content)} chars")
            else:
                print("MTL 다운로드 실패")
                return None, None, None
            
            # 텍스처 파일들 다운로드
            print("\n3. 텍스처 파일들 다운로드...")
            texture_data = {}
            for texture_path in file_paths['texture_paths']:
                texture_name = os.path.basename(texture_path)
                print(f"텍스처 다운로드: {texture_name}")
                texture_content = self.download_file(texture_path)
                if texture_content:
                    texture_data[texture_name] = texture_content
                    print(f"텍스처 성공: {len(texture_content)} bytes")
                else:
                    print(f"텍스처 실패: {texture_name}")
                    return None, None, None
            
            print(f"\n모든 파일 로드 성공!")
            return obj_content, mtl_content, texture_data
            
        except Exception as e:
            print(f"모델 로드 중 오류: {str(e)}")
            return None, None, None

if __name__ == "__main__":
    storage = TestWebStorage()
    
    # 실제 서버에 있는 파일 테스트
    model_data = {
        'obj_path': 'test-44a85c20/model.obj',
        'mtl_path': 'test-44a85c20/model.mtl', 
        'texture_paths': ['test-44a85c20/coca-cola-texture.jpg']
    }
    
    obj_content, mtl_content, texture_data = storage.load_model_from_server(model_data)
    
    if obj_content and mtl_content and texture_data:
        print(f"\n✅ 전체 테스트 성공!")
        print(f"OBJ: {len(obj_content)} chars")
        print(f"MTL: {len(mtl_content)} chars") 
        print(f"텍스처: {len(texture_data)} files")
    else:
        print(f"\n❌ 테스트 실패")
