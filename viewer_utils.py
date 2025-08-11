import base64
from pathlib import Path

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
            body {{ margin: 0; padding: 0; overflow: hidden; background: #1a1a1a; }}
            #container {{ 
                width: 100vw; 
                height: 100vh; 
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            canvas {{
                display: block;
                margin: 0 auto;
            }}
            .loading {{ 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                color: white;
                font-family: Arial, sans-serif;
                font-size: 18px;
                z-index: 100;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div class="loading" id="loading">모델 로딩 중...</div>
        </div>
        
        <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/loaders/MTLLoader.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <script>
            let scene, camera, renderer, controls;
            let model;
            
            function init() {{
                try {{
                    console.log('Three.js version:', THREE.REVISION);
                    
                    // Scene 생성
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x222222);
                    
                    // Camera 생성
                    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 0, 5);
                    
                    // Renderer 생성
                    renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(window.innerWidth, window.innerHeight);
                    renderer.setPixelRatio(window.devicePixelRatio);
                    renderer.shadowMap.enabled = true;
                    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                    
                    const container = document.getElementById('container');
                    container.appendChild(renderer.domElement);
                    
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
                    
                    console.log('Scene setup complete');
                    
                    // 모델 로드
                    loadModel();
                    
                    // 렌더링 시작
                    animate();
                    
                    // 창 크기 변경 이벤트
                    window.addEventListener('resize', onWindowResize);
                }} catch (error) {{
                    console.error('Init error:', error);
                    document.getElementById('loading').innerHTML = 'Error: ' + error.message;
                }}
            }}
            
            function loadModel() {{
                try {{
                    console.log('Starting model load...');
                    
                    // 텍스처 로더
                    const textureLoader = new THREE.TextureLoader();
                    const textures = {{}};
                    
                    // 텍스처 로딩
                    {create_texture_loading_code(texture_base64)}
                    
                    console.log('Textures loaded:', Object.keys(textures));
                    
                    // MTL 로더
                    console.log('Loading MTL...');
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
                    
                    console.log('Materials loaded');
                    
                    // OBJ 로더
                    console.log('Loading OBJ...');
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
                    
                    console.log('Model loaded successfully');
                    document.getElementById('loading').style.display = 'none';
                }} catch (error) {{
                    console.error('Model loading error:', error);
                    document.getElementById('loading').innerHTML = 'Model loading failed: ' + error.message;
                }}
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
    if not texture_base64:
        return "// No textures available"
    
    code_lines = []
    for name, data in texture_base64.items():
        safe_name = name.replace('.', '_').replace('-', '_')
        ext = Path(name).suffix.lower()
        mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
        code_lines.append(f"""
                const img_{safe_name} = new Image();
                img_{safe_name}.src = 'data:{mime_type};base64,{data}';
                textures['{name}'] = textureLoader.load(img_{safe_name}.src);
        """)
    
    return '\n'.join(code_lines)
