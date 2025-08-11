import json
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
import sqlite3
from web_storage import WebServerStorage, LocalBackupStorage
import streamlit as st

def reset_database(db_path="data/models.db"):
    """데이터베이스 완전 초기화 (문제 해결용)"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        st.write(f"🔄 기존 DB를 {backup_path}로 백업")
        os.remove(db_path)
    
    # 새 데이터베이스 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            file_paths TEXT NOT NULL,
            backup_paths TEXT,
            storage_type TEXT DEFAULT 'local',
            share_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP,
            access_count INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    st.success("✅ 새 데이터베이스 생성 완료")

class ModelDatabase:
    def __init__(self, db_path="data/models.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
        self.web_storage = WebServerStorage()
        self.local_backup = LocalBackupStorage()
    
    def init_db(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 테이블 구조 확인
        cursor.execute("PRAGMA table_info(models)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if not columns:
            # 새 테이블 생성
            cursor.execute('''
                CREATE TABLE models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    file_paths TEXT NOT NULL,
                    backup_paths TEXT,
                    storage_type TEXT DEFAULT 'web',
                    share_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            ''')
            st.write("🆕 새 데이터베이스 테이블 생성")
        else:
            # 구 스키마 감지 시 테이블 재생성
            if 'obj_path' in columns and 'file_paths' not in columns:
                st.write("🔄 구 스키마 감지 - 테이블 마이그레이션 시작")
                
                # 기존 데이터 백업
                cursor.execute('SELECT * FROM models')
                old_data = cursor.fetchall()
                
                # 기존 테이블 삭제
                cursor.execute('DROP TABLE models')
                
                # 새 테이블 생성
                cursor.execute('''
                    CREATE TABLE models (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        file_paths TEXT NOT NULL,
                        backup_paths TEXT,
                        storage_type TEXT DEFAULT 'local',
                        share_token TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP,
                        access_count INTEGER DEFAULT 0
                    )
                ''')
                
                # 기존 데이터 복원 (구 형식 → 신 형식)
                for row in old_data:
                    try:
                        # 안전하게 데이터 추출
                        obj_path = row[3] if len(row) > 3 and row[3] else ""
                        mtl_path = row[4] if len(row) > 4 and row[4] else ""
                        texture_paths_raw = row[5] if len(row) > 5 and row[5] else "[]"
                        
                        # JSON 파싱 안전하게 처리
                        try:
                            texture_paths = json.loads(texture_paths_raw)
                        except:
                            texture_paths = []
                        
                        old_file_paths = {
                            'obj_path': obj_path,
                            'mtl_path': mtl_path,
                            'texture_paths': texture_paths
                        }
                        
                        # share_token이 없으면 새로 생성
                        share_token = row[6] if len(row) > 6 and row[6] else str(uuid.uuid4())
                        created_at = row[7] if len(row) > 7 and row[7] else datetime.now().isoformat()
                        access_count = row[9] if len(row) > 9 else 0
                        
                        cursor.execute('''
                            INSERT INTO models (id, name, description, file_paths, 
                                              storage_type, share_token, created_at, access_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (row[0], row[1], row[2], json.dumps(old_file_paths), 
                              'local', share_token, created_at, access_count))
                    except Exception as e:
                        st.warning(f"데이터 마이그레이션 중 일부 오류: {str(e)}")
                        st.write(f"문제 행 데이터: {row}")
                
                st.success("✅ 데이터베이스 마이그레이션 완료")
            
            elif 'storage_type' not in columns:
                # storage_type 컬럼만 추가
                cursor.execute('ALTER TABLE models ADD COLUMN storage_type TEXT DEFAULT "local"')
                st.write("📝 storage_type 컬럼 추가")
        
        conn.commit()
        conn.close()
    
    def save_model(self, name, description, obj_content, mtl_content, texture_data):
        """모델 저장 (웹서버 + 로컬 백업)"""
        model_id = str(uuid.uuid4())
        share_token = str(uuid.uuid4())
        
        st.write(f"🚀 모델 저장 시작: {model_id}")
        
        # 웹서버에 저장 시도
        st.write("🌐 웹서버 저장 시도 중...")
        file_paths = self.web_storage.save_model_to_server(
            model_id, obj_content, mtl_content, texture_data
        )
        
        storage_type = 'web'
        backup_paths = None
        
        if file_paths:
            st.success("✅ 웹서버 저장 성공!")
            st.write(f"웹서버 경로: {file_paths}")
            
            # 성공 시 로컬 백업도 저장
            st.write("💾 로컬 백업 저장 중...")
            backup_paths = self.local_backup.save_model_backup(
                model_id, obj_content, mtl_content, texture_data
            )
            if backup_paths:
                st.write("✅ 로컬 백업 완료")
        else:
            st.error("❌ 웹서버 저장 실패 - 로컬 저장으로 폴백")
            # 웹서버 실패 시 로컬에만 저장
            file_paths = self.local_backup.save_model_backup(
                model_id, obj_content, mtl_content, texture_data
            )
            storage_type = 'local'
            
            if not file_paths:
                raise Exception("파일 저장에 실패했습니다.")
            st.warning("⚠️ 로컬 저장으로 처리됨 (임시)")
        
        # 데이터베이스에 저장
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO models (id, name, description, file_paths, backup_paths, 
                              storage_type, share_token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (model_id, name, description, json.dumps(file_paths), 
              json.dumps(backup_paths) if backup_paths else None, 
              storage_type, share_token))
        
        conn.commit()
        conn.close()
        
        st.write(f"💾 데이터베이스 저장 완료 - 저장 타입: {storage_type}")
        
        return model_id, share_token
    
    def get_all_models(self):
        """모든 모델 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 테이블 구조 확인
        cursor.execute("PRAGMA table_info(models)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'storage_type' in columns:
            # 새 스키마
            cursor.execute('''
                SELECT id, name, description, created_at, access_count, share_token, storage_type
                FROM models ORDER BY created_at DESC
            ''')
        else:
            # 구 스키마 (호환성)
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
                'share_token': row[5],
                'storage_type': row[6] if len(row) > 6 else 'local'
            })
        
        conn.close()
        return models
    
    def get_model_by_token(self, share_token):
        """공유 토큰으로 모델 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 테이블 구조 확인
        cursor.execute("PRAGMA table_info(models)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'file_paths' in columns:
            # 새 스키마
            cursor.execute('''
                SELECT id, name, description, file_paths, backup_paths, storage_type
                FROM models WHERE share_token = ?
            ''', (share_token,))
        else:
            # 구 스키마 (호환성)
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
            
            if 'file_paths' in columns:
                # 새 스키마
                model = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'file_paths': json.loads(row[3]) if row[3] else {},
                    'backup_paths': json.loads(row[4]) if row[4] else None,
                    'storage_type': row[5] if len(row) > 5 else 'local'
                }
            else:
                # 구 스키마 (호환성)
                model = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'obj_path': row[3],
                    'mtl_path': row[4],
                    'texture_paths': json.loads(row[5]),
                    'storage_type': 'local'
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
        cursor.execute('''
            SELECT storage_type, backup_paths FROM models WHERE id = ?
        ''', (model_id,))
        row = cursor.fetchone()
        
        if row:
            storage_type = row[0] if row[0] else 'local'
            backup_paths = row[1] if len(row) > 1 else None
            
            # 웹서버에서 삭제
            if storage_type == 'web':
                self.web_storage.delete_model(model_id)
            
            # 로컬 백업 삭제
            if backup_paths:
                self.local_backup.delete_model_backup(model_id)
            elif storage_type == 'local':
                self.local_backup.delete_model_backup(model_id)
            
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
    web_storage = WebServerStorage()
    local_backup = LocalBackupStorage()
    
    storage_type = model_data.get('storage_type', 'local')
    
    if storage_type == 'web':
        # 웹서버에서 로드 시도
        result = web_storage.load_model_from_server(model_data['file_paths'])
        
        if result[0] is not None:  # 성공
            return result
        
        # 웹서버 실패 시 로컬 백업에서 로드
        if model_data.get('backup_paths'):
            return local_backup.load_model_backup(model_data['backup_paths'])
    else:
        # 구 형식 호환성 - obj_path가 있으면 구 형식
        if 'obj_path' in model_data:
            # 기존 로컬 저장 방식
            with open(model_data['obj_path'], 'r') as f:
                obj_content = f.read()
            
            with open(model_data['mtl_path'], 'r') as f:
                mtl_content = f.read()
            
            texture_data = {}
            for texture_path in model_data['texture_paths']:
                texture_name = os.path.basename(texture_path)
                with open(texture_path, 'rb') as f:
                    texture_data[texture_name] = f.read()
            
            return obj_content, mtl_content, texture_data
        else:
            # 새 로컬 백업 방식
            return local_backup.load_model_backup(model_data['file_paths'])
    
    return None, None, None

def generate_share_url(share_token, base_url=None):
    """공유 URL 생성"""
    if base_url is None:
        base_url = "https://airbible-3d-viewer.streamlit.app"
    
    return f"{base_url}?token={share_token}"
