#!/usr/bin/env python3
"""
텍스처 최적화 테스트 및 수정된 기능 확인
"""

from texture_optimizer import auto_optimize_textures
import io
from PIL import Image

def test_large_png():
    """큰 PNG 파일 최적화 테스트"""
    print("🧪 큰 PNG 파일 최적화 테스트")
    print("=" * 50)
    
    # 7000x7000 RGB 이미지 생성 (투명도 없음)
    test_image = Image.new('RGB', (7000, 7000), color=(255, 100, 100))
    output = io.BytesIO()
    test_image.save(output, format='PNG')
    
    test_data = {
        'large_test.png': output.getvalue()
    }
    
    original_size = len(test_data['large_test.png'])
    print(f"원본: large_test.png - {original_size:,} bytes ({original_size/(1024*1024):.1f}MB)")
    
    # 최적화 실행
    optimized_data, success = auto_optimize_textures(test_data, max_size=1024, quality=80)
    
    print(f"\n최적화 결과:")
    for filename, data in optimized_data.items():
        new_size = len(data)
        compression_ratio = (1 - new_size/original_size) * 100
        print(f"- {filename}: {new_size:,} bytes ({compression_ratio:.1f}% 감소)")
    
    return optimized_data

def test_rgba_png():
    """투명도가 있는 PNG 파일 테스트"""
    print("\n🧪 투명도 PNG 파일 최적화 테스트")
    print("=" * 50)
    
    # RGBA 이미지 생성 (투명도 있음)
    test_image = Image.new('RGBA', (2048, 2048), color=(255, 100, 100, 128))
    output = io.BytesIO()
    test_image.save(output, format='PNG')
    
    test_data = {
        'transparent_test.png': output.getvalue()
    }
    
    original_size = len(test_data['transparent_test.png'])
    print(f"원본: transparent_test.png - {original_size:,} bytes ({original_size/(1024*1024):.1f}MB)")
    
    # 최적화 실행
    optimized_data, success = auto_optimize_textures(test_data, max_size=1024, quality=80)
    
    print(f"\n최적화 결과:")
    for filename, data in optimized_data.items():
        new_size = len(data)
        compression_ratio = (1 - new_size/original_size) * 100
        print(f"- {filename}: {new_size:,} bytes ({compression_ratio:.1f}% 감소)")
    
    return optimized_data

if __name__ == "__main__":
    # 큰 RGB PNG 테스트 (JPEG로 변환되어야 함)
    rgb_result = test_large_png()
    
    # 투명도 PNG 테스트 (PNG로 유지되어야 함)
    rgba_result = test_rgba_png()
    
    print(f"\n📊 테스트 완료!")
    print(f"RGB PNG → JPEG 변환: {'✅' if any('.jpg' in name for name in rgb_result.keys()) else '❌'}")
    print(f"RGBA PNG → PNG 유지: {'✅' if any('.png' in name for name in rgba_result.keys()) else '❌'}")
