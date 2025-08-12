import sys
import os
sys.path.append(os.getcwd())

from database import ModelDatabase
import uuid
import secrets

# 데이터베이스 연결
db = ModelDatabase('data/models.db')

# 새 모델 추가
model_id = str(uuid.uuid4())
share_token = secrets.token_urlsafe(8)

# 모델 데이터 준비
model_data = {
    'id': model_id,
    'name': 'Coca Cola Test',
    'description': 'Test model for viewer',
    'file_paths': 'data/coca-cola.obj,data/coca-cola.mtl,data/coca-cola-zero.jpg',
    'backup_paths': '',
    'storage_type': 'local',
    'share_token': share_token,
    'author': 'Test'
}

# SQL 쿼리 실행
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute('''
    INSERT INTO models (id, name, description, file_paths, backup_paths, storage_type, share_token, author)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (model_data['id'], model_data['name'], model_data['description'], 
      model_data['file_paths'], model_data['backup_paths'], 
      model_data['storage_type'], model_data['share_token'], model_data['author']))

conn.commit()
conn.close()

print(f'Model added successfully!')
print(f'Share URL: http://localhost:8501/viewer?token={share_token}')
