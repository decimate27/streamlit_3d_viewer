"""
웹서버 DB와 로컬 DB 동기화 모듈
웹서버의 streamlit_3d.db를 다운로드하여 로컬 DB와 동기화합니다.
"""

import sqlite3
import requests
import tempfile
import os
import json
import streamlit as st
from datetime import datetime
import shutil

class WebDBSync:
    def __init__(self):
        # 웹서버의 DB 직접 접근 URL
        self.web_db_url = "https://www.airbible.kr/streamlit_data/streamlit_3d.db"
        # API 대체 URL (DB 직접 접근 실패 시)
        self.api_base_url = "https://www.airbible.kr/streamlit_data"
        self.get_models_url = f"{self.api_base_url}/get_all_models.php"
        self.local_db_path = "data/models.db"
        self.temp_db_path = None
        
    def download_web_db(self):
        """웹서버에서 DB 파일 다운로드"""
        try:
            st.info("🌐 웹서버 DB 다운로드 중...")
            
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
                self.temp_db_path = tmp_file.name
                
                # 헤더 추가하여 DB 파일 다운로드
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Referer': 'https://www.airbible.kr/'
                }
                
                response = requests.get(self.web_db_url, headers=headers, timeout=30, verify=False)
                response.raise_for_status()
                
                tmp_file.write(response.content)
                
            st.success(f"✅ 웹서버 DB 다운로드 완료 (크기: {len(response.content):,} bytes)")
            return True
            
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ DB 직접 다운로드 실패, API 사용 시도 중...")
            # API를 통한 대체 방법 시도
            return self.download_via_api()
        except Exception as e:
            st.error(f"❌ 예상치 못한 오류: {str(e)}")
            return False
    
    def download_via_api(self):
        """API를 통해 모델 데이터 가져오기 (대체 방법)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(self.get_models_url, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.web_models_data = data.get('models', [])
                    st.success(f"✅ API를 통해 {len(self.web_models_data)}개 모델 정보 수신")
                    return True
            
            st.error("❌ API 응답 오류")
            return False
            
        except Exception as e:
            st.error(f"❌ API 접근 실패: {str(e)}")
            return False
    
    def analyze_databases(self):
        """로컬 DB와 웹서버 DB 비교 분석"""
        if not self.temp_db_path or not os.path.exists(self.temp_db_path):
            st.error("웹서버 DB가 다운로드되지 않았습니다.")
            return None
            
        analysis = {
            'local_models': [],
            'web_models': [],
            'missing_models': [],
            'local_count': 0,
            'web_count': 0,
            'sync_needed': False
        }
        
        try:
            # 로컬 DB 분석
            if os.path.exists(self.local_db_path):
                conn_local = sqlite3.connect(self.local_db_path)
                cursor_local = conn_local.cursor()
                
                cursor_local.execute("SELECT id, name, author, created_at FROM models")
                local_models = cursor_local.fetchall()
                analysis['local_models'] = local_models
                analysis['local_count'] = len(local_models)
                
                local_ids = set(model[0] for model in local_models)
                conn_local.close()
            else:
                local_ids = set()
                
            # 웹서버 DB 분석
            conn_web = sqlite3.connect(self.temp_db_path)
            cursor_web = conn_web.cursor()
            
            cursor_web.execute("SELECT id, name, author, created_at FROM models ORDER BY created_at")
            web_models = cursor_web.fetchall()
            analysis['web_models'] = web_models
            analysis['web_count'] = len(web_models)
            
            # 누락된 모델 찾기
            for model in web_models:
                if model[0] not in local_ids:
                    analysis['missing_models'].append(model)
                    
            analysis['sync_needed'] = len(analysis['missing_models']) > 0
            conn_web.close()
            
            return analysis
            
        except Exception as e:
            st.error(f"❌ DB 분석 중 오류: {str(e)}")
            return None
    
    def convert_web_to_local_format(self, web_data):
        """웹서버 DB 형식을 로컬 DB 형식으로 변환"""
        # 웹서버 DB 스키마:
        # id, name, author, description, share_token, obj_path, mtl_path, texture_paths, storage_type, access_count, created_at
        
        # 로컬 DB 스키마:
        # id, name, author, description, file_paths, backup_paths, storage_type, share_token, created_at, last_accessed, access_count, real_height
        
        id_val = web_data[0]
        name = web_data[1]
        author = web_data[2]
        description = web_data[3]
        share_token = web_data[4]
        obj_path = web_data[5]
        mtl_path = web_data[6]
        texture_paths = web_data[7]
        storage_type = web_data[8] or 'web'
        access_count = web_data[9]
        created_at = web_data[10]
        
        # file_paths JSON 생성 (웹서버 경로 형식)
        file_paths = {
            "obj_path": f"{id_val}/model.obj",
            "mtl_path": f"{id_val}/model.mtl",
            "texture_paths": []
        }
        
        # 텍스처 경로 처리
        if texture_paths:
            try:
                # JSON 형식인 경우
                if texture_paths.startswith('['):
                    texture_list = json.loads(texture_paths)
                else:
                    # 단일 경로인 경우
                    texture_list = [texture_paths]
                    
                for tex_path in texture_list:
                    # files/ 경로 제거하고 모델 ID 이후 부분만 추출
                    if 'files/' in tex_path:
                        # files/model_id/texture.png -> model_id/texture.png
                        clean_path = tex_path.replace('files/', '')
                    else:
                        clean_path = tex_path
                    
                    # 파일명만 추출하여 경로 구성
                    filename = os.path.basename(clean_path)
                    if filename:
                        file_paths["texture_paths"].append(f"{id_val}/{filename}")
            except:
                # 파싱 실패 시 빈 리스트
                pass
        
        # backup_paths JSON 생성 (로컬 백업 경로)
        backup_paths = {
            "obj_path": f"data/models/{id_val}/model.obj",
            "mtl_path": f"data/models/{id_val}/model.mtl",
            "texture_paths": []
        }
        
        for tex_path in file_paths["texture_paths"]:
            filename = os.path.basename(tex_path)
            if filename:
                backup_paths["texture_paths"].append(f"data/models/{id_val}/{filename}")
        
        return (
            id_val,
            name,
            author,
            description,
            json.dumps(file_paths),
            json.dumps(backup_paths),
            storage_type,
            share_token,
            created_at,
            None,  # last_accessed
            access_count,
            1.0    # real_height (기본값)
        )
    
    def sync_databases(self, show_progress=True):
        """웹서버 DB와 로컬 DB 동기화"""
        try:
            # 1. 웹서버 DB 다운로드
            if not self.download_web_db():
                return False
                
            # 2. DB 분석
            analysis = self.analyze_databases()
            if not analysis:
                return False
                
            # 3. 동기화 상태 표시
            if show_progress:
                st.write("📊 **동기화 분석 결과:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("로컬 DB", f"{analysis['local_count']}개 모델")
                with col2:
                    st.metric("웹서버 DB", f"{analysis['web_count']}개 모델")
                with col3:
                    st.metric("복구 필요", f"{len(analysis['missing_models'])}개 모델")
            
            # 4. 동기화 필요 없으면 종료
            if not analysis['sync_needed']:
                st.success("✅ 이미 동기화된 상태입니다.")
                return True
                
            # 5. 누락된 모델 복구
            if show_progress:
                st.info(f"🔄 {len(analysis['missing_models'])}개 모델 복구 중...")
                
            # 웹서버 DB에서 전체 데이터 가져오기
            conn_web = sqlite3.connect(self.temp_db_path)
            cursor_web = conn_web.cursor()
            
            cursor_web.execute("""
                SELECT id, name, author, description, share_token, 
                       obj_path, mtl_path, texture_paths, storage_type, 
                       access_count, created_at 
                FROM models
                WHERE id IN ({})
            """.format(','.join(['?'] * len(analysis['missing_models']))),
                [model[0] for model in analysis['missing_models']])
            
            missing_data = cursor_web.fetchall()
            conn_web.close()
            
            # 로컬 DB에 삽입
            conn_local = sqlite3.connect(self.local_db_path)
            cursor_local = conn_local.cursor()
            
            recovered_count = 0
            for web_data in missing_data:
                try:
                    # 데이터 형식 변환
                    local_data = self.convert_web_to_local_format(web_data)
                    
                    # 로컬 DB에 삽입
                    cursor_local.execute("""
                        INSERT OR IGNORE INTO models (
                            id, name, author, description, file_paths, backup_paths,
                            storage_type, share_token, created_at, last_accessed, 
                            access_count, real_height
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, local_data)
                    
                    if show_progress:
                        st.success(f"✅ 복구: {web_data[1]} by {web_data[2]}")
                    recovered_count += 1
                    
                except Exception as e:
                    st.error(f"❌ 복구 실패: {web_data[1]} - {str(e)}")
            
            conn_local.commit()
            conn_local.close()
            
            # 6. 결과 표시
            if show_progress:
                st.success(f"🎉 동기화 완료! {recovered_count}개 모델이 복구되었습니다.")
                
            return True
            
        except Exception as e:
            st.error(f"❌ 동기화 중 오류 발생: {str(e)}")
            return False
            
        finally:
            # 임시 파일 정리
            if self.temp_db_path and os.path.exists(self.temp_db_path):
                try:
                    os.remove(self.temp_db_path)
                except:
                    pass
    
    def quick_sync_check(self):
        """빠른 동기화 필요 여부 확인 (UI 표시 없음)"""
        try:
            # 웹서버 DB 다운로드 (조용히)
            response = requests.get(self.web_db_url, timeout=10)
            if response.status_code != 200:
                return False
                
            # 임시 파일에 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
                tmp_path = tmp_file.name
                tmp_file.write(response.content)
            
            # 웹서버 DB 모델 수 확인
            conn_web = sqlite3.connect(tmp_path)
            cursor_web = conn_web.cursor()
            cursor_web.execute("SELECT COUNT(*) FROM models")
            web_count = cursor_web.fetchone()[0]
            conn_web.close()
            
            # 로컬 DB 모델 수 확인
            local_count = 0
            if os.path.exists(self.local_db_path):
                conn_local = sqlite3.connect(self.local_db_path)
                cursor_local = conn_local.cursor()
                cursor_local.execute("SELECT COUNT(*) FROM models")
                local_count = cursor_local.fetchone()[0]
                conn_local.close()
            
            # 임시 파일 삭제
            os.remove(tmp_path)
            
            # 동기화 필요 여부 반환
            return web_count > local_count
            
        except:
            return False