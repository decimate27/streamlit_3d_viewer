#!/usr/bin/env python3
import sqlite3
import os

# 데이터베이스 파일 경로
db_path = 'models.db'

# 기존 DB 삭제
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"기존 {db_path} 삭제됨")

# 새 연결 생성
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# models 테이블 생성
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
print("✅ models 테이블 생성됨")

# annotations 테이블 생성
cursor.execute('''
    CREATE TABLE IF NOT EXISTS annotations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_token TEXT NOT NULL,
        position_x REAL NOT NULL,
        position_y REAL NOT NULL,
        position_z REAL NOT NULL,
        text TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (model_token) REFERENCES models(share_token) ON DELETE CASCADE
    )
''')
print("✅ annotations 테이블 생성됨")

# 커밋 및 닫기
conn.commit()

# 테이블 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\n생성된 테이블들:")
for table in tables:
    print(f"  - {table[0]}")

# annotations 테이블 스키마 확인
cursor.execute("PRAGMA table_info(annotations)")
schema = cursor.fetchall()
print("\nannotations 테이블 스키마:")
for col in schema:
    print(f"  - {col[1]} {col[2]} {'(PRIMARY KEY)' if col[5] else ''}")

conn.close()
print(f"\n✅ {db_path} 데이터베이스 초기화 완료!")
