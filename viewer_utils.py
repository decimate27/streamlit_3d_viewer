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
                margin: 0 !important; 
                padding: 0 !important; 
                width: 100% !important; 
                height: 100% !important; 
                overflow: hidden !important; 
                background: {bg_color} !important; 
                border: none !important;
                outline: none !important;
            }}
            
            /* Streamlit 요소 완전 숨기기 */
            header[data-testid="stHeader"] {{ display: none !important; }}
            div[data-testid="stToolbar"] {{ display: none !important; }}
            div[data-testid="stDecoration"] {{ display: none !important; }}
            div[data-testid="stStatusWidget"] {{ display: none !important; }}
            div[data-testid="stBottom"] {{ display: none !important; }}
            footer {{ display: none !important; }}
            .stActionButton {{ display: none !important; }}
            .stDeployButton {{ display: none !important; }}
            
            /* GitHub fork banner 숨기기 */
            .github-corner {{ display: none !important; }}
            a[href*="github"] {{ display: none !important; }}
            
            /* Streamlit 로고 및 메뉴 숨기기 */
            [data-testid="stSidebar"] {{ display: none !important; }}
            .st-emotion-cache-1ww3bz2 {{ display: none !important; }}
            .st-emotion-cache-10trblm {{ display: none !important; }}
            
            /* 추가 스트림릿 하단 요소 숨기기 */
            [data-testid="stBottomBlockContainer"] {{ display: none !important; }}
            .streamlit-footer {{ display: none !important; }}
            .streamlit-badge {{ display: none !important; }}
            .st-emotion-cache-nahz7x {{ display: none !important; }}
            .st-emotion-cache-1y0tadg {{ display: none !important; }}
            
            /* 모든 footer 및 하단 링크 제거 */
            .footer, [class*="footer"], [class*="Footer"] {{ display: none !important; }}
            a[href*="streamlit"], a[href*="share.streamlit.io"] {{ display: none !important; }}
            img[alt*="Streamlit"], img[src*="streamlit"] {{ display: none !important; }}
            
            /* 하단 고정 요소들 제거 */
            [style*="position: fixed"][style*="bottom"], 
            [style*="position: absolute"][style*="bottom"] {{ display: none !important; }}
            
            /* 모든 여백 제거 */
            .main .block-container {{ 
                padding: 0 !important; 
                margin: 0 !important; 
                max-width: none !important;
                width: 100% !important;
            }}
            
            #container {{ 
                width: 100vw !important; 
                height: 100vh !important; 
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                z-index: 1000;
            }}
            canvas {{
                width: 100% !important;
                height: 100% !important;
                display: block !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
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
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 6px;
                pointer-events: auto;
            }}
            .bg-btn {{
                padding: 8px 12px;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                transition: all 0.3s ease;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                min-width: 60px;
                text-align: center;
            }}
            .bg-btn:hover {{
                transform: translateY(-1px);
                box-shadow: 0 3px 8px rgba(0,0,0,0.3);
                border-color: rgba(255,255,255,0.6);
            }}
            
            /* 모바일 최적화 */
            @media (max-width: 768px) {{
                .controls {{
                    top: 10px;
                    left: 10px;
                    gap: 4px;
                }}
                .bg-btn {{
                    padding: 6px 8px;
                    font-size: 10px;
                    min-width: 40px;
                    border-width: 1px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }}
                .bg-btn:hover {{
                    transform: none;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
                }}
            }}
            
            /* 아주 작은 화면 (스마트폰) */
            @media (max-width: 480px) {{
                .controls {{
                    top: 5px;
                    left: 5px;
                    gap: 3px;
                }}
                .bg-btn {{
                    padding: 4px 6px;
                    font-size: 9px;
                    min-width: 30px;
                    border-radius: 3px;
                }}
            }}
            .bg-white {{ 
                background: #ffffff; 
                color: #333; 
                border-color: #ccc;
            }}
            .bg-gray {{ 
                background: #808080; 
                color: white; 
                border-color: #666;
            }}
            .bg-black {{ 
                background: #000000; 
                color: white; 
                border-color: #333;
            }}
            
            /* 텍스트 표시 제어 */
            .btn-text-mobile {{
                display: none;
            }}
            .btn-text-full {{
                display: inline;
            }}
            
            /* 모바일에서 텍스트 변경 */
            @media (max-width: 768px) {{
                .btn-text-mobile {{
                    display: inline;
                }}
                .btn-text-full {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div class="loading" id="loading">모델 로딩 중...</div>
            
            <!-- 배경색 변경 컨트롤 -->
            <div class="controls">
                <button class="bg-btn bg-white" onclick="changeBackground('white')">
                    <span class="btn-text-full">⚪ 흰색</span>
                    <span class="btn-text-mobile">⚪</span>
                </button>
                <button class="bg-btn bg-gray" onclick="changeBackground('gray')">
                    <span class="btn-text-full">🔘 회색</span>
                    <span class="btn-text-mobile">🔘</span>
                </button>
                <button class="bg-btn bg-black" onclick="changeBackground('black')">
                    <span class="btn-text-full">⚫ 검은색</span>
                    <span class="btn-text-mobile">⚫</span>
                </button>
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
                    
                    // 모바일 감지
                    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
                    const isAndroid = /Android/i.test(navigator.userAgent);
                    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
                    
                    if (isMobile) {{
                        console.log('Mobile device detected:', isAndroid ? 'Android' : 'iOS');
                    }}
                    
                    // Scene 생성
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x{bg_color[1:]});
                    
                    // Camera 생성 - 제품 전시용 FOV (45도)
                    // FOV 45도: 왜곡 최소화, 전문적인 제품 사진 느낌
                    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 0, 5);
                    
                    // Renderer 생성
                    const container = document.getElementById('container');
                    renderer = new THREE.WebGLRenderer({{ 
                        antialias: true,
                        powerPreference: "high-performance", // 고성능 GPU 사용
                        preserveDrawingBuffer: true // 모바일 호환성
                    }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(window.devicePixelRatio);
                    renderer.setClearColor(0x{bg_color[1:]}, 1); // 초기 배경색 설정
                    
                    // 이방성 필터링 최대값 확인 (모바일은 제한)
                    const maxAnisotropy = isMobile ? 1 : renderer.capabilities.getMaxAnisotropy();
                    console.log('Anisotropy setting:', maxAnisotropy);
                    
                    // 모바일에서는 초기에 캔버스 숨기기
                    if (isMobile) {{
                        renderer.domElement.style.opacity = '0';
                        renderer.domElement.style.transition = 'opacity 0.3s';
                    }}
                    
                    container.appendChild(renderer.domElement);
                    
                    // Controls 생성 - 제품 전시용 설정
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.08; // 더 부드러운 움직임
                    controls.enableZoom = true;
                    controls.enablePan = true;
                    controls.enableRotate = true;
                    controls.rotateSpeed = 0.5; // 천천히 회전
                    controls.zoomSpeed = 0.8; // 부드러운 줌
                    
                    // 줌 제한 설정 (너무 가깝거나 멀어지지 않도록)
                    controls.minDistance = 2;
                    controls.maxDistance = 10;
                    
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
                    
                    // 모바일이 아닌 경우에만 즉시 애니메이션 시작
                    if (!isMobile) {{
                        animate();
                    }}
                    // 모바일은 loadModel 내부의 setTimeout 후에 animate 시작
                    
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
                    
                    // 모바일 감지 (loadModel 스코프용)
                    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
                    const isAndroid = /Android/i.test(navigator.userAgent);
                    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
                    
                    // 텍스처 로더
                    const textureLoader = new THREE.TextureLoader();
                    const textures = {{}};
                    
                    // 텍스처 로딩
                    {create_texture_loading_code(texture_base64)}
                    
                    console.log('Textures loaded:', Object.keys(textures));
                    console.log('Total textures:', Object.keys(textures).length);
                    
                    // 텍스처 디버깅 정보
                    for (let texName in textures) {{
                        const tex = textures[texName];
                        const hasImage = tex && tex.image ? 'Yes' : 'No';
                        console.log('  - ' + texName + ': Loaded (has image: ' + hasImage + ')');
                    }}
                    
                    // MTL 로더
                    console.log('Loading MTL...');
                    const mtlLoader = new THREE.MTLLoader();
                    
                    // MTLLoader에 텍스처 매니저 설정
                    mtlLoader.setMaterialOptions({{
                        ignoreZeroRGBs: true,
                        invertTrProperty: false
                    }});
                    
                    // MTL 파싱 전에 모든 텍스처가 로드되었는지 확인
                    console.log('Pre-check: Available textures before MTL parsing:');
                    for (let texName in textures) {{
                        console.log('  ✓ ' + texName);
                    }}
                    
                    // MTL 파싱
                    const materials = mtlLoader.parse(`{mtl_content}`, '');
                    
                    // MTL에서 텍스처 참조 추출
                    const mtlText = `{mtl_content}`;
                    const textureRefs = {{}};
                    const lines = mtlText.split('\\n');
                    let currentMaterial = null;
                    
                    for (let line of lines) {{
                        line = line.trim();
                        if (line.startsWith('newmtl ')) {{
                            currentMaterial = line.substring(7).trim();
                        }} else if (line.startsWith('map_Kd ') && currentMaterial) {{
                            const textureName = line.substring(7).trim();
                            textureRefs[currentMaterial] = textureName;
                            console.log('MTL mapping found: ' + currentMaterial + ' -> ' + textureName);
                        }}
                    }}
                    
                    materials.preload();
                    
                    // 모든 재질을 매트하게 처리
                    for (let materialName in materials.materials) {{
                        const material = materials.materials[materialName];
                        
                        // 반사도 제거 (매트 효과)
                        material.shininess = 0;
                        material.specular.setRGB(0, 0, 0);
                        
                        // 텍스처 적용 - MTL 파싱에서 찾은 매핑 사용
                        const textureFileName = textureRefs[materialName];
                        if (textureFileName) {{
                            console.log('Applying texture to ' + materialName + ': ' + textureFileName);
                            
                            if (textures[textureFileName]) {{
                                material.map = textures[textureFileName];
                                material.map.sourceFile = textureFileName; // sourceFile 설정
                                console.log('  ✅ Texture applied: ' + textureFileName);
                            }} else {{
                                console.warn('  ⚠️ Texture not found: ' + textureFileName);
                                console.log('  Available textures:', Object.keys(textures));
                            }}
                        }} else if (material.map) {{
                            // MTL에서 매핑을 찾지 못했지만 map이 있는 경우
                            console.warn('Material ' + materialName + ' has map but no texture reference found');
                        }}
                        
                        // 텍스처가 성공적으로 적용된 경우 필터 설정
                        if (material.map && material.map.image) {{
                            if (isMobile) {{
                                // 모바일: 간단한 설정으로 UV 시음 최소화
                                material.map.minFilter = THREE.LinearFilter;
                                material.map.magFilter = THREE.LinearFilter;
                                material.map.generateMipmaps = false;
                                material.map.anisotropy = 1;
                            }} else {{
                                // 데스크톱: 고품질 설정
                                material.map.anisotropy = renderer.capabilities.getMaxAnisotropy();
                                material.map.minFilter = THREE.LinearMipmapLinearFilter;
                                material.map.magFilter = THREE.LinearFilter;
                                material.map.generateMipmaps = true;
                            }}
                            
                            // 공통: 텍스처 래핑
                            material.map.wrapS = THREE.ClampToEdgeWrapping;
                            material.map.wrapT = THREE.ClampToEdgeWrapping;
                            material.map.needsUpdate = true;
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
                    
                    // 최종 재질 확인 (디버깅)
                    console.log('=== Final Material Check ===');
                    object.traverse((child) => {{
                        if (child.isMesh && child.material) {{
                            const mat = child.material;
                            if (mat.name) {{
                                console.log('Mesh uses material: ' + mat.name);
                                if (mat.map) {{
                                    const sourceFile = mat.map.sourceFile || 'Not set';
                                    const hasImage = mat.map.image ? 'Yes' : 'No';
                                    console.log('  -> Texture file: ' + sourceFile);
                                    console.log('  -> Has image data: ' + hasImage);
                                }} else {{
                                    console.log('  -> No texture');
                                }}
                            }}
                        }}
                    }});
                    console.log('=========================');
                    
                    // 카메라 위치 조정 - FOV 45도에 맞춰 거리 증가
                    // FOV가 작아지면 같은 크기로 보이려면 더 멀리서 봐야 함
                    const distance = maxDim * scale * 3; // 2 -> 3으로 증가
                    camera.position.set(distance, distance * 0.7, distance);
                    camera.lookAt(0, 0, 0);
                    
                    // 카메라 설정 로그
                    console.log('Camera FOV: 45° (Product display mode)');
                    console.log('Camera distance: ' + distance.toFixed(2));
                    
                    console.log('Model loaded successfully');
                    
                    // 모바일 GPU 워밍업 및 지연 표시
                    if (isMobile) {{
                        console.log('Mobile optimization: GPU warmup starting...');
                        
                        // GPU 워밍업: 보이지 않는 상태에서 여러 프레임 렌더링
                        const warmupFrames = isAndroid ? 5 : 3;
                        for (let i = 0; i < warmupFrames; i++) {{
                            renderer.render(scene, camera);
                        }}
                        console.log('GPU warmup complete (' + warmupFrames + ' frames)');
                        
                        // 지연 시간 설정 (Android는 더 길게)
                        const delay = isAndroid ? 500 : 300;
                        
                        // 로딩 메시지 업데이트
                        const loadingEl = document.getElementById('loading');
                        if (loadingEl) {{
                            loadingEl.innerHTML = '렌더링 최적화 중...';
                        }}
                        
                        // 지연 후 표시
                        setTimeout(() => {{
                            // 로딩 숨기기
                            if (loadingEl) {{
                                loadingEl.style.display = 'none';
                            }}
                            
                            // 캔버스 페이드인
                            renderer.domElement.style.opacity = '1';
                            
                            // 최종 렌더링
                            renderer.render(scene, camera);
                            
                            // 모바일에서 애니메이션 시작
                            animate();
                            
                            console.log('Mobile optimization complete, displaying model');
                        }}, delay);
                    }} else {{
                        // 데스크톱: 즉시 표시
                        document.getElementById('loading').style.display = 'none';
                    }}
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
                console.log('배경색 변경 시작:', color);
                
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
                
                // Three.js Scene 배경색 변경
                if (scene) {{
                    scene.background = new THREE.Color(colors[color]);
                    console.log('Scene 배경색 변경됨:', color);
                }}
                
                // Three.js 렌더러 배경색 변경
                if (renderer) {{
                    renderer.setClearColor(colors[color], 1);
                    console.log('Renderer 배경색 변경됨:', color);
                }}
                
                // HTML body 배경색 변경
                document.body.style.background = bodyColors[color];
                document.body.style.backgroundColor = bodyColors[color];
                
                // 컨테이너 배경색도 변경
                const container = document.getElementById('container');
                if (container) {{
                    container.style.background = bodyColors[color];
                    container.style.backgroundColor = bodyColors[color];
                }}
                
                // 로딩 텍스트 색상 변경
                const loadingEl = document.getElementById('loading');
                if (loadingEl) {{
                    loadingEl.style.color = color === 'black' ? 'white' : 'black';
                }}
                
                // 강제 렌더링
                if (renderer && scene && camera) {{
                    renderer.render(scene, camera);
                }}
                
                console.log('배경색 변경 완료:', color);
            }}
            
            // 배경색 버튼 강제 생성
            function createBackgroundButtons() {{
                // 기존 컨트롤 제거
                const existingControls = document.querySelector('.controls');
                if (existingControls) {{
                    existingControls.remove();
                }}
                
                // 새 컨트롤 생성
                const controlsDiv = document.createElement('div');
                controlsDiv.className = 'controls';
                controlsDiv.innerHTML = `
                    <button class="bg-btn bg-white" onclick="changeBackground('white')">
                        <span class="btn-text-full">⚪ 흰색</span>
                        <span class="btn-text-mobile">⚪</span>
                    </button>
                    <button class="bg-btn bg-gray" onclick="changeBackground('gray')">
                        <span class="btn-text-full">🔘 회색</span>
                        <span class="btn-text-mobile">🔘</span>
                    </button>
                    <button class="bg-btn bg-black" onclick="changeBackground('black')">
                        <span class="btn-text-full">⚫ 검은색</span>
                        <span class="btn-text-mobile">⚫</span>
                    </button>
                `;
                
                document.body.appendChild(controlsDiv);
                console.log('배경색 버튼 강제 생성됨');
            }}
            
            // 페이지 로드 후 버튼 확인 및 생성
            window.addEventListener('load', function() {{
                console.log('페이지 로드 완료');
                
                // Streamlit 요소 강제 제거
                function hideStreamlitElements() {{
                    const elementsToHide = [
                        'header[data-testid="stHeader"]',
                        'div[data-testid="stToolbar"]', 
                        'div[data-testid="stDecoration"]',
                        'div[data-testid="stStatusWidget"]',
                        'div[data-testid="stBottom"]',
                        'div[data-testid="stBottomBlockContainer"]',
                        'footer',
                        '.footer',
                        '[class*="footer"]',
                        '[class*="Footer"]',
                        '.stActionButton',
                        '.stDeployButton',
                        '.github-corner',
                        'a[href*="github"]',
                        'a[href*="streamlit"]',
                        'a[href*="share.streamlit.io"]',
                        '[data-testid="stSidebar"]',
                        '.streamlit-footer',
                        '.streamlit-badge',
                        '.st-emotion-cache-1ww3bz2',
                        '.st-emotion-cache-10trblm',
                        '.st-emotion-cache-nahz7x',
                        '.st-emotion-cache-1y0tadg',
                        'img[alt*="Streamlit"]',
                        'img[src*="streamlit"]',
                        '[style*="position: fixed"][style*="bottom"]',
                        '[style*="position: absolute"][style*="bottom"]'
                    ];
                    
                    elementsToHide.forEach(selector => {{
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {{
                            if (el) {{
                                el.style.display = 'none';
                                el.style.visibility = 'hidden';
                                el.remove();
                            }}
                        }});
                    }});
                    
                    // 부모 window에서도 제거 시도
                    if (window.parent && window.parent !== window) {{
                        try {{
                            const parentDoc = window.parent.document;
                            elementsToHide.forEach(selector => {{
                                const elements = parentDoc.querySelectorAll(selector);
                                elements.forEach(el => {{
                                    if (el) {{
                                        el.style.display = 'none';
                                        el.style.visibility = 'hidden';
                                    }}
                                }});
                            }});
                        }} catch (e) {{
                            // Cross-origin 에러 무시
                        }}
                    }}
                }}
                
                // 즉시 실행 및 주기적 실행
                hideStreamlitElements();
                setInterval(hideStreamlitElements, 500); // 더 빈번하게 실행
                
                // 추가적인 MutationObserver로 DOM 변화 감지
                const observer = new MutationObserver(function(mutations) {{
                    hideStreamlitElements();
                }});
                observer.observe(document.body, {{ 
                    childList: true, 
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['style', 'class']
                }});
                
                setTimeout(() => {{
                    const controls = document.querySelector('.controls');
                    const buttons = document.querySelectorAll('.bg-btn');
                    console.log('컨트롤 요소:', controls);
                    console.log('버튼 개수:', buttons.length);
                    
                    if (!controls || buttons.length === 0) {{
                        console.log('버튼이 없음 - 강제 생성');
                        createBackgroundButtons();
                    }} else {{
                        console.log('버튼이 정상적으로 존재함');
                    }}
                }}, 1000);
            }});
            
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
                const tex_{safe_name} = textureLoader.load(img_{safe_name}.src);
                
                // 모바일 최적화 설정
                if (typeof isMobile !== 'undefined' && isMobile) {{
                    // 모바일: 밉맵 OFF, 단순 필터
                    tex_{safe_name}.generateMipmaps = false;
                    tex_{safe_name}.minFilter = THREE.LinearFilter;
                    tex_{safe_name}.magFilter = THREE.LinearFilter;
                    tex_{safe_name}.anisotropy = 1;
                }} else {{
                    // 데스크톱: 고품질 설정
                    tex_{safe_name}.anisotropy = 16;
                    tex_{safe_name}.generateMipmaps = true;
                    tex_{safe_name}.minFilter = THREE.LinearMipmapLinearFilter;
                    tex_{safe_name}.magFilter = THREE.LinearFilter;
                }}
                
                // 공통 설정
                tex_{safe_name}.wrapS = THREE.ClampToEdgeWrapping;
                tex_{safe_name}.wrapT = THREE.ClampToEdgeWrapping;
                tex_{safe_name}.needsUpdate = true;
                
                textures['{name}'] = tex_{safe_name};
        """)
    
    return '\n'.join(code_lines)
