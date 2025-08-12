// Service Worker for caching 3D model files
const CACHE_NAME = '3d-viewer-cache-v1';
const urlsToCache = [
  '/static/three.min.js',
  '/static/OBJLoader.js',
  '/static/MTLLoader.js'
];

// 설치 이벤트
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// 페치 이벤트 - 캐시 우선 전략
self.addEventListener('fetch', event => {
  // Base64 데이터 URL은 캐싱하지 않음
  if (event.request.url.startsWith('data:')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 캐시에 있으면 캐시에서 반환
        if (response) {
          console.log('Cache hit:', event.request.url);
          return response;
        }

        // 캐시에 없으면 네트워크에서 가져오기
        return fetch(event.request).then(response => {
          // 응답이 유효하지 않으면 그대로 반환
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // 3D 모델 관련 파일인 경우 캐싱
          const url = event.request.url;
          if (url.includes('.obj') || url.includes('.mtl') || 
              url.includes('.png') || url.includes('.jpg') || 
              url.includes('.jpeg')) {
            
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
                console.log('Cached:', event.request.url);
              });
          }

          return response;
        });
      })
  );
});

// 활성화 이벤트 - 오래된 캐시 정리
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
