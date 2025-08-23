<?php
/**
 * 모델 저장 API
 * POST로 모델 정보와 파일들을 받아서 저장합니다.
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    // POST 데이터 받기
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        throw new Exception('Only POST method allowed');
    }
    
    // JSON 데이터 파싱
    $input = json_decode(file_get_contents('php://input'), true);
    if (!$input) {
        throw new Exception('Invalid JSON data');
    }
    
    // 필수 필드 확인
    $required_fields = ['model_id', 'name', 'author', 'share_token', 'obj_content', 'mtl_content', 'texture_data'];
    foreach ($required_fields as $field) {
        if (!isset($input[$field])) {
            throw new Exception("Missing required field: $field");
        }
    }
    
    // 데이터베이스 연결
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 파일 저장 디렉토리 생성
    $model_dir = "files/{$input['model_id']}";
    if (!is_dir($model_dir)) {
        mkdir($model_dir, 0755, true);
    }
    
    // OBJ 파일 저장
    $obj_path = "{$model_dir}/model.obj";
    file_put_contents($obj_path, $input['obj_content']);
    
    // MTL 파일 저장
    $mtl_path = "{$model_dir}/model.mtl";
    file_put_contents($mtl_path, $input['mtl_content']);
    
    // 텍스처 파일들 저장
    $texture_paths = [];
    foreach ($input['texture_data'] as $filename => $base64_data) {
        $texture_path = "{$model_dir}/{$filename}";
        $binary_data = base64_decode($base64_data);
        file_put_contents($texture_path, $binary_data);
        $texture_paths[] = $texture_path;
    }
    
    // 데이터베이스에 모델 정보 저장
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
        'files_saved' => [
            'obj' => $obj_path,
            'mtl' => $mtl_path,
            'textures' => $texture_paths
        ]
    ]);
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => 'Database error: ' . $e->getMessage()
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error', 
        'message' => $e->getMessage()
    ]);
}
?>
