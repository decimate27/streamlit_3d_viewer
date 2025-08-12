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
            
            /* 로딩 스피너 스타일 */
            .loading-container {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                z-index: 1000;
                opacity: 1;
                transition: opacity 0.5s ease-out;
            }}
            
            .loading-container.fade-out {{
                opacity: 0;
            }}
            
            /* 에어바이블 로고 컨테이너 */
            .logo-container {{
                width: 120px;
                height: 120px;
                margin: 0 auto 30px;
                position: relative;
            }}
            
            .airbible-logo {{
                width: 100%;
                height: 100%;
                object-fit: contain;
                animation: heartbeat 1.5s ease-in-out infinite;
            }}
            
            /* 심장박동 애니메이션 */
            @keyframes heartbeat {{
                0% {{
                    transform: scale(1);
                }}
                14% {{
                    transform: scale(1.15);
                }}
                28% {{
                    transform: scale(1);
                }}
                42% {{
                    transform: scale(1.12);
                }}
                70% {{
                    transform: scale(1);
                }}
            }}
            
            .loading-text {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: 500;
                color: #333;
                margin-top: 20px;
                letter-spacing: 0.5px;
            }}
            
            .loading-text-dark {{
                color: #fff;
            }}
            
            /* 로딩 점 애니메이션 */
            .loading-dots {{
                display: inline-block;
                width: 60px;
                text-align: left;
            }}
            
            .loading-dots::after {{
                content: '';
                animation: dots 2s steps(5, end) infinite;
            }}
            
            @keyframes dots {{
                0%, 20% {{
                    content: '.';
                }}
                40% {{
                    content: '..';
                }}
                60% {{
                    content: '...';
                }}
                80% {{
                    content: '....';
                }}
                100% {{
                    content: '.....';
                }}
            }}
            
            /* 모바일 반응형 */
            @media (max-width: 768px) {{
                .logo-container {{
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 20px;
                }}
                
                .loading-text {{
                    font-size: 16px;
                }}
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div class="loading-container" id="loading">
                <div class="logo-container">
                    <!-- 에어바이블 로고 SVG (위치 아이콘 스타일) -->
                    <svg class="airbible-logo" id="airbibleLogo" viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                        <!-- 핀 모양 본체 -->
                        <path d="M100 10 C50 10, 10 50, 10 100 C10 130, 30 160, 100 230 C170 160, 190 130, 190 100 C190 50, 150 10, 100 10 Z" 
                              fill="#000000" id="logoBody"/>
                        <!-- 내부 원 -->
                        <circle cx="100" cy="85" r="35" fill="#ffffff" id="logoInner"/>
                    </svg>
                </div>
                <div class="loading-text" id="loadingText">
                    Loading<span class="loading-dots"></span>
                </div>
            </div>
            
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
            
            // 로딩 상태 업데이트 함수
            function updateLoadingProgress(message) {{
                // 로고 색상 업데이트
                const bgColor = '{bg_color}';
                const isDark = bgColor === 'black' || bgColor === '#000000';
                const logoBody = document.getElementById('logoBody');
                const logoInner = document.getElementById('logoInner');
                const textEl = document.getElementById('loadingText');
                
                if (logoBody) {{
                    // 배경색에 따라 로고 색상 변경
                    logoBody.setAttribute('fill', isDark ? '#ffffff' : '#000000');
                }}
                
                if (logoInner) {{
                    logoInner.setAttribute('fill', isDark ? '#000000' : '#ffffff');
                }}
                
                if (textEl) {{
                    textEl.className = isDark ? 'loading-text loading-text-dark' : 'loading-text';
                }}
            }}
            
            // 로딩 완료 시 페이드 아웃
            function hideLoadingSpinner() {{
                const loadingEl = document.getElementById('loading');
                if (loadingEl) {{
                    loadingEl.classList.add('fade-out');
                    setTimeout(() => {{
                        loadingEl.style.display = 'none';
                    }}, 500);
                }}
            }}
            
            function init() {{
                try {{
                    console.log('Three.js version:', THREE.REVISION);
                    updateLoadingProgress('초기화 중...');
                    
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
                    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 0, 5);
                    
                    // Renderer 생성
                    const container = document.getElementById('container');
                    renderer = new THREE.WebGLRenderer({{ 
                        antialias: true,
                        powerPreference: "high-performance",
                        preserveDrawingBuffer: true,
                        alpha: false,
                        premultipliedAlpha: false,
                        stencil: false,
                        depth: true
                    }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                    renderer.setClearColor(0x{bg_color[1:]}, 1);
                    
                    // 색상 보정 완전 비활성화
                    renderer.outputEncoding = THREE.LinearEncoding;
                    renderer.toneMapping = THREE.NoToneMapping;
                    renderer.shadowMap.enabled = false;
                    renderer.gammaFactor = 1.0;
                    renderer.gammaInput = false;
                    renderer.gammaOutput = false;
                    renderer.physicallyCorrectLights = false; // 물리 기반 조명 비활성화
                    
                    // 모바일에서는 초기에 캔버스 숨기기
                    if (isMobile) {{
                        renderer.domElement.style.opacity = '0';
                        renderer.domElement.style.transition = 'opacity 0.3s';
                    }}
                    
                    container.appendChild(renderer.domElement);
                    
                    // Controls 생성
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.08;
                    controls.enableZoom = true;
                    controls.enablePan = true;
                    controls.enableRotate = true;
                    controls.rotateSpeed = 0.5;
                    controls.zoomSpeed = 0.8;
                    controls.minDistance = 2;
                    controls.maxDistance = 10;
                    
                    // 조명 설정 - 색상 유지하면서 입체감 추가
                    // HemisphereLight로 자연스러운 상하 명암
                    const hemisphereLight = new THREE.HemisphereLight(
                        0xffffff, // 하늘색 (위)
                        0xf0f0f0, // 지면색 (아래) - 약간 어둡게
                        0.75
                    );
                    scene.add(hemisphereLight);
                    
                    // 주 조명 (Key Light)
                    const keyLight = new THREE.DirectionalLight(0xffffff, 0.4);
                    keyLight.position.set(5, 5, 5);
                    keyLight.castShadow = false;
                    scene.add(keyLight);
                    
                    // 보조 조명 (Fill Light) - 그림자 부분을 부드럽게
                    const fillLight = new THREE.DirectionalLight(0xffffff, 0.25);
                    fillLight.position.set(-3, 3, -3);
                    scene.add(fillLight);
                    
                    // 림 라이트 (Rim Light) - 윤곽선 강조
                    const rimLight = new THREE.DirectionalLight(0xffffff, 0.2);
                    rimLight.position.set(0, 0, -5);
                    scene.add(rimLight);
                    
                    // 전체적인 밝기 보정을 위한 약한 주변광
                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.25);
                    scene.add(ambientLight);
                    
                    console.log('Scene setup complete');
                    
                    // 모델 로드
                    loadModel();
                    
                    // 모바일이 아닌 경우에만 즉시 애니메이션 시작
                    if (!isMobile) {{
                        animate();
                    }}
                    
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
                    
                    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
                    const isAndroid = /Android/i.test(navigator.userAgent);
                    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
                    
                    // 텍스처 로더
                    const textureLoader = new THREE.TextureLoader();
                    const textures = {{}};
                    
                    // 텍스처 로딩
                    {create_texture_loading_code(texture_base64)}
                    
                    console.log('Textures loaded:', Object.keys(textures));
                    
                    // MTL 로더
                    console.log('Loading MTL...');
                    const mtlLoader = new THREE.MTLLoader();
                    mtlLoader.setMaterialOptions({{
                        ignoreZeroRGBs: true,
                        invertTrProperty: false
                    }});
                    
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
                            console.log('MTL mapping: ' + currentMaterial + ' -> ' + textureName);
                        }}
                    }}
                    
                    materials.preload();
                    
                    // 모든 재질 처리
                    for (let materialName in materials.materials) {{
                        const material = materials.materials[materialName];
                        
                        // 텍스처 참조 가져오기
                        const textureFileName = textureRefs[materialName];
                        
                        // MeshLambertMaterial로 변환 - 색상 유지하면서 입체감 추가
                        if (textureFileName && textures[textureFileName]) {{
                            // Lambert Material 생성 (Phong보다 부드럽고 색상 왜곡 적음)
                            const lambertMaterial = new THREE.MeshLambertMaterial({{
                                map: textures[textureFileName],
                                side: THREE.FrontSide,
                                transparent: false,
                                alphaTest: 0,
                                depthWrite: true,
                                depthTest: true,
                                color: new THREE.Color(1, 1, 1), // 흰색으로 텍스처 색상 유지
                                emissive: new THREE.Color(0.05, 0.05, 0.05), // 매우 약한 자체 발광
                                emissiveIntensity: 0.05, // 최소한의 발광으로 어두운 부분만 보완
                                reflectivity: 0,
                                refractionRatio: 0.98,
                                combine: THREE.MultiplyOperation
                            }});
                            
                            // 텍스처 설정
                            lambertMaterial.map.encoding = THREE.LinearEncoding;
                            lambertMaterial.map.minFilter = THREE.LinearFilter;
                            lambertMaterial.map.magFilter = THREE.LinearFilter;
                            lambertMaterial.map.generateMipmaps = false;
                            lambertMaterial.map.anisotropy = 1;
                            lambertMaterial.map.wrapS = THREE.ClampToEdgeWrapping;
                            lambertMaterial.map.wrapT = THREE.ClampToEdgeWrapping;
                            lambertMaterial.map.needsUpdate = true;
                            
                            // 기존 material을 lambertMaterial로 교체
                            materials.materials[materialName] = lambertMaterial;
                            
                            console.log('✅ LambertMaterial applied: ' + textureFileName);
                        }} else {{
                            // 텍스처가 없는 경우 기존 설정 유지
                            material.side = THREE.FrontSide;
                            material.transparent = false;
                            material.alphaTest = 0;
                            material.depthWrite = true;
                            material.depthTest = true;
                            material.shininess = 0;
                            material.specular.setRGB(0, 0, 0);
                        }}
                    }}
                    
                    console.log('Materials loaded');
                    
                    // OBJ 로더
                    console.log('Loading OBJ...');
                    const objLoader = new THREE.OBJLoader();
                    objLoader.setMaterials(materials);
                    
                    const object = objLoader.parse(`{obj_content}`);
                    
                    // UV 좌표 조정 - 경계에서 약간 안쪽으로
                    object.traverse((child) => {{
                        if (child.isMesh && child.geometry) {{
                            const geometry = child.geometry;
                            if (geometry.attributes.uv) {{
                                const uvArray = geometry.attributes.uv.array;
                                const epsilon = 0.001; // UV 경계에서 0.1% 안쪽으로
                                
                                for (let i = 0; i < uvArray.length; i++) {{
                                    // UV 좌표를 epsilon만큼 안쪽으로 조정
                                    if (uvArray[i] < epsilon) {{
                                        uvArray[i] = epsilon;
                                    }} else if (uvArray[i] > 1 - epsilon) {{
                                        uvArray[i] = 1 - epsilon;
                                    }}
                                }}
                                
                                geometry.attributes.uv.needsUpdate = true;
                            }}
                        }}
                    }});
                    
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
                    const distance = maxDim * scale * 3;
                    camera.position.set(distance, distance * 0.7, distance);
                    camera.lookAt(0, 0, 0);
                    
                    console.log('Model loaded successfully');
                    
                    // 모바일 GPU 워밍업 및 지연 표시
                    if (isMobile) {{
                        console.log('Mobile optimization: GPU warmup starting...');
                        
                        const warmupFrames = isAndroid ? 5 : 3;
                        for (let i = 0; i < warmupFrames; i++) {{
                            renderer.render(scene, camera);
                        }}
                        
                        const delay = isAndroid ? 500 : 300;
                        
                        setTimeout(() => {{
                            hideLoadingSpinner();
                            renderer.domElement.style.opacity = '1';
                            renderer.render(scene, camera);
                            animate();
                            console.log('Mobile optimization complete');
                        }}, delay);
                    }} else {{
                        setTimeout(() => {{
                            hideLoadingSpinner();
                        }}, 500);
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
                
                if (scene) {{
                    scene.background = new THREE.Color(colors[color]);
                }}
                
                if (renderer) {{
                    renderer.setClearColor(colors[color], 1);
                }}
                
                document.body.style.background = bodyColors[color];
                document.body.style.backgroundColor = bodyColors[color];
                
                const container = document.getElementById('container');
                if (container) {{
                    container.style.background = bodyColors[color];
                    container.style.backgroundColor = bodyColors[color];
                }}
                
                // 로고 색상도 변경
                const isDark = color === 'black';
                const logoBody = document.getElementById('logoBody');
                const logoInner = document.getElementById('logoInner');
                const textEl = document.getElementById('loadingText');
                
                if (logoBody) {{
                    logoBody.setAttribute('fill', isDark ? '#ffffff' : '#000000');
                }}
                
                if (logoInner) {{
                    logoInner.setAttribute('fill', isDark ? '#000000' : '#ffffff');
                }}
                
                if (textEl) {{
                    textEl.className = isDark ? 'loading-text loading-text-dark' : 'loading-text';
                }}
                
                if (renderer && scene && camera) {{
                    renderer.render(scene, camera);
                }}
                
                console.log('배경색 변경 완료:', color);
            }}
            
            // 배경색 버튼 강제 생성
            function createBackgroundButtons() {{
                const existingControls = document.querySelector('.controls');
                if (existingControls) {{
                    existingControls.remove();
                }}
                
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
                setInterval(hideStreamlitElements, 500);
                
                // MutationObserver로 DOM 변화 감지
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
                // {name} 텍스처 로딩
                const img_{safe_name} = new Image();
                img_{safe_name}.src = 'data:{mime_type};base64,{data}';
                const tex_{safe_name} = textureLoader.load(img_{safe_name}.src);
                
                // 원본 색상 100% 유지
                tex_{safe_name}.encoding = THREE.LinearEncoding;
                tex_{safe_name}.flipY = true;
                
                // UV Seam 방지 + 색상 정확도
                tex_{safe_name}.generateMipmaps = false;
                tex_{safe_name}.minFilter = THREE.LinearFilter;
                tex_{safe_name}.magFilter = THREE.LinearFilter;
                tex_{safe_name}.anisotropy = 1;
                tex_{safe_name}.wrapS = THREE.ClampToEdgeWrapping;
                tex_{safe_name}.wrapT = THREE.ClampToEdgeWrapping;
                tex_{safe_name}.format = THREE.RGBFormat; // RGB 포맷 (알파 채널 제외)
                tex_{safe_name}.type = THREE.UnsignedByteType;
                tex_{safe_name}.needsUpdate = true;
                
                textures['{name}'] = tex_{safe_name};
                console.log('Texture loaded with original colors: {name}');
        """)
    
    return '\n'.join(code_lines)
