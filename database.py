import json
import os
import uuid
import shutil
from datetime import datetime
import pytz
from pathlib import Path
import sqlite3
from web_storage import WebServerStorage, LocalBackupStorage
from web_db_sync import WebDBSync
import streamlit as st

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def reset_database(db_path="data/models.db"):
    """데이터베이스 완전 초기화 (문제 해결용)"""
    if os.path.exists(db_path):
        kst_now = datetime.now(KST)
        backup_path = f"{db_path}.backup_{kst_now.strftime('%Y%m%d_%H%M%S')}"
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
    def __init__(self, db_path="data/models.db", auto_sync=True):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
        self.web_storage = WebServerStorage()
        self.local_backup = LocalBackupStorage()
        self.web_db_sync = WebDBSync()
        
        # 초기화 시 자동 동기화 (옵션)
        if auto_sync:
            self.auto_sync_with_web()
    
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
                    author TEXT,
                    description TEXT,
                    file_paths TEXT NOT NULL,
                    backup_paths TEXT,
                    storage_type TEXT DEFAULT 'web',
                    share_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    real_height REAL DEFAULT 1.0
                )
            ''')
            st.write("🆕 새 데이터베이스 테이블 생성")
        else:
            # 스키마 문제가 있으면 강제로 새 테이블 생성
            if 'obj_path' in columns or 'file_paths' not in columns:
                st.write("🔄 스키마 문제 감지 - 데이터베이스 재생성")
                
                # 기존 데이터 백업 (선택적)
                try:
                    cursor.execute('SELECT * FROM models')
                    old_data = cursor.fetchall()
                    if old_data:
                        st.write(f"📦 기존 데이터 {len(old_data)}개 발견")
                except:
                    old_data = []
                
                # 기존 테이블 삭제
                cursor.execute('DROP TABLE IF EXISTS models')
                
                # 새 테이블 생성
                cursor.execute('''
                    CREATE TABLE models (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        author TEXT,
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
                
                st.success("✅ 새 스키마로 데이터베이스 재생성 완료")
                
                # 기존 데이터 복원 시도 (구 형식 → 신 형식)
                restored_count = 0
                for row in old_data:
                    try:
                        # 안전하게 데이터 추출
                        if len(row) >= 6:  # 최소 필요 컬럼 수 확인
                            # 구 스키마에서 file_paths 생성
                            if len(row) > 3 and row[3]:  # obj_path가 있는 경우
                                old_file_paths = {
                                    'obj_path': row[3] if len(row) > 3 else "",
                                    'mtl_path': row[4] if len(row) > 4 else "",
                                    'texture_paths': json.loads(row[5]) if len(row) > 5 and row[5] else []
                                }
                            else:
                                continue  # 유효하지 않은 데이터 스킵
                            
                            # share_token 확인
                            share_token = row[6] if len(row) > 6 and row[6] else str(uuid.uuid4())
                            created_at = row[7] if len(row) > 7 and row[7] else datetime.now(KST).isoformat()
                            access_count = row[9] if len(row) > 9 else 0
                            
                            cursor.execute('''
                                INSERT INTO models (id, name, description, file_paths, 
                                                  storage_type, share_token, created_at, access_count)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (row[0], row[1], row[2], json.dumps(old_file_paths), 
                                  'local', share_token, created_at, access_count))
                            restored_count += 1
                    except Exception as e:
                        st.warning(f"데이터 복원 중 일부 오류: {str(e)}")
                        continue
                
                if restored_count > 0:
                    st.write(f"📥 {restored_count}개 기존 데이터 복원 완료")
            
            elif 'storage_type' not in columns:
                # storage_type 컬럼만 추가
                cursor.execute('ALTER TABLE models ADD COLUMN storage_type TEXT DEFAULT "local"')
                st.write("📝 storage_type 컬럼 추가")
            
            # author 컬럼 추가 (없는 경우)
            if 'author' not in columns:
                cursor.execute('ALTER TABLE models ADD COLUMN author TEXT DEFAULT ""')
                st.write("📝 author 컬럼 추가")
                conn.commit()
            
            # real_height 컬럼 추가 (없는 경우)
            if 'real_height' not in columns:
                cursor.execute('ALTER TABLE models ADD COLUMN real_height REAL DEFAULT 1.0')
                st.write("📝 real_height 컬럼 추가 (모델 실제 높이 - 미터)")
                conn.commit()
        
        # annotations 테이블 생성 (존재하지 않을 경우)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_token TEXT NOT NULL,
                position_x REAL NOT NULL,
                position_y REAL NOT NULL,
                position_z REAL NOT NULL,
                text TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_token) REFERENCES models(share_token) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_model(self, name, author, description, obj_content, mtl_content, texture_data, real_height=1.0):
        """모델 저장 (웹서버 + 로컬 백업)"""
        model_id = str(uuid.uuid4()).replace('-', '')  # 하이픈 제거
        share_token = str(uuid.uuid4())
        
        st.write(f"🚀 모델 저장 시작: {model_id}")
        
        # 웹서버에 저장 시도
        st.write("🌐 웹서버 저장 시도 중...")
        file_paths = self.web_storage.save_model_to_server(
            model_id, obj_content, mtl_content, texture_data, 
            name, author, description, share_token, real_height
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
        
        # 한국 시간으로 created_at 설정
        kst_now = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO models (id, name, author, description, file_paths, backup_paths, 
                              storage_type, share_token, real_height, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (model_id, name, author, description, json.dumps(file_paths), 
              json.dumps(backup_paths) if backup_paths else None, 
              storage_type, share_token, real_height, kst_now))
        
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
        
        if 'real_height' in columns:
            # 최신 스키마 (real_height 포함)
            cursor.execute('''
                SELECT id, name, author, description, created_at, access_count, share_token, storage_type, real_height
                FROM models ORDER BY created_at DESC
            ''')
        elif 'storage_type' in columns:
            # 중간 스키마 (real_height 없음)
            cursor.execute('''
                SELECT id, name, author, description, created_at, access_count, share_token, storage_type
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
            if len(row) >= 9:  # 최신 스키마 (real_height 포함)
                models.append({
                    'id': row[0],
                    'name': row[1],
                    'author': row[2],
                    'description': row[3],
                    'created_at': row[4],
                    'access_count': row[5],
                    'share_token': row[6],
                    'storage_type': row[7],
                    'real_height': row[8] if row[8] is not None else 1.0
                })
            elif len(row) >= 8:  # 중간 스키마 (real_height 없음)
                models.append({
                    'id': row[0],
                    'name': row[1],
                    'author': row[2],
                    'description': row[3],
                    'created_at': row[4],
                    'access_count': row[5],
                    'share_token': row[6],
                    'storage_type': row[7],
                    'real_height': 1.0  # 기본값
                })
            elif len(row) >= 7:  # 구 스키마 (author 포함)
                models.append({
                    'id': row[0],
                    'name': row[1],
                    'author': row[2],
                    'description': row[3],
                    'created_at': row[4],
                    'access_count': row[5],
                    'share_token': row[6],
                    'storage_type': 'local',
                    'real_height': 1.0  # 기본값
                })
            else:  # 아주 구 스키마 (author 없음)
                models.append({
                    'id': row[0],
                    'name': row[1],
                    'author': '',  # 기본값
                    'description': row[2],
                    'created_at': row[3],
                    'access_count': row[4],
                    'share_token': row[5],
                    'storage_type': 'local',
                    'real_height': 1.0  # 기본값
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
                SELECT id, name, author, description, file_paths, backup_paths, storage_type, share_token, real_height
                FROM models WHERE share_token = ?
            ''', (share_token,))
        else:
            # 구 스키마 (호환성)
            cursor.execute('''
                SELECT id, name, description, obj_path, mtl_path, texture_paths, share_token
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
                    'author': row[2] if len(row) > 2 else '',
                    'description': row[3] if len(row) > 3 else '',
                    'file_paths': json.loads(row[4]) if len(row) > 4 and row[4] else {},
                    'backup_paths': json.loads(row[5]) if len(row) > 5 and row[5] else None,
                    'storage_type': row[6] if len(row) > 6 else 'local',
                    'share_token': row[7] if len(row) > 7 else share_token,
                    'real_height': row[8] if len(row) > 8 else 1.0
                }
            else:
                # 구 스키마 (호환성)
                model = {
                    'id': row[0],
                    'name': row[1],
                    'author': '',  # 기본값
                    'description': row[2],
                    'obj_path': row[3],
                    'mtl_path': row[4],
                    'texture_paths': json.loads(row[5]),
                    'storage_type': 'local',
                    'share_token': row[6] if len(row) > 6 else share_token
                }
        else:
            model = None
        
        conn.close()
        return model
    
    def delete_model(self, model_id):
        """모델 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 모델 정보 조회 (share_token 포함)
        cursor.execute('''
            SELECT storage_type, backup_paths, share_token FROM models WHERE id = ?
        ''', (model_id,))
        row = cursor.fetchone()
        
        if row:
            storage_type = row[0] if row[0] else 'local'
            backup_paths = row[1] if len(row) > 1 else None
            share_token = row[2] if len(row) > 2 else None
            
            # 웹서버에서 삭제
            if storage_type == 'web':
                self.web_storage.delete_model(model_id)
            
            # 로컬 백업 삭제
            if backup_paths:
                self.local_backup.delete_model_backup(model_id)
            elif storage_type == 'local':
                self.local_backup.delete_model_backup(model_id)
            
            # 해당 모델의 모든 annotations 삭제
            if share_token:
                cursor.execute('DELETE FROM annotations WHERE model_token = ?', (share_token,))
            
            # 데이터베이스에서 모델 삭제
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
    
    # ============ Annotations 관련 메서드 ============
    def add_annotation(self, model_token, position, text):
        """수정점 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO annotations (model_token, position_x, position_y, position_z, text, completed)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (model_token, position['x'], position['y'], position['z'], text))
        
        annotation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return annotation_id
    
    def get_annotations(self, model_token):
        """특정 모델의 모든 수정점 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, position_x, position_y, position_z, text, completed
            FROM annotations
            WHERE model_token = ?
            ORDER BY created_at
        ''', (model_token,))
        
        annotations = []
        for row in cursor.fetchall():
            annotations.append({
                'id': row[0],
                'position': {'x': row[1], 'y': row[2], 'z': row[3]},
                'text': row[4],
                'completed': bool(row[5])
            })
        
        conn.close()
        return annotations
    
    def update_annotation_status(self, annotation_id, completed):
        """수정점 상태 업데이트 (완료/미완료)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE annotations
            SET completed = ?
            WHERE id = ?
        ''', (1 if completed else 0, annotation_id))
        
        conn.commit()
        conn.close()
    
    def delete_annotation(self, annotation_id):
        """수정점 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM annotations WHERE id = ?', (annotation_id,))
        
        conn.commit()
        conn.close()
    
    def delete_model_annotations(self, model_token):
        """모델의 모든 수정점 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM annotations WHERE model_token = ?', (model_token,))
        
        conn.commit()
        conn.close()
    
    def update_model_height(self, model_id, height):
        """모델의 실제 높이 업데이트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE models 
                SET real_height = ?
                WHERE id = ?
            ''', (height, model_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating model height: {e}")
            return False
        finally:
            conn.close()
    
    def sync_with_web_db(self, show_progress=True):
        """웹서버 DB와 수동 동기화"""
        try:
            if show_progress:
                st.info("🔄 웹서버 DB와 동기화를 시작합니다...")
            
            # WebDBSync 클래스를 사용하여 동기화
            success = self.web_db_sync.sync_databases(show_progress=show_progress)
            
            if success and show_progress:
                st.success("✅ 웹서버 DB와 동기화가 완료되었습니다!")
                st.rerun()  # 페이지 새로고침
                
            return success
            
        except Exception as e:
            if show_progress:
                st.error(f"❌ 동기화 중 오류 발생: {str(e)}")
            return False
    
    def auto_sync_with_web(self):
        """앱 시작 시 자동 동기화 (조용히)"""
        try:
            # 동기화 필요 여부 빠르게 확인
            if self.web_db_sync.quick_sync_check():
                # 동기화 필요하면 수행 (UI 표시 없음)
                self.web_db_sync.sync_databases(show_progress=False)
                return True
            return False
        except:
            # 자동 동기화 실패 시 조용히 넘어감
            return False
    
    def get_sync_status(self):
        """동기화 상태 확인"""
        try:
            # 로컬 DB 모델 수
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM models")
            local_count = cursor.fetchone()[0]
            conn.close()
            
            # 웹서버 DB 확인은 필요시에만
            return {
                'local_count': local_count,
                'synced': True  # 기본적으로 동기화됨으로 표시
            }
        except:
            return {
                'local_count': 0,
                'synced': False
            }

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
