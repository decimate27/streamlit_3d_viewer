#!/usr/bin/env python3
"""
텍스처 이미지 최적화 스크립트
큰 텍스처 파일을 압축하여 로딩 속도 개선
"""

from PIL import Image
import os

def optimize_texture(image_path, max_size=1024, quality=85):
    """텍스처 이미지 최적화"""
    print(f"🔍 이미지 최적화: {image_path}")
    
    # 원본 파일 정보
    original_size = os.path.getsize(image_path)
    print(f"   원본 크기: {original_size:,} bytes ({original_size/1024/1024:.1f}MB)")
    
    # 이미지 열기
    with Image.open(image_path) as img:
        print(f"   원본 해상도: {img.size}")
        
        # 이미지 크기 조정 (max_size 이하로)
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"   새 해상도: {img.size}")
        
        # RGB 모드로 변환 (JPEG 저장을 위해)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 백업 생성
        backup_path = f"{image_path}.backup"
        if not os.path.exists(backup_path):
            os.rename(image_path, backup_path)
            print(f"   백업 생성: {backup_path}")
        
        # 최적화된 이미지 저장
        img.save(image_path, 'JPEG', quality=quality, optimize=True)
    
    # 결과 확인
    new_size = os.path.getsize(image_path)
    compression_ratio = (1 - new_size/original_size) * 100
    
    print(f"   최적화 후: {new_size:,} bytes ({new_size/1024/1024:.1f}MB)")
    print(f"   압축률: {compression_ratio:.1f}% 감소")
    
    return new_size < original_size

def main():
    """메인 함수"""
    texture_path = "/Users/bag-wonseog/temp/streamlit_3dviewer/data/bi/santa_5M_low_131209_Material1_color.png"
    
    if not os.path.exists(texture_path):
        print(f"❌ 파일을 찾을 수 없습니다: {texture_path}")
        return
    
    print("🚀 텍스처 이미지 최적화 시작")
    print("=" * 50)
    
    # 이미지 최적화 실행
    success = optimize_texture(texture_path, max_size=1024, quality=80)
    
    if success:
        print("\n✅ 최적화 완료!")
        print("💡 로딩 속도가 크게 개선될 것입니다.")
    else:
        print("\n⚠️ 최적화 실패 또는 불필요")

if __name__ == "__main__":
    main()
