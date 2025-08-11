import requests
import os
import json
import uuid
import tempfile
import streamlit as st
from datetime import datetime
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebServerStorage:
    def __init__(self):
        self.base_url = "https://airbible.kr/streamlit_data"
        self.upload_url = f"{self.base_url}/upload.php"  # 업로드용 PHP 스크립트
        self.download_url = f"{self.base_url}/files"     # 파일 다운로드 경로
        
    def upload_file(self, file_content, filename, model_id):
        """웹서버에 파일 업로드"""
        try:
            # 파일 데이터 준비
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            files = {
                'file': (filename, file_content),
                'model_id': (None, model_id),
                'action': (None, 'upload')
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(
                self.upload_url, 
                files=files, 
                headers=headers,
                timeout=30, 
                verify=False  # SSL 검증 비활성화
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return result.get('file_path')
                else:
                    st.error(f"업로드 실패: {result.get('message')}")
                    return None
            else:
                st.error(f"서버 오류: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"파일 업로드 중 오류: {str(e)}")
            return None
    
    def download_file(self, file_path):
        """웹서버에서 파일 다운로드"""
        try:
            url = f"{self.download_url}/{file_path}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                return response.content
            else:
                st.error(f"파일 다운로드 실패: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"파일 다운로드 중 오류: {str(e)}")
            return None
    
    def delete_model(self, model_id):
        """모델 폴더 삭제"""
        try:
            data = {
                'model_id': model_id,
                'action': 'delete'
            }
            
            response = requests.post(self.upload_url, data=data, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('status') == 'success'
            else:
                return False
                
        except Exception as e:
            st.error(f"모델 삭제 중 오류: {str(e)}")
            return False
    
    def save_model_to_server(self, model_id, obj_content, mtl_content, texture_data):
        """모델을 웹서버에 저장"""
        file_paths = {}
        
        # OBJ 파일 업로드
        obj_path = self.upload_file(obj_content, "model.obj", model_id)
        if obj_path:
            file_paths['obj_path'] = obj_path
        else:
            return None
        
        # MTL 파일 업로드
        mtl_path = self.upload_file(mtl_content, "model.mtl", model_id)
        if mtl_path:
            file_paths['mtl_path'] = mtl_path
        else:
            return None
        
        # 텍스처 파일들 업로드
        texture_paths = []
        for texture_name, texture_content in texture_data.items():
            texture_path = self.upload_file(texture_content, texture_name, model_id)
            if texture_path:
                texture_paths.append(texture_path)
            else:
                # 업로드 실패 시 이미 업로드된 파일들 삭제
                self.delete_model(model_id)
                return None
        
        file_paths['texture_paths'] = texture_paths
        return file_paths
    
    def load_model_from_server(self, file_paths):
        """웹서버에서 모델 로드"""
        try:
            # OBJ 파일 다운로드
            obj_content = self.download_file(file_paths['obj_path'])
            if obj_content:
                obj_content = obj_content.decode('utf-8')
            else:
                return None, None, None
            
            # MTL 파일 다운로드
            mtl_content = self.download_file(file_paths['mtl_path'])
            if mtl_content:
                mtl_content = mtl_content.decode('utf-8')
            else:
                return None, None, None
            
            # 텍스처 파일들 다운로드
            texture_data = {}
            for texture_path in file_paths['texture_paths']:
                texture_name = os.path.basename(texture_path)
                texture_content = self.download_file(texture_path)
                if texture_content:
                    texture_data[texture_name] = texture_content
                else:
                    return None, None, None
            
            return obj_content, mtl_content, texture_data
            
        except Exception as e:
            st.error(f"모델 로드 중 오류: {str(e)}")
            return None, None, None

# 로컬 백업 저장소 (웹서버 실패 시 사용)
class LocalBackupStorage:
    def __init__(self):
        self.base_path = "data/models"
        os.makedirs(self.base_path, exist_ok=True)
    
    def save_model_backup(self, model_id, obj_content, mtl_content, texture_data):
        """로컬에 백업 저장"""
        model_dir = os.path.join(self.base_path, model_id)
        os.makedirs(model_dir, exist_ok=True)
        
        try:
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
            
        except Exception as e:
            st.error(f"로컬 백업 저장 실패: {str(e)}")
            return None
    
    def load_model_backup(self, file_paths):
        """로컬 백업에서 로드"""
        try:
            # OBJ 파일 읽기
            with open(file_paths['obj_path'], 'r') as f:
                obj_content = f.read()
            
            # MTL 파일 읽기
            with open(file_paths['mtl_path'], 'r') as f:
                mtl_content = f.read()
            
            # 텍스처 파일들 읽기
            texture_data = {}
            for texture_path in file_paths['texture_paths']:
                texture_name = os.path.basename(texture_path)
                with open(texture_path, 'rb') as f:
                    texture_data[texture_name] = f.read()
            
            return obj_content, mtl_content, texture_data
            
        except Exception as e:
            st.error(f"로컬 백업 로드 실패: {str(e)}")
            return None, None, None
    
    def delete_model_backup(self, model_id):
        """로컬 백업 삭제"""
        model_dir = os.path.join(self.base_path, model_id)
        if os.path.exists(model_dir):
            import shutil
            shutil.rmtree(model_dir)
            return True
        return False
