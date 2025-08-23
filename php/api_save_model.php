<?php
/**
 * 모델 메타데이터만 저장하는 API
 * 파일은 이미 upload.php로 업로드됨
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Content-Type: application/json');

try {
    // POST 데이터 받기
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!$input) {
        throw new Exception('Invalid JSON data');
    }
    
    // 필수 필드 확인
    $required_fields = ['model_id', 'name', 'author', 'share_token'];
    foreach ($required_fields as $field) {
        if (!isset($input[$field])) {
            throw new Exception("Missing required field: $field");
        }
    }
    
    // 데이터베이스 연결
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 모델 디렉토리 확인
    $model_dir = "files/{$input['model_id']}";
    if (!is_dir($model_dir)) {
        throw new Exception("Model directory not found: {$model_dir}");
    }
    
    // 디렉토리 내 파일들 스캔
    $files = scandir($model_dir);
    $obj_path = null;
    $mtl_path = null;
    $texture_paths = [];
    
    foreach ($files as $file) {
        if ($file === '.' || $file === '..') continue;
        
        $file_path = "{$model_dir}/{$file}";
        $ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));
        
        if ($ext === 'obj') {
            $obj_path = $file_path;
        } elseif ($ext === 'mtl') {
            $mtl_path = $file_path;
        } elseif (in_array($ext, ['png', 'jpg', 'jpeg', 'gif', 'bmp'])) {
            $texture_paths[] = $file_path;
        }
    }
    
    if (!$obj_path) {
        throw new Exception("OBJ file not found in model directory");
    }
    
    // 데이터베이스에 저장
    $stmt = $db->prepare("
        INSERT OR REPLACE INTO models 
        (id, name, author, description, share_token, obj_path, mtl_path, texture_paths, storage_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'web', datetime('now'))
    ");
    
    $stmt->execute([
        $input['model_id'],
        $input['name'],
        $input['author'],
        $input['description'] ?? '',
        $input['share_token'],
        $obj_path,
        $mtl_path,
        json_encode($texture_paths)
    ]);
    
    echo json_encode([
        'status' => 'success',
        'message' => 'Model saved successfully',
        'model_id' => $input['model_id'],
        'share_token' => $input['share_token']
    ]);
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => 'Database error: ' . $e->getMessage()
    ]);
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>