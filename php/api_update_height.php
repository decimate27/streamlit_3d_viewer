<?php
/**
 * 모델 높이 업데이트 API
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// OPTIONS 요청 처리 (CORS preflight)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// POST 요청만 허용
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit;
}

// JSON 데이터 파싱
$input = json_decode(file_get_contents('php://input'), true);

// 필수 파라미터 확인
if (!isset($input['model_id']) || !isset($input['height'])) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Missing required parameters']);
    exit;
}

$model_id = $input['model_id'];
$height = floatval($input['height']);

// 높이 유효성 검사
if ($height <= 0 || $height > 100) {
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'Invalid height value (must be between 0.1 and 100)']);
    exit;
}

try {
    // 데이터베이스 연결
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 먼저 real_height 컬럼이 있는지 확인하고 없으면 추가
    try {
        $db->exec("ALTER TABLE models ADD COLUMN real_height REAL DEFAULT 1.0");
    } catch (PDOException $e) {
        // 컬럼이 이미 존재하는 경우 무시
    }
    
    // 높이 업데이트
    $stmt = $db->prepare("UPDATE models SET real_height = :height WHERE id = :id");
    $stmt->bindParam(':height', $height);
    $stmt->bindParam(':id', $model_id);
    $result = $stmt->execute();
    
    if ($stmt->rowCount() > 0) {
        // 업데이트된 모델 정보 반환
        $stmt = $db->prepare("SELECT * FROM models WHERE id = :id");
        $stmt->bindParam(':id', $model_id);
        $stmt->execute();
        $model = $stmt->fetch(PDO::FETCH_ASSOC);
        
        echo json_encode([
            'status' => 'success',
            'message' => 'Height updated successfully',
            'model' => $model
        ]);
    } else {
        http_response_code(404);
        echo json_encode([
            'status' => 'error',
            'message' => 'Model not found'
        ]);
    }
    
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
        'message' => 'Error: ' . $e->getMessage()
    ]);
}
?>