# 3D 치수선 기능 구현 수정 내역

## 구현 일자
2025년 8월 18일

## 구현 목적
3D 모델의 실제 크기를 직관적으로 파악할 수 있도록 CAD 스타일의 치수선 기능 구현

## 주요 구현 내역

### 1. 데이터베이스 스키마 수정

#### 파일: `database.py`

**1.1 테이블 스키마 업데이트**
```python
# models 테이블에 real_height 컬럼 추가
# init_db 메서드 내에 추가
if 'real_height' not in columns:
    cursor.execute('ALTER TABLE models ADD COLUMN real_height REAL DEFAULT 1.0')
    st.write("📝 real_height 컬럼 추가 (모델 실제 높이 - 미터)")
    conn.commit()

# 새 테이블 생성 시에도 포함
CREATE TABLE models (
    ...
    real_height REAL DEFAULT 1.0
)
```

**1.2 save_model 메서드 수정**
```python
def save_model(self, name, author, description, obj_content, mtl_content, texture_data, real_height=1.0):
    # real_height 파라미터 추가
    cursor.execute('''
        INSERT INTO models (id, name, author, description, file_paths, backup_paths, 
                          storage_type, share_token, real_height)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (model_id, name, author, description, json.dumps(file_paths), 
          json.dumps(backup_paths) if backup_paths else None, 
          storage_type, share_token, real_height))
```

**1.3 get_model_by_token 메서드 수정**
```python
# SELECT 쿼리에 real_height 필드 추가
cursor.execute('''
    SELECT id, name, author, description, file_paths, backup_paths, storage_type, share_token, real_height
    FROM models WHERE share_token = ?
''', (share_token,))

# 모델 데이터 딕셔너리에 real_height 포함
model = {
    ...
    'real_height': row[8] if len(row) > 8 else 1.0
}
```

### 2. 업로드 UI 개선

#### 파일: `app.py`

**2.1 높이 입력 필드 추가**
```python
# 3열 레이아웃으로 변경
col1, col2, col3 = st.columns(3)
with col1:
    model_name = st.text_input("모델 이름", placeholder="예: 자동차 모델")
with col2:
    author_name = st.text_input("작성자", placeholder="작성자 이름을 입력하세요")
with col3:
    # 새로 추가되는 높이 입력 필드
    real_height = st.number_input(
        "실제 높이 (미터)", 
        min_value=0.1, 
        max_value=100.0, 
        value=1.0,
        step=0.1,
        format="%.1f",
        help="모델의 실제 높이를 미터 단위로 입력하세요. 예: 1.8 (사람), 3.0 (차량), 10.0 (건물)"
    )
```

**2.2 save_model 호출 수정**
```python
# real_height를 키워드 인자로 전달 (오류 수정)
model_id, share_token = db.save_model(
    model_name, 
    author_name,
    model_description,
    obj_content, 
    mtl_content, 
    texture_data,
    real_height=real_height  # 키워드 인자로 전달
)
```

### 3. 3D 뷰어 치수선 렌더링

#### 파일: `viewer_utils.py`

**3.1 함수 시그니처 수정**
```python
def create_3d_viewer_html(obj_content, mtl_content, texture_data, 
                         background_color="white", model_token=None, 
                         annotations=None, real_height=None):
    """Three.js 기반 3D 뷰어 HTML 생성 - 치수선 기능 포함"""
```

**3.2 JavaScript 변수 추가**
```javascript
// 치수선 관련 변수들
let dimensionGroup = null;
let isDimensionVisible = false;
const realHeight = {real_height if real_height else 1.0};  // 실제 높이 (미터)
let realDimensions = null;  // 계산된 실제 크기
```

**3.3 실제 크기 계산 함수**
```javascript
function calculateRealDimensions(object) {
    if (!object) return null;
    
    const box = new THREE.Box3().setFromObject(object);
    const modelSize = box.getSize(new THREE.Vector3());
    
    // 높이 기준 스케일 팩터 계산
    const scaleFactor = realHeight / modelSize.y;
    
    // 실제 크기 계산 (미터 단위)
    const dimensions = {
        width: modelSize.x * scaleFactor,
        height: realHeight,
        depth: modelSize.z * scaleFactor
    };
    
    // 표시용 포맷팅 (1m 이상은 m, 미만은 cm)
    const formatDimension = (meters) => {
        if (meters >= 1.0) {
            return `${meters.toFixed(1)}m`;
        } else {
            return `${(meters * 100).toFixed(0)}cm`;
        }
    };
    
    return {
        raw: dimensions,
        formatted: {
            width: formatDimension(dimensions.width),
            height: formatDimension(dimensions.height),
            depth: formatDimension(dimensions.depth)
        }
    };
}
```

**3.4 치수선 생성 함수**
```javascript
function createDimensionLine(start, end, label, color = 0x0000ff) {
    const group = new THREE.Group();
    
    // 메인 라인
    const lineGeometry = new THREE.BufferGeometry().setFromPoints([start, end]);
    const lineMaterial = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
    const line = new THREE.Line(lineGeometry, lineMaterial);
    group.add(line);
    
    // 화살표 (양끝)
    const arrowLength = 0.05;
    const arrowGeometry = new THREE.ConeGeometry(0.02, arrowLength, 8);
    const arrowMaterial = new THREE.MeshBasicMaterial({ color: color });
    
    // 시작점 화살표
    const arrow1 = new THREE.Mesh(arrowGeometry, arrowMaterial);
    arrow1.position.copy(start);
    const dir1 = new THREE.Vector3().subVectors(end, start).normalize();
    arrow1.lookAt(start.clone().add(dir1));
    arrow1.rotateX(Math.PI / 2);
    group.add(arrow1);
    
    // 끝점 화살표
    const arrow2 = new THREE.Mesh(arrowGeometry, arrowMaterial);
    arrow2.position.copy(end);
    const dir2 = new THREE.Vector3().subVectors(start, end).normalize();
    arrow2.lookAt(end.clone().add(dir2));
    arrow2.rotateX(Math.PI / 2);
    group.add(arrow2);
    
    // 텍스트 라벨 (Sprite)
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;
    const context = canvas.getContext('2d');
    context.fillStyle = 'rgba(255, 255, 255, 0.9)';
    context.fillRect(0, 0, 256, 128);
    context.font = 'Bold 48px Arial';
    context.fillStyle = 'rgba(0, 0, 255, 1.0)';
    context.textAlign = 'center';
    context.fillText(label, 128, 75);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        depthTest: false,
        depthWrite: false
    });
    const sprite = new THREE.Sprite(spriteMaterial);
    
    const midPoint = new THREE.Vector3().lerpVectors(start, end, 0.5);
    sprite.position.copy(midPoint);
    sprite.scale.set(0.5, 0.25, 1);
    group.add(sprite);
    
    return group;
}
```

**3.5 치수선 배치 함수 (겹침 문제 수정)**
```javascript
function addDimensionLines(object) {
    if (!object || dimensionGroup) return;
    
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    
    // 실제 크기 계산
    realDimensions = calculateRealDimensions(object);
    if (!realDimensions) return;
    
    dimensionGroup = new THREE.Group();
    dimensionGroup.name = 'dimensions';
    
    const offset = Math.max(size.x, size.y, size.z) * 0.15;  // 모델 크기의 15% 오프셋
    
    // X축 치수선 (너비) - 모델 아래쪽에 배치
    const xStart = new THREE.Vector3(box.min.x, box.min.y - offset, center.z);
    const xEnd = new THREE.Vector3(box.max.x, box.min.y - offset, center.z);
    const xLine = createDimensionLine(xStart, xEnd, realDimensions.formatted.width, 0xff0000);
    dimensionGroup.add(xLine);
    
    // Y축 치수선 (높이) - 모델 왼쪽에 배치
    const yStart = new THREE.Vector3(box.min.x - offset, box.min.y, center.z);
    const yEnd = new THREE.Vector3(box.min.x - offset, box.max.y, center.z);
    const yLine = createDimensionLine(yStart, yEnd, realDimensions.formatted.height, 0x00ff00);
    dimensionGroup.add(yLine);
    
    // Z축 치수선 (깊이) - 모델 오른쪽에 배치 (위치 변경으로 겹침 해결)
    const zStart = new THREE.Vector3(box.max.x + offset, center.y, box.min.z);
    const zEnd = new THREE.Vector3(box.max.x + offset, center.y, box.max.z);
    const zLine = createDimensionLine(zStart, zEnd, realDimensions.formatted.depth, 0x0000ff);
    dimensionGroup.add(zLine);
    
    scene.add(dimensionGroup);
    dimensionGroup.visible = false;  // 초기에는 숨김
    
    // 크기 정보 UI 업데이트
    updateDimensionInfo();
}
```

**3.6 UI 버튼 추가**
```python
# Python 코드에서 조건부 렌더링
{f'''<button class="dimension-btn" id="dimensionBtn" onclick="toggleDimensions()" 
     style="position: fixed; top: 140px; right: 20px; z-index: 99999; 
            padding: 12px 16px; background: #4CAF50; color: white; 
            border: none; border-radius: 6px; cursor: pointer; 
            font-size: 14px; font-weight: bold; 
            box-shadow: 0 3px 8px rgba(0,0,0,0.25); 
            min-width: 120px; text-align: center; transition: all 0.2s ease;">
    📐 치수 OFF
</button>
<div id="dimensionInfo" style="position: fixed; top: 200px; right: 20px; 
     z-index: 99999; min-width: 150px;"></div>''' if real_height and real_height > 0 else ''}
```

**3.7 모델 로드 시 치수선 추가**
```javascript
// 모델 로드 완료 후
scene.add(object);
model = object;

// 치수선 추가 (실제 높이가 설정된 경우)
if (realHeight && realHeight > 0) {
    addDimensionLines(object);
    console.log('Dimension lines added with real height:', realHeight);
}
```

**3.8 치수 표시 토글 함수**
```javascript
function toggleDimensions() {
    if (!dimensionGroup) return;
    
    isDimensionVisible = !isDimensionVisible;
    dimensionGroup.visible = isDimensionVisible;
    
    const btn = document.getElementById('dimensionBtn');
    if (btn) {
        if (isDimensionVisible) {
            btn.classList.add('active');
            btn.textContent = '📐 치수 ON';
        } else {
            btn.classList.remove('active');
            btn.textContent = '📐 치수 OFF';
        }
    }
    
    render();
}
```

### 4. 뷰어 페이지 통합

#### 파일: `viewer.py`

**4.1 치수 데이터 전달**
```python
# 3D 뷰어 HTML 생성 (배경색, annotations 및 실제 높이 포함)
from viewer_utils import create_3d_viewer_html
real_height = model_data.get('real_height', 1.0)  # 데이터베이스에서 실제 높이 가져오기
viewer_html = create_3d_viewer_html(
    obj_content, 
    mtl_content, 
    texture_data, 
    background_color,
    model_token=share_token,
    annotations=annotations,
    real_height=real_height
)
```

## 버그 수정 내역

### 1. save_model 파라미터 오류
- **문제**: "ModelDatabase.save_model() takes 7 positional arguments but 8 were given" 오류
- **원인**: real_height를 positional argument로 전달
- **해결**: real_height를 키워드 인자로 전달 (`real_height=real_height`)

### 2. 치수선 텍스트 겹침 문제
- **문제**: Y축(높이)과 Z축(깊이) 치수선이 같은 위치에 표시되어 텍스트 겹침
- **원인**: 두 치수선 모두 모델 왼쪽(`box.min.x - offset`)에 배치
- **해결**: Z축 치수선을 모델 오른쪽(`box.max.x + offset`)으로 이동

## 기능 특징

1. **높이 기반 스케일 계산**
   - 사용자가 입력한 실제 높이를 기준으로 나머지 치수 자동 계산
   - 모델 비율 유지하면서 실제 크기 표시

2. **단위 자동 변환**
   - 1m 이상: 미터(m) 단위로 표시 (예: 2.5m)
   - 1m 미만: 센티미터(cm) 단위로 표시 (예: 45cm)

3. **색상 구분**
   - X축(너비): 빨간색 (0xff0000)
   - Y축(높이): 초록색 (0x00ff00)
   - Z축(깊이): 파란색 (0x0000ff)

4. **UI/UX**
   - 토글 버튼으로 치수선 표시/숨기기
   - 실제 크기 정보 패널 제공
   - 고정 위치 버튼 (position: fixed)
   - 높은 z-index로 항상 최상단 표시

5. **렌더링 최적화**
   - Sprite 기반 텍스트 라벨로 가독성 확보
   - depthTest/depthWrite 비활성화로 항상 보이도록 설정
   - 모델 크기의 15% 오프셋으로 적절한 거리 유지

## 파일별 수정 요약

| 파일 | 수정 내용 |
|------|----------|
| `database.py` | - real_height 컬럼 추가<br>- save_model 메서드에 real_height 파라미터 추가<br>- get_model_by_token에서 real_height 반환 |
| `app.py` | - 3열 레이아웃으로 변경<br>- 실제 높이 입력 필드 추가<br>- save_model 호출 시 real_height 전달 |
| `viewer_utils.py` | - 치수선 계산 및 렌더링 함수 구현<br>- 토글 버튼 및 정보 패널 추가<br>- 모델 로드 시 치수선 자동 생성 |
| `viewer.py` | - real_height 데이터 전달<br>- create_3d_viewer_html에 real_height 파라미터 추가 |

## 테스트 결과
- ✅ 데이터베이스 마이그레이션 정상 작동
- ✅ 높이 입력 및 저장 정상 작동
- ✅ 치수선 렌더링 정상 표시
- ✅ 텍스트 겹침 문제 해결
- ✅ 토글 기능 정상 작동
- ✅ 단위 자동 변환 정상 작동

## 향후 개선 사항
- [ ] 치수선 스타일 커스터마이징 옵션
- [ ] 단위 선택 옵션 (mm, cm, m, inch, feet)
- [ ] 치수선 위치 자동 조정 (카메라 뷰에 따라)
- [ ] 치수 정보 다운로드 기능
- [ ] 부분 치수 측정 도구
- [ ] 치수선 애니메이션 효과
- [ ] 모바일 반응형 개선