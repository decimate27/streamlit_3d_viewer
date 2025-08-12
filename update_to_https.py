#!/usr/bin/env python3
"""
HTTPS 적용 후 자동 업데이트 스크립트
모든 HTTP URL을 HTTPS로 변경합니다.
"""

import os
import re

def update_urls_to_https():
    """모든 파일에서 HTTP URL을 HTTPS로 변경"""
    
    files_to_update = [
        'web_database.py',
        'web_storage.py', 
        'viewer_utils.py'
    ]
    
    http_pattern = r'http://decimate27\.dothome\.co\.kr'
    https_replacement = 'https://decimate27.dothome.co.kr'
    
    for filename in files_to_update:
        if os.path.exists(filename):
            print(f"📝 업데이트 중: {filename}")
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # HTTP를 HTTPS로 변경
            updated_content = re.sub(http_pattern, https_replacement, content)
            
            # 변경사항이 있는지 확인
            if content != updated_content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                # 변경된 줄 수 계산
                changes = content.count('http://decimate27.dothome.co.kr')
                print(f"  ✅ {changes}개 URL을 HTTPS로 변경했습니다.")
            else:
                print(f"  ℹ️  변경할 내용이 없습니다.")
        else:
            print(f"  ❌ 파일을 찾을 수 없습니다: {filename}")
    
    print("\n🎉 HTTPS 업데이트 완료!")
    print("이제 Mixed Content 오류 없이 피드백 시스템을 사용할 수 있습니다.")

if __name__ == "__main__":
    print("🔒 HTTPS 서비스 적용 후 자동 업데이트")
    print("=" * 50)
    
    # 현재 디렉토리 확인
    if not os.path.exists('web_database.py'):
        print("❌ 올바른 디렉토리에서 실행해주세요.")
        print("   streamlit_3dviewer 폴더에서 실행하세요.")
        exit(1)
    
    update_urls_to_https()
