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
from viewer_utils import create_3d_viewer_html
from texture_optimizer import auto_optimize_textures
from viewer import show_shared_model
from viewer_utils import create_3d_viewer_html, create_texture_loading_code
from auth import check_password, show_logout_button, update_activity_time, show_session_info

# 페이지 설정 (항상 먼저 실행)
st.set_page_config(
    page_title="3D Model Manager",
    page_icon="🎮",
    layout="wide"
)

# URL 파라미터 체크
query_params = st.query_params
if 'token' in query_params:
    # 공유 링크로 접근한 경우 (인증 불필요)
    show_shared_model()
    st.stop()

# 관리자 페이지는 인증 필요
if not check_password():
    st.stop()

# 인증 성공 후 활동 시간 업데이트
update_activity_time()

# 스트림릿 하단 요소 숨기기
hide_streamlit_style = """
<style>
/* 스트림릿 하단 로고/아이콘 숨기기 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stBottomBlockContainer"] {display: none;}
[data-testid="stBottom"] {display: none;}
.streamlit-footer {display: none;}
.streamlit-badge {display: none;}
.st-emotion-cache-1ww3bz2 {display: none;}
.st-emotion-cache-10trblm {display: none;}
.st-emotion-cache-nahz7x {display: none;}
.st-emotion-cache-1y0tadg {display: none;}
.footer, [class*="footer"], [class*="Footer"] {display: none;}
a[href*="streamlit"], a[href*="share.streamlit.io"] {display: none;}
img[alt*="Streamlit"], img[src*="streamlit"] {display: none;}
[style*="position: fixed"][style*="bottom"] {display: none;}
[style*="position: absolute"][style*="bottom"] {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 타이틀과 세션 정보
col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
with col1:
    st.title("🎮 3D Model Manager")
with col2:
    # 세션 정보 표시
    import time
    from datetime import datetime
    
    if st.session_state.get("password_correct", False):
        time_since_activity = time.time() - st.session_state.get("last_activity_time", 0)
        remaining_time = 3600 - time_since_activity  # 60분
        
        if remaining_time > 0:
            mins = int(remaining_time // 60)
            st.success(f"세션: {mins}분")
with col3:
    # 새로고침 버튼
    if st.button("🔄 새로고침", key="header_refresh"):
        st.rerun()
with col4:
    # 로그아웃 버튼
    if st.button("🚪 로그아웃", key="header_logout"):
        from auth import logout
        logout()
        st.rerun()

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
        
        # 멀티 텍스처 지원을 위해 MTL 파일과 텍스처 파일 모두 필요
        if not file_types['material']:
            return False, "MTL 재질 파일이 필요합니다. (멀티 텍스처 지원)"
        
        if not file_types['texture']:
            return False, "텍스처 이미지 파일이 필요합니다."
        
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
        
        # MTL 파일 저장 (업로드된 파일 그대로 사용)
        for file in file_types['material']:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.getbuffer())
            saved_files['material'] = file_path
        
        # 텍스처 파일들 저장 및 최적화
        saved_files['textures'] = []
        texture_data = {}
        for file in file_types['texture']:
            texture_content = file.getbuffer()
            texture_data[file.name] = bytes(texture_content)
        
        # 🔧 텍스처 자동 최적화
        st.write("🎨 텍스처 최적화 중...")
        optimized_texture_data, should_continue = auto_optimize_textures(texture_data)
        
        if not should_continue:
            st.error("텍스처 최적화에 실패했습니다.")
            return None
        
        # 최적화된 텍스처 파일들을 디스크에 저장
        for filename, data in optimized_texture_data.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(data)
            saved_files['textures'].append(file_path)
        
        # MTL 파일 처리 - 업로드된 MTL 파일 사용 (멀티 텍스처 지원)
        st.info("✅ 업로드된 MTL 파일을 사용합니다. (멀티 텍스처 지원)")
        
        # MTL 파일 내용 확인 및 분석
        with open(saved_files['material'], 'r', encoding='utf-8', errors='ignore') as f:
            mtl_content = f.read()
        
        # MTL 파일에서 재질 정보 추출
        materials_in_mtl = self.extract_materials_from_mtl(mtl_content)
        texture_files_in_mtl, path_issues = self.extract_texture_files_from_mtl(mtl_content)
        
        # 경로 문제가 있으면 자동 수정 시도
        if path_issues:
            st.warning("🔧 MTL 파일의 경로 문제를 자동으로 수정하는 중...")
            
            corrected_mtl_content = self.fix_mtl_paths(mtl_content)
            
            # 수정된 MTL 파일 저장
            with open(saved_files['material'], 'w', encoding='utf-8') as f:
                f.write(corrected_mtl_content)
            
            # 다시 텍스처 파일 추출 (수정된 버전에서)
            materials_in_mtl = self.extract_materials_from_mtl(corrected_mtl_content)
            texture_files_in_mtl, remaining_issues = self.extract_texture_files_from_mtl(corrected_mtl_content)
            
            if not remaining_issues:
                st.success("✅ MTL 파일의 경로 문제가 자동으로 수정되었습니다!")
            else:
                st.warning("⚠️ 일부 경로 문제가 남아있습니다.")
        
        # 경로 문제점 검사 및 표시 (수정 후에도 남은 문제들)
        if path_issues:
            with st.expander("🔍 MTL 파일 경로 검증 결과"):
                serious_issues = [issue for issue in path_issues if issue['type'] in ['absolute_path', 'directory_path']]
                minor_issues = [issue for issue in path_issues if issue['type'] in ['space_in_path', 'non_ascii']]
                
                if serious_issues:
                    st.error(f"심각한 문제 {len(serious_issues)}개 발견 (자동 수정됨):")
                    for issue in serious_issues:
                        st.write(f"- 라인 {issue['line']}: {issue['message']}")
                
                if minor_issues:
                    st.info(f"참고사항 {len(minor_issues)}개:")
                    for issue in minor_issues:
                        st.write(f"- 라인 {issue['line']}: {issue['message']}")
        else:
            st.success("✅ MTL 파일의 모든 텍스처 경로가 올바릅니다!")
        
        # 업로드된 텍스처와 MTL에서 참조하는 텍스처 비교
        uploaded_texture_names = set(optimized_texture_data.keys())
        referenced_texture_names = set(texture_files_in_mtl)
        
        # 매핑 정보 표시
        with st.expander("🎨 멀티 텍스처 매핑 정보"):
            st.write(f"**MTL 파일에서 발견된 재질**: {len(materials_in_mtl)}개")
            for material in materials_in_mtl:
                st.write(f"- {material}")
            
            st.write(f"**MTL에서 참조하는 텍스처**: {len(referenced_texture_names)}개")
            for texture in referenced_texture_names:
                if texture in uploaded_texture_names:
                    st.write(f"- ✅ {texture} (업로드됨)")
                else:
                    st.write(f"- ⚠️ {texture} (업로드되지 않음)")
            
            missing_textures = referenced_texture_names - uploaded_texture_names
            if missing_textures:
                st.warning(f"누락된 텍스처: {', '.join(missing_textures)}")
            else:
                st.success("✅ 모든 참조 텍스처가 업로드되었습니다!")
        
        return saved_files
    
    def extract_materials_from_mtl(self, mtl_content):
        """MTL 파일에서 재질명 추출"""
        materials = []
        for line in mtl_content.split('\n'):
            line = line.strip()
            if line.startswith('newmtl '):
                material_name = line[7:].strip()
                if material_name:
                    materials.append(material_name)
        return materials
    
    def extract_texture_files_from_mtl(self, mtl_content):
        """MTL 파일에서 텍스처 파일명 추출 및 경로 검증"""
        textures = []
        problematic_paths = []
        
        for line_num, line in enumerate(mtl_content.split('\n'), 1):
            line = line.strip()
            # 다양한 텍스처 맵 지원
            if any(line.startswith(prefix) for prefix in ['map_Kd ', 'map_Ka ', 'map_Ks ', 'map_Bump ', 'map_d ', 'bump ']):
                parts = line.split()
                if len(parts) >= 2:
                    texture_path = parts[-1]  # 마지막 부분이 파일 경로
                    
                    # 경로 검증
                    path_issues = self.validate_texture_path(texture_path, line_num, line)
                    if path_issues:
                        problematic_paths.extend(path_issues)
                    
                    # 파일명만 추출 (경로 제거)
                    texture_file = os.path.basename(texture_path)
                    if texture_file not in textures:
                        textures.append(texture_file)
        
        return textures, problematic_paths
    
    def validate_texture_path(self, texture_path, line_num, full_line):
        """텍스처 경로 검증 및 문제점 탐지"""
        issues = []
        
        # 절대 경로 검사 (Windows, Linux, Mac)
        if (texture_path.startswith('/') or  # Unix 절대경로
            (len(texture_path) >= 3 and texture_path[1:3] == ':') or  # Windows C:\ 형태
            texture_path.startswith('\\') or  # Windows UNC 경로
            ':\\' in texture_path or  # Windows 경로
            texture_path.startswith('~/')):  # Unix 홈 디렉토리
            
            issues.append({
                'type': 'absolute_path',
                'line': line_num,
                'content': full_line,
                'path': texture_path,
                'message': f"절대 경로 발견: {texture_path}"
            })
        
        # 상위 디렉토리 참조 검사
        if '../' in texture_path or '..\\' in texture_path:
            issues.append({
                'type': 'relative_parent',
                'line': line_num,
                'content': full_line,
                'path': texture_path,
                'message': f"상위 디렉토리 참조 발견: {texture_path}"
            })
        
        # 하위 디렉토리 경로 검사
        if ('/' in texture_path or '\\' in texture_path) and not texture_path.startswith('./'):
            # 단순 파일명이 아닌 경우
            if os.path.dirname(texture_path):  # 디렉토리 부분이 있는 경우
                issues.append({
                    'type': 'directory_path',
                    'line': line_num,
                    'content': full_line,
                    'path': texture_path,
                    'message': f"디렉토리 경로 포함: {texture_path} → 파일명만 사용하세요: {os.path.basename(texture_path)}"
                })
        
        # 특수 문자나 공백이 포함된 경로 검사
        if ' ' in texture_path:
            issues.append({
                'type': 'space_in_path',
                'line': line_num,
                'content': full_line,
                'path': texture_path,
                'message': f"경로에 공백 포함: {texture_path}"
            })
        
        # 한글이나 특수 문자 검사
        try:
            texture_path.encode('ascii')
        except UnicodeEncodeError:
            issues.append({
                'type': 'non_ascii',
                'line': line_num,
                'content': full_line,
                'path': texture_path,
                'message': f"비ASCII 문자 포함: {texture_path}"
            })
        
        return issues
    
    def fix_mtl_paths(self, mtl_content):
        """MTL 파일의 경로 문제 자동 수정"""
        lines = mtl_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            original_line = line
            stripped_line = line.strip()
            
            # 텍스처 맵 라인인지 확인
            if any(stripped_line.startswith(prefix) for prefix in ['map_Kd ', 'map_Ka ', 'map_Ks ', 'map_Bump ', 'map_d ', 'bump ']):
                parts = stripped_line.split()
                if len(parts) >= 2:
                    # 텍스처 경로 부분
                    texture_path = parts[-1]
                    
                    # 경로에서 파일명만 추출
                    filename_only = os.path.basename(texture_path)
                    
                    # 라인 재구성 (파일명만 사용)
                    parts[-1] = filename_only
                    fixed_line = ' '.join(parts)
                    
                    # 들여쓰기 유지
                    indent = len(original_line) - len(original_line.lstrip())
                    fixed_line = ' ' * indent + fixed_line
                    
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(original_line)
            else:
                fixed_lines.append(original_line)
        
        return '\n'.join(fixed_lines)

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
        author_name = st.text_input("작성자", placeholder="작성자 이름을 입력하세요")
    with col2:
        model_description = st.text_area("설명 (선택사항)", placeholder="모델에 대한 간단한 설명")
    
    # 파일 업로드
    st.markdown("### 📁 파일 업로드")
    
    # 멀티 텍스처 가이드
    with st.expander("🎨 멀티 텍스처 업로드 가이드"):
        st.markdown("""
        **담당자가 준비한 완성된 파일들을 업로드**하세요:
        
        **1. 필수 파일들:**
        - `model.obj` - 3D 모델 파일
        - `model.mtl` - 재질 정보 파일 (담당자가 미리 매핑 완료)
        - 텍스처 이미지들 - MTL에서 참조하는 모든 텍스처 파일
        
        **2. MTL 파일에는 이미 다음이 설정되어 있어야 합니다:**
        ```mtl
        newmtl Material1
        map_Kd texture1.jpg
        
        newmtl Material2  
        map_Kd texture2.png
        
        newmtl Material3
        map_Kd texture3.jpg
        ```
        
        **3. 업로드 파일 예시:**
        ```
        character.obj           (3D 모델)
        character.mtl          (재질 매핑 파일)
        head_texture.jpg       (얼굴 텍스처)
        body_texture.png       (몸통 텍스처)  
        arm_texture.jpg        (팔 텍스처)
        leg_texture.png        (다리 텍스처)
        ```
        
        **4. 시스템 기능:**
        - MTL 파일을 분석하여 재질 정보 확인
        - 참조된 텍스처와 업로드된 텍스처 매칭 확인
        - 누락된 텍스처 파일 알림
        - 자동 텍스처 최적화 (2MB 이상 시)
        
        **⚠️ 주의사항:**
        - MTL 파일에서 참조하는 모든 텍스처를 함께 업로드해야 합니다
        - 파일명은 MTL에서 지정한 이름과 정확히 일치해야 합니다
        """)
    
    uploaded_files = st.file_uploader(
        "완성된 모델 파일들을 선택하세요 (OBJ + MTL + 텍스처들)",
        type=['obj', 'mtl', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="담당자가 준비한 OBJ, MTL, 텍스처 파일들을 모두 선택해서 업로드하세요."
    )
    
    if uploaded_files and model_name and author_name:
        processor = ModelProcessor()
        
        # 파일 유효성 검사
        is_valid, result = processor.validate_files(uploaded_files)
        
        if not is_valid:
            st.error(result)
            st.info("필요한 파일: OBJ 모델 파일, MTL 재질 파일, 텍스처 이미지 파일들")
            st.markdown("""
            **올바른 업로드 방법:**
            1. 담당자가 준비한 OBJ 파일
            2. 담당자가 준비한 MTL 파일 (재질 매핑 완료)
            3. MTL에서 참조하는 모든 텍스처 이미지 파일들
            """)
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
                                author_name,
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
                            st.text_input("공유 링크", value=share_url, key="new_share_link")
                            st.markdown("위 링크를 복사하여 다른 사람들과 공유하세요!")
                    
                    except Exception as e:
                        st.error(f"모델 저장 중 오류가 발생했습니다: {str(e)}")
    elif uploaded_files and model_name and not author_name:
        st.warning("⚠️ 작성자 이름을 입력해주세요.")
    elif uploaded_files and not model_name and author_name:
        st.warning("⚠️ 모델 이름을 입력해주세요.")

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
        
        # 날짜 포맷팅 (YYYY-MM-DD 형식으로)
        created_date = model['created_at'][:10] if model['created_at'] else "날짜 없음"
        author_text = model.get('author', '') or "작성자 없음"
        description_text = model['description'] or ""
        
        # 제목 형식: "제목 🍀(조회수 : N) - 작성자 - YYYY-MM-DD : 설명(선택사항)"
        if description_text:
            title_format = f"{model['name']} 🍀(조회수 : {model['access_count']}) - {author_text} - {created_date} : {description_text}"
        else:
            title_format = f"{model['name']} 🍀(조회수 : {model['access_count']}) - {author_text} - {created_date}"
        
        with st.expander(f"{title_format} {storage_icon}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**모델명:** {model['name']}")
                st.write(f"**작성자:** {author_text}")
                st.write(f"**설명:** {model['description'] or '설명 없음'}")
                st.write(f"**생성일:** {model['created_at']}")
                st.write(f"**저장 위치:** {storage_text}")
                
                # 공유 링크
                share_url = generate_share_url(model['share_token'])
                st.text_input("공유 링크", value=share_url, key=f"share_{model['id']}")
            
            with col2:
                # 삭제 버튼 (상단에 배치)
                st.write("")  # 여백
                st.write("")  # 여백
                if st.button("🗑️ 삭제", key=f"delete_{model['id']}", type="secondary", use_container_width=True):
                    if db.delete_model(model['id']):
                        st.success("모델이 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("삭제 중 오류가 발생했습니다.")

def show_feedback_management():
    """피드백 관리 섹션"""
    st.header("💬 피드백 관리")
    
    db = ModelDatabase()
    models = db.get_all_models()
    
    if not models:
        st.info("📋 업로드된 모델이 없습니다.")
        return
    
    # 모델 선택
    model_options = [f"{model['name']} (ID: {model['id'][:8]}...)" for model in models]
    selected_idx = st.selectbox("모델 선택", range(len(models)), format_func=lambda x: model_options[x])
    
    if selected_idx is not None:
        selected_model = models[selected_idx]
        
        st.subheader(f"📋 {selected_model['name']} - 피드백 목록")
        
        # 선택된 모델의 피드백 조회
        feedbacks = db.get_feedbacks(selected_model['id'])
        
        if not feedbacks:
            st.info("💬 등록된 피드백이 없습니다.")
            return
        
        st.write(f"**총 {len(feedbacks)}개의 피드백**")
        
        # 피드백 목록 표시
        for i, feedback in enumerate(feedbacks):
            with st.expander(f"📍 피드백 #{feedback['id']} - {feedback['comment'][:30]}...", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**내용:** {feedback['comment']}")
                    st.write(f"**위치:** X={feedback['x']:.3f}, Y={feedback['y']:.3f}, Z={feedback['z']:.3f}")
                    st.write(f"**등록일:** {feedback['created_at']}")
                
                with col2:
                    # 상태 변경
                    current_status = feedback['status']
                    status_options = ['pending', 'reviewed', 'resolved']
                    status_labels = {'pending': '🔴 대기중', 'reviewed': '🟡 검토중', 'resolved': '🟢 완료'}
                    
                    current_idx = status_options.index(current_status) if current_status in status_options else 0
                    new_status_idx = st.selectbox(
                        "상태", 
                        range(len(status_options)),
                        index=current_idx,
                        format_func=lambda x: status_labels[status_options[x]],
                        key=f"status_{feedback['id']}"
                    )
                    
                    new_status = status_options[new_status_idx]
                    
                    # 상태 변경 버튼
                    if new_status != current_status:
                        if st.button(f"상태 변경", key=f"update_{feedback['id']}"):
                            if db.update_feedback_status(feedback['id'], new_status):
                                st.success(f"상태가 '{status_labels[new_status]}'로 변경되었습니다!")
                                st.rerun()
                            else:
                                st.error("상태 변경에 실패했습니다.")
                    
                    # 삭제 버튼
                    if st.button(f"🗑️ 삭제", key=f"delete_{feedback['id']}", type="secondary"):
                        if db.delete_feedback(feedback['id']):
                            st.success("피드백이 삭제되었습니다!")
                            st.rerun()
                        else:
                            st.error("삭제에 실패했습니다.")
        
        # 통계 정보
        st.subheader("📊 피드백 통계")
        col1, col2, col3 = st.columns(3)
        
        pending_count = len([f for f in feedbacks if f['status'] == 'pending'])
        reviewed_count = len([f for f in feedbacks if f['status'] == 'reviewed'])
        resolved_count = len([f for f in feedbacks if f['status'] == 'resolved'])
        
        with col1:
            st.metric("🔴 대기중", pending_count)
        with col2:
            st.metric("🟡 검토중", reviewed_count)
        with col3:
            st.metric("🟢 완료", resolved_count)

def main():
    # 타이틀은 이미 상단에 표시됨
    st.write("(주)에어바이블 3D 모델 고객용 뷰어 관리 시스템")
    
    # 페이지 활동시마다 세션 시간 갱신
    update_activity_time()
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📤 업로드", "📋 관리", "💬 피드백", "ℹ️ 사용법"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_model_management()
    
    with tab3:
        show_feedback_management()
    
    with tab4:
        st.markdown("""
        ### 🎯 사용법
        
        **1. 모델 업로드**
        - OBJ 파일 (3D 모델) - 필수
        - MTL 파일 (재질 정보) - 필수, 담당자가 미리 매핑 완료
        - 텍스처 이미지들 (PNG, JPG) - 필수, MTL에서 참조하는 모든 파일
        
        **2. 멀티 텍스처 지원** 🆕
        - 담당자가 준비한 완성된 파일들 업로드
        - MTL 파일의 재질 매핑 정보 그대로 사용
        - 업로드된 텍스처와 MTL 참조 확인
        
        **3. 파일 준비 방법 (담당자용)**
        ```
        1. 3D 모델링 소프트웨어에서 재질별로 분리
        2. 각 재질에 맞는 텍스처 할당
        3. MTL 파일로 익스포트
        4. OBJ + MTL + 모든 텍스처 파일 함께 업로드
        ```
        
        **4. 공유**
        - 업로드 후 생성되는 링크 복사
        - 링크를 통해 누구나 접근 가능
        
        **5. 관리**
        - 최대 20개 모델 저장
        - 미리보기 및 삭제 가능
        
        **6. 뷰어 조작**
        - 마우스 드래그: 회전
        - 마우스 휠: 확대/축소
        - 우클릭 드래그: 이동
        - 우상단 버튼: 배경색 변경 (흰색/회색/검은색)
        
        **7. 자동 최적화**
        - 큰 텍스처 파일 자동 압축
        - 2MB 이상 또는 1024px 초과 시 최적화
        - 투명도 유지 (PNG) 또는 JPEG 변환
        
        **8. 보안**
        - 와이어프레임 모드 차단
        - 파일 다운로드 불가
        - 텍스처 필수 적용
        - 관리자 인증 시스템
        """)
        
        # 멀티 텍스처 예시 추가
        with st.expander("🎨 멀티 텍스처 파일 구조 예시"):
            st.markdown("""
            ### 올바른 파일 구조
            
            **업로드할 파일들:**
            ```
            character.obj          (3D 모델)
            character.mtl          (재질 매핑, 아래 내용 포함)
            head_diffuse.jpg       (얼굴 텍스처)
            body_diffuse.png       (몸통 텍스처)
            arm_diffuse.jpg        (팔 텍스처)
            leg_diffuse.png        (다리 텍스처)
            hair_diffuse.jpg       (머리카락 텍스처)
            clothes_diffuse.png    (옷 텍스처)
            ```
            
            **character.mtl 파일 내용:**
            ```mtl
            newmtl HeadMaterial
            Ka 1.0 1.0 1.0
            Kd 1.0 1.0 1.0
            Ks 0.0 0.0 0.0
            map_Kd head_diffuse.jpg
            
            newmtl BodyMaterial
            Ka 1.0 1.0 1.0
            Kd 1.0 1.0 1.0
            Ks 0.0 0.0 0.0
            map_Kd body_diffuse.png
            
            newmtl ArmMaterial
            Ka 1.0 1.0 1.0
            Kd 1.0 1.0 1.0
            Ks 0.0 0.0 0.0
            map_Kd arm_diffuse.jpg
            
            newmtl LegMaterial
            Ka 1.0 1.0 1.0
            Kd 1.0 1.0 1.0
            Ks 0.0 0.0 0.0
            map_Kd leg_diffuse.png
            
            newmtl HairMaterial
            Ka 1.0 1.0 1.0
            Kd 1.0 1.0 1.0
            Ks 0.0 0.0 0.0
            map_Kd hair_diffuse.jpg
            
            newmtl ClothesMaterial
            Ka 1.0 1.0 1.0
            Kd 1.0 1.0 1.0
            Ks 0.0 0.0 0.0
            map_Kd clothes_diffuse.png
            ```
            
            **character.obj 파일에는:**
            ```obj
            mtllib character.mtl
            usemtl HeadMaterial
            f 1/1/1 2/2/2 3/3/3
            usemtl BodyMaterial  
            f 4/4/4 5/5/5 6/6/6
            # ... 각 부분별로 재질 지정
            ```
            
            ### 시스템 동작
            1. MTL 파일에서 6개 재질 인식
            2. 6개 텍스처 파일 참조 확인
            3. 업로드된 텍스처와 매칭 검증
            4. 모든 텍스처가 있으면 성공 표시
            5. 3D 뷰어에서 멀티 텍스처 렌더링
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
            
            # 텍스처 최적화 테스트
            st.divider()
            st.subheader("🎨 텍스처 최적화 테스트")
            
            test_file = st.file_uploader(
                "테스트할 이미지 파일",
                type=['png', 'jpg', 'jpeg'],
                key="texture_test"
            )
            
            if test_file:
                st.write(f"**원본 파일**: {test_file.name}")
                st.write(f"**원본 크기**: {len(test_file.getbuffer()):,} bytes ({len(test_file.getbuffer())/(1024*1024):.2f}MB)")
                
                if st.button("🔧 최적화 테스트"):
                    test_data = {test_file.name: test_file.getbuffer()}
                    optimized_data, _ = auto_optimize_textures(test_data)
                    
                    for filename, data in optimized_data.items():
                        st.write(f"**최적화 후**: {filename}")
                        st.write(f"**새 크기**: {len(data):,} bytes ({len(data)/(1024*1024):.2f}MB)")
                        
                        # 최적화된 이미지 다운로드 제공
                        st.download_button(
                            label="최적화된 파일 다운로드",
                            data=data,
                            file_name=f"optimized_{filename}",
                            mime="image/jpeg" if filename.endswith('.jpg') else "image/png"
                        )




if __name__ == "__main__":
    main()
