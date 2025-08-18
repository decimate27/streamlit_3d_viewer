# UV Seam 문제 해결 방안 문서

## 1. 문제 정의
- **현상**: 3D 모델 로딩 시 텍스처 경계선(UV seam)에서 회색 선이 보임
- **원인**: 텍스처 필터링, UV 좌표 정밀도, 카메라 거리 등의 복합적 요인
- **해결 상태**: 모델 확대 시 UV seam이 사라지는 것을 확인

## 2. 적용한 해결 방법

### 2.1 텍스처 필터링 설정 개선

**파일**: `viewer_utils.py`  
**함수**: `create_texture_loading_code()`  
**코드 위치**: 2438-2445줄

**수정 전 코드**:
```javascript
tex_{safe_name}.generateMipmaps = false;
tex_{safe_name}.minFilter = THREE.LinearFilter;
tex_{safe_name}.magFilter = THREE.LinearFilter;
tex_{safe_name}.anisotropy = 1;
tex_{safe_name}.wrapS = THREE.ClampToEdgeWrapping;
tex_{safe_name}.wrapT = THREE.ClampToEdgeWrapping;
tex_{safe_name}.format = THREE.RGBFormat;
```

**수정 후 코드**:
```javascript
tex_{safe_name}.generateMipmaps = true;
tex_{safe_name}.minFilter = THREE.LinearMipmapLinearFilter;
tex_{safe_name}.magFilter = THREE.LinearFilter;
tex_{safe_name}.anisotropy = renderer.capabilities.getMaxAnisotropy();
tex_{safe_name}.wrapS = THREE.ClampToEdgeWrapping;
tex_{safe_name}.wrapT = THREE.ClampToEdgeWrapping;
tex_{safe_name}.format = THREE.RGBAFormat;
```

### 2.2 Material 설정 변경

**파일**: `viewer_utils.py`  
**함수**: OBJ 로더 내 material 생성 부분  
**코드 위치**: 2043-2047줄, 2069-2072줄

**수정 내용**:
- `side: THREE.FrontSide` → `side: THREE.DoubleSide`
- `alphaTest: 0` → `alphaTest: 0.01`

### 2.3 UV 좌표 패딩 알고리즘 개선

**파일**: `viewer_utils.py`  
**함수**: OBJ 파싱 후 UV 좌표 조정  
**코드 위치**: 2093-2119줄

**주요 변경사항**:
- epsilon 값: 0.001 → 0.005
- softEdge 영역 추가: 0.01
- 선형 보간 알고리즘 적용

**수정 후 전체 코드**:
```javascript
object.traverse((child) => {
    if (child.isMesh && child.geometry) {
        const geometry = child.geometry;
        if (geometry.attributes.uv) {
            const uvArray = geometry.attributes.uv.array;
            const epsilon = 0.005;
            const softEdge = 0.01;
            
            for (let i = 0; i < uvArray.length; i++) {
                const value = uvArray[i];
                
                if (value < softEdge) {
                    uvArray[i] = epsilon + (value / softEdge) * epsilon;
                } else if (value > 1 - softEdge) {
                    const dist = 1 - value;
                    uvArray[i] = 1 - epsilon - (dist / softEdge) * epsilon;
                }
            }
            
            geometry.attributes.uv.needsUpdate = true;
        }
    }
});
```

### 2.4 카메라 거리 및 모델 스케일 조정

**파일**: `viewer_utils.py`

**초기 카메라 위치 (1862줄)**:
- 변경: `camera.position.set(0, 0, 5)` → `camera.position.set(0, 0, 3.5)`

**모델 스케일 (2144줄)**:
- 변경: `const scale = 2 / maxDim` → `const scale = 2.5 / maxDim`

**로드 후 카메라 거리 (2153줄)**:
- 변경: `const distance = maxDim * scale * 2.2` → `const distance = maxDim * scale * 1.8`

## 3. 각 수정사항의 효과

### 3.1 Mipmap 활성화 효과
- 거리별 텍스처 해상도 자동 조정
- 텍스처 샘플링 정확도 향상
- 메모리 사용량 약 33% 증가

### 3.2 Anisotropic 필터링 효과
- 비스듬한 각도에서의 텍스처 품질 향상
- UV seam의 시각적 품질 개선

### 3.3 UV 패딩 효과
- 텍스처 경계선 근처 샘플링 오류 감소
- 부드러운 전환으로 급격한 색상 변화 방지

### 3.4 카메라 거리 조정 효과
- 가까운 거리에서 텍스처 필터링 정확도 향상
- UV seam이 주로 먼 거리에서 발생하는 문제 회피

## 4. 테스트 결과
- 모델 확대 시 UV seam 즉시 사라짐 확인
- 초기 로딩 시 더 가까운 거리에서 표시되도록 조정
- 대부분의 일반적인 뷰잉 거리에서 UV seam 문제 해결

## 5. 추가 개선 가능 옵션

### 5.1 렌더러 정밀도 향상 (미적용)
```javascript
renderer = new THREE.WebGLRenderer({
    // 기존 설정...
    logarithmicDepthBuffer: false,
    precision: "highp"
});
```

### 5.2 텍스처 전처리 (미적용)
- 텍스처 이미지에 1-2픽셀 투명 테두리 추가
- 텍스처 압축 포맷 변경 (DXT, ETC2 등)

## 6. 성능 영향
- **메모리**: Mipmap으로 인한 약 33% 증가
- **초기 로딩**: Mipmap 생성으로 약간의 시간 증가
- **렌더링 성능**: Anisotropic 필터링으로 GPU 부하 약간 증가
- **전체적 영향**: 일반적인 사용에는 문제없는 수준

## 7. 롤백 방법
각 수정사항을 원래대로 되돌리려면:
1. `generateMipmaps = false`로 변경
2. `minFilter = THREE.LinearFilter`로 변경
3. `anisotropy = 1`로 변경
4. `format = THREE.RGBFormat`로 변경
5. UV epsilon을 0.001로 변경
6. 카메라 거리와 스케일 값을 원래대로 복원