import base64
from pathlib import Path

def create_3d_viewer_html(obj_content, mtl_content, texture_data, background_color="white"):
    """Three.js 기반 3D 뷰어 HTML 생성"""
    
    # 배경색 설정
    bg_colors = {
        "white": "#ffffff",
        "gray": "#808080", 
        "black": "#000000"
    }
    bg_color = bg_colors.get(background_color, "#ffffff")
    
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
            * {{ box-sizing: border-box; }}
            html, body {{ 
                margin: 0; 
                padding: 0; 
                width: 100%; 
                height: 100%; 
                overflow: hidden; 
                background: {bg_color}; 
            }}
            #container {{ 
                width: 100%; 
                height: 100%; 
                position: relative;
            }}
            canvas {{
                width: 100% !important;
                height: 100% !important;
                display: block;
            }}
            .loading {{ 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                color: {'white' if background_color == 'black' else 'black'};
                font-family: Arial, sans-serif;
                font-size: 18px;
                z-index: 100;
            }}
            .controls {{
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 200;
                display: flex;
                flex-direction: column;
                gap: 5px;
            }}
            .bg-btn {{
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                font-family: Arial, sans-serif;
                transition: opacity 0.3s;
            }}
            .bg-btn:hover {{
                opacity: 0.8;
            }}
            .bg-white {{ background: white; color: black; border: 1px solid #ccc; }}
            .bg-gray {{ background: #808080; color: white; }}
            .bg-black {{ background: black; color: white; }}
        </style>
    </head>
    <body>
        <div id="container">
            <div class="loading" id="loading">모델 로딩 중...</div>
            
            <!-- 배경색 변경 컨트롤 -->
            <div class="controls">
                <button class="bg-btn bg-white" onclick="changeBackground('white')">⚪ 흰색</button>
                <button class="bg-btn bg-gray" onclick="changeBackground('gray')">🔘 회색</button>
                <button class="bg-btn bg-black" onclick="changeBackground('black')">⚫ 검은색</button>
            </div>
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
                    scene.background = new THREE.Color(0xffffff);
                    
                    // Camera 생성
                    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 0, 5);
                    
                    // Renderer 생성
                    const container = document.getElementById('container');
                    renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(window.devicePixelRatio);
                    renderer.setClearColor(0x{bg_color[1:]}, 1); // 초기 배경색 설정
                    container.appendChild(renderer.domElement);
                    
                    // Controls 생성
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.05;
                    controls.enableZoom = true;
                    controls.enablePan = true;
                    controls.enableRotate = true;
                    
                    // 조명 설정 - 매트한 렌더링용
                    const ambientLight = new THREE.AmbientLight(0xffffff, 1.0); // 밝은 주변광
                    scene.add(ambientLight);
                    
                    // 방향광은 매우 부드럽게
                    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.3);
                    directionalLight1.position.set(1, 1, 1);
                    scene.add(directionalLight1);
                    
                    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.2);
                    directionalLight2.position.set(-1, -1, -1);
                    scene.add(directionalLight2);
                    
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
                    
                    // 모든 재질을 매트하게 처리
                    for (let materialName in materials.materials) {{
                        const material = materials.materials[materialName];
                        
                        // 반사도 제거 (매트 효과)
                        material.shininess = 0;
                        material.specular.setRGB(0, 0, 0);
                        
                        // 텍스처 적용 보장
                        if (material.map && !material.map.image) {{
                            const textureNames = Object.keys(textures);
                            if (textureNames.length > 0) {{
                                material.map = textures[textureNames[0]];
                            }}
                        }}
                        
                        // 추가 매트 설정
                        if (material.map) {{
                            material.map.minFilter = THREE.LinearFilter;
                            material.map.magFilter = THREE.LinearFilter;
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
                const container = document.getElementById('container');
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }}
            
            // 배경색 변경 함수
            function changeBackground(color) {{
                const colors = {{
                    'white': 0xffffff,
                    'gray': 0x808080,
                    'black': 0x000000
                }};
                
                const bodyColors = {{
                    'white': '#ffffff',
                    'gray': '#808080', 
                    'black': '#000000'
                }};
                
                // Three.js 렌더러 배경색 변경
                if (renderer) {{
                    renderer.setClearColor(colors[color], 1);
                }}
                
                // HTML body 배경색 변경
                document.body.style.background = bodyColors[color];
                
                // 로딩 텍스트 색상 변경
                const loadingEl = document.getElementById('loading');
                if (loadingEl) {{
                    loadingEl.style.color = color === 'black' ? 'white' : 'black';
                }}
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
