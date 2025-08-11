#!/usr/bin/env python3
"""
데이터베이스 오류 수정 스크립트
NOT NULL constraint failed 문제 해결
"""

import os
import sys
from database import reset_database

def main():
    print("🔧 데이터베이스 수정 스크립트")
    print("=" * 40)
    
    try:
        # 현재 데이터베이스 상태 확인
        db_path = "data/models.db"
        if os.path.exists(db_path):
            print(f"📁 기존 데이터베이스 발견: {db_path}")
            print("🔄 초기화 시작...")
        else:
            print("📁 데이터베이스가 없습니다. 새로 생성합니다.")
        
        # 데이터베이스 초기화
        reset_database(db_path)
        
        print("✅ 데이터베이스 수정 완료!")
        print("이제 앱을 다시 실행해보세요.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print("수동으로 data/models.db 파일을 삭제하고 앱을 재시작해보세요.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
