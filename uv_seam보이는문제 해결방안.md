UV Seam 문제 해결 계획                                                                      │
     │                                                                                             │
     │ UV seam (텍스처 경계선)이 회색 선으로 보이는 문제를 해결하기 위해 다음과 같이               │
     │ 수정하겠습니다:                                                                             │
     │                                                                                             │
     │ 1. 텍스처 설정 강화 (2433-2440줄)                                                           │
     │                                                                                             │
     │ - generateMipmaps를 true로 변경 (현재 false)                                                │     
     │ - minFilter를 THREE.LinearMipmapLinearFilter로 변경                                         │     
     │ - anisotropy를 렌더러 최대값으로 증가                                                       │     
     │ - format을 THREE.RGBAFormat으로 변경 (알파 채널 포함)                                       │     
     │                                                                                             │     
     │ 2. Material 설정 개선 (2044-2074줄)                                                         │     
     │                                                                                             │     
     │ - side를 THREE.DoubleSide로 변경                                                            │     
     │ - alphaTest를 0.5로 설정하여 투명도 처리 개선                                               │     
     │                                                                                             │     
     │ 3. UV 좌표 조정 개선 (2099줄)                                                               │     
     │                                                                                             │     
     │ - epsilon 값을 0.001에서 0.002로 증가                                                       │     
     │                                                                                             │     
     │ 4. Phong Material 텍스처 설정 동기화 (1626-1631, 1694-1699줄)                               │     
     │                                                                                             │     
     │ - 메인 텍스처 로딩과 동일한 설정 적용                                                       │     
     │ - generateMipmaps를 일관되게 설정                                                           │     
     │                                                                                             │     
     │ 5. 렌더러 설정 추가 (1866-1873줄)                                                           │     
     │                                                                                             │     
     │ - logarithmicDepthBuffer: false 추가로 정밀도 개선                                          │     
     │ - precision: "highp" 추가   