<?php
/**
 * files 폴더를 스캔하여 DB를 재구축하는 스크립트
 * 실제 파일 시스템 기반으로 DB를 다시 생성
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header('Content-Type: application/json');

// 디버깅 모드
$debug = isset($_GET['debug']) ? true : false;

try {
    // 1. files 디렉토리 스캔
    $files_dir = 'files';
    $models_found = [];
    
    if (!is_dir($files_dir)) {
        throw new Exception("files 디렉토리가 존재하지 않습니다.");
    }
    
    // 모든 하위 디렉토리 스캔 (각 디렉토리가 하나의 모델)
    $directories = scandir($files_dir);
    
    foreach ($directories as $dir) {
        if ($dir === '.' || $dir === '..') continue;
        
        $model_path = $files_dir . '/' . $dir;
        if (!is_dir($model_path)) continue;
        
        // 모델 ID는 디렉토리 이름
        $model_id = $dir;
        
        // 디렉토리 내 파일들 스캔
        $model_files = scandir($model_path);
        $obj_file = null;
        $mtl_file = null;
        $texture_files = [];
        
        foreach ($model_files as $file) {
            if ($file === '.' || $file === '..') continue;
            
            $file_path = $model_path . '/' . $file;
            $ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
            
            if ($ext === 'obj') {
                $obj_file = $file_path;
            } elseif ($ext === 'mtl') {
                $mtl_file = $file_path;
            } elseif (in_array($ext, ['png', 'jpg', 'jpeg', 'gif', 'bmp'])) {
                $texture_files[] = $file_path;
            }
        }
        
        // OBJ 파일이 있는 경우만 유효한 모델로 간주
        if ($obj_file) {
            // 파일 수정 시간으로 생성일 추정
            $created_at = date('Y-m-d H:i:s', filemtime($obj_file));
            
            $models_found[] = [
                'id' => $model_id,
                'obj_path' => $obj_file,
                'mtl_path' => $mtl_file,
                'texture_paths' => $texture_files,
                'created_at' => $created_at,
                'file_count' => count($model_files) - 2 // . 과 .. 제외
            ];
        }
    }
    
    // 2. 기존 DB 백업
    $db_file = 'streamlit_3d.db';
    if (file_exists($db_file)) {
        $backup_file = 'backup_' . date('Ymd_His') . '_streamlit_3d.db';
        copy($db_file, $backup_file);
        if ($debug) {
            echo "DB 백업 완료: $backup_file\n";
        }
    }
    
    // 3. DB 연결 및 테이블 재생성
    $db = new PDO('sqlite:' . $db_file);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 기존 테이블 삭제 (주의: 모든 데이터가 삭제됨)
    if (isset($_GET['rebuild']) && $_GET['rebuild'] === 'true') {
        $db->exec("DROP TABLE IF EXISTS models");
        $db->exec("DROP TABLE IF EXISTS feedbacks");
        
        // 새 테이블 생성
        $db->exec("
            CREATE TABLE models (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                author TEXT,
                description TEXT,
                share_token TEXT UNIQUE NOT NULL,
                obj_path TEXT,
                mtl_path TEXT,
                texture_paths TEXT,
                storage_type TEXT DEFAULT 'web',
                access_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ");
        
        $db->exec("CREATE INDEX idx_models_share_token ON models (share_token)");
        
        $db->exec("
            CREATE TABLE feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                share_token TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (share_token) REFERENCES models(share_token)
            )
        ");
    }
    
    // 4. 발견된 모델들을 DB에 추가
    $inserted = 0;
    $updated = 0;
    $errors = [];
    
    foreach ($models_found as $model) {
        try {
            // 기존 레코드 확인
            $stmt = $db->prepare("SELECT id, name FROM models WHERE id = ?");
            $stmt->execute([$model['id']]);
            $existing = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($existing) {
                // 업데이트 (파일 경로만)
                $stmt = $db->prepare("
                    UPDATE models 
                    SET obj_path = ?, mtl_path = ?, texture_paths = ?
                    WHERE id = ?
                ");
                $stmt->execute([
                    $model['obj_path'],
                    $model['mtl_path'],
                    json_encode($model['texture_paths']),
                    $model['id']
                ]);
                $updated++;
            } else {
                // 새로 추가
                $share_token = generateUUID();
                
                // 파일명에서 이름 추출 시도
                $name = "모델_" . substr($model['id'], 0, 8);
                $author = "Unknown";
                
                $stmt = $db->prepare("
                    INSERT INTO models 
                    (id, name, author, description, share_token, obj_path, mtl_path, texture_paths, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ");
                
                $stmt->execute([
                    $model['id'],
                    $name,
                    $author,
                    "자동으로 복구된 모델",
                    $share_token,
                    $model['obj_path'],
                    $model['mtl_path'],
                    json_encode($model['texture_paths']),
                    $model['created_at']
                ]);
                $inserted++;
            }
        } catch (Exception $e) {
            $errors[] = [
                'model_id' => $model['id'],
                'error' => $e->getMessage()
            ];
        }
    }
    
    // 5. 결과 반환
    $response = [
        'status' => 'success',
        'summary' => [
            'directories_scanned' => count($directories) - 2,
            'models_found' => count($models_found),
            'inserted' => $inserted,
            'updated' => $updated,
            'errors' => count($errors)
        ],
        'models' => $models_found
    ];
    
    if ($debug) {
        $response['errors'] = $errors;
    }
    
    echo json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}

// UUID 생성 함수
function generateUUID() {
    return sprintf('%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
        mt_rand(0, 0xffff), mt_rand(0, 0xffff),
        mt_rand(0, 0xffff),
        mt_rand(0, 0x0fff) | 0x4000,
        mt_rand(0, 0x3fff) | 0x8000,
        mt_rand(0, 0xffff), mt_rand(0, 0xffff), mt_rand(0, 0xffff)
    );
}
?>