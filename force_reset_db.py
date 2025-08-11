#!/usr/bin/env python3
"""
데이터베이스 스키마 문제 강제 해결
"""

import os
import sqlite3
import json
from datetime import datetime

def force_reset_database():
    """데이터베이스를 완전히 새로 만들기"""
    db_path = "data/models.db"
    
    print("🔄 데이터베이스 강제 초기화 시작")
    
    # 기존 DB 백업
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📦 기존 DB 백업: {backup_path}")
        
        # 기존 DB 삭제
        os.remove(db_path)
        print("🗑️ 기존 DB 삭제")
    
    # 새 DB 생성
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 새 스키마로 테이블 생성
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
    
    conn.commit()
    conn.close()
    
    print("✅ 새 데이터베이스 생성 완료!")
    print("이제 웹서버 저장이 정상 작동할 것입니다.")

if __name__ == "__main__":
    force_reset_database()
