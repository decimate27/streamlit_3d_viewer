import base64
import json
from pathlib import Path

def create_3d_viewer_html(obj_content, mtl_content, texture_data, background_color="white", model_token=None, annotations=None, real_height=None):
    """Three.js 기반 3D 뷰어 HTML 생성 - 치수선 기능 포함"""
    
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
    <html style="background: {bg_color};">
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
                background: transparent !important;
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
                    top: 8px;
                    left: 8px;
                    gap: 2px;
                }}
                .bg-btn {{
                    padding: 4px 6px;
                    font-size: 9px;
                    min-width: 36px;
                    border-width: 1px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.2);
                }}
                .bg-btn:hover {{
                    transform: none;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.3);
                }}
            }}
            
            /* 아주 작은 화면 (스마트폰) */
            @media (max-width: 480px) {{
                .controls {{
                    top: 4px;
                    left: 4px;
                    gap: 2px;
                }}
                .bg-btn {{
                    padding: 3px 5px;
                    font-size: 8px;
                    min-width: 28px;
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
            
            /* 퐁 쉐이딩 체크박스 스타일 */
            .phong-control {{
                position: fixed;
                top: 20px;
                left: 150px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                background: rgba(255, 255, 255, 0.9);
                padding: 8px 12px;
                border-radius: 6px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                font-family: Arial, sans-serif;
                font-size: 13px;
                font-weight: 500;
                color: #333;
                user-select: none;
                transition: all 0.3s ease;
            }}
            
            .phong-control:hover {{
                background: rgba(255, 255, 255, 0.95);
                box-shadow: 0 3px 8px rgba(0,0,0,0.3);
            }}
            
            .phong-checkbox-wrapper {{
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
            }}
            
            .phong-control input[type="checkbox"] {{
                width: 18px;
                height: 18px;
                cursor: pointer;
                margin: 0;
            }}
            
            .phong-control label {{
                cursor: pointer;
                margin: 0;
                white-space: nowrap;
            }}
            
            /* 슬라이더 컨테이너 */
            .phong-slider-container {{
                display: none;
                flex-direction: column;
                gap: 5px;
                width: 150px;
                opacity: 0;
                transition: opacity 0.3s ease;
            }}
            
            .phong-slider-container.active {{
                display: flex;
                opacity: 1;
            }}
            
            .phong-slider-label {{
                display: flex;
                justify-content: space-between;
                font-size: 11px;
                color: #666;
            }}
            
            .phong-slider {{
                width: 100%;
                height: 20px;
                -webkit-appearance: none;
                appearance: none;
                background: transparent;
                outline: none;
                cursor: pointer;
            }}
            
            .phong-slider::-webkit-slider-track {{
                width: 100%;
                height: 4px;
                background: #ddd;
                border-radius: 2px;
            }}
            
            .phong-slider::-webkit-slider-thumb {{
                -webkit-appearance: none;
                appearance: none;
                width: 16px;
                height: 16px;
                background: #4CAF50;
                border-radius: 50%;
                cursor: pointer;
                margin-top: -6px;
            }}
            
            .phong-slider::-moz-range-track {{
                width: 100%;
                height: 4px;
                background: #ddd;
                border-radius: 2px;
            }}
            
            .phong-slider::-moz-range-thumb {{
                width: 16px;
                height: 16px;
                background: #4CAF50;
                border-radius: 50%;
                border: none;
                cursor: pointer;
            }}
            
            /* 모바일 최적화 - 입체감 증가 버튼을 치수 버튼 아래로 배치 */
            @media (max-width: 768px) {{
                .phong-control {{
                    top: 126px !important;  /* 치수 버튼(88px) 아래로 이동 */
                    left: auto !important;
                    right: 12px !important;  /* 제출완료 버튼과 같은 오른쪽 정렬 */
                    font-size: 12px;
                    padding: 8px 10px;
                    background: rgba(255, 255, 255, 0.95);
                }}
                
                .phong-control input[type="checkbox"] {{
                    width: 15px;
                    height: 15px;
                }}
                
                .phong-slider-container {{
                    width: 120px;
                }}
            }}
            
            @media (max-width: 480px) {{
                .phong-control {{
                    top: 124px !important;  /* 치수 버튼(86px) 아래로 이동 */
                    left: auto !important;
                    right: 10px !important;  /* 제출완료 버튼과 같은 오른쪽 정렬 */
                    font-size: 11px;
                    padding: 6px 8px;
                    gap: 6px;
                }}
                
                .phong-control input[type="checkbox"] {{
                    width: 14px;
                    height: 14px;
                }}
                
                .phong-slider-container {{
                    width: 100px;
                }}
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
            
            /* 로딩 오버레이 */
            #loadingOverlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: {bg_color};
                z-index: 9999;
                display: flex;
                justify-content: center;
                align-items: center;
                transition: opacity 0.5s ease-in-out;
            }}
            
            #loadingOverlay.fade-out {{
                opacity: 0;
                pointer-events: none;
            }}
            
            /* 로딩 스피너 스타일 */
            .loading-container {{
                text-align: center;
                color: #333;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            }}
            
            /* 간단한 로딩 스피너 */
            .simple-loader {{
                width: 40px;
                height: 40px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #333;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }}
            
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
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
                padding: 6px 16px !important;
                border-radius: 20px !important;
                font-size: 13px !important;
                font-weight: 500 !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
                z-index: 99998 !important;
                white-space: nowrap !important;
                max-width: calc(100vw - 40px) !important;
                text-align: center !important;
                letter-spacing: 0.2px !important;
            }}
            
            /* 모바일에서 안내 텍스트 최적화 */
            @media (max-width: 768px) {{
                .top-notice {{
                    font-size: 11px !important;
                    padding: 4px 12px !important;
                    max-width: calc(100vw - 30px) !important;
                    border-radius: 15px !important;
                }}
                /* 실제 크기 정보 숨김 */
                #dimensionInfo {{
                    display: none !important;
                }}
            }}
            
            @media (max-width: 480px) {{
                .top-notice {{
                    font-size: 10px !important;
                    padding: 3px 10px !important;
                    max-width: calc(100vw - 20px) !important;
                    border-radius: 12px !important;
                    white-space: normal !important;
                    line-height: 1.3 !important;
                }}
            }}
            
            /* 수정점 표시 및 제출완료 버튼 통일 스타일 */
            .annotation-btn, .db-save-btn {{
                position: fixed !important;
                right: 20px !important;
                padding: 12px 16px !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                cursor: pointer !important;
                font-size: 14px !important;
                font-weight: bold !important;
                box-shadow: 0 3px 8px rgba(0,0,0,0.25) !important;
                z-index: 99999 !important;
                display: block !important;
                visibility: visible !important;
                min-width: 120px !important;
                text-align: center !important;
                transition: all 0.2s ease !important;
                letter-spacing: 0.3px !important;
            }}
            
            /* 수정점 표시 버튼 */
            .annotation-btn {{
                top: 20px !important;
                background: #ff4444 !important;
            }}
            
            .annotation-btn.active {{
                background: #cc0000 !important;
                box-shadow: 0 4px 12px rgba(204, 0, 0, 0.4) !important;
            }}
            
            .annotation-btn:hover {{
                background: #ff6666 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(255, 68, 68, 0.4) !important;
            }}
            
            /* 제출완료 버튼 */
            .db-save-btn {{
                top: 80px !important;
                background: #2196F3 !important;
            }}
            
            .db-save-btn:hover {{
                background: #1976D2 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4) !important;
            }}
            
            .db-save-btn:disabled {{
                background: #ccc !important;
                cursor: not-allowed !important;
                transform: none !important;
                box-shadow: 0 3px 8px rgba(0,0,0,0.15) !important;
            }}
            
            /* 모바일 반응형 - 태블릿 크기 */
            @media (max-width: 768px) {{
                .annotation-btn, .db-save-btn {{
                    right: 12px !important;
                    padding: 8px 12px !important;
                    font-size: 12px !important;
                    min-width: 92px !important;
                }}
                
                .annotation-btn {{ top: 12px !important; }}
                
                .db-save-btn {{ top: 50px !important; }}
                
                /* 치수 버튼: 제출완료 버튼 바로 아래 */
                .dimension-btn {{
                    position: fixed !important;
                    right: 12px !important;
                    top: 88px !important; /* 제출완료 버튼(50px) 바로 아래 */
                    padding: 8px 10px !important;
                    font-size: 12px !important;
                    min-width: 92px !important;
                    border-radius: 4px !important;
                }}
            }}
            
            /* 모바일 반응형 - 스마트폰 크기 */
            @media (max-width: 480px) {{
                .annotation-btn, .db-save-btn {{
                    right: 10px !important;
                    padding: 7px 10px !important;
                    font-size: 11px !important;
                    min-width: 86px !important;
                    border-radius: 4px !important;
                }}
                
                .annotation-btn {{ top: 10px !important; }}
                
                .db-save-btn {{ top: 48px !important; }}
                
                /* 치수 버튼: 제출완료 버튼 바로 아래 */
                .dimension-btn {{
                    position: fixed !important;
                    right: 10px !important;
                    top: 86px !important; /* 제출완료 버튼(48px) 바로 아래 */
                    padding: 7px 9px !important;
                    font-size: 11px !important;
                    min-width: 86px !important;
                    border-radius: 4px !important;
                }}
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
                border: 2px solid #ddd;
            }}
            
            .annotation-popup.show {{
                display: block;
            }}
            
            .popup-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 10px;
            }}
            
            .popup-text {{
                margin: 0;
                font-size: 14px;
                color: #333;
                flex: 1;
                margin-right: 10px;
                word-break: break-word;
            }}
            
            .popup-close-btn {{
                background: #ff4444;
                color: white;
                border: none;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                margin-left: 5px;
                position: relative;
                transition: all 0.2s ease;
                z-index: 10003;
                pointer-events: auto;
            }}
            
            .popup-close-btn:hover {{
                background: #cc0000;
                transform: scale(1.1);
            }}
            
            .popup-close-btn:active {{
                transform: scale(0.95);
            }}
            
            /* 터치 영역 확장 (가상 요소로) */
            .popup-close-btn::before {{
                content: '';
                position: absolute;
                top: -8px;
                left: -8px;
                right: -8px;
                bottom: -8px;
                border-radius: 50%;
                background: transparent;
            }}
            
            .popup-buttons {{
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }}
            
            .popup-btn {{
                padding: 8px 12px;
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
            
            /* 모바일에서 팝업 최적화 */
            @media (max-width: 768px) {{
                .annotation-popup {{
                    max-width: calc(100vw - 40px);
                    min-width: 250px;
                    padding: 15px;
                    border-radius: 12px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.4);
                }}
                
                .popup-header {{
                    margin-bottom: 12px;
                }}
                
                .popup-text {{
                    font-size: 16px;
                    line-height: 1.4;
                    margin-right: 8px;
                }}
                
                .popup-btn {{
                    padding: 12px 8px;
                    font-size: 16px;
                    font-weight: bold;
                    min-height: 44px;
                }}
                
                .popup-close-btn {{
                    width: 32px;
                    height: 32px;
                    font-size: 18px;
                    font-weight: bold;
                    margin-left: 8px;
                }}
                
                /* 모바일에서 터치 영역 더 크게 */
                .popup-close-btn::before {{
                    top: -12px;
                    left: -12px;
                    right: -12px;
                    bottom: -12px;
                }}
            }}
            
            /* 아주 작은 화면에서 팝업 추가 최적화 */
            @media (max-width: 480px) {{
                .annotation-popup {{
                    max-width: calc(100vw - 20px);
                    min-width: 200px;
                    padding: 12px;
                }}
                
                .popup-text {{
                    font-size: 15px;
                }}
                
                .popup-btn {{
                    font-size: 15px;
                    padding: 10px 6px;
                }}
                
                .popup-close-btn {{
                    width: 30px;
                    height: 30px;
                    font-size: 16px;
                }}
            }}
            

        </style>
    </head>
    <body style="background: {bg_color};">
        <!-- 상단 안내 텍스트 -->
        <div class="top-notice">
            수정점표시 → 3D표면 클릭 → 텍스트 입력 → 확인 → 제출완료 눌러주세요
        </div>
        
        <!-- 수정점 표시 버튼을 최상단에 배치 -->
        <button class="annotation-btn" id="annotationBtn" onclick="toggleAnnotationMode()">
            수정점표시
        </button>
        
        <!-- 제출완료 버튼 -->
        <button class="db-save-btn" id="dbSaveBtn" onclick="saveToDatabase()">
            제출완료
        </button>
        
        <!-- 치수 표시 버튼 (실제 높이가 설정된 경우에만 표시) -->
        {f'''<button class="dimension-btn" id="dimensionBtn" onclick="toggleDimensions()" style="position: fixed; top: 140px; right: 20px; z-index: 99999; padding: 10px 12px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; box-shadow: 0 2px 6px rgba(0,0,0,0.2); min-width: 110px; text-align: center; transition: all 0.2s ease;">
            📐 치수 OFF
        </button>
        <div id="dimensionInfo" style="position: fixed; top: 200px; right: 20px; z-index: 99999; min-width: 150px;"></div>''' if real_height and real_height > 0 else ''}
        
        <!-- 로딩 오버레이 -->
        <div id="loadingOverlay" style="background: {bg_color};">
            <div class="loading-container">
                <div class="simple-loader"></div>
                <div class="loading-text">로딩 중<span class="loading-dots"></span></div>
            </div>
        </div>
        
        <div id="container" style="background: {bg_color};">
            
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
            
            <!-- 퐁 쉐이딩 컨트롤 -->
            <div class="phong-control">
                <div class="phong-checkbox-wrapper" onclick="togglePhongShading(event)">
                    <input type="checkbox" id="phongCheckbox" onchange="applyPhongShading()">
                    <label for="phongCheckbox">입체감 증가</label>
                </div>
                <div class="phong-slider-container" id="phongSliderContainer">
                    <div class="phong-slider-label">
                        <span>조명 강도</span>
                        <span id="phongValue">50%</span>
                    </div>
                    <input type="range" class="phong-slider" id="phongSlider" 
                           min="10" max="100" value="50" 
                           oninput="updatePhongIntensity(this.value)">
                </div>
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
                <div class="popup-header">
                    <div class="popup-text" id="popupText"></div>
                    <button class="popup-close-btn" 
                            onclick="closeAnnotationPopup(); return false;" 
                            onmousedown="closeAnnotationPopup(); return false;"
                            ontouchstart="closeAnnotationPopup(); return false;"
                            title="팝업 닫기" 
                            aria-label="팝업 닫기">×</button>
                </div>
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
            
            // 터치 이벤트 처리용 변수들
            let touchStartTime = 0;
            let touchStartPos = null;
            let isTouchDevice = false;
            
            // Phong shading 관련 변수들
            let isPhongEnabled = false;
            let phongIntensity = 50; // 기본 강도 50%
            let lights = [];
            let basicLight = null; // 기본 조명 (항상 활성)
            let originalMaterials = new Map();
            let phongMaterials = new Map();
            
            // 치수선 관련 변수들
            let dimensionGroup = null;
            let isDimensionVisible = false;
            const realHeight = {real_height if real_height else 1.0};  // 실제 높이 (미터)
            let realDimensions = null;  // 계산된 실제 크기
            
            // 초기 annotations 데이터 로드
            const initialAnnotations = {json.dumps(annotations if annotations else [])};
            
            // Raycaster와 마우스 초기화
            function initInteraction() {{
                raycaster = new THREE.Raycaster();
                mouse = new THREE.Vector2();
                
                // 마우스 클릭 이벤트
                renderer.domElement.addEventListener('click', onMouseClick, false);
                renderer.domElement.addEventListener('mousemove', onMouseMove, false);
                
                // 모바일 터치 이벤트 추가
                renderer.domElement.addEventListener('touchstart', onTouchStart, false);
                renderer.domElement.addEventListener('touchend', onTouchEnd, false);
                
                // 기존 annotations 로드
                loadExistingAnnotations();
            }}
            
            // 기존 수정점 로드
            function loadExistingAnnotations() {{
                // 서버에서 전달된 annotations 로드
                if (initialAnnotations && initialAnnotations.length > 0) {{
                    initialAnnotations.forEach(ann => {{
                        const geometry = new THREE.SphereGeometry(0.05, 16, 16);
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
                
                // 초기 상태 설정
                hasChanges = false;
                changedAnnotations = [];
                
                // 제출완료 버튼 초기 상태 설정
                updateDbSaveButton();
            }}
            
            // 마우스 클릭 처리
            function onMouseClick(event) {{
                if (!model) return;
                
                // 마우스 좌표 계산
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                
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
            
            // 터치 시작 처리
            function onTouchStart(event) {{
                if (!model) return;
                
                event.preventDefault();
                touchStartTime = Date.now();
                isTouchDevice = true;
                
                const touch = event.touches[0];
                const rect = renderer.domElement.getBoundingClientRect();
                touchStartPos = {{
                    x: touch.clientX - rect.left,
                    y: touch.clientY - rect.top
                }};
            }}
            
            // 터치 종료 처리 (탭으로 간주되면 클릭 이벤트 발생)
            function onTouchEnd(event) {{
                if (!model || !touchStartPos) return;
                
                event.preventDefault();
                const touchEndTime = Date.now();
                const touchDuration = touchEndTime - touchStartTime;
                
                // 짧은 탭 (500ms 이하)이고 이동거리가 작으면 클릭으로 간주
                if (touchDuration < 500) {{
                    const touch = event.changedTouches[0];
                    const rect = renderer.domElement.getBoundingClientRect();
                    const touchEndPos = {{
                        x: touch.clientX - rect.left,
                        y: touch.clientY - rect.top
                    }};
                    
                    const distance = Math.sqrt(
                        Math.pow(touchEndPos.x - touchStartPos.x, 2) + 
                        Math.pow(touchEndPos.y - touchStartPos.y, 2)
                    );
                    
                    // 이동거리가 10px 이하면 탭으로 간주
                    if (distance < 10) {{
                        // 클릭 이벤트를 시뮬레이션
                        const fakeEvent = {{
                            clientX: touch.clientX,
                            clientY: touch.clientY,
                            target: event.target
                        }};
                        onMouseClick(fakeEvent);
                    }}
                }}
                
                touchStartPos = null;
            }}
            
            // 수정점 표시 모드 토글 (1회 제한)
            function toggleAnnotationMode() {{
                isAnnotationMode = !isAnnotationMode;
                const btn = document.getElementById('annotationBtn');
                if (isAnnotationMode) {{
                    btn.classList.add('active');
                    btn.textContent = '수정점표시 ON';
                    console.log('수정점 표시 모드 활성화');
                }} else {{
                    btn.classList.remove('active');
                    btn.textContent = '수정점표시';
                    console.log('수정점 표시 모드 비활성화');
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
            
            // 수정점 확인 (1회 제한 적용)
            function confirmAnnotation() {{
                const text = document.getElementById('annotationInput').value.trim();
                if (text && currentAnnotation) {{
                    // 서버에 저장
                    saveAnnotationToServer(currentAnnotation.point, text);
                    closeAnnotationModal();
                    
                    // 수정점 추가 후 자동으로 모드 해제
                    isAnnotationMode = false;
                    const btn = document.getElementById('annotationBtn');
                    btn.classList.remove('active');
                    btn.textContent = '수정점표시';
                    
                    console.log('수정점 추가 완료 - 모드 자동 해제');
                    showMessage('✅ 수정점이 추가되었습니다. 다시 표시하려면 "수정점표시" 버튼을 눌러주세요.', 'success');
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
            
            // 수정사항이 있는지 추적하는 변수
            let hasChanges = false;
            
            // 변경된 기존 수정점들을 추적
            let changedAnnotations = [];
            
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
                    
                    // 변경사항 표시
                    hasChanges = true;
                    
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
                    const newCount = pendingAnnotations.length;
                    const changeCount = changedAnnotations.length;
                    const totalChanges = newCount + changeCount;
                    
                    if (totalChanges > 0 || hasChanges) {{
                        let buttonText = '제출완료';
                        if (newCount > 0 && changeCount > 0) {{
                            buttonText = `제출완료 (신규 ${{newCount}}, 변경 ${{changeCount}})`;
                        }} else if (newCount > 0) {{
                            buttonText = `제출완료 (신규 ${{newCount}})`;
                        }} else if (changeCount > 0) {{
                            buttonText = `제출완료 (변경 ${{changeCount}})`;
                        }} else {{
                            buttonText = '제출완료 (변경사항 있음)';
                        }}
                        btn.textContent = buttonText;
                        btn.disabled = false;
                    }} else {{
                        btn.textContent = '제출완료';
                        btn.disabled = true;
                    }}
                }}
            }}
            
            // DB에 모든 수정점 저장
            function saveToDatabase() {{
                if (!modelToken) {{
                    showMessage('모델 토큰이 없습니다', 'error');
                    return;
                }}
                
                // 새 수정점이 있거나 기존 수정점에 변경사항이 있는지 확인
                if (pendingAnnotations.length === 0 && !hasChanges) {{
                    showMessage('저장할 수정점이 없습니다', 'info');
                    return;
                }}
                
                // 제출할 데이터 구성
                const dataToSave = {{
                    model_token: modelToken,
                    annotations: pendingAnnotations,
                    changes: changedAnnotations
                }};
                
                // 저장할 내용이 있는지 확인
                if (pendingAnnotations.length > 0 || changedAnnotations.length > 0) {{
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
                    const newCount = pendingAnnotations.length;
                    const changeCount = changedAnnotations.length;
                    let message = '💾 제출 중...';
                    if (newCount > 0 && changeCount > 0) {{
                        message = `💾 새 수정점 ${{newCount}}개, 변경사항 ${{changeCount}}개 제출 중...`;
                    }} else if (newCount > 0) {{
                        message = `💾 새 수정점 ${{newCount}}개 제출 중...`;
                    }} else if (changeCount > 0) {{
                        message = `💾 변경사항 ${{changeCount}}개 제출 중...`;
                    }}
                    showMessage(message, 'info');
                    
                    // 변경사항 초기화
                    hasChanges = false;
                    pendingAnnotations = [];
                    changedAnnotations = [];
                    
                    // 페이지 리로드하여 서버에 저장
                    setTimeout(() => {{
                        window.location.href = window.location.pathname + '?' + params.toString();
                    }}, 1000);
                }} else {{
                    // 단순 새로고침 (hasChanges만 있는 경우)
                    showMessage('💾 변경사항 저장 중...', 'info');
                    hasChanges = false;
                    
                    // 현재 token만 유지하고 새로고침
                    const currentUrl = new URL(window.location.href);
                    const currentParams = new URLSearchParams(currentUrl.search);
                    const token = currentParams.get('token') || modelToken;
                    
                    setTimeout(() => {{
                        window.location.href = window.location.pathname + '?token=' + token;
                    }}, 1000);
                }}
            }}
            
            // 메시지 표시 함수 (개선된 버전)
            function showMessage(text, type) {{
                const message = document.createElement('div');
                message.style.cssText = `
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: ${{type === 'success' ? '#4CAF50' : type === 'info' ? '#2196F3' : '#f44336'}};
                    color: white;
                    padding: 20px 30px;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: bold;
                    z-index: 100000;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    max-width: 80vw;
                    text-align: center;
                    line-height: 1.4;
                    animation: fadeInOut 0.3s ease-in;
                `;
                message.textContent = text;
                document.body.appendChild(message);
                
                // 긴 메시지의 경우 더 오래 표시
                const displayTime = text.length > 50 ? 4000 : 3000;
                
                setTimeout(() => {{
                    message.style.opacity = '0';
                    message.style.transition = 'opacity 0.3s ease-out';
                    setTimeout(() => {{
                        if (message.parentNode) {{
                            message.remove();
                        }}
                    }}, 300);
                }}, displayTime);
            }}
            
            // 수정점 생성
            function createAnnotation(point, text, id) {{
                const geometry = new THREE.SphereGeometry(0.05, 16, 16);
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
            
            // 안전한 팝업 위치 계산
            function calculateSafePopupPosition(event, popup) {{
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;
                const popupRect = popup.getBoundingClientRect();
                const popupWidth = popup.offsetWidth || 300; // 기본값 사용
                const popupHeight = popup.offsetHeight || 150; // 기본값 사용
                
                let x = event.clientX + 10;
                let y = event.clientY + 10;
                
                // 오른쪽 경계 확인
                if (x + popupWidth > viewportWidth - 20) {{
                    x = event.clientX - popupWidth - 10;
                    // 왼쪽으로도 안 들어가면 중앙 정렬
                    if (x < 20) {{
                        x = (viewportWidth - popupWidth) / 2;
                    }}
                }}
                
                // 하단 경계 확인
                if (y + popupHeight > viewportHeight - 20) {{
                    y = event.clientY - popupHeight - 10;
                    // 위로도 안 들어가면 중앙 정렬
                    if (y < 20) {{
                        y = (viewportHeight - popupHeight) / 2;
                    }}
                }}
                
                // 최소 여백 보장
                x = Math.max(10, Math.min(x, viewportWidth - popupWidth - 10));
                y = Math.max(10, Math.min(y, viewportHeight - popupHeight - 10));
                
                return {{ x, y }};
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
                
                // 팝업을 일시적으로 표시하여 크기 계산
                popup.style.visibility = 'hidden';
                popup.style.display = 'block';
                
                // 안전한 위치 계산
                const position = calculateSafePopupPosition(event, popup);
                
                // 위치 설정 및 표시
                popup.style.left = position.x + 'px';
                popup.style.top = position.y + 'px';
                popup.style.visibility = 'visible';
                popup.style.display = 'block';
                popup.classList.add('show');
                
                // X 버튼에 추가 이벤트 리스너 등록
                const closeBtn = popup.querySelector('.popup-close-btn');
                if (closeBtn) {{
                    closeBtn.addEventListener('click', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('X 버튼 클릭됨 (이벤트 리스너)');
                        closeAnnotationPopup();
                    }}, {{ once: true }});
                    
                    closeBtn.addEventListener('touchend', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('X 버튼 터치됨 (이벤트 리스너)');
                        closeAnnotationPopup();
                    }}, {{ once: true }});
                }}
                

                
                // 클릭 외부 영역 클릭 시 팝업 닫기
                setTimeout(() => {{
                    document.addEventListener('click', hidePopupOnClickOutside);
                }}, 100);
                
                // ESC 키로 팝업 닫기
                const escKeyHandler = function(e) {{
                    if (e.key === 'Escape') {{
                        closeAnnotationPopup();
                        document.removeEventListener('keydown', escKeyHandler);
                    }}
                }};
                document.addEventListener('keydown', escKeyHandler);
            }}
            
            // 팝업 외부 클릭 시 숨기기
            function hidePopupOnClickOutside(event) {{
                const popup = document.getElementById('annotationPopup');
                if (!popup.contains(event.target)) {{
                    popup.classList.remove('show');
                    document.removeEventListener('click', hidePopupOnClickOutside);
                }}
            }}
            
            // 수정점 팝업 닫기 함수
            function closeAnnotationPopup() {{
                console.log('closeAnnotationPopup 호출됨'); // 디버그 로그
                
                const popup = document.getElementById('annotationPopup');
                if (popup) {{
                    popup.classList.remove('show');
                    popup.style.display = 'none'; // 강제로 숨기기
                    

                    
                    document.removeEventListener('click', hidePopupOnClickOutside);
                    
                    // ESC 키 이벤트도 제거
                    document.removeEventListener('keydown', function() {{}});
                    
                    console.log('팝업 닫기 완료'); // 디버그 로그
                }} else {{
                    console.error('팝업 요소를 찾을 수 없습니다');
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
                    }} else {{
                        // 기존 DB 수정점의 변경사항 추적
                        if (!String(id).startsWith('temp_')) {{
                            const existingChange = changedAnnotations.find(c => c.id === id);
                            if (existingChange) {{
                                existingChange.action = 'complete';
                            }} else {{
                                changedAnnotations.push({{
                                    id: id,
                                    action: 'complete'
                                }});
                            }}
                        }}
                        hasChanges = true;
                    }}
                    
                    // 제출완료 버튼 상태 업데이트
                    updateDbSaveButton();
                    
                    showMessage('✅ 수정 완료로 표시되었습니다', 'success');
                }}
                closeAnnotationPopup();
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
                    }} else {{
                        // 기존 DB 수정점의 변경사항 추적
                        if (!String(id).startsWith('temp_')) {{
                            const existingChange = changedAnnotations.find(c => c.id === id);
                            if (existingChange) {{
                                existingChange.action = 'delete';
                            }} else {{
                                changedAnnotations.push({{
                                    id: id,
                                    action: 'delete'
                                }});
                            }}
                        }}
                        hasChanges = true;
                    }}
                    
                    // 제출완료 버튼 상태 업데이트
                    updateDbSaveButton();
                    
                    showMessage('✅ 수정점이 삭제되었습니다', 'success');
                }}
                closeAnnotationPopup();
            }}
            
            // 모든 수정점 제거 (모델 삭제 시 호출용)
            function clearAllAnnotations() {{
                annotations.forEach(annotation => {{
                    scene.remove(annotation.mesh);
                }});
                annotations = [];
            }}
            
            // 조명 설정 함수
            function setupLights() {{
                // Ambient Light - 전체적인 밝기 (Phong shading용) - 적절한 밝기
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.6); // 적절한 밝기로 조정
                ambientLight.visible = false; // 초기에는 비활성화
                scene.add(ambientLight);
                lights.push(ambientLight);
                
                // Directional Light - 메인 광원 (적절한 강도)
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.25); // 적절한 강도로 조정
                directionalLight.position.set(5, 10, 5);
                directionalLight.visible = false; // 초기에는 비활성화
                scene.add(directionalLight);
                lights.push(directionalLight);
                
                // Point Light - 보조 광원 (적절한 강도)
                const pointLight = new THREE.PointLight(0xffffff, 0.15); // 적절한 강도로 조정
                pointLight.position.set(-5, 5, 10);
                pointLight.visible = false; // 초기에는 비활성화
                scene.add(pointLight);
                lights.push(pointLight);
                
                console.log('Lights setup complete (initially disabled)');
            }}
            
            // Phong shading 토글 함수
            // 실제 크기 계산 함수
            function calculateRealDimensions(object) {{
                if (!object) return null;
                
                const box = new THREE.Box3().setFromObject(object);
                const modelSize = box.getSize(new THREE.Vector3());
                
                // 높이 기준 스케일 팩터 계산
                const scaleFactor = realHeight / modelSize.y;
                
                // 실제 크기 계산 (미터 단위)
                const dimensions = {{
                    width: modelSize.x * scaleFactor,
                    height: realHeight,
                    depth: modelSize.z * scaleFactor
                }};
                
                // 표시용 포맷팅 (1m 이상은 m, 미만은 cm)
                const formatDimension = (meters) => {{
                    if (meters >= 1.0) {{
                        return `${{meters.toFixed(1)}}m`;
                    }} else {{
                        return `${{(meters * 100).toFixed(0)}}cm`;
                    }}
                }};
                
                return {{
                    raw: dimensions,
                    formatted: {{
                        width: formatDimension(dimensions.width),
                        height: formatDimension(dimensions.height),
                        depth: formatDimension(dimensions.depth)
                    }}
                }};
            }}
            
            // 치수선 생성 함수
            function createDimensionLine(start, end, label, color = 0x0000ff) {{
                const group = new THREE.Group();
                
                // 메인 라인
                const lineGeometry = new THREE.BufferGeometry().setFromPoints([start, end]);
                const lineMaterial = new THREE.LineBasicMaterial({{ color: color, linewidth: 2 }});
                const line = new THREE.Line(lineGeometry, lineMaterial);
                group.add(line);
                
                // 화살표 (양끝)
                const arrowLength = 0.05;
                const arrowGeometry = new THREE.ConeGeometry(0.02, arrowLength, 8);
                const arrowMaterial = new THREE.MeshBasicMaterial({{ color: color }});
                
                // 시작점 화살표
                const arrow1 = new THREE.Mesh(arrowGeometry, arrowMaterial);
                arrow1.position.copy(start);
                const dir1 = new THREE.Vector3().subVectors(end, start).normalize();
                arrow1.lookAt(start.clone().add(dir1));
                arrow1.rotateX(Math.PI / 2);
                group.add(arrow1);
                
                // 끝점 화살표
                const arrow2 = new THREE.Mesh(arrowGeometry, arrowMaterial);
                arrow2.position.copy(end);
                const dir2 = new THREE.Vector3().subVectors(start, end).normalize();
                arrow2.lookAt(end.clone().add(dir2));
                arrow2.rotateX(Math.PI / 2);
                group.add(arrow2);
                
                // 텍스트 라벨 (Sprite)
                const canvas = document.createElement('canvas');
                canvas.width = 256;
                canvas.height = 128;
                const context = canvas.getContext('2d');
                // 배경을 투명하게 설정
                context.clearRect(0, 0, 256, 128);
                context.font = 'Bold 48px Arial';
                context.textAlign = 'center';
                
                // 흰색 테두리 그리기 (strokeText를 여러 번 그려서 굵게)
                context.strokeStyle = 'rgba(255, 255, 255, 1.0)';
                context.lineWidth = 8;
                context.strokeText(label, 128, 75);
                context.lineWidth = 6;
                context.strokeText(label, 128, 75);
                
                // 파란색 텍스트 채우기
                context.fillStyle = 'rgba(0, 0, 255, 1.0)';
                context.fillText(label, 128, 75);
                
                const texture = new THREE.CanvasTexture(canvas);
                const spriteMaterial = new THREE.SpriteMaterial({{ 
                    map: texture,
                    depthTest: false,
                    depthWrite: false
                }});
                const sprite = new THREE.Sprite(spriteMaterial);
                
                const midPoint = new THREE.Vector3().lerpVectors(start, end, 0.5);
                sprite.position.copy(midPoint);
                sprite.scale.set(0.5, 0.25, 1);
                group.add(sprite);
                
                return group;
            }}
            
            // 모델에 치수선 추가
            function addDimensionLines(object) {{
                if (!object || dimensionGroup) return;
                
                const box = new THREE.Box3().setFromObject(object);
                const size = box.getSize(new THREE.Vector3());
                const center = box.getCenter(new THREE.Vector3());
                
                // 실제 크기 계산
                realDimensions = calculateRealDimensions(object);
                if (!realDimensions) return;
                
                dimensionGroup = new THREE.Group();
                dimensionGroup.name = 'dimensions';
                
                const offset = Math.max(size.x, size.y, size.z) * 0.15;  // 모델 크기의 15% 오프셋
                
                // X축 치수선 (너비) - 모델 아래쪽에 배치
                const xStart = new THREE.Vector3(box.min.x, box.min.y - offset, center.z);
                const xEnd = new THREE.Vector3(box.max.x, box.min.y - offset, center.z);
                const xLine = createDimensionLine(xStart, xEnd, realDimensions.formatted.width, 0xff0000);
                dimensionGroup.add(xLine);
                
                // Y축 치수선 (높이) - 모델 왼쪽에 배치
                const yStart = new THREE.Vector3(box.min.x - offset, box.min.y, center.z);
                const yEnd = new THREE.Vector3(box.min.x - offset, box.max.y, center.z);
                const yLine = createDimensionLine(yStart, yEnd, realDimensions.formatted.height, 0x00ff00);
                dimensionGroup.add(yLine);
                
                // Z축 치수선 (깊이) - 모델 오른쪽 바닥에 배치
                const zStart = new THREE.Vector3(box.max.x + offset, box.min.y - offset, box.min.z);
                const zEnd = new THREE.Vector3(box.max.x + offset, box.min.y - offset, box.max.z);
                const zLine = createDimensionLine(zStart, zEnd, realDimensions.formatted.depth, 0x0000ff);
                dimensionGroup.add(zLine);
                
                scene.add(dimensionGroup);
                dimensionGroup.visible = false;  // 초기에는 숨김
                
                // 크기 정보 UI 업데이트
                updateDimensionInfo();
            }}
            
            // 치수 표시 토글
            function toggleDimensions() {{
                if (!dimensionGroup) return;
                
                isDimensionVisible = !isDimensionVisible;
                dimensionGroup.visible = isDimensionVisible;
                
                const btn = document.getElementById('dimensionBtn');
                if (btn) {{
                    if (isDimensionVisible) {{
                        btn.classList.add('active');
                        btn.textContent = '📐 치수 ON';
                    }} else {{
                        btn.classList.remove('active');
                        btn.textContent = '📐 치수 OFF';
                    }}
                }}
                
                // render() 함수가 정의되지 않았으므로 제거
                // animate() 루프가 자동으로 렌더링 처리
            }}
            
            // 치수 정보 UI 업데이트
            function updateDimensionInfo() {{
                if (!realDimensions) return;
                
                const infoEl = document.getElementById('dimensionInfo');
                if (infoEl) {{
                    infoEl.innerHTML = `
                        <div style="padding: 5px; background: rgba(255,255,255,0.9); border-radius: 5px;">
                            <strong>실제 크기:</strong><br>
                            너비: ${{realDimensions.formatted.width}}<br>
                            높이: ${{realDimensions.formatted.height}}<br>
                            깊이: ${{realDimensions.formatted.depth}}
                        </div>
                    `;
                }}
            }}
            
            function togglePhongShading(event) {{
                if (event && event.target.type === 'checkbox') {{
                    return; // 체크박스 직접 클릭은 무시
                }}
                
                const checkbox = document.getElementById('phongCheckbox');
                checkbox.checked = !checkbox.checked;
                applyPhongShading();
            }}
            
            // 조명 강도 업데이트 함수
            function updatePhongIntensity(value) {{
                phongIntensity = parseInt(value);
                document.getElementById('phongValue').textContent = phongIntensity + '%';
                
                if (isPhongEnabled) {{
                    // 조명 강도 실시간 업데이트
                    const intensity = phongIntensity / 100;
                    
                    lights.forEach((light, index) => {{
                        if (light.type === 'AmbientLight') {{
                            light.intensity = 0.3 + (0.7 * intensity); // 0.3 ~ 1.0
                        }} else if (light.type === 'DirectionalLight') {{
                            light.intensity = 0.1 + (0.4 * intensity); // 0.1 ~ 0.5
                        }} else if (light.type === 'PointLight') {{
                            light.intensity = 0.05 + (0.25 * intensity); // 0.05 ~ 0.3
                        }}
                    }});
                }}
            }}
            
            // Phong shading 적용/해제 함수
            function applyPhongShading() {{
                try {{
                    const checkbox = document.getElementById('phongCheckbox');
                    isPhongEnabled = checkbox.checked;
                    
                    console.log('Phong shading:', isPhongEnabled ? 'enabled' : 'disabled');
                    
                    // 슬라이더 컨테이너 표시/숨김
                    const sliderContainer = document.getElementById('phongSliderContainer');
                    if (sliderContainer) {{
                        if (isPhongEnabled) {{
                            sliderContainer.classList.add('active');
                            // 초기 강도 적용
                            updatePhongIntensity(phongIntensity);
                        }} else {{
                            sliderContainer.classList.remove('active');
                        }}
                    }}
                    
                    // 조명 활성화/비활성화
                    lights.forEach(light => {{
                        light.visible = isPhongEnabled;
                    }});
                    
                    if (model) {{
                        model.traverse((child) => {{
                            if (child.isMesh && child.material) {{
                                if (isPhongEnabled) {{
                                    // 이미 PhongMaterial인 경우는 조명 설정만 조정
                                    if (child.material.type === 'MeshPhongMaterial' || 
                                        (Array.isArray(child.material) && child.material[0]?.type === 'MeshPhongMaterial')) {{
                                        console.log('Already PhongMaterial, adjusting properties:', child.name || 'unnamed');
                                        
                                        // PhongMaterial은 이미 적용되어 있으므로 추가 조정 불필요
                                        console.log('Already PhongMaterial, no adjustments needed');
                                        return;
                                    }}
                                    
                                    // Phong Material 적용
                                    if (!phongMaterials.has(child)) {{
                                        // 기존 material 저장
                                        originalMaterials.set(child, child.material);
                                        
                                        // Material이 배열인 경우 처리 (멀티 텍스처)
                                        if (Array.isArray(child.material)) {{
                                            const phongMats = [];
                                            child.material.forEach((mat, idx) => {{
                                                // 각 material에 대해 개별적으로 처리
                                                let materialColor = new THREE.Color(0xffffff);
                                                if (mat.color) {{
                                                    materialColor = mat.color.clone();
                                                }} else if (!mat.map) {{
                                                    materialColor = new THREE.Color(0xcccccc);
                                                }}
                                                
                                                const phongMat = new THREE.MeshPhongMaterial({{
                                                    map: mat.map || null,
                                                    color: materialColor,
                                                    side: THREE.DoubleSide,
                                                    transparent: mat.transparent || false,
                                                    opacity: mat.opacity !== undefined ? mat.opacity : 1,
                                                    shininess: 30, // 기본 광택
                                                    specular: new THREE.Color(0x111111), // 약간의 반사광
                                                    vertexColors: mat.vertexColors || false,
                                                    flatShading: false // Smooth shading
                                                }});
                                                
                                                // 텍스처 설정 - 원본과 동일한 인코딩 유지
                                                if (phongMat.map) {{
                                                    phongMat.map.encoding = THREE.LinearEncoding; // Linear 유지
                                                    phongMat.map.minFilter = THREE.LinearMipmapLinearFilter;
                                                    phongMat.map.magFilter = THREE.LinearFilter;
                                                    phongMat.map.generateMipmaps = true;
                                                    phongMat.map.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
                                                    phongMat.map.wrapS = THREE.ClampToEdgeWrapping;
                                                    phongMat.map.wrapT = THREE.ClampToEdgeWrapping;
                                                }}
                                                
                                                phongMats.push(phongMat);
                                                console.log(`✅ Phong material [${{idx}}] created for multi-texture mesh`);
                                            }});
                                            phongMaterials.set(child, phongMats);
                                        }} else {{
                                            // 단일 material 처리
                                            // Geometry 스무스 처리 - Normal을 삭제하지 말고 유지
                                            if (child.geometry) {{
                                                // 기존 normal이 없는 경우에만 생성
                                                if (!child.geometry.attributes.normal) {{
                                                    child.geometry.computeVertexNormals();
                                                    console.log('Computed vertex normals for:', child.name || 'unnamed mesh');
                                                }} else {{
                                                    // 기존 normal이 있으면 그대로 사용
                                                    console.log('Using existing normals for:', child.name || 'unnamed mesh');
                                                }}
                                            }}
                                            
                                            // 5번 수정: 디버깅 로그 추가
                                            console.log('🔍 Phong Shading Debug - Original material:', {{
                                                meshName: child.name || 'unnamed',
                                                materialType: child.material.type,
                                                hasMap: !!child.material.map,
                                                mapName: child.material.map ? child.material.map.name : 'none',
                                                color: child.material.color ? child.material.color.getHexString() : 'none',
                                                side: child.material.side,
                                                transparent: child.material.transparent,
                                                opacity: child.material.opacity,
                                                vertexColors: child.material.vertexColors,
                                                geometryHasNormals: child.geometry ? !!child.geometry.attributes.normal : false,
                                                geometryHasUV: child.geometry ? !!child.geometry.attributes.uv : false,
                                                geometryHasColors: child.geometry ? !!child.geometry.attributes.color : false
                                            }});
                                            
                                            // 색상 결정 로직 개선
                                            let materialColor = new THREE.Color(0xffffff); // 기본 흰색
                                            if (child.material.color) {{
                                                materialColor = child.material.color.clone();
                                            }} else if (!child.material.map) {{
                                                // 텍스처도 없고 색상도 없으면 밝은 회색 사용
                                                materialColor = new THREE.Color(0xcccccc);
                                            }}
                                            
                                            // Phong material 생성 (무광 효과)
                                            const phongMat = new THREE.MeshPhongMaterial({{
                                                map: child.material.map || null,
                                                color: materialColor,
                                                side: THREE.DoubleSide,
                                                transparent: child.material.transparent || false,
                                                opacity: child.material.opacity !== undefined ? child.material.opacity : 1,
                                                shininess: 30, // 기본 광택
                                                specular: new THREE.Color(0x111111), // 약간의 반사광
                                                vertexColors: child.material.vertexColors || false,
                                                flatShading: false // Smooth shading
                                            }});
                                            
                                            // 텍스처 설정 - 원본과 동일한 인코딩 유지
                                            if (phongMat.map) {{
                                                phongMat.map.encoding = THREE.LinearEncoding; // Linear 유지
                                                phongMat.map.minFilter = THREE.LinearMipmapLinearFilter;
                                                phongMat.map.magFilter = THREE.LinearFilter;
                                                phongMat.map.generateMipmaps = true;
                                                phongMat.map.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
                                                phongMat.map.wrapS = THREE.ClampToEdgeWrapping;
                                                phongMat.map.wrapT = THREE.ClampToEdgeWrapping;
                                            }}
                                            
                                            phongMaterials.set(child, phongMat);
                                            
                                            // 5번 추가: Phong material 생성 로그
                                            console.log('✅ Phong material created:', {{
                                                meshName: child.name || 'unnamed',
                                                materialColor: phongMat.color.getHexString(),
                                                hasTexture: !!phongMat.map,
                                                emissive: phongMat.emissive.getHexString(),
                                                side: phongMat.side === THREE.DoubleSide ? 'DoubleSide' : 'Other'
                                            }});
                                        }}
                                    }}
                                    
                                    // Material 교체 전 추가 처리
                                    const phongMaterial = phongMaterials.get(child);
                                    if (phongMaterial) {{
                                        // Material 교체
                                        child.material = phongMaterial;
                                        
                                        // Geometry와 Material 업데이트 플래그 설정
                                        if (child.geometry) {{
                                            child.geometry.computeBoundingSphere();
                                            child.geometry.computeBoundingBox();
                                            
                                            // Normal 속성 업데이트 확인
                                            if (child.geometry.attributes.normal) {{
                                                child.geometry.attributes.normal.needsUpdate = true;
                                            }}
                                        }}
                                        
                                        // Material 업데이트
                                        if (Array.isArray(child.material)) {{
                                            child.material.forEach(mat => {{
                                                mat.needsUpdate = true;
                                            }});
                                        }} else {{
                                            child.material.needsUpdate = true;
                                        }}
                                        
                                        // Mesh 업데이트
                                        child.updateMatrix();
                                        child.updateMatrixWorld(true);
                                    }}
                                }} else {{
                                    // 원본 BasicMaterial 복원
                                    if (originalMaterials.has(child)) {{
                                        // Material 교체 전 geometry 업데이트
                                        if (child.geometry) {{
                                            child.geometry.computeBoundingSphere();
                                            child.geometry.computeBoundingBox();
                                        }}
                                        
                                        const originalMat = originalMaterials.get(child);
                                        child.material = originalMat;
                                        
                                        // 원본 material의 텍스처 인코딩 복원
                                        if (child.material.map) {{
                                            child.material.map.encoding = THREE.LinearEncoding;
                                            child.material.map.needsUpdate = true;
                                        }}
                                        
                                        child.material.needsUpdate = true; // material 변경 시에만 업데이트
                                        
                                        // Mesh matrix 업데이트
                                        child.updateMatrix();
                                        child.updateMatrixWorld(true);
                                    }}
                                }}
                            }}
                        }});
                        
                        // 즉시 렌더링
                        if (renderer && scene && camera) {{
                            renderer.render(scene, camera);
                        }}
                    }}
                }} catch (error) {{
                    console.error('Phong shading 적용 중 오류:', error);
                    console.error('오류 스택:', error.stack);
                    
                    // 오류 발생 시 원본 material로 복원
                    if (model && originalMaterials.size > 0) {{
                        model.traverse((child) => {{
                            if (child.isMesh && originalMaterials.has(child)) {{
                                child.material = originalMaterials.get(child);
                                child.material.needsUpdate = true;
                            }}
                        }});
                    }}
                    
                    // 체크박스 상태 초기화
                    const checkbox = document.getElementById('phongCheckbox');
                    if (checkbox) {{
                        checkbox.checked = false;
                        isPhongEnabled = false;
                    }}
                    
                    // 조명 비활성화
                    lights.forEach(light => {{
                        light.visible = false;
                    }});
                    
                    alert('퐁 셰이딩 적용 중 문제가 발생했습니다. 원본 상태로 복원되었습니다.');
                }}
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
            function hideLoadingOverlay() {{
                const loadingOverlay = document.getElementById('loadingOverlay');
                if (loadingOverlay) {{
                    loadingOverlay.classList.add('fade-out');
                    setTimeout(() => {{
                        loadingOverlay.style.display = 'none';
                    }}, 500);
                }}
            }}
            
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
                    
                    // Scene 생성 (명시적 배경색 사용)
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x{bg_color[1:]});
                    
                    // Camera 생성 - 제품 전시용 FOV (45도)
                    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 0, 4);  // 5 -> 3.5로 했다가 너무 가까워서 4로 고침. 
                    
                    // Renderer 생성
                    const container = document.getElementById('container');
                    renderer = new THREE.WebGLRenderer({{ 
                        antialias: true,
                        powerPreference: "high-performance",
                        alpha: false,
                        premultipliedAlpha: false,
                        preserveDrawingBuffer: false,
                        stencil: false,
                        depth: true,
                        precision: "highp"
                    }});
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setPixelRatio(window.devicePixelRatio);
                    // 명시적 배경색으로 초기화
                    renderer.setClearColor(0x{bg_color[1:]}, 1);
                    if (renderer.setClearAlpha) {{ renderer.setClearAlpha(1); }}
                    
                    // Linear 색상 공간 사용 (텍스처 원본 색상 보존)
                    renderer.outputEncoding = THREE.LinearEncoding;
                    renderer.toneMapping = THREE.NoToneMapping;
                    renderer.shadowMap.enabled = false; // 그림자 비활성화
                    renderer.physicallyCorrectLights = false; // 물리 기반 조명 비활성화
                    
                    // 모든 플랫폼에서 초기에 캔버스 숨기기 (첫 유효 렌더 후 표시)
                    renderer.domElement.style.opacity = '0';
                    renderer.domElement.style.transition = 'opacity 0.3s';

                    container.appendChild(renderer.domElement);
                    // 초기 프레임 프라임 렌더로 버퍼 상태 확정
                    try {{
                        renderer.clear(true, true, true);
                        renderer.render(scene, camera);
                        requestAnimationFrame(() => renderer.render(scene, camera));
                    }} catch (e) {{ /* no-op */ }}
                    
                    // Controls 생성
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.08;
                    controls.enableZoom = true;
                    controls.enablePan = true;
                    controls.enableRotate = true;
                    controls.rotateSpeed = 0.5;
                    controls.zoomSpeed = 0.8;
                    controls.minDistance = 1.5;  // 약간 더 가까이 갈 수 있도록
                    controls.maxDistance = 5;   // 기본 최대 거리
                    // 모바일에서 더 멀리까지 줌 아웃 허용
                    if (isMobile) {{
                        controls.maxDistance = 20;
                    }}
                    
                    // 상호작용 초기화
                    initInteraction();
                    
                    // 조명 설정 (초기에는 비활성화)
                    setupLights();
                    
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
                    const loadingText = document.querySelector('.loading-text');
                    if (loadingText) {{
                        loadingText.textContent = '초기화 실패: ' + error.message;
                        loadingText.style.color = '#ff0000';
                    }}
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
                        invertTrProperty: false,
                        side: THREE.DoubleSide
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
                    
                    // 모든 재질 처리 - 항상 BasicMaterial로 강제 변환
                    for (let materialName in materials.materials) {{
                        const material = materials.materials[materialName];
                        
                        // 텍스처 참조 가져오기
                        const textureFileName = textureRefs[materialName];
                        
                        // 텍스처 찾기 (확장자 무시하고 파일명으로 매칭)
                        let matchedTexture = null;
                        let matchedTextureName = null;
                        
                        if (textureFileName) {{
                            // 정확한 이름으로 먼저 찾기
                            if (textures[textureFileName]) {{
                                matchedTexture = textures[textureFileName];
                                matchedTextureName = textureFileName;
                            }} else {{
                                // 확장자를 제거한 파일명으로 찾기
                                const baseFileName = textureFileName.replace(/\.[^/.]+$/, "");
                                // 공백과 특수문자를 제거한 정규화된 이름으로 비교
                                const normalizedBaseName = baseFileName.replace(/[\s_-]/g, '').toLowerCase();
                                
                                for (let texName in textures) {{
                                    const texBaseName = texName.replace(/\.[^/.]+$/, "");
                                    const normalizedTexBaseName = texBaseName.replace(/[\s_-]/g, '').toLowerCase();
                                    
                                    // 정규화된 이름으로 비교
                                    if (normalizedTexBaseName === normalizedBaseName || 
                                        texBaseName === baseFileName) {{
                                        matchedTexture = textures[texName];
                                        matchedTextureName = texName;
                                        console.log('Texture matched: ' + textureFileName + ' -> ' + texName);
                                        break;
                                    }}
                                }}
                                
                                // 여전히 못 찾았다면 부분 매칭 시도
                                if (!matchedTexture) {{
                                    for (let texName in textures) {{
                                        // 텍스처 파일명에 material 이름이 포함되어 있는지 확인
                                        const normalizedTexName = texName.replace(/[\s_-]/g, '').toLowerCase();
                                        const normalizedMaterialName = materialName.replace(/[\s_-]/g, '').toLowerCase();
                                        
                                        if (normalizedTexName.includes(normalizedMaterialName) || 
                                            normalizedMaterialName.includes('material')) {{
                                            matchedTexture = textures[texName];
                                            matchedTextureName = texName;
                                            console.log('Texture partially matched: ' + materialName + ' -> ' + texName);
                                            break;
                                        }}
                                    }}
                                }}
                                
                                // 마지막으로 텍스처가 하나뿐이면 그것을 사용
                                if (!matchedTexture && Object.keys(textures).length === 1) {{
                                    const singleTexName = Object.keys(textures)[0];
                                    matchedTexture = textures[singleTexName];
                                    matchedTextureName = singleTexName;
                                    console.log('Single texture auto-matched: ' + materialName + ' -> ' + singleTexName);
                                }}
                            }}
                        }}
                        
                        // 무조건 MeshBasicMaterial로 변환 (Phong은 토글 시 적용)
                        if (matchedTexture) {{
                            // 기존 material 대신 새로운 BasicMaterial 생성
                            const basicMaterial = new THREE.MeshBasicMaterial({{
                                map: matchedTexture,
                                color: 0xffffff,  // 흰색으로 설정하여 텍스처 색상 100% 표현
                                side: THREE.DoubleSide,
                                transparent: false,
                                alphaTest: 0.01,
                                depthWrite: true,
                                depthTest: true
                            }});
                            
                            // 텍스처 설정 - Linear 인코딩으로 원본 색상 보존
                            basicMaterial.map.encoding = THREE.LinearEncoding;
                            basicMaterial.map.minFilter = THREE.LinearMipmapLinearFilter;
                            basicMaterial.map.magFilter = THREE.LinearFilter;
                            basicMaterial.map.generateMipmaps = true;
                            basicMaterial.map.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
                            basicMaterial.map.wrapS = THREE.ClampToEdgeWrapping;
                            basicMaterial.map.wrapT = THREE.ClampToEdgeWrapping;
                            basicMaterial.map.needsUpdate = true;
                            
                            // 기존 material을 basicMaterial로 교체
                            materials.materials[materialName] = basicMaterial;
                            
                            console.log('✅ BasicMaterial applied: ' + matchedTextureName);
                        }} else {{
                            // 텍스처가 없는 경우도 BasicMaterial로 변환
                            const basicMaterial = new THREE.MeshBasicMaterial({{
                                color: material.color || new THREE.Color(0xcccccc),
                                side: THREE.DoubleSide,
                                transparent: false,
                                alphaTest: 0.01,
                                depthWrite: true,
                                depthTest: true
                            }});
                            
                            // 기존 material을 basicMaterial로 교체
                            materials.materials[materialName] = basicMaterial;
                            
                            console.log('✅ BasicMaterial applied (no texture): ' + materialName);
                        }}
                    }}
                    
                    console.log('Materials loaded');
                    
                    // OBJ 로더
                    console.log('Loading OBJ...');
                    const objLoader = new THREE.OBJLoader();
                    objLoader.setMaterials(materials);
                    
                    const object = objLoader.parse(`{obj_content}`);
                    
                    // UV 좌표 조정 - 0.001~0.999 범위로 제한
                    object.traverse((child) => {{
                        if (child.isMesh && child.geometry) {{
                            const geometry = child.geometry;
                            if (geometry.attributes.uv) {{
                                const uvArray = geometry.attributes.uv.array;
                                
                                // 모든 UV 좌표를 0.001~0.999 범위로 제한
                                for (let i = 0; i < uvArray.length; i++) {{
                                    uvArray[i] = Math.max(0.001, Math.min(0.999, uvArray[i]));
                                }}
                                
                                geometry.attributes.uv.needsUpdate = true;
                            }}
                        }}
                    }});
                    
                    // AO 효과 비활성화 - 텍스처 색상 100% 보존
                    // Vertex colors 비활성화하여 텍스처 원본 색상 유지
                    object.traverse((child) => {{
                        if (child.isMesh && child.material) {{
                            // Vertex colors 완전히 비활성화
                            child.material.vertexColors = false;
                            child.material.needsUpdate = true;
                            
                            // Normal 벡터는 유지 (Phong shading 시 필요)
                            if (child.geometry && !child.geometry.attributes.normal) {{
                                child.geometry.computeVertexNormals();
                            }}
                            
                            console.log('Vertex colors disabled for pure texture color:', child.name || 'unnamed');
                        }}
                    }});
                    
                    // 모델 크기 조정 및 중앙 정렬
                    const box = new THREE.Box3().setFromObject(object);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const scale = 2.1 / maxDim;  // 2 -> 2.1로 모델을 더 크게
                    object.scale.set(scale, scale, scale);
                    
                    object.position.sub(center.multiplyScalar(scale));
                    
                    scene.add(object);
                    model = object;
                    
                    // 치수선 추가 (실제 높이가 설정된 경우)
                    if (realHeight && realHeight > 0) {{
                        addDimensionLines(object);
                        console.log('Dimension lines added with real height:', realHeight);
                    }}
                    
                    // 카메라 위치 조정 - 더 가까이 배치하여 UV 경계선 문제 완화
                    let distance = maxDim * scale * 1.8; // 기본 데스크톱 거리
                    if (isMobile) {{
                        // 모바일에서는 더 멀리 보기 (버튼 가림 및 근접 왜곡 완화)
                        const mobileFactor = isAndroid ? 2.3 : 2.1; // 이전보다 더 멀리 배치
                        distance = maxDim * scale * mobileFactor;
                    }}
                    camera.position.set(distance * 0.9, distance * 0.6, distance * 0.9); // 약간 더 정면에서 보기
                    
                    // 모바일에서 줌 아웃 한계 더 멀게 설정
                    if (isMobile && controls) {{
                        const desiredMax = Math.max(controls.maxDistance || 0, distance * 3.5);
                        controls.maxDistance = desiredMax;
                    }}
                    camera.lookAt(0, 0, 0);
                    
                    console.log('Model loaded successfully');
                    
                    // 모바일 GPU 워밍업 및 지연 표시
                    if (isMobile) {{
                        console.log('Mobile optimization: GPU warmup starting...');
                        
                        const warmupFrames = isAndroid ? 5 : 3;
                        for (let i = 0; i < warmupFrames; i++) {{
                            renderer.render(scene, camera);
                        }}
                        
                        const delay = isAndroid ? 300 : 200;
                        
                        setTimeout(() => {{
                            hideLoadingOverlay();
                            renderer.domElement.style.opacity = '1';
                            renderer.render(scene, camera);
                            animate();
                            console.log('Mobile optimization complete');
                        }}, delay);
                    }} else {{
                        setTimeout(() => {{
                            hideLoadingOverlay();
                            renderer.domElement.style.opacity = '1';
                            renderer.render(scene, camera);
                            animate();
                        }}, 120);
                    }}
                }} catch (error) {{
                    console.error('Model loading error:', error);
                    const loadingText = document.querySelector('.loading-text');
                    if (loadingText) {{
                        loadingText.textContent = '로딩 실패: ' + error.message;
                        loadingText.style.color = '#ff0000';
                    }}
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
                    if (renderer.setClearAlpha) {{ renderer.setClearAlpha(1); }}
                }}
                
                document.body.style.background = bodyColors[color];
                document.body.style.backgroundColor = bodyColors[color];
                
                const container = document.getElementById('container');
                if (container) {{
                    container.style.background = bodyColors[color];
                    container.style.backgroundColor = bodyColors[color];
                }}

                // 로딩 오버레이 배경도 동기화 (아직 표시 중인 경우)
                const overlay = document.getElementById('loadingOverlay');
                if (overlay) {{
                    overlay.style.background = bodyColors[color];
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
                
                // Linear 색상 공간 사용 (원본 색상 정확히 표현)
                tex_{safe_name}.encoding = THREE.LinearEncoding;
                tex_{safe_name}.flipY = true;
                
                // UV Seam 방지 + 색상 정확도
                tex_{safe_name}.generateMipmaps = true;
                tex_{safe_name}.minFilter = THREE.LinearMipmapLinearFilter;
                tex_{safe_name}.magFilter = THREE.LinearFilter;
                tex_{safe_name}.anisotropy = renderer.capabilities.getMaxAnisotropy();
                tex_{safe_name}.wrapS = THREE.ClampToEdgeWrapping;
                tex_{safe_name}.wrapT = THREE.ClampToEdgeWrapping;
                tex_{safe_name}.format = THREE.RGBAFormat; // RGBA 포맷 (알파 채널 포함)
                tex_{safe_name}.type = THREE.UnsignedByteType;
                tex_{safe_name}.needsUpdate = true;
                
                textures['{name}'] = tex_{safe_name};
                console.log('Texture loaded with original colors: {name}');
        """)
    
    return '\n'.join(code_lines)
