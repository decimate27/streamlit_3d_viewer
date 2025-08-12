#!/usr/bin/env python3
"""
MTL 경로 검증 및 수정 테스트
"""
import os

def test_mtl_path_validation():
    """MTL 경로 검증 테스트"""
    
    # 문제가 있는 MTL 내용
    problematic_mtl = """# 문제가 있는 MTL 파일
newmtl Material1
map_Kd C:/temp_z/__airganpan neko/texture1.jpg

newmtl Material2  
map_Kd /Users/designer/Desktop/project/texture2.png

newmtl Material3
map_Kd textures/subfolder/texture3.jpg

newmtl Material4
map_Kd ../parent_folder/texture4.png

newmtl Material5
map_Kd texture5.jpg
"""

    print("🧪 MTL 경로 검증 및 수정 테스트")
    print("=" * 50)
    
    def validate_texture_path(texture_path, line_num, full_line):
        """텍스처 경로 검증"""
        issues = []
        
        # 절대 경로 검사
        if (texture_path.startswith('/') or  
            (len(texture_path) >= 3 and texture_path[1:3] == ':') or  
            texture_path.startswith('\\') or  
            ':\\' in texture_path or  
            texture_path.startswith('~/')):
            
            issues.append({
                'type': 'absolute_path',
                'line': line_num,
                'path': texture_path,
                'message': f"절대 경로: {texture_path}"
            })
        
        # 상위 디렉토리 참조
        if '../' in texture_path or '..\\' in texture_path:
            issues.append({
                'type': 'relative_parent',
                'line': line_num,
                'path': texture_path,
                'message': f"상위 디렉토리 참조: {texture_path}"
            })
        
        # 하위 디렉토리 경로
        if ('/' in texture_path or '\\' in texture_path) and not texture_path.startswith('./'):
            if os.path.dirname(texture_path):
                issues.append({
                    'type': 'directory_path',
                    'line': line_num,
                    'path': texture_path,
                    'message': f"디렉토리 경로: {texture_path}"
                })
        
        # 공백 포함
        if ' ' in texture_path:
            issues.append({
                'type': 'space_in_path',
                'line': line_num,
                'path': texture_path,
                'message': f"공백 포함: {texture_path}"
            })
        
        return issues
    
    def fix_mtl_paths(mtl_content):
        """MTL 경로 자동 수정"""
        lines = mtl_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            original_line = line
            stripped_line = line.strip()
            
            if any(stripped_line.startswith(prefix) for prefix in ['map_Kd ', 'map_Ka ', 'map_Ks ', 'map_Bump ']):
                parts = stripped_line.split()
                if len(parts) >= 2:
                    texture_path = parts[-1]
                    filename_only = os.path.basename(texture_path)
                    parts[-1] = filename_only
                    fixed_line = ' '.join(parts)
                    
                    # 들여쓰기 유지
                    indent = len(original_line) - len(original_line.lstrip())
                    fixed_line = ' ' * indent + fixed_line
                    
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(original_line)
            else:
                fixed_lines.append(original_line)
        
        return '\n'.join(fixed_lines)
    
    # 1. 문제 탐지
    print("1️⃣ 경로 문제 탐지:")
    all_issues = []
    
    for line_num, line in enumerate(problematic_mtl.split('\n'), 1):
        line = line.strip()
        if any(line.startswith(prefix) for prefix in ['map_Kd ', 'map_Ka ', 'map_Ks ']):
            parts = line.split()
            if len(parts) >= 2:
                texture_path = parts[-1]
                issues = validate_texture_path(texture_path, line_num, line)
                all_issues.extend(issues)
    
    for issue in all_issues:
        print(f"  ❌ 라인 {issue['line']}: {issue['message']}")
    
    print(f"\n총 {len(all_issues)}개 문제 발견")
    
    # 2. 자동 수정
    print("\n2️⃣ 자동 수정 결과:")
    fixed_mtl = fix_mtl_paths(problematic_mtl)
    
    print("수정된 MTL:")
    print("-" * 30)
    for line_num, line in enumerate(fixed_mtl.split('\n'), 1):
        if 'map_Kd' in line:
            print(f"{line_num:2d}: {line}")
    
    # 3. 수정 후 검증
    print("\n3️⃣ 수정 후 검증:")
    remaining_issues = []
    
    for line_num, line in enumerate(fixed_mtl.split('\n'), 1):
        line = line.strip()
        if any(line.startswith(prefix) for prefix in ['map_Kd ', 'map_Ka ', 'map_Ks ']):
            parts = line.split()
            if len(parts) >= 2:
                texture_path = parts[-1]
                issues = validate_texture_path(texture_path, line_num, line)
                remaining_issues.extend(issues)
    
    if remaining_issues:
        print(f"  ⚠️ {len(remaining_issues)}개 문제가 남아있습니다")
        for issue in remaining_issues:
            print(f"    - {issue['message']}")
    else:
        print("  ✅ 모든 경로 문제가 해결되었습니다!")
    
    print("\n🎯 테스트 완료!")

if __name__ == "__main__":
    test_mtl_path_validation()
