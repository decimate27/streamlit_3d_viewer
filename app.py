import streamlit as st
import os
import tempfile
import base64
from pathlib import Path
import trimesh
from PIL import Image
import zipfile
import shutil
from database import ModelDatabase, load_model_files, generate_share_url, reset_database
from mtl_generator import auto_generate_mtl
from viewer import show_shared_model
from viewer_utils import create_3d_viewer_html, create_texture_loading_code

# URL 파라미터 체크
query_params = st.query_params
if 'token' in query_params:
    # 공유 링크로 접근한 경우
    show_shared_model()
    st.stop()

# 메인 관리 페이지
st.set_page_config(
    page_title="3D Model Manager",
    page_icon="🎮",
    layout="wide"
)

class ModelProcessor:
    def __init__(self):
        self.supported_model_formats = ['.obj']
        self.supported_material_formats = ['.mtl']
        self.supported_texture_formats = ['.png', '.jpg', '.jpeg']
    
    def validate_files(self, uploaded_files):
        """업로드된 파일들의 유효성 검사"""
        file_types = {
            'model': [],
            'material': [],
            'texture': []
        }
        
        for file in uploaded_files:
            ext = Path(file.name).suffix.lower()
            if ext in self.supported_model_formats:
                file_types['model'].append(file)
            elif ext in self.supported_material_formats:
                file_types['material'].append(file)
            elif ext in self.supported_texture_formats:
                file_types['texture'].append(file)
        
        # 필수 파일 확인
        if not file_types['model']:
            return False, "OBJ 모델 파일이 필요합니다."
        
        # MTL 파일은 선택사항, 텍스처는 필수
        if not file_types['texture']:
            return False, "텍스처 이미지 파일이 필요합니다."
        
        # MTL 파일이 없으면 자동 생성됨을 알림
        if not file_types['material']:
            st.info("💡 MTL 파일이 없습니다. 텍스처를 기반으로 자동 생성됩니다.")
        
        return True, file_types
    
    def save_uploaded_files(self, file_types, temp_dir):
        """업로드된 파일들을 임시 디렉토리에 저장"""
        saved_files = {}
        
        # 모델 파일 저장
        for file in file_types['model']:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            saved_files['model'] = file_path
        
        # 텍스처 파일들 저장
        saved_files['textures'] = []
        texture_data = {}
        for file in file_types['texture']:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, 'wb') as f:
                texture_content = file.getbuffer()
                f.write(texture_content)
                texture_data[file.name] = bytes(texture_content)
            saved_files['textures'].append(file_path)
        
        # MTL 파일 처리
        if file_types['material']:
            # MTL 파일이 있는 경우 그대로 사용
            for file in file_types['material']:
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, 'wb') as f:
                    f.write(file.getbuffer())
                saved_files['material'] = file_path
        else:
            # MTL 파일이 없는 경우 자동 생성
            st.info("🔧 MTL 파일을 자동 생성하는 중...")
            
            # OBJ 파일 내용 읽기
            with open(saved_files['model'], 'r', encoding='utf-8', errors='ignore') as f:
                obj_content = f.read()
            
            # MTL 자동 생성
            updated_obj_content, generated_mtl_content = auto_generate_mtl(obj_content, texture_data)
            
            # 수정된 OBJ 파일 저장
            with open(saved_files['model'], 'w', encoding='utf-8') as f:
                f.write(updated_obj_content)
            
            # 생성된 MTL 파일 저장
            mtl_path = os.path.join(temp_dir, 'model.mtl')
            with open(mtl_path, 'w', encoding='utf-8') as f:
                f.write(generated_mtl_content)
            saved_files['material'] = mtl_path
            
            st.success("✅ MTL 파일이 자동 생성되었습니다!")
        
        return saved_files

def show_upload_section():
    """파일 업로드 섹션"""
    st.header("📤 새 모델 업로드")
    
    # 데이터베이스 연결
    db = ModelDatabase()
    current_count = db.get_model_count()
    
    if current_count >= 20:
        st.error("최대 20개의 모델만 저장할 수 있습니다. 기존 모델을 삭제 후 다시 시도하세요.")
        return
    
    # 저장된 모델들의 storage_type 확인
    models = db.get_all_models()
    web_count = sum(1 for model in models if model.get('storage_type') == 'web')
    local_count = sum(1 for model in models if model.get('storage_type') == 'local')
    
    # 상태 메시지 생성
    if web_count > 0 and local_count > 0:
        storage_status = f"웹서버: {web_count}개, 로컬: {local_count}개"
    elif web_count > 0:
        storage_status = "웹서버 저장"
    elif local_count > 0:
        storage_status = "로컬 임시 저장"
    else:
        storage_status = "저장소 준비됨"
    
    st.info(f"현재 저장된 모델: {current_count}/20 ({storage_status})")
    
    # 모델 정보 입력
    col1, col2 = st.columns(2)
    with col1:
        model_name = st.text_input("모델 이름", placeholder="예: 자동차 모델")
    with col2:
        model_description = st.text_area("설명 (선택사항)", placeholder="모델에 대한 간단한 설명")
    
    # 파일 업로드
    uploaded_files = st.file_uploader(
        "모델 파일들을 선택하세요",
        type=['obj', 'mtl', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="OBJ 모델 파일과 텍스처 이미지 파일이 필요합니다. MTL 파일은 선택사항입니다."
    )
    
    if uploaded_files and model_name:
        processor = ModelProcessor()
        
        # 파일 유효성 검사
        is_valid, result = processor.validate_files(uploaded_files)
        
        if not is_valid:
            st.error(result)
            st.info("필요한 파일: OBJ 모델 파일, 텍스처 이미지 파일 (MTL은 자동 생성됨)")
        else:
            file_types = result
            
            if st.button("모델 저장 및 공유 링크 생성", type="primary"):
                with st.spinner("모델을 저장하고 있습니다..."):
                    try:
                        # 임시 디렉토리 생성
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # 파일 저장
                            saved_files = processor.save_uploaded_files(file_types, temp_dir)
                            
                            # 파일 내용 읽기
                            with open(saved_files['model'], 'r') as f:
                                obj_content = f.read()
                            
                            with open(saved_files['material'], 'r') as f:
                                mtl_content = f.read()
                            
                            # 텍스처 데이터 읽기
                            texture_data = {}
                            for texture_path in saved_files['textures']:
                                texture_name = os.path.basename(texture_path)
                                with open(texture_path, 'rb') as f:
                                    texture_data[texture_name] = f.read()
                            
                            # 데이터베이스에 저장
                            model_id, share_token = db.save_model(
                                model_name, 
                                model_description,
                                obj_content, 
                                mtl_content, 
                                texture_data
                            )
                            
                            # 성공 메시지 및 공유 링크
                            st.success("✅ 모델이 성공적으로 저장되었습니다!")
                            
                            # 공유 링크 생성
                            share_url = generate_share_url(share_token)
                            st.markdown("### 🔗 공유 링크")
                            st.code(share_url, language="text")
                            st.markdown("위 링크를 복사하여 다른 사람들과 공유하세요!")
                    
                    except Exception as e:
                        st.error(f"모델 저장 중 오류가 발생했습니다: {str(e)}")

def show_model_management():
    """모델 관리 섹션"""
    st.header("📋 저장된 모델 관리")
    
    db = ModelDatabase()
    models = db.get_all_models()
    
    if not models:
        st.info("저장된 모델이 없습니다.")
        return
    
    for model in models:
        # 저장 타입에 따른 아이콘과 설명
        storage_type = model.get('storage_type', 'local')
        if storage_type == 'web':
            storage_icon = "🌐"
            storage_text = "웹서버 저장"
        else:
            storage_icon = "💾"
            storage_text = "로컬 임시 저장"
        
        with st.expander(f"🎮 {model['name']} {storage_icon} (조회수: {model['access_count']})"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**설명:** {model['description'] or '설명 없음'}")
                st.write(f"**생성일:** {model['created_at']}")
                st.write(f"**저장 위치:** {storage_text}")
                
                # 공유 링크
                share_url = generate_share_url(model['share_token'])
                st.text_input("공유 링크", value=share_url, key=f"share_{model['id']}")
            
            with col2:
                # 미리보기 버튼
                if st.button("미리보기", key=f"preview_{model['id']}"):
                    st.session_state[f"show_preview_{model['id']}"] = True
            
            with col3:
                # 삭제 버튼
                if st.button("🗑️ 삭제", key=f"delete_{model['id']}", type="secondary"):
                    if db.delete_model(model['id']):
                        st.success("모델이 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("삭제 중 오류가 발생했습니다.")
            
            # 미리보기 표시
            if st.session_state.get(f"show_preview_{model['id']}", False):
                try:
                    model_data = db.get_model_by_token(model['share_token'])
                    if model_data:
                        obj_content, mtl_content, texture_data = load_model_files(model_data)
                        viewer_html = create_3d_viewer_html(obj_content, mtl_content, texture_data)
                        st.components.v1.html(viewer_html, height=600, scrolling=False)
                except Exception as e:
                    st.error(f"미리보기 로딩 중 오류: {str(e)}")

def main():
    st.title("🎮 (주)에어바이블 3D 모델 고객용 뷰어 관리")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📤 업로드", "📋 관리", "ℹ️ 사용법"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_model_management()
    
    with tab3:
        st.markdown("""
        ### 🎯 사용법
        
        **1. 모델 업로드**
        - OBJ 파일 (3D 모델) - 필수
        - 텍스처 이미지 (PNG, JPG) - 필수
        - MTL 파일 (재질 정보) - 선택사항 (자동 생성됨)
        
        **2. 공유**
        - 업로드 후 생성되는 링크 복사
        - 링크를 통해 누구나 접근 가능
        
        **3. 관리**
        - 최대 20개 모델 저장
        - 미리보기 및 삭제 가능
        
        **4. 뷰어 조작**
        - 마우스 드래그: 회전
        - 마우스 휠: 확대/축소
        - 우클릭 드래그: 이동
        
        **5. 보안**
        - 와이어프레임 모드 차단
        - 파일 다운로드 불가
        - 텍스처 필수 적용
        """)
        
        # 데이터베이스 문제 해결 옵션
        with st.expander("🔧 문제 해결"):
            st.warning("데이터베이스 오류가 발생하면 아래 버튼을 클릭하세요.")
            if st.button("🔄 데이터베이스 초기화", type="secondary"):
                try:
                    reset_database()
                    st.success("데이터베이스가 초기화되었습니다. 페이지를 새로고침하세요.")
                    st.rerun()
                except Exception as e:
                    st.error(f"초기화 실패: {str(e)}")
            
            st.info("⚠️ 초기화하면 기존 모델 목록이 삭제됩니다. (파일은 백업됨)")
            
            # 웹서버 연결 테스트
            st.divider()
            st.subheader("🌐 웹서버 연결 테스트")
            
            # 사용자 정의 URL 입력
            custom_url = st.text_input(
                "서버 URL 테스트", 
                value="http://decimate27.dothome.co.kr/streamlit_data/upload.php",
                help="정확한 upload.php 경로를 입력하세요"
            )
            
            if st.button("🔍 서버 연결 테스트"):
                import requests
                try:
                    response = requests.post(custom_url, data={}, timeout=10, verify=False)
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            st.success(f"✅ 서버 연결 성공! 응답: {result}")
                        except:
                            st.warning(f"⚠️ 서버 응답은 있으나 JSON이 아님: {response.text[:100]}...")
                    else:
                        st.error(f"❌ 서버 오류: {response.status_code}")
                        st.write(f"응답 내용: {response.text[:200]}...")
                except Exception as e:
                    st.error(f"❌ 연결 실패: {str(e)}")
            
            st.caption("💡 올바른 경로를 찾으면 개발자에게 알려주세요!")
            
            # 서버 모델 목록 조회
            st.divider()
            st.subheader("🗂️ 서버 모델 관리")
            
            if st.button("📋 서버 모델 목록 조회"):
                from web_storage import WebServerStorage
                web_storage = WebServerStorage()
                server_models = web_storage.list_server_models()
                
                if server_models:
                    st.success(f"✅ 서버에 {len(server_models)}개 모델 발견")
                    
                    for model in server_models:
                        with st.expander(f"🎮 서버 모델: {model['model_id']}"):
                            st.write(f"**파일 수**: {len(model['files'])}")
                            for file_info in model['files']:
                                file_size_mb = file_info['size'] / (1024 * 1024)
                                st.write(f"- `{file_info['name']}` ({file_size_mb:.2f}MB)")
                else:
                    st.info("서버에 모델이 없거나 조회에 실패했습니다.")
            
            st.caption("⚠️ 이 기능은 디버깅 및 관리 목적으로 제공됩니다.")




if __name__ == "__main__":
    main()
