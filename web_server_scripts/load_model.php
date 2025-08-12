<?php
/**
 * 모델 로드 API
 * share_token으로 모델 정보와 파일들을 조회합니다.
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
        throw new Exception('Only GET method allowed');
    }
    
    $share_token = $_GET['token'] ?? '';
    if (!$share_token) {
        throw new Exception('share_token is required');
    }
    
    // 데이터베이스 연결
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 모델 정보 조회
    $stmt = $db->prepare("
        SELECT id, name, author, description, obj_path, mtl_path, texture_paths, access_count
        FROM models 
        WHERE share_token = ?
    ");
    $stmt->execute([$share_token]);
    $model = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$model) {
        throw new Exception('Model not found');
    }
    
    // 조회수 증가
    $stmt = $db->prepare("UPDATE models SET access_count = access_count + 1 WHERE share_token = ?");
    $stmt->execute([$share_token]);
    
    // 파일 내용 읽기
    $obj_content = '';
    $mtl_content = '';
    $texture_data = [];
    
    // OBJ 파일 읽기
    if (file_exists($model['obj_path'])) {
        $obj_content = file_get_contents($model['obj_path']);
    }
    
    // MTL 파일 읽기  
    if (file_exists($model['mtl_path'])) {
        $mtl_content = file_get_contents($model['mtl_path']);
    }
    
    // 텍스처 파일들 읽기
    $texture_paths = json_decode($model['texture_paths'], true) ?: [];
    foreach ($texture_paths as $texture_path) {
        if (file_exists($texture_path)) {
            $filename = basename($texture_path);
            $texture_data[$filename] = base64_encode(file_get_contents($texture_path));
        }
    }
    
    // 기존 피드백들 조회
    $stmt = $db->prepare("
        SELECT id, x, y, z, screen_x, screen_y, comment, feedback_type, status, created_at
        FROM feedbacks 
        WHERE model_id = ?
        ORDER BY created_at DESC
    ");
    $stmt->execute([$model['id']]);
    $feedbacks = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode([
        'status' => 'success',
        'model' => [
            'id' => $model['id'],
            'name' => $model['name'],
            'author' => $model['author'],
            'description' => $model['description'],
            'access_count' => $model['access_count'] + 1
        ],
        'files' => [
            'obj_content' => $obj_content,
            'mtl_content' => $mtl_content,
            'texture_data' => $texture_data
        ],
        'feedbacks' => $feedbacks
    ]);
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => 'Database error: ' . $e->getMessage()
    ]);
} catch (Exception $e) {
    http_response_code(404);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>
