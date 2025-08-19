import streamlit as st
import importlib
import sys
from database import ModelDatabase, load_model_files, generate_share_url

# viewer_utils 모듈 강제 리로드
if 'viewer_utils' in sys.modules:
    importlib.reload(sys.modules['viewer_utils'])

def show_viewer_page(model_data):
    """공유 링크로 접근한 뷰어 페이지"""
    st.set_page_config(
        page_title=f"3D Model: {model_data['name']}",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # URL 파라미터 확인 및 annotation 처리
    query_params = st.query_params
    action = query_params.get("action", "")
    
    # share_token 가져오기
    share_token = model_data.get('share_token', None)
    
    if action and share_token:
        db = ModelDatabase()
        
        try:
            if action == "save_annotations":
                # 여러 수정점 일괄 저장
                import base64
                import json
                
                encoded_data = query_params.get("data", "")
                if encoded_data:
                    # Base64 디코딩
                    try:
                        decoded = base64.b64decode(encoded_data).decode('utf-8')
                        data = json.loads(decoded)
                        
                        if data.get('model_token') == share_token:
                            # 새 annotation 저장
                            saved_count = 0
                            for ann in data.get('annotations', []):
                                try:
                                    ann_id = db.add_annotation(
                                        share_token, 
                                        ann['position'], 
                                        ann['text']
                                    )
                                    saved_count += 1
                                    print(f"Annotation saved with ID: {ann_id}")  # 디버깅용
                                except Exception as e:
                                    print(f"Error saving annotation: {e}")
                                    st.error(f"수정점 저장 오류: {str(e)}")
                            
                            # 기존 annotation 변경사항 처리
                            changed_count = 0
                            for change in data.get('changes', []):
                                try:
                                    if change['action'] == 'complete':
                                        db.update_annotation_status(int(change['id']), True)
                                        changed_count += 1
                                        print(f"Annotation {change['id']} marked as completed")
                                    elif change['action'] == 'delete':
                                        db.delete_annotation(int(change['id']))
                                        changed_count += 1
                                        print(f"Annotation {change['id']} deleted")
                                except Exception as e:
                                    print(f"Error processing change for annotation {change['id']}: {e}")
                                    st.error(f"수정점 변경 오류: {str(e)}")
                            
                            # 결과 메시지
                            total_changes = saved_count + changed_count
                            if total_changes > 0:
                                message_parts = []
                                if saved_count > 0:
                                    message_parts.append(f"{saved_count}개의 새 수정점")
                                if changed_count > 0:
                                    message_parts.append(f"{changed_count}개의 변경사항")
                                st.success(f"✅ {', '.join(message_parts)}이 제출완료되었습니다!")
                            else:
                                st.warning("저장된 변경사항이 없습니다.")
                            
                            # 성공 후 token 파라미터만 유지하고 리다이렉트
                            import time
                            time.sleep(2)  # 성공 메시지를 보여주기 위한 딜레이
                            st.query_params.clear()
                            st.query_params["token"] = share_token
                            st.rerun()
                    except Exception as e:
                        st.error(f"데이터 디코딩 오류: {str(e)}")
                        import time
                        time.sleep(2)
                        st.query_params.clear()
                        st.query_params["token"] = share_token
                        st.rerun()
            
            elif action == "add_annotation":
                # 개별 수정점 추가 (기존 코드)
                x = float(query_params.get("x", "0"))
                y = float(query_params.get("y", "0"))
                z = float(query_params.get("z", "0"))
                
                # Base64로 인코딩된 텍스트 또는 일반 텍스트 처리
                text_b64 = query_params.get("text_b64", "")
                text = query_params.get("text", "")
                
                if text_b64:
                    # Base64 디코딩
                    import base64
                    try:
                        text = base64.b64decode(text_b64).decode('utf-8')
                    except:
                        text = text_b64  # 디코딩 실패 시 원본 사용
                
                if text:
                    db.add_annotation(share_token, {"x": x, "y": y, "z": z}, text)
                    # 파라미터 제거하고 리다이렉트
                    st.query_params.clear()
                    st.rerun()
            
            elif action == "complete_annotation":
                # 수정점 완료 처리
                annotation_id = query_params.get("annotation_id", "")
                if annotation_id:
                    db.update_annotation_status(int(annotation_id), True)
                    st.query_params.clear()
                    st.rerun()
            
            elif action == "delete_annotation":
                # 수정점 삭제
                annotation_id = query_params.get("annotation_id", "")
                if annotation_id:
                    db.delete_annotation(int(annotation_id))
                    st.query_params.clear()
                    st.rerun()
        except Exception as e:
            st.error(f"수정점 처리 중 오류: {str(e)}")
            st.query_params.clear()
    
    # Streamlit UI 완전히 숨기기
    hide_streamlit_style = """
    <style>
    /* Streamlit 기본 요소 숨기기 */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    div[data-testid="stHeader"] {display: none !important;}
    div[data-testid="stBottom"] {display: none !important;}
    .stActionButton {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* GitHub fork banner 및 Streamlit 로고 숨기기 */
    .github-corner {display: none !important;}
    a[href*="github"] {display: none !important;}
    a[href*="streamlit"] {display: none !important;}
    [data-testid="stSidebar"] {display: none !important;}
    
    /* 스트림릿 하단 로고/아이콘 숨기기 - 추가 선택자들 */
    [data-testid="stBottomBlockContainer"] {display: none !important;}
    [data-testid="stBottom"] {display: none !important;}
    .streamlit-footer {display: none !important;}
    .streamlit-badge {display: none !important;}
    
    /* 스트림릿 특정 CSS 클래스들 숨기기 */
    .st-emotion-cache-1ww3bz2 {display: none !important;}
    .st-emotion-cache-10trblm {display: none !important;}
    .st-emotion-cache-nahz7x {display: none !important;}
    .st-emotion-cache-1y0tadg {display: none !important;}
    
    /* 모든 footer 관련 요소 제거 */
    footer, .footer, [class*="footer"], [class*="Footer"] {display: none !important;}
    
    /* 깃허브/스트림릿 관련 모든 링크와 아이콘 제거 */
    a[href*="github"], a[href*="streamlit"], a[href*="share.streamlit.io"] {display: none !important;}
    img[alt*="GitHub"], img[alt*="Streamlit"], img[src*="github"], img[src*="streamlit"] {display: none !important;}
    
    /* 하단 고정 요소들 제거 */
    [style*="position: fixed"][style*="bottom"], 
    [style*="position: absolute"][style*="bottom"] {display: none !important;}
    
    /* 전체 앱 여백 제거 */
    .stApp {
        margin: 0 !important; 
        padding: 0 !important;
        top: 0 !important;
        background: transparent !important;
    }
    .stApp > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* 메인 컨테이너 여백 제거 */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: none !important;
        width: 100vw !important;
        height: 100vh !important;
    }
    
    /* iframe 전체 화면 */
    iframe {
        width: 100vw !important; 
        height: 100vh !important;
        border: none !important;
        overflow: hidden !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 9999 !important;
    }
    
    /* 전체 화면 body */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        width: 100% !important;
        height: 100% !important;
    }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    try:
        # URL 파라미터에서 배경색 가져오기 (기본값: white)
        query_params = st.query_params
        background_color = query_params.get("bg", "white")
        bg_map = {"white": "#ffffff", "gray": "#808080", "black": "#000000"}
        host_bg = bg_map.get(background_color, "#ffffff")
        # 호스트 페이지(스트림릿)의 배경 동기화
        st.markdown(
            f"""
            <style>
            .stApp {{ background: {host_bg} !important; }}
            html, body {{ background: {host_bg} !important; }}
            iframe {{ background: {host_bg} !important; }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        # 모델 파일 로드
        obj_content, mtl_content, texture_data = load_model_files(model_data)
        
        # 데이터베이스에서 annotations 로드 (share_token이 있는 경우에만)
        annotations = []
        share_token = model_data.get('share_token', None)
        if share_token:
            db = ModelDatabase()
            annotations = db.get_annotations(share_token)
        
        # 3D 뷰어 HTML 생성 (배경색, annotations 및 실제 높이 포함)
        from viewer_utils import create_3d_viewer_html
        real_height = model_data.get('real_height', 1.0)  # 데이터베이스에서 실제 높이 가져오기
        viewer_html = create_3d_viewer_html(
            obj_content, 
            mtl_content, 
            texture_data, 
            background_color,
            model_token=share_token,
            annotations=annotations,
            real_height=real_height
        )
        
        # 전체 화면 뷰어 표시
        st.components.v1.html(viewer_html, width=None, height=None, scrolling=False)
    
    except Exception as e:
        st.error(f"모델 로딩 중 오류가 발생했습니다: {str(e)}")

def show_shared_model():
    """공유된 모델 뷰어"""
    # URL 파라미터에서 토큰 가져오기
    query_params = st.query_params
    token = query_params.get("token")
    
    if not token:
        st.error("유효하지 않은 공유 링크입니다.")
        st.info("올바른 공유 링크를 사용해주세요.")
        return
    
    # 토큰으로 모델 조회
    db = ModelDatabase()
    model_data = db.get_model_by_token(token)
    
    if not model_data:
        st.error("모델을 찾을 수 없습니다.")
        st.info("링크가 만료되었거나 삭제된 모델일 수 있습니다.")
        return
    
    # 뷰어 페이지 표시
    show_viewer_page(model_data)
