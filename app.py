import streamlit as st
import os
import tempfile
import base64
from pathlib import Path
import trimesh
from PIL import Image
import zipfile
import shutil

# 페이지 설정
st.set_page_config(
    page_title="3D Model Viewer",
    page_icon="🎮",
    layout="wide"
)

class ModelProcessor:
    def __init__(self):
        self.supported_model_formats = ['.obj']
        self.supported_material_formats = ['.mtl']
        self.supported_texture_formats = ['.png', '.jpg', '.jpeg']
    
    def validate_files(self, uploaded_files):
        """업로드된 파일들의 유효성 검사"""
        file_types = {
            'model': [],
            'material': [],
            'texture': []
        }
        
        for file in uploaded_files:
            ext = Path(file.name).suffix.lower()
            if ext in self.supported_model_formats:
                file_types['model'].append(file)
            elif ext in self.supported_material_formats:
                file_types['material'].append(file)
            elif ext in self.supported_texture_formats:
                file_types['texture'].append(file)
        
        # 필수 파일 확인
        if not file_types['model']:
            return False, "OBJ 모델 파일이 필요합니다."
        if not file_types['material']:
            return False, "MTL 재질 파일이 필요합니다."
        if not file_types['texture']:
            return False, "텍스처 이미지 파일이 필요합니다."
        
        return True, file_types
    
    def save_uploaded_files(self, file_types, temp_dir):
        """업로드된 파일들을 임시 디렉토리에 저장"""
        saved_files = {}
        
        # 모델 파일 저장
        for file in file_types['model']:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            saved_files['model'] = file_path
        
        # 재질 파일 저장
        for file in file_types['material']:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            saved_files['material'] = file_path
        
        # 텍스처 파일들 저장
        saved_files['textures'] = []
        for file in file_types['texture']:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            saved_files['textures'].append(file_path)
        
        return saved_files

def create_3d_viewer_html(obj_content, mtl_content, texture_data):
    """Three.js 기반 3D 뷰어 HTML 생성"""
    
    # 텍스처를 base64로 인코딩
    texture_base64 = {}
    for name, data in texture_data.items():
        texture_base64[name] = base64.b64encode(data).decode('utf-8')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>3D Model Viewer</title>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; }}
            #container {{ width: 100%; height: 100vh; }}
            .loading {{ 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                color: white;
                font-family: Arial, sans-serif;
                font-size: 18px;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div class="loading" id="loading">모델 로딩 중...</div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <script>
            let scene, camera, renderer, controls;
            let model;
            
            function init() {{
                // Scene 생성
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x222222);
                
                // Camera 생성
                camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(0, 0, 5);
                
                // Renderer 생성
                renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                document.getElementById('container').appendChild(renderer.domElement);
                
                // Controls 생성
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.enableZoom = true;
                controls.enablePan = true;
                controls.enableRotate = true;
                
                // 조명 추가
                const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                scene.add(ambientLight);
                
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(1, 1, 1);
                directionalLight.castShadow = true;
                scene.add(directionalLight);
                
                // 모델 로드
                loadModel();
                
                // 렌더링 시작
                animate();
                
                // 창 크기 변경 이벤트
                window.addEventListener('resize', onWindowResize);
            }}
            
            function loadModel() {{
                // 텍스처 로더
                const textureLoader = new THREE.TextureLoader();
                const textures = {{}};
                
                // 텍스처 로딩
                {create_texture_loading_code(texture_base64)}
                
                // MTL 로더
                const mtlLoader = new THREE.MTLLoader();
                const materials = mtlLoader.parse(`{mtl_content}`, '');
                materials.preload();
                
                // 텍스처 적용 보장
                for (let materialName in materials.materials) {{
                    const material = materials.materials[materialName];
                    if (material.map && !material.map.image) {{
                        // 기본 텍스처가 없으면 첫 번째 텍스처 사용
                        const textureNames = Object.keys(textures);
                        if (textureNames.length > 0) {{
                            material.map = textures[textureNames[0]];
                        }}
                    }}
                }}
                
                // OBJ 로더
                const objLoader = new THREE.OBJLoader();
                objLoader.setMaterials(materials);
                
                const object = objLoader.parse(`{obj_content}`);
                
                // 모델 크기 조정 및 중앙 정렬
                const box = new THREE.Box3().setFromObject(object);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 2 / maxDim;
                object.scale.set(scale, scale, scale);
                
                object.position.sub(center.multiplyScalar(scale));
                
                scene.add(object);
                model = object;
                
                // 카메라 위치 조정
                const distance = maxDim * scale * 2;
                camera.position.set(distance, distance, distance);
                camera.lookAt(0, 0, 0);
                
                document.getElementById('loading').style.display = 'none';
            }}
            
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            
            function onWindowResize() {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }}
            
            init();
        </script>
    </body>
    </html>
    """
    
    return html_content

def create_texture_loading_code(texture_base64):
    """텍스처 로딩 JavaScript 코드 생성"""
    code_lines = []
    for name, data in texture_base64.items():
        ext = Path(name).suffix.lower()
        mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
        code_lines.append(f"""
                const img_{name.replace('.', '_')} = new Image();
                img_{name.replace('.', '_')}.src = 'data:{mime_type};base64,{data}';
                textures['{name}'] = textureLoader.load(img_{name.replace('.', '_')}.src);
        """)
    
    return '\n'.join(code_lines)

def main():
    st.title("🎮 3D 모델 뷰어")
    st.markdown("### OBJ, MTL, 텍스처 파일을 업로드하여 3D 모델을 확인하세요")
    
    # 사이드바에 파일 업로드
    with st.sidebar:
        st.header("파일 업로드")
        
        uploaded_files = st.file_uploader(
            "모델 파일들을 선택하세요",
            type=['obj', 'mtl', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="OBJ 모델 파일, MTL 재질 파일, 그리고 텍스처 이미지 파일들이 필요합니다."
        )
        
        if uploaded_files:
            st.success(f"{len(uploaded_files)}개 파일이 업로드되었습니다")
            
            # 파일 목록 표시
            for file in uploaded_files:
                st.write(f"📁 {file.name}")
    
    # 메인 영역
    if uploaded_files:
        processor = ModelProcessor()
        
        # 파일 유효성 검사
        is_valid, result = processor.validate_files(uploaded_files)
        
        if not is_valid:
            st.error(result)
            st.info("필요한 파일: OBJ 모델 파일, MTL 재질 파일, 텍스처 이미지 파일")
        else:
            file_types = result
            
            with st.spinner("3D 모델을 처리하고 있습니다..."):
                try:
                    # 임시 디렉토리 생성
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # 파일 저장
                        saved_files = processor.save_uploaded_files(file_types, temp_dir)
                        
                        # 파일 내용 읽기
                        with open(saved_files['model'], 'r') as f:
                            obj_content = f.read()
                        
                        with open(saved_files['material'], 'r') as f:
                            mtl_content = f.read()
                        
                        # 텍스처 데이터 읽기
                        texture_data = {}
                        for texture_path in saved_files['textures']:
                            texture_name = os.path.basename(texture_path)
                            with open(texture_path, 'rb') as f:
                                texture_data[texture_name] = f.read()
                        
                        # 3D 뷰어 HTML 생성
                        viewer_html = create_3d_viewer_html(obj_content, mtl_content, texture_data)
                        
                        # HTML 컴포넌트로 표시
                        st.components.v1.html(viewer_html, height=600)
                        
                        st.success("✅ 3D 모델이 성공적으로 로드되었습니다!")
                        st.info("마우스로 회전, 확대/축소, 이동이 가능합니다.")
                
                except Exception as e:
                    st.error(f"모델 처리 중 오류가 발생했습니다: {str(e)}")
    else:
        # 안내 메시지
        st.info("왼쪽 사이드바에서 3D 모델 파일들을 업로드해주세요.")
        
        with st.expander("사용법 안내"):
            st.markdown("""
            **필요한 파일:**
            - **OBJ 파일**: 3D 모델의 기하학적 정보
            - **MTL 파일**: 재질 정보 
            - **이미지 파일**: 텍스처 매핑용 (PNG, JPG)
            
            **조작법:**
            - **회전**: 마우스 드래그
            - **확대/축소**: 마우스 휠
            - **이동**: 마우스 오른쪽 버튼 드래그
            
            **보안 정책:**
            - 와이어프레임 모드 비활성화
            - 파일 다운로드 불가
            - 텍스처 필수 적용
            """)

if __name__ == "__main__":
    main()
