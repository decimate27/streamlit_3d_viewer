import json
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
import sqlite3

class ModelDatabase:
    def __init__(self, db_path="data/models.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                obj_path TEXT NOT NULL,
                mtl_path TEXT NOT NULL,
                texture_paths TEXT NOT NULL,
                share_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_model(self, name, description, obj_content, mtl_content, texture_data):
        """모델 저장"""
        model_id = str(uuid.uuid4())
        share_token = str(uuid.uuid4())
        
        # 파일 저장 디렉토리 생성
        model_dir = f"data/models/{model_id}"
        os.makedirs(model_dir, exist_ok=True)
        
        # 파일들 저장
        obj_path = f"{model_dir}/model.obj"
        mtl_path = f"{model_dir}/model.mtl"
        
        with open(obj_path, 'w') as f:
            f.write(obj_content)
        
        with open(mtl_path, 'w') as f:
            f.write(mtl_content)
        
        # 텍스처 파일들 저장
        texture_paths = []
        for texture_name, texture_content in texture_data.items():
            texture_path = f"{model_dir}/{texture_name}"
            with open(texture_path, 'wb') as f:
                f.write(texture_content)
            texture_paths.append(texture_path)
        
        # 데이터베이스에 저장
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO models (id, name, description, obj_path, mtl_path, 
                              texture_paths, share_token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (model_id, name, description, obj_path, mtl_path, 
              json.dumps(texture_paths), share_token))
        
        conn.commit()
        conn.close()
        
        return model_id, share_token
    
    def get_all_models(self):
        """모든 모델 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, created_at, access_count, share_token
            FROM models ORDER BY created_at DESC
        ''')
        
        models = []
        for row in cursor.fetchall():
            models.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'created_at': row[3],
                'access_count': row[4],
                'share_token': row[5]
            })
        
        conn.close()
        return models
    
    def get_model_by_token(self, share_token):
        """공유 토큰으로 모델 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, obj_path, mtl_path, texture_paths
            FROM models WHERE share_token = ?
        ''', (share_token,))
        
        row = cursor.fetchone()
        if row:
            # 접근 횟수 증가
            cursor.execute('''
                UPDATE models 
                SET access_count = access_count + 1, 
                    last_accessed = CURRENT_TIMESTAMP
                WHERE share_token = ?
            ''', (share_token,))
            conn.commit()
            
            model = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'obj_path': row[3],
                'mtl_path': row[4],
                'texture_paths': json.loads(row[5])
            }
        else:
            model = None
        
        conn.close()
        return model
    
    def delete_model(self, model_id):
        """모델 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 모델 정보 조회
        cursor.execute('SELECT obj_path FROM models WHERE id = ?', (model_id,))
        row = cursor.fetchone()
        
        if row:
            # 파일 디렉토리 삭제
            model_dir = os.path.dirname(row[0])
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
            
            # 데이터베이스에서 삭제
            cursor.execute('DELETE FROM models WHERE id = ?', (model_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def get_model_count(self):
        """저장된 모델 수 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM models')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

def load_model_files(model_data):
    """저장된 모델 파일들 로드"""
    # OBJ 파일 읽기
    with open(model_data['obj_path'], 'r') as f:
        obj_content = f.read()
    
    # MTL 파일 읽기
    with open(model_data['mtl_path'], 'r') as f:
        mtl_content = f.read()
    
    # 텍스처 파일들 읽기
    texture_data = {}
    for texture_path in model_data['texture_paths']:
        texture_name = os.path.basename(texture_path)
        with open(texture_path, 'rb') as f:
            texture_data[texture_name] = f.read()
    
    return obj_content, mtl_content, texture_data

def generate_share_url(share_token, base_url=None):
    """공유 URL 생성"""
    if base_url is None:
        # 실제 배포된 앱 URL로 변경 필요
        base_url = "https://share.streamlit.io/decimate27/streamlit_3dviewer/main/app.py"
    
    return f"{base_url}?token={share_token}"
