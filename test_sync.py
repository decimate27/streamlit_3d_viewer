#!/usr/bin/env python3
"""
웹서버 DB 동기화 테스트 스크립트
"""

import sqlite3
import os
from web_db_sync import WebDBSync
from database import ModelDatabase

def test_sync():
    """동기화 기능 테스트"""
    print("="*50)
    print("🧪 웹서버 DB 동기화 테스트")
    print("="*50)
    
    # 1. 현재 로컬 DB 상태 확인
    print("\n1️⃣ 현재 로컬 DB 상태:")
    if os.path.exists("data/models.db"):
        conn = sqlite3.connect("data/models.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM models")
        local_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT id, name, author FROM models")
        local_models = cursor.fetchall()
        conn.close()
        
        print(f"   - 로컬 모델 수: {local_count}개")
        for model in local_models:
            print(f"     • {model[1]} by {model[2]}")
    else:
        print("   - 로컬 DB 파일이 없습니다.")
        local_count = 0
    
    # 2. WebDBSync 테스트
    print("\n2️⃣ WebDBSync 클래스 테스트:")
    sync = WebDBSync()
    
    # 웹서버 DB 다운로드
    print("   - 웹서버 DB 다운로드 중...")
    if sync.download_web_db():
        print("   ✅ 다운로드 성공")
        
        # DB 분석
        print("\n   - DB 분석 중...")
        analysis = sync.analyze_databases()
        
        if analysis:
            print(f"   - 웹서버 모델: {analysis['web_count']}개")
            print(f"   - 로컬 모델: {analysis['local_count']}개")
            print(f"   - 복구 필요: {len(analysis['missing_models'])}개")
            
            if analysis['missing_models']:
                print("\n   누락된 모델:")
                for model in analysis['missing_models']:
                    print(f"     • {model[1]} by {model[2]} ({model[3]})")
        else:
            print("   ❌ DB 분석 실패")
    else:
        print("   ❌ 다운로드 실패")
    
    # 3. ModelDatabase 자동 동기화 테스트
    print("\n3️⃣ ModelDatabase 자동 동기화 테스트:")
    print("   - ModelDatabase(auto_sync=True) 실행...")
    
    db = ModelDatabase(auto_sync=True)
    
    # 동기화 후 상태 확인
    print("\n   - 동기화 후 상태:")
    models = db.get_all_models()
    print(f"   - 총 모델 수: {len(models)}개")
    
    for model in models:
        storage_type = model.get('storage_type', 'unknown')
        print(f"     • {model['name']} by {model.get('author', 'Unknown')} [{storage_type}]")
    
    # 4. 수동 동기화 테스트
    print("\n4️⃣ 수동 동기화 테스트:")
    print("   - db.sync_with_web_db(show_progress=False) 실행...")
    
    if db.sync_with_web_db(show_progress=False):
        print("   ✅ 수동 동기화 성공")
    else:
        print("   ❌ 수동 동기화 실패")
    
    # 최종 상태
    print("\n5️⃣ 최종 상태:")
    final_count = db.get_model_count()
    print(f"   - 최종 모델 수: {final_count}개")
    
    if final_count > local_count:
        print(f"   ✅ {final_count - local_count}개 모델이 복구되었습니다!")
    else:
        print("   ℹ️ 이미 동기화된 상태입니다.")
    
    print("\n" + "="*50)
    print("테스트 완료!")
    print("="*50)

if __name__ == "__main__":
    test_sync()