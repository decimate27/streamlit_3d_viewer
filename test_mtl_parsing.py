#!/usr/bin/env python3
"""
MTL 파일 파싱 테스트 스크립트
"""

def test_mtl_parsing():
    """MTL 파일 파싱 테스트"""
    
    # 테스트용 MTL 내용
    mtl_content = """# Test MTL file
newmtl HeadMaterial
Ka 1.0 0.9 0.8
Kd 1.0 0.9 0.8
map_Kd head_diffuse.jpg

newmtl BodyMaterial
Ka 0.2 0.4 0.8
Kd 0.3 0.5 0.9
map_Kd body_diffuse.png

newmtl ArmMaterial
Ka 1.0 0.9 0.8
map_Kd arm_diffuse.jpg
map_Bump arm_normal.jpg

newmtl LegMaterial
Ka 0.2 0.2 0.2
map_Kd leg_diffuse.png
"""

    print("🧪 MTL 파일 파싱 테스트")
    print("=" * 40)
    
    # 재질명 추출
    def extract_materials_from_mtl(mtl_content):
        materials = []
        for line in mtl_content.split('\n'):
            line = line.strip()
            if line.startswith('newmtl '):
                material_name = line[7:].strip()
                if material_name:
                    materials.append(material_name)
        return materials
    
    # 텍스처 파일명 추출
    def extract_texture_files_from_mtl(mtl_content):
        textures = []
        for line in mtl_content.split('\n'):
            line = line.strip()
            if any(line.startswith(prefix) for prefix in ['map_Kd ', 'map_Ka ', 'map_Ks ', 'map_Bump ', 'map_d ', 'bump ']):
                parts = line.split()
                if len(parts) >= 2:
                    texture_file = parts[-1]
                    if texture_file not in textures:
                        textures.append(texture_file)
        return textures
    
    materials = extract_materials_from_mtl(mtl_content)
    textures = extract_texture_files_from_mtl(mtl_content)
    
    print("📄 발견된 재질:")
    for material in materials:
        print(f"  - {material}")
    
    print(f"\n🎨 참조된 텍스처 ({len(textures)}개):")
    for texture in textures:
        print(f"  - {texture}")
    
    # 실제 파일과 비교
    print(f"\n✅ 실제 생성된 파일들과 비교:")
    actual_files = [
        'head_diffuse.jpg',
        'body_diffuse.png', 
        'arm_diffuse.jpg',
        'leg_diffuse.png'
    ]
    
    for texture in textures:
        if texture in actual_files:
            print(f"  ✅ {texture} - 존재함")
        else:
            print(f"  ❌ {texture} - 누락됨")
    
    print("\n🎯 테스트 완료!")

if __name__ == "__main__":
    test_mtl_parsing()
