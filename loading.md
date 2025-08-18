# 3D 모델 로딩 화면 구현 가능성 분석

## 현재 상황
- **문제**: 3D 모델 뷰어 클릭 시 검은 화면이 먼저 표시되고 모델이 로딩됨
- **원인**: Three.js가 모델과 텍스처를 로드하는 동안 빈 캔버스가 먼저 렌더링됨
- **목표**: loading.php와 같은 로딩 화면을 표시하여 사용자 경험 개선

## 기존 구현 분석

### 1. loading.php 구조
```html
- 단순한 HTML/CSS/JS 애니메이션
- "Loading" 텍스트 + 점(.) 애니메이션 (1~4개 반복)
- 500ms 간격으로 업데이트
- 흰색 배경에 검은색 텍스트
```

### 2. viewer_utils.py 현재 구조
```python
- 이미 로딩 오버레이 구현되어 있음 (line 286-330)
- #loadingOverlay 요소 존재
- fade-out 애니메이션 지원
- 간단한 스피너 애니메이션 포함
```

## 구현 가능성: ✅ **완전 가능**

### 이유
1. **기존 인프라 활용 가능**: viewer_utils.py에 이미 로딩 오버레이 구조가 구현되어 있음
2. **간단한 수정으로 개선 가능**: loading.php의 애니메이션을 기존 오버레이에 적용하면 됨
3. **성능 영향 없음**: 순수 CSS 애니메이션으로 렌더링 성능에 영향 없음

## 구현 방법

### 방법 1: 기존 로딩 오버레이 개선 (권장) ⭐
```javascript
// viewer_utils.py의 HTML 템플릿 수정
1. #loadingOverlay 내부에 loading.php와 동일한 애니메이션 추가
2. 모델 로드 완료 시점 감지 개선
3. 모든 리소스(OBJ, MTL, 텍스처) 로드 완료 후 fade-out
```

### 방법 2: iframe을 통한 loading.php 직접 로드
```javascript
1. 초기에 loading.php를 iframe으로 표시
2. 백그라운드에서 Three.js 로드
3. 로드 완료 시 iframe 제거하고 3D 뷰어 표시
```

### 방법 3: 프로그레시브 로딩
```javascript
1. 로딩 진행률 표시 (0% → 100%)
2. OBJ 로드 (30%) → MTL 로드 (60%) → 텍스처 로드 (100%)
3. 각 단계별 피드백 제공
```

## 구체적 구현 계획

### 1단계: 로딩 오버레이 개선
```javascript
// 현재 코드 (line 286-330)를 수정
#loadingOverlay {
    // 기존 스타일 유지
}

.loading-text {
    font-size: 48px;
    font-weight: bold;
    color: #333;
}

.dots {
    // loading.php와 동일한 점 애니메이션
}
```

### 2단계: 로드 완료 감지 개선
```javascript
// 모든 리소스 로드 완료 체크
Promise.all([
    objLoader.loadAsync(),
    mtlLoader.loadAsync(),
    textureLoader.loadAsync()
]).then(() => {
    // 로딩 오버레이 fade-out
    document.getElementById('loadingOverlay').classList.add('fade-out');
});
```

### 3단계: 에러 처리
```javascript
// 로드 실패 시 에러 메시지 표시
.catch(error => {
    showErrorMessage("모델 로드 실패");
});
```

## 예상 효과
1. **사용자 경험 개선**: 검은 화면 대신 명확한 로딩 상태 표시
2. **전문성 향상**: 깔끔한 로딩 애니메이션으로 완성도 높은 서비스 인상
3. **에러 처리 개선**: 로드 실패 시 명확한 피드백 제공

## 구현 시간 예상
- **최소 구현** (방법 1): 30분
- **중간 구현** (프로그레스 바 추가): 1시간
- **완전 구현** (에러 처리 포함): 2시간

## 결론
✅ **즉시 구현 가능**하며, 기존 코드를 최대한 활용하여 빠르게 개선할 수 있습니다.
loading.php의 심플한 애니메이션을 그대로 적용하면 사용자 경험이 크게 개선될 것입니다.