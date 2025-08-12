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
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>3D Model Viewer</title>
        
        <!-- Three.js CDN -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <style>
            * {{ 
                box-sizing: border-box; 
                margin: 0;
                padding: 0;
            }}
            
            html, body {{ 
                width: 100%; 
                height: 100%; 
                overflow: hidden;
                background: {bg_color};
            }}
            
            #container {{ 
                width: 100vw; 
                height: 100vh; 
                position: fixed;
                top: 0;
                left: 0;
            }}
            
            canvas {{
                display: block;
                width: 100%;
                height: 100%;
            }}
            
            .loading-container {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                z-index: 1000;
            }}
            
            .loading-text {{
                font-family: Arial, sans-serif;
                font-size: 18px;
                color: {'white' if background_color == 'black' else 'black'};
                margin-top: 20px;
            }}
            
            /* 컨트롤 버튼들 */
            .controls {{
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            
            .bg-btn {{
                padding: 8px 12px;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                font-weight: bold;
                transition: all 0.3s ease;
                min-width: 60px;
                text-align: center;
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
            
            /* 수정점 표시 버튼 */
            .annotation-btn {{
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 15px;
                background: #ff4444;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                z-index: 99999;
            }}
            
            .annotation-btn.active {{
                background: #cc0000;
            }}
            
            /* 제출완료 버튼 */
            .db-save-btn {{
                position: fixed;
                top: 70px;
                right: 20px;
                padding: 10px 15px;
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                z-index: 99999;
            }}
            
            .db-save-btn:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
            
            /* 모달 */
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
            
            .annotation-modal {{
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 10px;
                z-index: 10001;
                min-width: 300px;
            }}
            
            .annotation-modal.show {{
                display: block;
            }}
            
            .annotation-input {{
                width: 100%;
                padding: 8px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
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
            
            /* 팝업 */
            .annotation-popup {{
                display: none;
                position: fixed;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.3);
                z-index: 10002;
                min-width: 200px;
            }}
            
            .annotation-popup.show {{
                display: block;
            }}
            
            .popup-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .popup-close {{
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                color: #666;
                padding: 0;
                width: 24px;
                height: 24px;
            }}
            
            .popup-text {{
                font-size: 14px;
                color: #333;
            }}
            
            .popup-buttons {{
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }}
            
            .popup-btn {{
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                flex: 1;
            }}
            
            .popup-btn.complete {{
                background: #2196F3;
                color: white;
            }}
            
            .popup-btn.delete {{
                background: #f44336;
                color: white;
            }}
            
            .popup-btn.close {{
                background: #9E9E9E;
                color: white;
            }}
            
            /* 모바일 최적화 */
            @media (max-width: 768px) {{
                .controls {{
                    top: 10px;
                    left: 10px;
                }}
                
                .annotation-btn, .db-save-btn {{
                    padding: 8px 12px;
                    font-size: 12px;
                }}
                
                .annotation-btn {{
                    top: 10px;
                    right: 10px;
                }}
                
                .db-save-btn {{
                    top: 55px;
                    right: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- 수정점 표시 버튼 -->
        <button class="annotation-btn" id="annotationBtn" onclick="toggleAnnotationMode()">
            수정점표시
        </button>
        
        <!-- 제출완료 버튼 -->
        <button class="db-save-btn" id="dbSaveBtn" onclick="saveToDatabase()">
            제출완료
        </button>
        
        <div id="container">
            <div class="loading-container" id="loading">
                <div class="loading-text">Loading...</div>
            </div>
            
            <!-- 배경색 변경 컨트롤 -->
            <div class="controls">
                <button class="bg-btn bg-white" onclick="changeBackground('white')">⚪ 흰색</button>
                <button class="bg-btn bg-gray" onclick="changeBackground('gray')">🔘 회색</button>
                <button class="bg-btn bg-black" onclick="changeBackground('black')">⚫ 검은색</button>
            </div>
        </div>
        
        <!-- 수정점 입력 모달 -->
        <div class="modal-overlay" id="modalOverlay"></div>
        <div class="annotation-modal" id="annotationModal">
            <h3>수정사항 입력</h3>
            <textarea class="annotation-input" id="annotationInput" rows="3" placeholder="수정할 사항을 입력하세요..."></textarea>
            <div class="modal-buttons">
                <button class="modal-btn cancel" onclick="closeAnnotationModal()">취소</button>
                <button class="modal-btn confirm" onclick="confirmAnnotation()">확인</button>
            </div>
        </div>
        
        <!-- 수정점 정보 팝업 -->
        <div class="annotation-popup" id="annotationPopup">
            <div class="popup-header">
                <div class="popup-text" id="popupText"></div>
                <button class="popup-close" onclick="closeAnnotationPopup()">×</button>
            </div>
            <div class="popup-buttons" id="popupButtons"></div>
        </div>
        
        <script>
            let scene, camera, renderer, controls;
            let model;
            let raycaster, mouse;
            let isAnnotationMode = false;
            let annotations = [];
            let currentAnnotation = null;
            let pendingAnnotations = [];
            const modelToken = '{model_token if model_token else ""}';
            
            // 초기 annotations 데이터
            const initialAnnotations = {json.dumps(annotations if annotations else [])};
            
            function init() {{
                try {{
                    console.log('Initializing 3D viewer...');
                    
                    // Scene 생성
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color('{bg_color}');
                    
                    // Camera 생성
                    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 0, 5);
                    
                    // Renderer 생성
                    const container = document.getElementById('container');
                    renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                    container.appendChild(renderer.domElement);
                    
                    // Controls 생성
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.08;
                    
                    // 조명 추가
                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
                    scene.add(ambientLight);
                    
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.2);
                    directionalLight.position.set(5, 5, 5);
                    scene.add(directionalLight);
                    
                    // 모델 로드
                    loadModel();
                    
                    // Interaction 초기화
                    initInteraction();
                    
                    // 애니메이션 시작
                    animate();
                    
                }} catch (error) {{
                    console.error('Init error:', error);
                    document.getElementById('loading').innerHTML = 'Error: ' + error.message;
                }}
            }}
            
            function loadModel() {{
                try {{
                    console.log('Loading model...');
                    
                    // 텍스처 데이터
                    const textureBase64 = {str(texture_base64)};
                    const textures = {{}};
                    
                    // Base64 텍스처를 THREE.Texture로 변환
                    for (const [name, base64] of Object.entries(textureBase64)) {{
                        const img = new Image();
                        img.src = 'data:image/png;base64,' + base64;
                        const texture = new THREE.Texture(img);
                        texture.needsUpdate = true;
                        img.onload = () => {{ texture.needsUpdate = true; }};
                        textures[name] = texture;
                    }}
                    
                    // MTL 로더
                    const mtlLoader = new THREE.MTLLoader();
                    const materials = mtlLoader.parse(`{mtl_content}`, '');
                    
                    // 텍스처 매핑
                    for (const [name, material] of Object.entries(materials.materials)) {{
                        if (material.map && textures[material.map.name]) {{
                            material.map = textures[material.map.name];
                        }}
                    }}
                    
                    materials.preload();
                    
                    // OBJ 로더
                    const objLoader = new THREE.OBJLoader();
                    objLoader.setMaterials(materials);
                    const object = objLoader.parse(`{obj_content}`);
                    
                    // 모델 크기 조정
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
                    
                    // 로딩 화면 숨기기
                    document.getElementById('loading').style.display = 'none';
                    
                    console.log('Model loaded successfully');
                    
                }} catch (error) {{
                    console.error('Model loading error:', error);
                    document.getElementById('loading').innerHTML = 'Loading failed: ' + error.message;
                }}
            }}
            
            function initInteraction() {{
                raycaster = new THREE.Raycaster();
                mouse = new THREE.Vector2();
                
                renderer.domElement.addEventListener('click', onMouseClick, false);
                renderer.domElement.addEventListener('touchstart', onTouchStart, false);
                
                // 기존 annotations 로드
                loadExistingAnnotations();
            }}
            
            function loadExistingAnnotations() {{
                if (initialAnnotations && initialAnnotations.length > 0) {{
                    initialAnnotations.forEach(ann => {{
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
                            saved: true
                        }});
                    }});
                }}
                
                updateDbSaveButton();
            }}
            
            function handleInteraction(clientX, clientY, event) {{
                if (!model) return;
                
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
                
                // 수정점 추가 모드
                if (isAnnotationMode) {{
                    const intersects = raycaster.intersectObject(model, true);
                    if (intersects.length > 0) {{
                        const point = intersects[0].point;
                        openAnnotationModal(point);
                    }}
                }}
            }}
            
            function onMouseClick(event) {{
                event.preventDefault();
                handleInteraction(event.clientX, event.clientY, event);
            }}
            
            function onTouchStart(event) {{
                event.preventDefault();
                if (event.touches.length === 1) {{
                    const touch = event.touches[0];
                    handleInteraction(touch.clientX, touch.clientY, touch);
                }}
            }}
            
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
            
            function openAnnotationModal(point) {{
                currentAnnotation = {{ point: point.clone() }};
                document.getElementById('annotationInput').value = '';
                document.getElementById('annotationModal').classList.add('show');
                document.getElementById('modalOverlay').classList.add('show');
            }}
            
            function closeAnnotationModal() {{
                document.getElementById('annotationModal').classList.remove('show');
                document.getElementById('modalOverlay').classList.remove('show');
                currentAnnotation = null;
            }}
            
            function confirmAnnotation() {{
                const text = document.getElementById('annotationInput').value.trim();
                if (text && currentAnnotation) {{
                    saveAnnotationToServer(currentAnnotation.point, text);
                    closeAnnotationModal();
                }}
            }}
            
            function saveAnnotationToServer(point, text) {{
                if (!modelToken) {{
                    console.error('Model token is missing');
                    return;
                }}
                
                const tempId = 'temp_' + Date.now();
                createAnnotation(point, text, tempId);
                
                pendingAnnotations.push({{
                    tempId: tempId,
                    position: {{ x: point.x, y: point.y, z: point.z }},
                    text: text,
                    completed: false
                }});
                
                updateDbSaveButton();
                showMessage('✅ 수정점이 추가되었습니다', 'success');
            }}
            
            function createAnnotation(point, text, id) {{
                const geometry = new THREE.SphereGeometry(0.035, 16, 16);
                const material = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.copy(point);
                
                scene.add(mesh);
                
                annotations.push({{
                    id: id,
                    mesh: mesh,
                    point: point.clone(),
                    text: text,
                    completed: false
                }});
            }}
            
            function showAnnotationPopup(annotation, event) {{
                const popup = document.getElementById('annotationPopup');
                const popupText = document.getElementById('popupText');
                const popupButtons = document.getElementById('popupButtons');
                
                popupText.textContent = annotation.text;
                
                if (annotation.completed) {{
                    popupButtons.innerHTML = `
                        <button class="popup-btn delete" onclick="deleteAnnotation('${{annotation.id}}')">삭제</button>
                        <button class="popup-btn close" onclick="closeAnnotationPopup()">닫기</button>
                    `;
                }} else {{
                    popupButtons.innerHTML = `
                        <button class="popup-btn complete" onclick="completeAnnotation('${{annotation.id}}')">수정완료</button>
                        <button class="popup-btn close" onclick="closeAnnotationPopup()">닫기</button>
                    `;
                }}
                
                // 모바일에서는 중앙에 표시
                const isMobile = window.innerWidth <= 768;
                if (isMobile) {{
                    popup.style.left = '50%';
                    popup.style.top = '50%';
                    popup.style.transform = 'translate(-50%, -50%)';
                }} else {{
                    popup.style.left = event.clientX + 10 + 'px';
                    popup.style.top = event.clientY + 10 + 'px';
                    popup.style.transform = 'none';
                }}
                
                popup.classList.add('show');
            }}
            
            function closeAnnotationPopup() {{
                document.getElementById('annotationPopup').classList.remove('show');
            }}
            
            function completeAnnotation(id) {{
                const annotation = annotations.find(a => a.id == id);
                if (annotation) {{
                    annotation.completed = true;
                    annotation.mesh.material.color.setHex(0x0000ff);
                    
                    const pending = pendingAnnotations.find(p => p.tempId === id);
                    if (pending) {{
                        pending.completed = true;
                    }}
                    
                    updateDbSaveButton();
                }}
                closeAnnotationPopup();
            }}
            
            function deleteAnnotation(id) {{
                const index = annotations.findIndex(a => a.id == id);
                if (index !== -1) {{
                    const annotation = annotations[index];
                    scene.remove(annotation.mesh);
                    annotations.splice(index, 1);
                    
                    const pendingIndex = pendingAnnotations.findIndex(p => p.tempId === id);
                    if (pendingIndex !== -1) {{
                        pendingAnnotations.splice(pendingIndex, 1);
                    }}
                    
                    updateDbSaveButton();
                }}
                closeAnnotationPopup();
            }}
            
            function updateDbSaveButton() {{
                const btn = document.getElementById('dbSaveBtn');
                if (btn) {{
                    const hasChanges = pendingAnnotations.length > 0;
                    if (hasChanges) {{
                        btn.textContent = `⚠️ 제출완료 (${{pendingAnnotations.length}}개)`;
                        btn.disabled = false;
                        btn.style.backgroundColor = '#ff4444';
                    }} else {{
                        btn.textContent = '제출완료';
                        btn.disabled = false;
                        btn.style.backgroundColor = '#2196F3';
                    }}
                }}
            }}
            
            function saveToDatabase() {{
                if (!modelToken) {{
                    showMessage('모델 토큰이 없습니다', 'error');
                    return;
                }}
                
                if (pendingAnnotations.length === 0) {{
                    showMessage('저장할 변경사항이 없습니다', 'info');
                    return;
                }}
                
                const dataToSave = {{
                    model_token: modelToken,
                    annotations: pendingAnnotations
                }};
                
                const encodedData = btoa(unescape(encodeURIComponent(JSON.stringify(dataToSave))));
                
                const currentUrl = new URL(window.location.href);
                const currentParams = new URLSearchParams(currentUrl.search);
                const token = currentParams.get('token') || modelToken;
                
                const params = new URLSearchParams();
                params.set('token', token);
                params.set('action', 'save_annotations');
                params.set('data', encodedData);
                
                showMessage('💾 제출 중...', 'info');
                
                setTimeout(() => {{
                    window.location.href = window.location.pathname + '?' + params.toString();
                }}, 1000);
            }}
            
            function showMessage(text, type) {{
                const message = document.createElement('div');
                const bgColor = type === 'success' ? '#4CAF50' : 
                              type === 'error' ? '#f44336' : 
                              type === 'warning' ? '#ff9800' : '#2196F3';
                
                message.style.cssText = `
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: ${{bgColor}};
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    font-size: 16px;
                    z-index: 100000;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                    max-width: 80%;
                    text-align: center;
                `;
                message.textContent = text;
                document.body.appendChild(message);
                
                setTimeout(() => {{
                    message.remove();
                }}, 2500);
            }}
            
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
                
                if (scene) {{
                    scene.background = new THREE.Color(colors[color]);
                }}
                
                if (renderer) {{
                    renderer.setClearColor(colors[color], 1);
                }}
                
                document.body.style.background = bodyColors[color];
                document.getElementById('container').style.background = bodyColors[color];
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
            
            // 초기화
            window.addEventListener('DOMContentLoaded', init);
            window.addEventListener('resize', onWindowResize);
            
            // 대체 초기화
            if (document.readyState === 'complete' || document.readyState === 'interactive') {{
                setTimeout(init, 100);
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content
