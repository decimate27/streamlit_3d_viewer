#!/usr/bin/env python3
"""
멀티 텍스처 수정 테스트
"""

def test_viewer_utils_fix():
    """viewer_utils.py의 수정사항 확인"""
    
    print("🔧 멀티 텍스처 수정 확인")
    print("=" * 50)
    
    with open('viewer_utils.py', 'r') as f:
        content = f.read()
    
    # 수정된 부분 확인
    checks = {
        "material.map.sourceFile": "✅ sourceFile 체크 추가됨",
        "Material ${materialName} -> Texture": "✅ 텍스처 매핑 로그 추가됨",
        "✅ Texture applied": "✅ 적용 성공 로그 추가됨",
        "⚠️ Texture not found": "✅ 텍스처 없음 경고 추가됨",
        "MTLLoader requesting texture": "✅ MTL 로더 디버깅 추가됨",
        "Final Material Check": "✅ 최종 재질 확인 추가됨"
    }
    
    for check_str, message in checks.items():
        if check_str in content:
            print(f"  {message}")
        else:
            print(f"  ❌ {check_str} 찾을 수 없음")
    
    print("\n📝 주요 수정 내용:")
    print("  1. 모든 material에 첫 번째 텍스처만 적용하는 버그 수정")
    print("  2. MTL에서 지정한 올바른 텍스처 파일명 사용")
    print("  3. 디버깅 로그 추가로 문제 추적 가능")
    print("  4. 최종 재질 상태 확인 기능 추가")
    
    print("\n🚀 테스트 방법:")
    print("  1. streamlit run app.py 실행")
    print("  2. 멀티 텍스처 모델 업로드")
    print("  3. 브라우저 개발자 콘솔에서 로그 확인")
    print("  4. 각 Material이 올바른 텍스처를 사용하는지 확인")

if __name__ == "__main__":
    test_viewer_utils_fix()
