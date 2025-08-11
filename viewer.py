import streamlit as st
from database import ModelDatabase, load_model_files, generate_share_url

def show_viewer_page(model_data):
    """공유 링크로 접근한 뷰어 페이지"""
    st.set_page_config(
        page_title=f"3D Model: {model_data['name']}",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Streamlit UI 완전히 숨기기
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp > div:first-child {margin-top: -80px;}
    .stApp {margin: 0; padding: 0;}
    iframe {width: 100vw !important; height: 100vh !important;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    try:
        # URL 파라미터에서 배경색 가져오기 (기본값: white)
        query_params = st.query_params
        background_color = query_params.get("bg", "white")
        
        # 모델 파일 로드
        obj_content, mtl_content, texture_data = load_model_files(model_data)
        
        # 3D 뷰어 HTML 생성 (배경색 포함)
        from viewer_utils import create_3d_viewer_html
        viewer_html = create_3d_viewer_html(obj_content, mtl_content, texture_data, background_color)
        
        # 전체 화면 뷰어 표시
        st.components.v1.html(viewer_html, width=None, height=1000, scrolling=False)
    
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
