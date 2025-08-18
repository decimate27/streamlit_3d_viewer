# 3D 치수선 기능 구현 계획

## 1. 핵심 기능 정의
- **높이 입력 기반 스케일 자동 계산 시스템**
  - 사용자는 실제 높이(미터 단위)만 입력 (소수점 1자리까지 허용: 1.5m, 2.3m 등)
  - 시스템이 자동으로 가로, 세로 비율 계산하여 표시
  - 예시: 모델 비율이 10:20:50이고 높이 2m 입력 시 → 40cm x 80cm x 200cm로 자동 변환
- 3D 모델의 실제 크기(가로x세로x높이) 표시
- CAD 스타일의 치수선(dimension line) 렌더링
- 동적 업데이트 (카메라 회전시 가독성 유지)
- 토글 버튼으로 표시/숨기기

## 2. 기술 구현 방안

### 2.1 Three.js 확장 구현
- **치수선 그룹 생성**: THREE.Group으로 모든 치수선 요소 관리
- **선 렌더링**: THREE.LineSegments로 치수선 그리기
- **텍스트 라벨**: THREE.Sprite 또는 CSS2DRenderer로 숫자 표시
- **화살표**: THREE.ConeGeometry로 양끝 화살표 구현

### 2.2 측정 및 계산
- THREE.Box3로 모델의 bounding box 계산
- X, Y, Z 축별 크기 추출
- 적절한 오프셋으로 치수선 위치 설정

### 2.3 UI 컨트롤
- 기존 컨트롤 패널에 "치수 표시" 토글 버튼 추가
- 단위 선택 옵션 (mm, cm, m)
- 색상 및 스타일 설정

## 3. 파일 수정 계획

### 3.1 `app.py` 수정 - 업로드 섹션
- 높이 입력 필드 추가 (미터 단위, 소수점 1자리)
- `st.number_input()` 사용하여 높이 입력 받기
- 데이터베이스에 실제 높이값 저장

### 3.2 `database.py` 수정
- `models` 테이블에 `real_height` 컬럼 추가 (REAL 타입)
- 높이 값 저장/조회 메서드 추가

### 3.3 `viewer_utils.py` 수정
- 높이 비율 기반 스케일 계산 함수 추가
- `create_dimension_lines()` 함수 구현
- 실제 크기 표시를 위한 텍스트 라벨 생성
- CSS2DRenderer 또는 Sprite 기반 텍스트 라벨

### 3.4 `viewer.py` 수정
- 모델 데이터에서 실제 높이 값 가져오기
- 치수 표시 토글 버튼 추가
- 계산된 실제 크기 표시

## 4. 구현 세부사항

### 4.1 치수선 스타일
```javascript
// 치수선 기본 스타일
const dimensionStyle = {
    lineColor: 0x0000ff,
    textColor: 0x000000,
    fontSize: 14,
    lineWidth: 2,
    arrowSize: 0.1,
    offset: 0.2  // 모델로부터의 거리
};
```

### 4.2 동적 업데이트
- 카메라 회전시 텍스트가 항상 카메라를 향하도록
- 줌 레벨에 따른 치수선 크기 자동 조정
- 모델 크기 변경시 자동 재계산

## 5. 구현 단계

### Step 1: 데이터베이스 스키마 업데이트
- `models` 테이블에 `real_height` 컬럼 추가
- 마이그레이션 스크립트 작성

### Step 2: 업로드 UI 개선
- 높이 입력 필드 추가 (미터 단위)
- 입력 검증 (0.1 ~ 100.0m 범위, 소수점 1자리)
- 툴팁으로 사용 가이드 제공

### Step 3: 스케일 계산 로직 구현
- 모델의 bounding box에서 원본 비율 추출
- 입력된 높이를 기준으로 스케일 팩터 계산
- 가로, 세로 크기 자동 계산

### Step 4: 치수선 렌더링
- Three.js로 치수선 및 화살표 그리기
- 실제 크기 값을 텍스트로 표시
- 단위 표시 (cm 또는 m)

### Step 5: UI 컨트롤 통합
- 뷰어에 "치수 표시" 토글 버튼 추가
- 치수선 표시/숨기기 기능
- 색상 및 스타일 커스터마이징

### Step 6: 최적화 및 테스트
- 다양한 모델 크기 테스트
- 성능 최적화
- 모바일 대응

## 6. 예상 결과
- CAD 소프트웨어처럼 전문적인 치수 표시
- 3D 모델의 실제 크기를 직관적으로 파악
- 엔지니어링/제조 분야 활용도 증대

## 7. 구현 예시 코드

### 7.1 업로드 UI 높이 입력 필드 (app.py)
```python
# 파일 업로드 섹션에 추가
col1, col2, col3 = st.columns(3)
with col1:
    model_name = st.text_input("모델 이름", placeholder="예: 캐릭터 모델")
with col2:
    author_name = st.text_input("작성자", placeholder="홍길동")
with col3:
    # 새로 추가되는 높이 입력 필드
    real_height = st.number_input(
        "실제 높이 (미터)", 
        min_value=0.1, 
        max_value=100.0, 
        value=1.0,
        step=0.1,
        format="%.1f",
        help="모델의 실제 높이를 미터 단위로 입력하세요. 예: 1.8 (사람), 3.0 (차량)"
    )

model_description = st.text_area("설명 (선택사항)", placeholder="모델에 대한 간단한 설명")
```

### 7.2 스케일 계산 함수 (viewer_utils.py)
```javascript
function calculateRealDimensions(object, realHeightMeters) {
    // 모델의 bounding box 계산
    const box = new THREE.Box3().setFromObject(object);
    const modelSize = box.getSize(new THREE.Vector3());
    
    // 높이 기준 스케일 팩터 계산
    const scaleFactor = realHeightMeters / modelSize.y;
    
    // 실제 크기 계산 (미터 단위)
    const realDimensions = {
        width: modelSize.x * scaleFactor,
        height: realHeightMeters,
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
        raw: realDimensions,
        formatted: {
            width: formatDimension(realDimensions.width),
            height: formatDimension(realDimensions.height),
            depth: formatDimension(realDimensions.depth)
        }
    };
}
```

### 7.3 치수선 생성 함수
```javascript
function createDimensionLine(start, end, label, scene) {
    const dimensionGroup = new THREE.Group();
    
    // 메인 라인
    const lineGeometry = new THREE.BufferGeometry().setFromPoints([start, end]);
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x0000ff });
    const line = new THREE.Line(lineGeometry, lineMaterial);
    dimensionGroup.add(line);
    
    // 텍스트 라벨 (Sprite)
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    context.font = 'Bold 40px Arial';
    context.fillStyle = 'rgba(0, 0, 0, 1.0)';
    context.fillText(label, 0, 40);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    
    const midPoint = new THREE.Vector3().lerpVectors(start, end, 0.5);
    sprite.position.copy(midPoint);
    sprite.scale.set(0.5, 0.25, 1);
    dimensionGroup.add(sprite);
    
    // 화살표
    const arrowGeometry = new THREE.ConeGeometry(0.05, 0.2, 8);
    const arrowMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
    
    const arrow1 = new THREE.Mesh(arrowGeometry, arrowMaterial);
    arrow1.position.copy(start);
    arrow1.lookAt(end);
    arrow1.rotateX(Math.PI / 2);
    dimensionGroup.add(arrow1);
    
    const arrow2 = new THREE.Mesh(arrowGeometry, arrowMaterial);
    arrow2.position.copy(end);
    arrow2.lookAt(start);
    arrow2.rotateX(Math.PI / 2);
    dimensionGroup.add(arrow2);
    
    scene.add(dimensionGroup);
    return dimensionGroup;
}
```

### 7.4 모델에 치수선 추가 (스케일 적용)
```javascript
function addModelDimensions(object, scene, realHeightMeters) {
    const box = new THREE.Box3().setFromObject(object);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    
    // 실제 크기 계산
    const realDims = calculateRealDimensions(object, realHeightMeters);
    
    const offset = 0.3;
    
    // X축 치수선 (너비)
    const xStart = new THREE.Vector3(box.min.x, box.min.y - offset, center.z);
    const xEnd = new THREE.Vector3(box.max.x, box.min.y - offset, center.z);
    createDimensionLine(xStart, xEnd, realDims.formatted.width, scene);
    
    // Y축 치수선 (높이)
    const yStart = new THREE.Vector3(box.min.x - offset, box.min.y, center.z);
    const yEnd = new THREE.Vector3(box.min.x - offset, box.max.y, center.z);
    createDimensionLine(yStart, yEnd, realDims.formatted.height, scene);
    
    // Z축 치수선 (깊이)
    const zStart = new THREE.Vector3(box.min.x - offset, center.y, box.min.z);
    const zEnd = new THREE.Vector3(box.min.x - offset, center.y, box.max.z);
    createDimensionLine(zStart, zEnd, realDims.formatted.depth, scene);
    
    // 치수 정보 반환 (UI 표시용)
    return realDims;
}
```

### 7.5 데이터베이스 스키마 업데이트 (database.py)
```python
def create_tables(self):
    """테이블 생성"""
    self.conn.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            obj_path TEXT NOT NULL,
            mtl_path TEXT,
            texture_paths TEXT,
            share_token TEXT UNIQUE,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            real_height REAL DEFAULT 1.0  -- 새로 추가되는 컬럼
        )
    ''')
    
    # 기존 테이블에 컬럼 추가 (마이그레이션)
    try:
        self.conn.execute('ALTER TABLE models ADD COLUMN real_height REAL DEFAULT 1.0')
        self.conn.commit()
    except:
        pass  # 컬럼이 이미 존재하는 경우

def add_model(self, name, author, description, obj_path, mtl_path, texture_paths, real_height=1.0):
    """모델 추가 (높이 정보 포함)"""
    share_token = str(uuid.uuid4())
    texture_paths_str = json.dumps(texture_paths) if texture_paths else None
    
    cursor = self.conn.execute('''
        INSERT INTO models (name, author, description, obj_path, mtl_path, texture_paths, share_token, real_height)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, author, description, obj_path, mtl_path, texture_paths_str, share_token, real_height))
    
    self.conn.commit()
    return cursor.lastrowid, share_token
```

## 8. 참고 사항
- Three.js CSS2DRenderer를 사용하면 HTML 요소로 더 깔끔한 텍스트 렌더링 가능
- 높이 입력값을 기준으로 전체 스케일 자동 계산
- 1m 이상은 미터(m), 1m 미만은 센티미터(cm)로 표시
- 사용자 정의 가능한 스타일 옵션 제공
- 모바일 환경에서의 터치 인터랙션 고려

## 9. 예상 사용 시나리오
1. 사용자가 3D 모델 업로드 시 실제 높이 입력 (예: 1.8m)
2. 시스템이 모델의 원본 비율을 분석
3. 입력된 높이를 기준으로 가로, 세로 자동 계산
4. 뷰어에서 "치수 표시" 버튼 클릭 시 실제 크기 표시
5. 예: "1.8m(높이) x 45cm(너비) x 30cm(깊이)"로 표시