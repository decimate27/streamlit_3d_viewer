#!/usr/bin/env python3
"""
MTL 파일 자동 생성 유틸리티
OBJ 파일과 텍스처 이미지로부터 MTL 파일을 자동 생성
"""

import os
import re
from pathlib import Path

def extract_material_names_from_obj(obj_content):
    """OBJ 파일에서 사용된 재질 이름들을 추출"""
    materials = set()
    
    for line in obj_content.split('\n'):
        line = line.strip()
        if line.startswith('usemtl '):
            material_name = line[7:].strip()  # 'usemtl ' 제거
            materials.add(material_name)
    
    return list(materials)

def generate_mtl_content(texture_files, materials_from_obj=None):
    """텍스처 파일들로부터 MTL 내용 자동 생성"""
    
    if not texture_files:
        # 텍스처가 없는 경우 기본 재질
        return """# Auto-generated MTL file
newmtl DefaultMaterial
Ka 0.8 0.8 0.8
Kd 0.8 0.8 0.8
Ks 0.2 0.2 0.2
Ns 100
d 1.0
illum 2
"""
    
    mtl_content = "# Auto-generated MTL file\n\n"
    
    # OBJ에서 추출한 재질명이 있으면 사용, 없으면 자동 생성
    if materials_from_obj:
        for i, material_name in enumerate(materials_from_obj):
            texture_file = list(texture_files.keys())[i % len(texture_files)]
            mtl_content += create_material_block(material_name, texture_file)
    else:
        # 텍스처 파일별로 재질 생성
        for i, texture_name in enumerate(texture_files.keys()):
            material_name = f"Material{i+1}"
            mtl_content += create_material_block(material_name, texture_name)
    
    return mtl_content

def create_material_block(material_name, texture_filename):
    """개별 재질 블록 생성"""
    return f"""newmtl {material_name}
Ka 0.8 0.8 0.8
Kd 0.8 0.8 0.8
Ks 0.2 0.2 0.2
Ns 100
d 1.0
illum 2
map_Kd {texture_filename}

"""

def add_mtl_reference_to_obj(obj_content):
    """OBJ 파일에 MTL 참조 추가 (없는 경우)"""
    lines = obj_content.split('\n')
    
    # 이미 mtllib가 있는지 확인
    has_mtllib = any(line.strip().startswith('mtllib ') for line in lines)
    
    if not has_mtllib:
        # 첫 번째 비어있지 않은 라인 앞에 mtllib 추가
        new_lines = []
        mtllib_added = False
        
        for line in lines:
            if not mtllib_added and line.strip() and not line.strip().startswith('#'):
                new_lines.append('mtllib model.mtl')
                mtllib_added = True
            new_lines.append(line)
        
        # 만약 추가되지 않았다면 맨 앞에 추가
        if not mtllib_added:
            new_lines.insert(0, 'mtllib model.mtl')
        
        return '\n'.join(new_lines)
    
    # 기존 mtllib를 model.mtl로 변경
    new_lines = []
    for line in lines:
        if line.strip().startswith('mtllib '):
            new_lines.append('mtllib model.mtl')
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def auto_generate_mtl(obj_content, texture_data):
    """OBJ와 텍스처로부터 MTL 자동 생성"""
    
    # OBJ에서 재질명 추출
    materials_from_obj = extract_material_names_from_obj(obj_content)
    
    # MTL 내용 생성
    mtl_content = generate_mtl_content(texture_data, materials_from_obj)
    
    # OBJ에 MTL 참조 추가/수정
    updated_obj_content = add_mtl_reference_to_obj(obj_content)
    
    return updated_obj_content, mtl_content

# 테스트 함수
def test_mtl_generation():
    """MTL 생성 테스트"""
    
    # 테스트 OBJ 내용
    test_obj = """# Test OBJ file
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.0 1.0 0.0
vt 0.0 0.0
vt 1.0 0.0
vt 0.5 1.0
usemtl Material1
f 1/1 2/2 3/3
"""
    
    # 테스트 텍스처
    test_textures = {
        'texture1.jpg': b'fake_image_data',
        'texture2.png': b'fake_image_data2'
    }
    
    print("🧪 MTL 자동 생성 테스트")
    print("=" * 40)
    
    updated_obj, generated_mtl = auto_generate_mtl(test_obj, test_textures)
    
    print("📄 생성된 MTL:")
    print(generated_mtl)
    
    print("📄 수정된 OBJ:")
    print(updated_obj)

if __name__ == "__main__":
    test_mtl_generation()
