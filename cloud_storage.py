import io
import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import streamlit as st
import tempfile

class GoogleDriveManager:
    def __init__(self):
        self.api_key = "AIzaSyDjuTYKhecXA3dySC4AY3aFojh9RaNAnXE"
        self.service = None
        self.folder_id = None
        
    def authenticate(self):
        """Google Drive API 인증"""
        try:
            # API 키로 서비스 생성 (읽기 전용)
            self.service = build('drive', 'v3', developerKey=self.api_key)
            return True
        except Exception as e:
            st.error(f"Google Drive 인증 실패: {str(e)}")
            return False
    
    def get_or_create_folder(self, folder_name="streamlit_data"):
        """폴더 찾기 또는 생성"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # 폴더 검색
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.folder_id = folders[0]['id']
                return self.folder_id
            else:
                # 폴더 생성 (API 키로는 불가능하므로 OAuth 필요)
                st.warning("streamlit_data 폴더를 찾을 수 없습니다. 수동으로 생성해주세요.")
                return None
                
        except Exception as e:
            st.error(f"폴더 검색 중 오류: {str(e)}")
            return None
    
    def upload_file(self, file_content, file_name, mime_type='application/octet-stream'):
        """파일 업로드 (OAuth 인증 필요)"""
        # API 키로는 파일 업로드가 불가능합니다
        # OAuth 2.0 인증이 필요합니다
        st.warning("파일 업로드를 위해서는 OAuth 인증이 필요합니다.")
        return None
    
    def download_file(self, file_id):
        """파일 다운로드"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            return file_content.read()
            
        except Exception as e:
            st.error(f"파일 다운로드 중 오류: {str(e)}")
            return None
    
    def list_files_in_folder(self, folder_id=None):
        """폴더 내 파일 목록 조회"""
        if not self.service:
            if not self.authenticate():
                return []
        
        if not folder_id:
            folder_id = self.folder_id
        
        if not folder_id:
            return []
        
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, mimeType, size, createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            st.error(f"파일 목록 조회 중 오류: {str(e)}")
            return []

# OAuth 2.0을 위한 설정 (실제 구현 시 필요)
class GoogleDriveOAuth:
    def __init__(self):
        # OAuth 2.0 클라이언트 설정이 필요합니다
        self.client_config = {
            "web": {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8501"]
            }
        }
        self.scopes = ['https://www.googleapis.com/auth/drive.file']
    
    def get_authorization_url(self):
        """OAuth 인증 URL 생성"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = "http://localhost:8501"
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def exchange_code_for_tokens(self, code):
        """인증 코드를 토큰으로 교환"""
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = "http://localhost:8501"
        
        flow.fetch_token(code=code)
        return flow.credentials

# 임시방편: 로컬 파일 시스템 사용 (Google Drive 연동 전)
class LocalFileManager:
    def __init__(self, base_path="data/models"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save_model_files(self, model_id, obj_content, mtl_content, texture_data):
        """모델 파일들을 로컬에 저장"""
        model_dir = os.path.join(self.base_path, model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        # OBJ 파일 저장
        obj_path = os.path.join(model_dir, "model.obj")
        with open(obj_path, 'w') as f:
            f.write(obj_content)
        
        # MTL 파일 저장
        mtl_path = os.path.join(model_dir, "model.mtl")
        with open(mtl_path, 'w') as f:
            f.write(mtl_content)
        
        # 텍스처 파일들 저장
        texture_paths = []
        for texture_name, texture_content in texture_data.items():
            texture_path = os.path.join(model_dir, texture_name)
            with open(texture_path, 'wb') as f:
                f.write(texture_content)
            texture_paths.append(texture_path)
        
        return {
            'obj_path': obj_path,
            'mtl_path': mtl_path,
            'texture_paths': texture_paths
        }
    
    def load_model_files(self, obj_path, mtl_path, texture_paths):
        """저장된 모델 파일들 로드"""
        # OBJ 파일 읽기
        with open(obj_path, 'r') as f:
            obj_content = f.read()
        
        # MTL 파일 읽기
        with open(mtl_path, 'r') as f:
            mtl_content = f.read()
        
        # 텍스처 파일들 읽기
        texture_data = {}
        for texture_path in texture_paths:
            texture_name = os.path.basename(texture_path)
            with open(texture_path, 'rb') as f:
                texture_data[texture_name] = f.read()
        
        return obj_content, mtl_content, texture_data
    
    def delete_model_files(self, model_id):
        """모델 파일들 삭제"""
        model_dir = os.path.join(self.base_path, model_id)
        if os.path.exists(model_dir):
            import shutil
            shutil.rmtree(model_dir)
            return True
        return False
