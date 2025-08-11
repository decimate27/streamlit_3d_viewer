import io
import os
import json
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import tempfile
import uuid

class GoogleDriveStorage:
    def __init__(self):
        self.service = None
        self.folder_id = None
        self.credentials_file = "client_secret_138543323279-bgk18cj3kfn1sgu5ahqc6igsct8kb548.apps.googleusercontent.com.json"
        
    def authenticate(self):
        """Google Drive API 인증"""
        try:
            # JSON 파일에서 크리덴셜 로드
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    cred_data = json.load(f)
                
                # OAuth 클라이언트 정보 확인
                if 'installed' in cred_data:
                    # 이것은 OAuth 클라이언트 파일입니다
                    # Streamlit에서는 서비스 계정이 더 적합합니다
                    st.warning("OAuth 클라이언트 파일입니다. 서비스 계정 키가 필요합니다.")
                    return False
                elif 'type' in cred_data and cred_data['type'] == 'service_account':
                    # 서비스 계정 인증
                    credentials = Credentials.from_service_account_file(
                        self.credentials_file,
                        scopes=['https://www.googleapis.com/auth/drive.file']
                    )
                else:
                    st.error("지원되지 않는 크리덴셜 형식입니다.")
                    return False
            else:
                st.error("Google 크리덴셜 파일을 찾을 수 없습니다.")
                return False
                
            self.service = build('drive', 'v3', credentials=credentials)
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
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.folder_id = folders[0]['id']
                print(f"폴더 찾음: {folder_name} (ID: {self.folder_id})")
                return self.folder_id
            else:
                # 폴더 생성
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                self.folder_id = folder.get('id')
                print(f"폴더 생성: {folder_name} (ID: {self.folder_id})")
                return self.folder_id
                
        except Exception as e:
            st.error(f"폴더 작업 중 오류: {str(e)}")
            return None
    
    def upload_file(self, file_content, file_name, parent_folder_id=None):
        """파일 업로드"""
        if not self.service:
            if not self.authenticate():
                return None
        
        if not parent_folder_id:
            parent_folder_id = self.folder_id or self.get_or_create_folder()
        
        if not parent_folder_id:
            st.error("업로드할 폴더를 찾을 수 없습니다.")
            return None
        
        try:
            # 파일 메타데이터
            file_metadata = {
                'name': file_name,
                'parents': [parent_folder_id]
            }
            
            # 파일 내용을 BytesIO로 변환
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/octet-stream'
            )
            
            # 파일 업로드
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"파일 업로드 완료: {file_name} (ID: {file.get('id')})")
            return file.get('id')
            
        except Exception as e:
            st.error(f"파일 업로드 중 오류: {str(e)}")
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
    
    def delete_file(self, file_id):
        """파일 삭제"""
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"파일 삭제 완료: {file_id}")
            return True
            
        except Exception as e:
            st.error(f"파일 삭제 중 오류: {str(e)}")
            return False
    
    def list_files_in_folder(self, folder_id=None):
        """폴더 내 파일 목록 조회"""
        if not self.service:
            if not self.authenticate():
                return []
        
        if not folder_id:
            folder_id = self.folder_id or self.get_or_create_folder()
        
        if not folder_id:
            return []
        
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType, size, createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            st.error(f"파일 목록 조회 중 오류: {str(e)}")
            return []
    
    def save_model_to_drive(self, model_id, obj_content, mtl_content, texture_data):
        """모델을 Google Drive에 저장"""
        if not self.get_or_create_folder():
            return None
        
        # 모델별 폴더 생성
        model_folder_metadata = {
            'name': f"model_{model_id}",
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.folder_id]
        }
        
        try:
            model_folder = self.service.files().create(
                body=model_folder_metadata,
                fields='id'
            ).execute()
            
            model_folder_id = model_folder.get('id')
            
            # 파일들 업로드
            file_ids = {}
            
            # OBJ 파일
            obj_id = self.upload_file(obj_content, "model.obj", model_folder_id)
            if obj_id:
                file_ids['obj_id'] = obj_id
            
            # MTL 파일
            mtl_id = self.upload_file(mtl_content, "model.mtl", model_folder_id)
            if mtl_id:
                file_ids['mtl_id'] = mtl_id
            
            # 텍스처 파일들
            texture_ids = []
            for texture_name, texture_content in texture_data.items():
                texture_id = self.upload_file(texture_content, texture_name, model_folder_id)
                if texture_id:
                    texture_ids.append({'name': texture_name, 'id': texture_id})
            
            file_ids['texture_ids'] = texture_ids
            file_ids['folder_id'] = model_folder_id
            
            return file_ids
            
        except Exception as e:
            st.error(f"모델 저장 중 오류: {str(e)}")
            return None
    
    def load_model_from_drive(self, file_ids):
        """Google Drive에서 모델 로드"""
        try:
            # OBJ 파일 다운로드
            obj_content = self.download_file(file_ids['obj_id'])
            if obj_content:
                obj_content = obj_content.decode('utf-8')
            
            # MTL 파일 다운로드
            mtl_content = self.download_file(file_ids['mtl_id'])
            if mtl_content:
                mtl_content = mtl_content.decode('utf-8')
            
            # 텍스처 파일들 다운로드
            texture_data = {}
            for texture_info in file_ids['texture_ids']:
                texture_content = self.download_file(texture_info['id'])
                if texture_content:
                    texture_data[texture_info['name']] = texture_content
            
            return obj_content, mtl_content, texture_data
            
        except Exception as e:
            st.error(f"모델 로드 중 오류: {str(e)}")
            return None, None, None
    
    def delete_model_from_drive(self, file_ids):
        """Google Drive에서 모델 삭제"""
        try:
            # 모델 폴더 전체 삭제
            if 'folder_id' in file_ids:
                return self.delete_file(file_ids['folder_id'])
            return False
            
        except Exception as e:
            st.error(f"모델 삭제 중 오류: {str(e)}")
            return False
