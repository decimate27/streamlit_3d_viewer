import requests

def test_full_model_upload():
    """전체 모델 업로드 테스트 (OBJ + MTL + 텍스처)"""
    url = "http://airbible.kr/streamlit_data/upload.php"
    model_id = "test-full-model-456"
    
    # 테스트 파일들
    obj_content = """# Test OBJ file
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.0 1.0 0.0
vt 0.0 0.0
vt 1.0 0.0
vt 0.5 1.0
f 1/1 2/2 3/3"""
    
    mtl_content = """# Test MTL file
newmtl material1
Ka 1.0 1.0 1.0
Kd 0.8 0.8 0.8
Ks 0.0 0.0 0.0
map_Kd test_texture.jpg"""
    
    # 가짜 이미지 데이터 (작은 JPEG 헤더)
    texture_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    
    print("=== 3개 파일 업로드 테스트 ===")
    
    success_count = 0
    
    # 1. OBJ 파일 업로드
    print("1. OBJ 파일 업로드...")
    files = {
        'file': ('model.obj', obj_content.encode('utf-8')),
        'model_id': (None, model_id),
        'action': (None, 'upload')
    }
    
    response = requests.post(url, files=files, timeout=30)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print(f"✅ OBJ 업로드 성공: {result.get('file_path')}")
            success_count += 1
        else:
            print(f"❌ OBJ 업로드 실패: {result.get('message')}")
    else:
        print(f"❌ OBJ 업로드 HTTP 오류: {response.status_code}")
    
    # 2. MTL 파일 업로드
    print("2. MTL 파일 업로드...")
    files = {
        'file': ('model.mtl', mtl_content.encode('utf-8')),
        'model_id': (None, model_id),
        'action': (None, 'upload')
    }
    
    response = requests.post(url, files=files, timeout=30)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print(f"✅ MTL 업로드 성공: {result.get('file_path')}")
            success_count += 1
        else:
            print(f"❌ MTL 업로드 실패: {result.get('message')}")
    else:
        print(f"❌ MTL 업로드 HTTP 오류: {response.status_code}")
    
    # 3. 텍스처 파일 업로드
    print("3. 텍스처 파일 업로드...")
    files = {
        'file': ('test_texture.jpg', texture_content),
        'model_id': (None, model_id),
        'action': (None, 'upload')
    }
    
    response = requests.post(url, files=files, timeout=30)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print(f"✅ 텍스처 업로드 성공: {result.get('file_path')}")
            success_count += 1
        else:
            print(f"❌ 텍스처 업로드 실패: {result.get('message')}")
    else:
        print(f"❌ 텍스처 업로드 HTTP 오류: {response.status_code}")
    
    print(f"\n총 {success_count}/3 파일 업로드 성공")
    
    # 업로드된 파일들 확인
    print("\n=== 업로드된 파일 확인 ===")
    base_url = f"http://airbible.kr/streamlit_data/files/{model_id}"
    
    for filename in ['model.obj', 'model.mtl', 'test_texture.jpg']:
        try:
            response = requests.get(f"{base_url}/{filename}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {filename}: {len(response.content)} bytes")
            else:
                print(f"❌ {filename}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {filename}: {str(e)}")

if __name__ == "__main__":
    test_full_model_upload()
