// IndexedDB를 사용한 3D 모델 캐싱 모듈
class ModelCache {
    constructor() {
        this.dbName = '3DModelCache';
        this.dbVersion = 1;
        this.storeName = 'models';
        this.db = null;
    }

    // IndexedDB 초기화
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = () => {
                console.error('IndexedDB open failed');
                reject(request.error);
            };
            
            request.onsuccess = () => {
                this.db = request.result;
                console.log('IndexedDB initialized');
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const store = db.createObjectStore(this.storeName, { keyPath: 'id' });
                    store.createIndex('token', 'token', { unique: true });
                    store.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }
    // 모델 저장
    async saveModel(token, objData, mtlData, textures) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            
            const modelData = {
                id: token,
                token: token,
                obj: objData,
                mtl: mtlData,
                textures: textures,
                timestamp: Date.now(),
                size: this.calculateSize(objData, mtlData, textures)
            };
            
            const request = store.put(modelData);
            
            request.onsuccess = () => {
                console.log(`Model ${token} cached successfully`);
                this.cleanOldCache(); // 오래된 캐시 정리
                resolve();
            };
            
            request.onerror = () => {
                console.error('Failed to cache model');
                reject(request.error);
            };
        });
    }

    // 모델 불러오기
    async getModel(token) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.get(token);
            
            request.onsuccess = () => {
                if (request.result) {
                    console.log(`Model ${token} loaded from cache`);
                    // 캐시 히트 시 타임스탬프 업데이트
                    this.updateTimestamp(token);
                }
                resolve(request.result);
            };
            
            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    // 캐시 크기 계산
    calculateSize(objData, mtlData, textures) {
        let size = 0;
        if (objData) size += new Blob([objData]).size;
        if (mtlData) size += new Blob([mtlData]).size;
        if (textures) {
            Object.values(textures).forEach(tex => {
                size += new Blob([tex]).size;
            });
        }
        return size;
    }

    // 타임스탬프 업데이트 (LRU 캐시용)
    async updateTimestamp(token) {
        const transaction = this.db.transaction([this.storeName], 'readwrite');
        const store = transaction.objectStore(this.storeName);
        const request = store.get(token);
        
        request.onsuccess = () => {
            if (request.result) {
                request.result.timestamp = Date.now();
                store.put(request.result);
            }
        };
    }

    // 오래된 캐시 정리 (100MB 제한, LRU)
    async cleanOldCache() {
        const MAX_CACHE_SIZE = 100 * 1024 * 1024; // 100MB
        const transaction = this.db.transaction([this.storeName], 'readwrite');
        const store = transaction.objectStore(this.storeName);
        const index = store.index('timestamp');
        
        let totalSize = 0;
        const items = [];
        
        const request = index.openCursor();
        
        request.onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor) {
                items.push({
                    id: cursor.value.id,
                    size: cursor.value.size,
                    timestamp: cursor.value.timestamp
                });
                totalSize += cursor.value.size;
                cursor.continue();
            } else {
                // 캐시 크기가 제한을 초과하면 오래된 항목부터 삭제
                if (totalSize > MAX_CACHE_SIZE) {
                    items.sort((a, b) => a.timestamp - b.timestamp);
                    
                    let sizeToDelete = totalSize - MAX_CACHE_SIZE;
                    for (const item of items) {
                        if (sizeToDelete <= 0) break;
                        
                        store.delete(item.id);
                        sizeToDelete -= item.size;
                        console.log(`Deleted old cache: ${item.id}`);
                    }
                }
            }
        };
    }

    // 모든 캐시 삭제
    async clearAll() {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.clear();
            
            request.onsuccess = () => {
                console.log('All cache cleared');
                resolve();
            };
            
            request.onerror = () => {
                reject(request.error);
            };
        });
    }
}

// 전역 캐시 인스턴스
window.modelCache = new ModelCache();
