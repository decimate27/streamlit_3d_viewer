import base64
import json
from pathlib import Path

def create_3d_viewer_html(obj_content, mtl_content, texture_data, background_color="white", model_id=None, existing_feedbacks=None):
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
            
            /* 피드백 모드 버튼 */
            .feedback-mode-btn {{
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 16px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                z-index: 9999;
                transition: all 0.3s ease;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }}
            
            .feedback-mode-btn:hover {{
                background: #0056b3;
                transform: translateY(-1px);
                box-shadow: 0 3px 8px rgba(0,0,0,0.3);
            }}
            
            .feedback-mode-btn.active {{
                background: #dc3545;
            }}
            
            .feedback-mode-btn.active:hover {{
                background: #a71e2a;
            }}
            
            /* 피드백 핀 스타일 */
            .feedback-pin {{
                position: absolute;
                width: 30px;
                height: 30px;
                z-index: 1000;
                pointer-events: auto;
                cursor: pointer;
            }}
            
            .pin-icon {{
                width: 100%;
                height: 100%;
                background: #dc3545;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                animation: pinPulse 2s infinite;
            }}
            
            @keyframes pinPulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
                100% {{ transform: scale(1); }}
            }}
            
            .pin-tooltip {{
                position: absolute;
                bottom: 35px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                max-width: 200px;
                word-wrap: break-word;
                display: none;
            }}
            
            .feedback-pin:hover .pin-tooltip {{
                display: block;
            }}
            
            /* 피드백 입력 모달 */
            .feedback-modal {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            }}
            
            .feedback-modal-content {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                max-width: 400px;
                width: 90%;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }}
            
            .feedback-modal h3 {{
                margin: 0 0 15px 0;
                color: #333;
            }}
            
            .feedback-modal textarea {{
                width: 100%;
                height: 100px;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: Arial, sans-serif;
                font-size: 14px;
                resize: vertical;
                margin-bottom: 15px;
            }}
            
            .feedback-modal-buttons {{
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }}
            
            .feedback-modal button {{
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
            }}
            
            .btn-primary {{
                background: #007bff;
                color: white;
            }}
            
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            
            .btn-primary:hover {{
                background: #0056b3;
            }}
            
            .btn-secondary:hover {{
                background: #545b62;
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
            
            <!-- 피드백 모드 버튼 -->
            <button class="feedback-mode-btn" id="feedbackModeBtn" onclick="toggleFeedbackMode()">
                📝 피드백 모드
            </button>
            
            <!-- 피드백 동기화 버튼 -->
            <button class="feedback-mode-btn" id="syncFeedbackBtn" onclick="syncFeedbacksToServer()" 
                    style="top: 80px; background: #28a745;">
                💾 서버 동기화
            </button>
            
            <!-- 피드백 핀들 컨테이너 -->
            <div id="feedbackPins"></div>
            
            <!-- Mixed Content 안내 모달 -->
            <div class="feedback-modal" id="mixedContentModal" style="display: none;">
                <div class="feedback-modal-content" style="max-width: 500px;">
                    <h3>🔒 보안 설정 필요</h3>
                    <p>HTTPS 페이지에서 HTTP API 호출이 차단되었습니다.</p>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4>✅ 해결 방법 (Chrome):</h4>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>주소창 오른쪽의 <strong>방패🛡️ 아이콘</strong> 클릭</li>
                            <li><strong>"안전하지 않은 콘텐츠 허용"</strong> 클릭</li>
                            <li>페이지 자동 새로고침 후 다시 시도</li>
                        </ol>
                        
                        <h4>🔧 또는 설정에서:</h4>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>주소창 왼쪽 <strong>자물쇠🔒 아이콘</strong> 클릭</li>
                            <li><strong>"Site settings"</strong> 클릭</li>
                            <li><strong>"Insecure content"</strong> → <strong>"Allow"</strong> 변경</li>
                        </ol>
                    </div>
                    
                    <div class="feedback-modal-buttons">
                        <button class="btn-primary" onclick="closeMixedContentModal()">확인</button>
                        <button class="btn-secondary" onclick="location.reload()">페이지 새로고침</button>
                    </div>
                </div>
            </div>
            <div class="feedback-modal" id="feedbackModal" style="display: none;">
                <div class="feedback-modal-content">
                    <h3>피드백 등록</h3>
                    <textarea id="feedbackComment" placeholder="이 부분에 대한 피드백을 입력해주세요..."></textarea>
                    <div class="feedback-modal-buttons">
                        <button class="btn-secondary" onclick="closeFeedbackModal()">취소</button>
                        <button class="btn-primary" onclick="saveFeedback()">등록</button>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/loaders/OBJLoader.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/loaders/MTLLoader.js"></script>
        <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <script>
            let scene, camera, renderer, controls;
            let model;
            let feedbackMode = false;
            let pendingFeedback = null; // 저장 대기 중인 피드백 데이터
            let raycaster = new THREE.Raycaster();
            let mouse = new THREE.Vector2();
            let feedbackPins = []; // 3D 피드백 핀들을 추적하는 배열
            
            // 피드백 모드 토글
            function toggleFeedbackMode() {{
                feedbackMode = !feedbackMode;
                const btn = document.getElementById('feedbackModeBtn');
                
                if (feedbackMode) {{
                    btn.textContent = '❌ 피드백 종료';
                    btn.classList.add('active');
                    document.body.style.cursor = 'crosshair';
                }} else {{
                    btn.textContent = '📝 피드백 모드';
                    btn.classList.remove('active');
                    document.body.style.cursor = 'default';
                }}
                
                console.log('피드백 모드:', feedbackMode ? '활성화' : '비활성화');
            }}
            
            // 3D 좌표를 화면 좌표로 변환
            function toScreenPosition(point) {{
                const vector = point.clone();
                vector.project(camera);
                
                const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
                const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
                
                return {{ x: x, y: y }};
            }}
            
            // 피드백 모달 열기
            function openFeedbackModal(point3d, point2d) {{
                pendingFeedback = {{
                    x: point3d.x,
                    y: point3d.y,
                    z: point3d.z,
                    screen_x: point2d.x,
                    screen_y: point2d.y
                }};
                
                document.getElementById('feedbackModal').style.display = 'flex';
                document.getElementById('feedbackComment').focus();
            }}
            
            // Mixed Content 모달 관련 함수들
            function showMixedContentModal() {{
                document.getElementById('mixedContentModal').style.display = 'flex';
            }}
            
            function closeMixedContentModal() {{
                document.getElementById('mixedContentModal').style.display = 'none';
            }}
            
            // 피드백 모달 닫기
            function closeFeedbackModal() {{
                document.getElementById('feedbackModal').style.display = 'none';
                document.getElementById('feedbackComment').value = '';
                pendingFeedback = null;
            }}
            
            // 피드백 저장 (Streamlit로 전송)
            function saveFeedback() {{
                const comment = document.getElementById('feedbackComment').value.trim();
                
                if (!comment) {{
                    alert('피드백 내용을 입력해주세요.');
                    return;
                }}
                
                if (!pendingFeedback) {{
                    alert('피드백 위치 정보가 없습니다.');
                    return;
                }}
                
                // Streamlit으로 피드백 데이터 전송
                const feedbackData = {{
                    ...pendingFeedback,
                    comment: comment,
                    model_id: '{model_id or ""}', // 실제 model_id 사용
                    feedback_type: 'point'
                }};
                
                console.log('피드백 저장:', feedbackData);
                
                // TODO: Streamlit으로 데이터 전송하는 로직 추가
                // 지금은 임시로 핀만 표시
                addFeedbackPin(feedbackData);
                
                closeFeedbackModal();
                toggleFeedbackMode(); // 피드백 모드 종료
            }}
            
            // 피드백 핀 표시 (3D 좌표 추적)
            function addFeedbackPin(feedback) {{
                const pinElement = document.createElement('div');
                pinElement.className = 'feedback-pin';
                
                // 상태에 따른 핀 색상 변경
                let pinColor = '#dc3545'; // 기본 빨간색
                let statusIcon = '📍';
                
                switch(feedback.status) {{
                    case 'pending':
                        pinColor = '#dc3545'; // 빨간색
                        statusIcon = '📍';
                        break;
                    case 'reviewed':
                        pinColor = '#ffc107'; // 노란색
                        statusIcon = '👁️';
                        break;
                    case 'resolved':
                        pinColor = '#28a745'; // 초록색
                        statusIcon = '✅';
                        break;
                }}
                
                pinElement.innerHTML = `
                    <div class="pin-icon" style="background: ${{pinColor}};">${{statusIcon}}</div>
                    <div class="pin-tooltip">${{feedback.comment}}</div>
                `;
                
                // 3D 좌표 저장
                const point3d = new THREE.Vector3(feedback.x, feedback.y, feedback.z);
                
                // 핀 객체 생성 (3D 좌표와 DOM 요소 연결)
                const pinObject = {{
                    id: feedback.id || Date.now(),
                    element: pinElement,
                    position3d: point3d,
                    feedback: feedback
                }};
                
                // 핀 배열에 추가
                feedbackPins.push(pinObject);
                
                // DOM에 추가
                document.getElementById('feedbackPins').appendChild(pinElement);
                
                // 초기 위치 설정
                updatePinPosition(pinObject);
                
                console.log('3D 피드백 핀 추가:', pinObject.id, 'at', point3d);
            }}
            
            // 개별 핀 위치 업데이트
            function updatePinPosition(pinObject) {{
                if (!camera || !pinObject.element) return;
                
                // 3D 좌표를 현재 카메라 기준 2D 화면 좌표로 변환
                const screenPos = toScreenPosition(pinObject.position3d);
                
                // 화면 밖으로 나가면 숨기기
                if (screenPos.x < 0 || screenPos.x > window.innerWidth || 
                    screenPos.y < 0 || screenPos.y > window.innerHeight) {{
                    pinObject.element.style.display = 'none';
                }} else {{
                    pinObject.element.style.display = 'block';
                    pinObject.element.style.left = (screenPos.x - 15) + 'px';
                    pinObject.element.style.top = (screenPos.y - 15) + 'px';
                }}
            }}
            
            // 모든 핀 위치 업데이트 (카메라 움직임에 따라)
            function updateAllPinPositions() {{
                feedbackPins.forEach(pinObject => {{
                    updatePinPosition(pinObject);
                }});
            }}
            
            // 수동으로 로컬 피드백을 서버로 동기화 (간단한 버전)
            function syncFeedbacksToServer() {{
                try {{
                    const localFeedbacks = JSON.parse(localStorage.getItem('temp_feedbacks') || '[]');
                    const unsyncedFeedbacks = localFeedbacks.filter(f => !f.server_saved);
                    
                    if (unsyncedFeedbacks.length === 0) {{
                        alert('동기화할 피드백이 없습니다.');
                        return;
                    }}
                    
                    console.log('동기화할 피드백 수:', unsyncedFeedbacks.length);
                    
                    // 첫 번째 피드백만 동기화 (버튼을 여러 번 클릭하여 순차 처리)
                    const feedback = unsyncedFeedbacks[0];
                    console.log('동기화 중:', feedback);
                    
                    fetch('http://decimate27.dothome.co.kr/streamlit_data/feedback_api.php?action=save', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify(feedback)
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            console.log('서버 저장 성공 - ID:', data.feedback_id);
                            
                            // 로컬 스토리지에서 동기화 완료 표시
                            let allFeedbacks = JSON.parse(localStorage.getItem('temp_feedbacks') || '[]');
                            const idx = allFeedbacks.findIndex(f => f.id === feedback.id);
                            if (idx >= 0) {{
                                allFeedbacks[idx].server_saved = true;
                                allFeedbacks[idx].server_id = data.feedback_id;
                                localStorage.setItem('temp_feedbacks', JSON.stringify(allFeedbacks));
                            }}
                            
                            // 동기화 버튼 상태 업데이트
                            updateSyncButton();
                            
                            const remaining = unsyncedFeedbacks.length - 1;
                            if (remaining > 0) {{
                                alert(`✅ 1개 피드백 동기화 완료! 남은 개수: ${{remaining}}개`);
                            }} else {{
                                alert('🎉 모든 피드백이 동기화되었습니다!');
                            }}
                        }} else {{
                            console.error('서버 저장 실패:', data.error);
                            alert(`❌ 피드백 동기화 실패: ${{data.error || '알 수 없는 오류'}}`);
                        }}
                    }})
                    .catch(error => {{
                        console.error('네트워크 오류:', error);
                        
                        // Mixed Content 오류인지 확인
                        if (error.message.includes('Failed to fetch') && window.location.protocol === 'https:') {{
                            showMixedContentModal();
                        }} else {{
                            alert(`❌ 네트워크 오류: ${{error.message}}`);
                        }}
                    }});
                    
                }} catch (error) {{
                    console.error('동기화 오류:', error);
                    alert('동기화 중 오류가 발생했습니다.');
                }}
            }}
            
            // 동기화 버튼 상태 업데이트
            function updateSyncButton() {{
                try {{
                    const localFeedbacks = JSON.parse(localStorage.getItem('temp_feedbacks') || '[]');
                    const unsyncedCount = localFeedbacks.filter(f => !f.server_saved).length;
                    
                    const syncBtn = document.getElementById('syncFeedbackBtn');
                    if (syncBtn) {{
                        if (unsyncedCount > 0) {{
                            syncBtn.textContent = `💾 서버 동기화 (${{unsyncedCount}})`;
                            syncBtn.style.backgroundColor = '#dc3545'; // 빨간색 (동기화 필요)
                        }} else {{
                            syncBtn.textContent = '💾 서버 동기화';
                            syncBtn.style.backgroundColor = '#28a745'; // 초록색 (동기화 완료)
                        }}
                    }}
                }} catch (error) {{
                    console.error('동기화 버튼 업데이트 오류:', error);
                }}
            }}
            
            // 마우스 클릭 이벤트 핸들러
            function onMouseClick(event) {{
                if (!feedbackMode) return;
                
                // 마우스 좌표 정규화
                mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
                
                // Raycasting으로 3D 교점 찾기
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(scene.children, true);
                
                if (intersects.length > 0) {{
                    const point3d = intersects[0].point;
                    const point2d = toScreenPosition(point3d);
                    
                    console.log('3D 클릭 위치:', point3d);
                    console.log('2D 화면 위치:', point2d);
                    
                    openFeedbackModal(point3d, point2d);
                }}
            }}
            
            // 기존 피드백들 로드 및 표시
            function loadExistingFeedbacks() {{
                // 서버에서 전달된 피드백 (데이터베이스에서)
                const serverFeedbacks = {json.dumps(existing_feedbacks or [])};
                
                // 로컬 스토리지에서 임시 피드백 (테스트용)
                let localFeedbacks = [];
                try {{
                    localFeedbacks = JSON.parse(localStorage.getItem('temp_feedbacks') || '[]');
                }} catch (error) {{
                    console.error('로컬 피드백 로드 오류:', error);
                }}
                
                // 두 피드백 목록 병합
                const allFeedbacks = [...serverFeedbacks, ...localFeedbacks];
                
                console.log('서버 피드백:', serverFeedbacks.length, '개');
                console.log('로컬 피드백:', localFeedbacks.length, '개');
                console.log('전체 피드백:', allFeedbacks.length, '개');
                
                // 동기화 버튼 상태 업데이트
                updateSyncButton();
                
                allFeedbacks.forEach(feedback => {{
                    // 3D 좌표를 사용하여 핀 생성 (screen_x, screen_y 무시)
                    addFeedbackPin(feedback);
                }});
            }}
            
            // 피드백 저장 (서버로 전송)
            function saveFeedback() {{
                const comment = document.getElementById('feedbackComment').value.trim();
                
                if (!comment) {{
                    alert('피드백 내용을 입력해주세요.');
                    return;
                }}
                
                if (!pendingFeedback) {{
                    alert('피드백 위치 정보가 없습니다.');
                    return;
                }}
                
                // 피드백 데이터 생성
                const feedbackData = {{
                    ...pendingFeedback,
                    comment: comment,
                    model_id: '{model_id or ""}',
                    feedback_type: 'point'
                }};
                
                console.log('서버로 피드백 전송:', feedbackData);
                
                // 서버로 피드백 전송
                sendFeedbackToServer(feedbackData);
                
                closeFeedbackModal();
                toggleFeedbackMode(); // 피드백 모드 종료
            }}
            
            // 서버로 피드백 전송 (HTTPS)
            function sendFeedbackToServer(feedbackData) {{
                // 1. 로컬에 저장하고 핀 표시
                try {{
                    let savedFeedbacks = JSON.parse(localStorage.getItem('temp_feedbacks') || '[]');
                    feedbackData.id = Date.now();
                    feedbackData.status = 'pending';
                    feedbackData.created_at = new Date().toISOString();
                    savedFeedbacks.push(feedbackData);
                    localStorage.setItem('temp_feedbacks', JSON.stringify(savedFeedbacks));
                    
                    // 즉시 핀 표시
                    addFeedbackPin(feedbackData);
                    
                    console.log('✅ 피드백이 임시 저장되었습니다.');
                }} catch (error) {{
                    console.error('피드백 저장 오류:', error);
                    alert('피드백 저장에 실패했습니다.');
                    return;
                }}
                
                // 2. 서버로 전송 (HTTPS)
                console.log('📡 서버로 피드백 전송 시도');
                
                fetch('http://decimate27.dothome.co.kr/streamlit_data/feedback_api.php?action=save', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify(feedbackData)
                }})
                .then(response => response.json())
                .then(data => {{
                    console.log('✅ 서버 응답:', data);
                    if (data.success) {{
                        console.log('서버 저장 성공 - ID:', data.feedback_id);
                        // 로컬 스토리지에서 서버 저장 완료로 표시
                        let savedFeedbacks = JSON.parse(localStorage.getItem('temp_feedbacks') || '[]');
                        const idx = savedFeedbacks.findIndex(f => f.id === feedbackData.id);
                        if (idx >= 0) {{
                            savedFeedbacks[idx].server_saved = true;
                            savedFeedbacks[idx].server_id = data.feedback_id;
                            localStorage.setItem('temp_feedbacks', JSON.stringify(savedFeedbacks));
                        }}
                    }} else {{
                        console.error('서버 저장 실패:', data.error);
                    }}
                }})
                .catch(error => {{
                    console.error('네트워크 오류:', error);
                    alert(`❌ 서버 연결 실패: ${{error.message}}`);
                    console.log('서버가 실행 중인지 확인하세요: http://decimate27.dothome.co.kr/streamlit_data/feedback_api.php');
                }});
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
                    
                    // 조명 없음 - MeshBasicMaterial 사용으로 텍스처 색상 100% 유지
                    
                    console.log('Scene setup complete');
                    
                    // 전체 로딩 타임아웃 (10초)
                    setTimeout(() => {{
                        if (!model) {{
                            console.warn('🕐 전체 로딩 타임아웃, 강제 시작');
                            hideLoadingSpinner();
                            loadMTLAndOBJ();
                        }}
                    }}, 10000);
                    
                    // 모델 로드
                    loadModel();
                    
                    // 모바일이 아닌 경우에만 즉시 애니메이션 시작
                    if (!isMobile) {{
                        animate();
                    }}
                    
                    // 마우스 클릭 이벤트 등록 (피드백용)
                    renderer.domElement.addEventListener('click', onMouseClick, false);
                    
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
                    
                    // 모든 텍스처 로딩 완료까지 대기
                    const textureNames = Object.keys(textures);
                    let loadedCount = 0;
                    const totalCount = {len(texture_base64)};
                    
                    // 텍스처 로딩 대기 시간 제한 추가
                    let textureCheckCount = 0;
                    const maxChecks = 50; // 5초 제한
                    
                    function checkTexturesLoaded() {{
                        textureCheckCount++;
                        
                        if (Object.keys(textures).length >= totalCount) {{
                            console.log('✅ All textures loaded:', Object.keys(textures));
                            loadMTLAndOBJ();
                        }} else if (textureCheckCount >= maxChecks) {{
                            console.warn('⚠️ Texture loading timeout, proceeding with available textures');
                            console.log('Loaded textures:', Object.keys(textures));
                            loadMTLAndOBJ();
                        }} else {{
                            setTimeout(checkTexturesLoaded, 100);
                        }}
                    }}
                    
                    if (totalCount > 0) {{
                        console.log(`🎨 텍스처 ${{totalCount}}개 로딩 대기 중...`);
                        checkTexturesLoaded();
                    }} else {{
                        console.log('📦 텍스처가 없음, 직접 모델 로딩 시작');
                        loadMTLAndOBJ();
                    }}
                    
                    function loadMTLAndOBJ() {{
                    
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
                            
                            // 모바일에서도 마우스 클릭 이벤트 등록
                            renderer.domElement.addEventListener('click', onMouseClick, false);
                            
                            // 기존 피드백들 로드
                            loadExistingFeedbacks();
                            
                            console.log('Mobile optimization complete');
                        }}, delay);
                    }} else {{
                        setTimeout(() => {{
                            hideLoadingSpinner();
                            
                            // 기존 피드백들 로드
                            loadExistingFeedbacks();
                        }}, 500);
                    }}
                    
                    }} // loadMTLAndOBJ 함수 종료
                }} catch (error) {{
                    console.error('Model loading error:', error);
                    document.getElementById('loading').innerHTML = 'Model loading failed: ' + error.message;
                }}
            }}
            
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                
                // 모든 피드백 핀 위치 업데이트 (카메라 움직임 추적)
                updateAllPinPositions();
                
                renderer.render(scene, camera);
            }}
            
            function onWindowResize() {{
                const container = document.getElementById('container');
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
                
                // 창 크기 변경 시 모든 핀 위치 업데이트
                updateAllPinPositions();
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
    """텍스처 로딩 JavaScript 코드 생성 - 안전한 오류 처리 포함"""
    if not texture_base64:
        return "console.log('📦 No textures to load');"
    
    code_lines = []
    for name, data in texture_base64.items():
        safe_name = name.replace('.', '_').replace('-', '_').replace(' ', '_')
        ext = Path(name).suffix.lower()
        mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
        code_lines.append(f"""
                // {name} 텍스처 로딩 (안전한 오류 처리 포함)
                (function() {{
                    try {{
                        const img = new Image();
                        const dataUrl = 'data:{mime_type};base64,{data[:100]}...'; // 로그용 축약
                        
                        img.onload = function() {{
                            try {{
                                const canvas = document.createElement('canvas');
                                const ctx = canvas.getContext('2d');
                                canvas.width = img.width;
                                canvas.height = img.height;
                                ctx.drawImage(img, 0, 0);
                                
                                const texture = new THREE.CanvasTexture(canvas);
                                texture.encoding = THREE.LinearEncoding;
                                texture.flipY = true;
                                texture.generateMipmaps = false;
                                texture.minFilter = THREE.LinearFilter;
                                texture.magFilter = THREE.LinearFilter;
                                texture.anisotropy = 1;
                                texture.wrapS = THREE.ClampToEdgeWrapping;
                                texture.wrapT = THREE.ClampToEdgeWrapping;
                                texture.format = THREE.RGBFormat;
                                texture.type = THREE.UnsignedByteType;
                                texture.needsUpdate = true;
                                
                                textures['{name}'] = texture;
                                console.log('✅ Texture loaded:', '{name}');
                            }} catch (e) {{
                                console.error('❌ Texture processing error for {name}:', e);
                            }}
                        }};
                        
                        img.onerror = function() {{
                            console.error('❌ Failed to load texture image: {name}');
                        }};
                        
                        img.src = 'data:{mime_type};base64,{data}';
                    }} catch (e) {{
                        console.error('❌ Texture loading setup error for {name}:', e);
                    }}
                }})();
        """)
    
    return '\n'.join(code_lines)
