import base64
import json
from pathlib import Path

def create_3d_viewer_html(obj_content, mtl_content, texture_data, background_color="white", model_token=None, annotations=None):
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
            
            /* 상단 안내 텍스트 스타일 */
            .top-notice {{
                position: fixed !important;
                top: 5px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                background: rgba(255, 255, 255, 0.95) !important;
                color: #333 !important;
                padding: 5px 15px !important;
                border-radius: 20px !important;
                font-size: 12px !important;
                font-weight: normal !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
                z-index: 99998 !important;
                white-space: nowrap !important;
            }}
            
            /* 수정점 표시 버튼 스타일 */
            .annotation-btn {{
                position: fixed !important;
                top: 20px !important;
                right: 20px !important;
                padding: 10px 15px !important;
                background: #ff4444 !important;
                color: white !important;
                border: none !important;
                border-radius: 5px !important;
                cursor: pointer !important;
                font-size: 14px !important;
                font-weight: bold !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
                z-index: 99999 !important;
                display: block !important;
                visibility: visible !important;
            }}
            
            .annotation-btn.active {{
                background: #cc0000;
            }}
            
            .annotation-btn:hover {{
                background: #ff6666 !important;
            }}
            
            /* 모바일 반응형 수정점 버튼 */
            @media (max-width: 768px) {{
                .annotation-btn {{
                    top: 10px !important;
                    right: 10px !important;
                    padding: 8px 10px !important;
                    font-size: 12px !important;
                }}
            }}
            
            @media (max-width: 480px) {{
                .annotation-btn {{
                    top: 5px !important;
                    right: 5px !important;
                    padding: 6px 8px !important;
                    font-size: 11px !important;
                }}
            }}
            
            /* 제출완료 버튼 스타일 */
            .db-save-btn {{
                position: fixed !important;
                top: 70px !important;
                right: 20px !important;
                padding: 10px 15px !important;
                background: #2196F3 !important;
                color: white !important;
                border: none !important;
                border-radius: 5px !important;
                cursor: pointer !important;
                font-size: 14px !important;
                font-weight: bold !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
                z-index: 99999 !important;
                display: block !important;
                visibility: visible !important;
            }}
            
            .db-save-btn:hover {{
                background: #1976D2 !important;
            }}
            
            .db-save-btn:disabled {{
                background: #ccc !important;
                cursor: not-allowed !important;
            }}
            
            /* 수정점 입력 모달 */
            .annotation-modal {{
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                z-index: 10001;
                min-width: 300px;
            }}
            
            .annotation-modal.show {{
                display: block;
            }}
            
            .modal-overlay {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 10000;
            }}
            
            .modal-overlay.show {{
                display: block;
            }}
            
            .annotation-input {{
                width: 100%;
                padding: 8px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }}
            
            .modal-buttons {{
                display: flex;
                justify-content: space-between;
                margin-top: 15px;
            }}
            
            .modal-btn {{
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            
            .modal-btn.confirm {{
                background: #4CAF50;
                color: white;
            }}
            
            .modal-btn.cancel {{
                background: #f44336;
                color: white;
            }}
            
            /* 수정점 정보 팝업 */
            .annotation-popup {{
                display: none;
                position: fixed;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.3);
                z-index: 10002;
                min-width: 200px;
                max-width: 300px;
            }}
            
            .annotation-popup.show {{
                display: block;
            }}
            
            .popup-text {{
                margin-bottom: 10px;
                font-size: 14px;
                color: #333;
            }}
            
            .popup-buttons {{
                display: flex;
                gap: 10px;
            }}
            
            .popup-btn {{
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }}
            
            .popup-btn.complete {{
                background: #2196F3;
                color: white;
            }}
            
            .popup-btn.delete {{
                background: #f44336;
                color: white;
            }}
            
            /* 펄스 애니메이션 */
            @keyframes pulse {{
                0% {{
                    box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7);
                }}
                70% {{
                    box-shadow: 0 0 0 10px rgba(255, 68, 68, 0);
                }}
                100% {{
                    box-shadow: 0 0 0 0 rgba(255, 68, 68, 0);
                }}
            }}
            
            /* 모바일 최적화 */
            @media (max-width: 768px) {{
                .annotation-btn, .db-save-btn {{
                    font-size: 12px !important;
                    padding: 8px 12px !important;
                }}
                
                .top-notice {{
                    font-size: 11px !important;
                    padding: 4px 10px !important;
                }}
                
                .annotation-modal {{
                    width: 90% !important;
                    max-width: 350px !important;
                }}
                
                .annotation-popup {{
                    max-width: 250px !important;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- 상단 안내 텍스트 -->
        <div class="top-notice">
            📝 수정점 추가/수정/삭제 후 반드시 <span style="color: red; font-weight: bold;">제출완료</span> 버튼을 눌러 DB에 저장하세요!
        </div>
        
        <!-- 수정점 표시 버튼을 최상단에 배치 -->
        <button class="annotation-btn" id="annotationBtn" onclick="toggleAnnotationMode()">
            수정점표시
        </button>
        
        <!-- 제출완료 버튼 -->
        <button class="db-save-btn" id="dbSaveBtn" onclick="saveToDatabase()">
            제출완료
        </button>
        
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
            
            <!-- 수정점 입력 모달 -->
            <div class="modal-overlay" id="modalOverlay"></div>
            <div class="annotation-modal" id="annotationModal">
                <h3 style="margin-top: 0;">수정사항 입력</h3>
                <textarea class="annotation-input" id="annotationInput" rows="3" placeholder="수정할 사항을 입력하세요..."></textarea>
                <div class="modal-buttons">
                    <button class="modal-btn cancel" onclick="closeAnnotationModal()">취소</button>
                    <button class="modal-btn confirm" onclick="confirmAnnotation()">확인</button>
                </div>
            </div>
            
            <!-- 수정점 정보 팝업 -->
            <div class="annotation-popup" id="annotationPopup">
                <div class="popup-text" id="popupText"></div>
                <div class="popup-buttons" id="popupButtons"></div>
            </div>
        </div>
        
        <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/loaders/MTLLoader.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <script>
            let scene, camera, renderer, controls;
            let model;
            let raycaster, mouse;
            let isAnnotationMode = false;
            let annotations = [];
            let currentAnnotation = null;
            let annotationIdCounter = 0;
            const modelToken = '{model_token if model_token else ""}';
            
            // 초기 annotations 데이터 로드
            const initialAnnotations = {json.dumps(annotations if annotations else [])};
            
            // Raycaster와 마우스 초기화
            function initInteraction() {{
                raycaster = new THREE.Raycaster();
                mouse = new THREE.Vector2();
                
                // 마우스 이벤트
                renderer.domElement.addEventListener('click', onMouseClick, false);
                renderer.domElement.addEventListener('mousemove', onMouseMove, false);
                
                // 터치 이벤트 (모바일)
                renderer.domElement.addEventListener('touchstart', onTouchStart, false);
                renderer.domElement.addEventListener('touchend', function(e) {{ e.preventDefault(); }}, false);
                
                // 기존 annotations 로드
                loadExistingAnnotations();
            }}
            
            // 기존 수정점 로드
            function loadExistingAnnotations() {{
                // 서버에서 전달된 annotations 로드
                if (initialAnnotations && initialAnnotations.length > 0) {{
                    initialAnnotations.forEach(ann => {{
                        // 크기를 70%로 줄임 (0.05 -> 0.035)
                        const geometry = new THREE.SphereGeometry(0.035, 16, 16);
                        const material = new THREE.MeshBasicMaterial({{ 
                            color: ann.completed ? 0x0000ff : 0xff0000 
                        }});
                        const mesh = new THREE.Mesh(geometry, material);
                        mesh.position.set(ann.position.x, ann.position.y, ann.position.z);
                        
                        scene.add(mesh);
                        
                        annotations.push({{
                            id: ann.id,
                            mesh: mesh,
                            point: new THREE.Vector3(ann.position.x, ann.position.y, ann.position.z),
                            text: ann.text,
                            completed: ann.completed,
                            saved: true  // DB에 저장된 항목 표시
                        }});
                    }});
                }}
                
                // 제출완료 버튼 초기 상태 설정
                updateDbSaveButton();
            }}
            
            // 마우스/터치 클릭 처리 통합
            function handleInteraction(clientX, clientY, event) {{
                if (!model) return;
                
                // 좌표 계산
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;
                
                raycaster.setFromCamera(mouse, camera);
                
                // 수정점 클릭 확인
                const annotationMeshes = annotations.map(a => a.mesh);
                const annotationIntersects = raycaster.intersectObjects(annotationMeshes);
                
                if (annotationIntersects.length > 0) {{
                    const clickedMesh = annotationIntersects[0].object;
                    const annotation = annotations.find(a => a.mesh === clickedMesh);
                    if (annotation) {{
                        showAnnotationPopup(annotation, event);
                        return;
                    }}
                }}
                
                // 수정점 표시 모드일 때만 새 수정점 추가
                if (isAnnotationMode) {{
                    const intersects = raycaster.intersectObject(model, true);
                    
                    if (intersects.length > 0) {{
                        const point = intersects[0].point;
                        openAnnotationModal(point);
                    }}
                }}
            }}
            
            // 마우스 클릭 처리
            function onMouseClick(event) {{
                event.preventDefault();
                handleInteraction(event.clientX, event.clientY, event);
            }}
            
            // 터치 이벤트 처리 (모바일)
            function onTouchStart(event) {{
                event.preventDefault();
                if (event.touches.length === 1) {{
                    // 단일 터치만 처리
                    const touch = event.touches[0];
                    handleInteraction(touch.clientX, touch.clientY, touch);
                }}
            }}
            
            // 마우스 이동 처리 (커서 변경)
            function onMouseMove(event) {{
                if (!model) return;
                
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                
                raycaster.setFromCamera(mouse, camera);
                
                // 수정점에 호버 시 커서 변경
                const annotationMeshes = annotations.map(a => a.mesh);
                const intersects = raycaster.intersectObjects(annotationMeshes);
                
                if (intersects.length > 0) {{
                    renderer.domElement.style.cursor = 'pointer';
                }} else if (isAnnotationMode) {{
                    const modelIntersects = raycaster.intersectObject(model, true);
                    renderer.domElement.style.cursor = modelIntersects.length > 0 ? 'crosshair' : 'default';
                }} else {{
                    renderer.domElement.style.cursor = 'default';
                }}
            }}
            
            // 수정점 표시 모드 토글
            function toggleAnnotationMode() {{
                isAnnotationMode = !isAnnotationMode;
                const btn = document.getElementById('annotationBtn');
                if (isAnnotationMode) {{
                    btn.classList.add('active');
                    btn.textContent = '수정점표시 ON';
                }} else {{
                    btn.classList.remove('active');
                    btn.textContent = '수정점표시';
                }}
            }}
            
            // 수정점 입력 모달 열기
            function openAnnotationModal(point) {{
                currentAnnotation = {{ point: point.clone() }};
                document.getElementById('annotationInput').value = '';
                document.getElementById('annotationModal').classList.add('show');
                document.getElementById('modalOverlay').classList.add('show');
                document.getElementById('annotationInput').focus();
            }}
            
            // 수정점 입력 모달 닫기
            function closeAnnotationModal() {{
                document.getElementById('annotationModal').classList.remove('show');
                document.getElementById('modalOverlay').classList.remove('show');
                currentAnnotation = null;
            }}
            
            // 수정점 확인
            function confirmAnnotation() {{
                const text = document.getElementById('annotationInput').value.trim();
                if (text && currentAnnotation) {{
                    // 서버에 저장
                    saveAnnotationToServer(currentAnnotation.point, text);
                    closeAnnotationModal();
                }}
            }}
            
            // Base64 인코딩/디코딩 함수
            function encodeBase64(str) {{
                return btoa(unescape(encodeURIComponent(str)));
            }}
            
            function decodeBase64(str) {{
                return decodeURIComponent(escape(atob(str)));
            }}
            
            // DB에 저장할 수정점들을 추적
            let pendingAnnotations = [];
            
            // 서버에 수정점 저장 (로컬에만 저장)
            async function saveAnnotationToServer(point, text) {{
                if (!modelToken) {{
                    console.error('Model token is missing');
                    return;
                }}
                
                try {{
                    // 임시 ID 생성
                    const tempId = 'temp_' + Date.now();
                    
                    // 로컬에 즉시 표시
                    createAnnotation(point, text, tempId);
                    
                    // pendingAnnotations에 추가
                    pendingAnnotations.push({{
                        tempId: tempId,
                        position: {{ x: point.x, y: point.y, z: point.z }},
                        text: text,
                        completed: false
                    }});
                    
                    // 제출완료 버튼 활성화
                    updateDbSaveButton();
                    
                    // 성공 메시지
                    showMessage('✅ 수정점이 추가되었습니다', 'success');
                    
                }} catch (error) {{
                    console.error('Error saving annotation:', error);
                    showMessage('❌ 오류: ' + error.message, 'error');
                }}
            }}
            
            // 제출완료 버튼 상태 업데이트
            function updateDbSaveButton() {{
                const btn = document.getElementById('dbSaveBtn');
                if (btn) {{
                    const hasChanges = pendingAnnotations.length > 0 || 
                                      annotations.some(a => a.modified || a.deleted);
                    if (hasChanges) {{
                        btn.textContent = `⚠️ 제출완료 (변경사항 ${{pendingAnnotations.length}}개)`;
                        btn.disabled = false;
                        btn.style.backgroundColor = '#ff4444';
                        btn.style.animation = 'pulse 1s infinite';
                    }} else {{
                        btn.textContent = '제출완료';
                        btn.disabled = true;
                        btn.style.backgroundColor = '#ccc';
                        btn.style.animation = 'none';
                    }}
                }}
            }}
            
            // DB에 모든 수정점 저장
            function saveToDatabase() {{
                if (!modelToken || pendingAnnotations.length === 0) {{
                    showMessage('저장할 수정점이 없습니다', 'info');
                    return;
                }}
                
                // 저장할 데이터를 JSON으로 인코딩
                const dataToSave = {{
                    model_token: modelToken,
                    annotations: pendingAnnotations
                }};
                
                // Base64로 인코딩
                const encodedData = btoa(unescape(encodeURIComponent(JSON.stringify(dataToSave))));
                
                // 현재 URL 파라미터 가져오기
                const currentUrl = new URL(window.location.href);
                const currentParams = new URLSearchParams(currentUrl.search);
                
                // 기존 token 파라미터 유지
                const token = currentParams.get('token') || modelToken;
                
                // 새로운 파라미터 설정
                const params = new URLSearchParams();
                params.set('token', token);  // token 파라미터 유지
                params.set('action', 'save_annotations');
                params.set('data', encodedData);
                
                // 저장 중 메시지
                showMessage('💾 제출 중...', 'info');
                
                // 페이지 리로드하여 서버에 저장
                setTimeout(() => {{
                    window.location.href = window.location.pathname + '?' + params.toString();
                }}, 1000);
            }}
            
            // 메시지 표시 함수
            function showMessage(text, type) {{
                const message = document.createElement('div');
                message.style.cssText = `
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: ${{type === 'success' ? '#4CAF50' : '#f44336'}};
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    font-size: 16px;
                    z-index: 100000;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                `;
                message.textContent = text;
                document.body.appendChild(message);
                
                setTimeout(() => {{
                    message.remove();
                }}, 2000);
            }}
            
            // 수정점 생성
            function createAnnotation(point, text, id) {{
                // 크기를 70%로 줄임 (0.05 -> 0.035)
                const geometry = new THREE.SphereGeometry(0.035, 16, 16);
                const material = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.copy(point);
                
                scene.add(mesh);
                
                const annotation = {{
                    id: id || 'temp_' + annotationIdCounter++,
                    mesh: mesh,
                    point: point.clone(),
                    text: text,
                    completed: false
                }};
                
                annotations.push(annotation);
            }}
            
            // 수정점 팝업 표시
            function showAnnotationPopup(annotation, event) {{
                const popup = document.getElementById('annotationPopup');
                const popupText = document.getElementById('popupText');
                const popupButtons = document.getElementById('popupButtons');
                
                popupText.textContent = annotation.text;
                
                if (annotation.completed) {{
                    popupButtons.innerHTML = `
                        <button class="popup-btn delete" onclick="deleteAnnotation('${{annotation.id}}')">삭제</button>
                    `;
                }} else {{
                    popupButtons.innerHTML = `
                        <button class="popup-btn complete" onclick="completeAnnotation('${{annotation.id}}')">수정완료</button>
                    `;
                }}
                
                popup.style.left = event.clientX + 10 + 'px';
                popup.style.top = event.clientY + 10 + 'px';
                popup.classList.add('show');
                
                // 클릭 외부 영역 클릭 시 팝업 닫기
                setTimeout(() => {{
                    document.addEventListener('click', hidePopupOnClickOutside);
                }}, 100);
            }}
            
            // 팝업 외부 클릭 시 숨기기
            function hidePopupOnClickOutside(event) {{
                const popup = document.getElementById('annotationPopup');
                if (!popup.contains(event.target)) {{
                    popup.classList.remove('show');
                    document.removeEventListener('click', hidePopupOnClickOutside);
                }}
            }}
            
            // 수정 완료 처리
            function completeAnnotation(id) {{
                const annotation = annotations.find(a => a.id == id);
                if (annotation) {{
                    annotation.completed = true;
                    annotation.mesh.material.color.setHex(0x0000ff);
                    
                    // pendingAnnotations에서도 업데이트
                    const pending = pendingAnnotations.find(p => p.tempId === id);
                    if (pending) {{
                        pending.completed = true;
                    }}
                    
                    showMessage('✅ 수정 완료로 표시됨 (제출완료 버튼을 눌러 저장하세요)', 'info');
                    updateDbSaveButton();
                }}
                document.getElementById('annotationPopup').classList.remove('show');
            }}
            
            // 수정점 삭제
            function deleteAnnotation(id) {{
                const index = annotations.findIndex(a => a.id == id);
                if (index !== -1) {{
                    const annotation = annotations[index];
                    scene.remove(annotation.mesh);
                    annotations.splice(index, 1);
                    
                    // pendingAnnotations에서도 제거
                    const pendingIndex = pendingAnnotations.findIndex(p => p.tempId === id);
                    if (pendingIndex !== -1) {{
                        pendingAnnotations.splice(pendingIndex, 1);
                        updateDbSaveButton();
                    }}
                    
                    // DB에 저장된 항목이면 서버에서도 삭제 필요 표시
                    if (annotation.saved && !String(id).startsWith('temp_')) {{
                        // 삭제 마크 표시
                        showMessage('⚠️ 삭제 완료 (제출완료 버튼을 눌러 DB에 반영하세요)', 'warning');
                    }} else {{
                        showMessage('✅ 수정점이 삭제됨 (제출완료 버튼을 눌러 저장하세요)', 'info');
                    }}
                    updateDbSaveButton();
                }}
                document.getElementById('annotationPopup').classList.remove('show');
            }}
            
            // 모든 수정점 제거 (모델 삭제 시 호출용)
            function clearAllAnnotations() {{
                annotations.forEach(annotation => {{
                    scene.remove(annotation.mesh);
                }});
                annotations = [];
            }}
            
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
                    renderer.shadowMap.enabled = false; // 그림자 비활성화
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
                    
                    // 상호작용 초기화
                    initInteraction();
                    
                    // 조명 없음 - MeshBasicMaterial 사용으로 텍스처 색상 100% 유지
                    
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
                        
                        // MeshBasicMaterial로 변환하여 조명 영향 제거 (색상 100% 정확)
                        if (textureFileName && textures[textureFileName]) {{
                            // 기존 material 대신 새로운 BasicMaterial 생성
                            const basicMaterial = new THREE.MeshBasicMaterial({{
                                map: textures[textureFileName],
                                side: THREE.FrontSide,
                                transparent: false,
                                alphaTest: 0,
                                depthWrite: true,
                                depthTest: true
                            }});
                            
                            // 텍스처 설정
                            basicMaterial.map.encoding = THREE.LinearEncoding;
                            basicMaterial.map.minFilter = THREE.LinearFilter;
                            basicMaterial.map.magFilter = THREE.LinearFilter;
                            basicMaterial.map.generateMipmaps = false;
                            basicMaterial.map.anisotropy = 1;
                            basicMaterial.map.wrapS = THREE.ClampToEdgeWrapping;
                            basicMaterial.map.wrapT = THREE.ClampToEdgeWrapping;
                            basicMaterial.map.needsUpdate = true;
                            
                            // 기존 material을 basicMaterial로 교체
                            materials.materials[materialName] = basicMaterial;
                            
                            console.log('✅ BasicMaterial applied: ' + textureFileName);
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
                    
                    // AO(Ambient Occlusion) 효과 추가 - 색상 변화 없이 형태만 강조
                    object.traverse((child) => {{
                        if (child.isMesh && child.geometry) {{
                            const geometry = child.geometry;
                            
                            // Normal 벡터가 있는지 확인하고 없으면 생성
                            if (!geometry.attributes.normal) {{
                                geometry.computeVertexNormals();
                            }}
                            
                            // 간단한 AO 효과를 위한 vertex color 생성
                            const positions = geometry.attributes.position;
                            const normals = geometry.attributes.normal;
                            const vertexCount = positions.count;
                            
                            // Vertex color 배열 생성
                            const colors = new Float32Array(vertexCount * 3);
                            
                            for (let i = 0; i < vertexCount; i++) {{
                                // Normal 벡터를 이용한 간단한 AO 계산
                                const nx = normals.getX(i);
                                const ny = normals.getY(i);
                                const nz = normals.getZ(i);
                                
                                // Y축 기준으로 위쪽(밝음) vs 아래쪽(어두움) 계산
                                // 색상은 변화시키지 않고 brightness만 살짝 조정
                                let ao = 0.7 + (ny * 0.3); // 0.7~1.0 범위
                                ao = Math.max(0.8, Math.min(1.0, ao)); // 0.8~1.0으로 제한 (very subtle)
                                
                                colors[i * 3] = ao;     // R
                                colors[i * 3 + 1] = ao; // G  
                                colors[i * 3 + 2] = ao; // B
                            }}
                            
                            // Vertex color 속성 추가
                            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
                            
                            // Material에 vertex color 사용 설정
                            if (child.material) {{
                                child.material.vertexColors = true;
                                child.material.needsUpdate = true;
                            }}
                            
                            console.log('AO effect applied to mesh:', child.name || 'unnamed');
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
                    
                    // 수정점 표시 버튼 확인 및 생성
                    const annotationBtn = document.getElementById('annotationBtn');
                    if (!annotationBtn) {{
                        console.log('수정점 표시 버튼이 없음 - 강제 생성');
                        const newBtn = document.createElement('button');
                        newBtn.className = 'annotation-btn';
                        newBtn.id = 'annotationBtn';
                        newBtn.textContent = '수정점표시';
                        newBtn.onclick = toggleAnnotationMode;
                        document.body.appendChild(newBtn);
                    }} else {{
                        console.log('수정점 표시 버튼이 정상적으로 존재함');
                    }}
                    
                    if (!controls || buttons.length === 0) {{
                        console.log('버튼이 없음 - 강제 생성');
                        createBackgroundButtons();
                    }} else {{
                        console.log('버튼이 정상적으로 존재함');
                    }}
                }}, 1000);
            }});
            
            // 초기화 완료 후 버튼 상태 확인
            window.addEventListener('DOMContentLoaded', function() {{
                const annotationBtn = document.getElementById('annotationBtn');
                if (annotationBtn) {{
                    console.log('수정점 표시 버튼 발견:', annotationBtn);
                    console.log('버튼 스타일:', window.getComputedStyle(annotationBtn).display);
                    console.log('버튼 위치:', window.getComputedStyle(annotationBtn).position);
                    console.log('버튼 z-index:', window.getComputedStyle(annotationBtn).zIndex);
                }} else {{
                    console.error('수정점 표시 버튼을 찾을 수 없습니다!');
                }}
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
