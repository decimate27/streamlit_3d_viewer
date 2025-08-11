#!/usr/bin/env python3
"""
텍스처 최적화 유틸리티
업로드 시 자동으로 텍스처 이미지를 최적화
"""

from PIL import Image
import io
import streamlit as st

def optimize_texture_data(texture_data, max_size=1024, quality=85):
    """
    텍스처 데이터를 최적화
    
    Args:
        texture_data: dict {filename: bytes_data}
        max_size: 최대 이미지 크기 (기본: 1024px)
        quality: JPEG 품질 (기본: 85)
    
    Returns:
        dict: 최적화된 텍스처 데이터
    """
    optimized_data = {}
    optimization_stats = []
    
    for filename, data in texture_data.items():
        try:
            # 원본 크기
            original_size = len(data)
            
            # 이미지 열기
            with Image.open(io.BytesIO(data)) as img:
                original_dimensions = img.size
                
                # 최적화 여부 결정
                needs_optimization = (
                    max(img.size) > max_size or  # 크기가 큰 경우
                    original_size > 2 * 1024 * 1024  # 2MB 이상인 경우
                )
                
                if needs_optimization:
                    st.write(f"🔧 {filename} 최적화 중... (원본: {original_size:,} bytes, {original_dimensions})")
                    
                    # 이미지 크기 조정
                    if max(img.size) > max_size:
                        ratio = max_size / max(img.size)
                        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # RGB 모드로 변환 (JPEG 저장을 위해)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # 투명도가 있는 경우 PNG로 유지하되 크기만 조정
                        output = io.BytesIO()
                        img.save(output, format='PNG', optimize=True)
                        optimized_data[filename] = output.getvalue()
                    else:
                        # 투명도가 없는 경우 JPEG로 압축
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # 파일 확장자를 jpg로 변경
                        if filename.lower().endswith('.png'):
                            new_filename = filename[:-4] + '.jpg'
                        else:
                            new_filename = filename
                        
                        output = io.BytesIO()
                        img.save(output, format='JPEG', quality=quality, optimize=True)
                        optimized_data[new_filename] = output.getvalue()
                    
                    # 최적화 결과
                    new_size = len(optimized_data.get(new_filename, optimized_data[filename]))
                    compression_ratio = (1 - new_size/original_size) * 100
                    
                    optimization_stats.append({
                        'filename': filename,
                        'original_size': original_size,
                        'new_size': new_size,
                        'compression_ratio': compression_ratio,
                        'original_dimensions': original_dimensions,
                        'new_dimensions': img.size
                    })
                    
                    st.success(f"✅ {filename}: {new_size:,} bytes ({compression_ratio:.1f}% 감소)")
                
                else:
                    # 최적화 불필요
                    optimized_data[filename] = data
                    st.info(f"📝 {filename}: 최적화 불필요 ({original_size:,} bytes)")
        
        except Exception as e:
            st.warning(f"⚠️ {filename} 최적화 실패: {str(e)} - 원본 사용")
            optimized_data[filename] = data
    
    # 최적화 요약 표시
    if optimization_stats:
        total_original = sum(stat['original_size'] for stat in optimization_stats)
        total_new = sum(stat['new_size'] for stat in optimization_stats)
        total_savings = (1 - total_new/total_original) * 100
        
        st.info(f"📊 텍스처 최적화 완료: {len(optimization_stats)}개 파일, {total_savings:.1f}% 용량 절약")
    
    return optimized_data

def check_texture_size_warnings(texture_data):
    """텍스처 크기 경고 체크"""
    warnings = []
    
    for filename, data in texture_data.items():
        size_mb = len(data) / (1024 * 1024)
        
        if size_mb > 10:
            warnings.append(f"⚠️ {filename}: {size_mb:.1f}MB - 매우 큰 파일")
        elif size_mb > 5:
            warnings.append(f"🔶 {filename}: {size_mb:.1f}MB - 큰 파일")
    
    return warnings

def auto_optimize_textures(texture_data, max_size=1024, quality=85):
    """
    자동 텍스처 최적화 (업로드 시 호출)
    
    Returns:
        tuple: (optimized_data, should_continue)
    """
    if not texture_data:
        return {}, True
    
    # 크기 경고 체크
    warnings = check_texture_size_warnings(texture_data)
    if warnings:
        st.warning("큰 텍스처 파일이 감지되었습니다:")
        for warning in warnings:
            st.write(warning)
        st.info("자동으로 최적화를 진행합니다...")
    
    # 최적화 실행
    optimized_data = optimize_texture_data(texture_data, max_size, quality)
    
    return optimized_data, True

# 테스트 함수
def test_optimization():
    """최적화 기능 테스트"""
    print("🧪 텍스처 최적화 테스트")
    
    # 테스트용 큰 이미지 생성
    test_image = Image.new('RGB', (2048, 2048), color='red')
    output = io.BytesIO()
    test_image.save(output, format='PNG')
    
    test_data = {
        'test_large.png': output.getvalue()
    }
    
    print(f"원본 크기: {len(test_data['test_large.png']):,} bytes")
    
    # 최적화 실행
    optimized = optimize_texture_data(test_data, max_size=1024, quality=80)
    
    for filename, data in optimized.items():
        print(f"최적화 후: {filename} - {len(data):,} bytes")

if __name__ == "__main__":
    test_optimization()
