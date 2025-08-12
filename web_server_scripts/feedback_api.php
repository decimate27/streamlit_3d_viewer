<?php
/**
 * 피드백 API
 * 피드백 저장, 조회, 수정, 삭제 기능
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    // 데이터베이스 연결
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    $method = $_SERVER['REQUEST_METHOD'];
    $action = $_GET['action'] ?? '';
    
    switch ($method) {
        case 'POST':
            if ($action === 'save') {
                // 피드백 저장
                $input = json_decode(file_get_contents('php://input'), true);
                if (!$input) {
                    throw new Exception('Invalid JSON data');
                }
                
                $required = ['model_id', 'x', 'y', 'z', 'screen_x', 'screen_y', 'comment'];
                foreach ($required as $field) {
                    if (!isset($input[$field])) {
                        throw new Exception("Missing field: $field");
                    }
                }
                
                $stmt = $db->prepare("
                    INSERT INTO feedbacks 
                    (model_id, x, y, z, screen_x, screen_y, comment, feedback_type, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', datetime('now'))
                ");
                
                $stmt->execute([
                    $input['model_id'],
                    floatval($input['x']),
                    floatval($input['y']),
                    floatval($input['z']),
                    floatval($input['screen_x']),
                    floatval($input['screen_y']),
                    $input['comment'],
                    $input['feedback_type'] ?? 'point'
                ]);
                
                $feedback_id = $db->lastInsertId();
                
                echo json_encode([
                    'success' => true,
                    'feedback_id' => $feedback_id,
                    'message' => 'Feedback saved successfully'
                ]);
                
            } else {
                throw new Exception('Invalid action for POST');
            }
            break;
            
        case 'GET':
            if ($action === 'list') {
                // 특정 모델의 피드백 목록 조회
                $model_id = $_GET['model_id'] ?? '';
                if (!$model_id) {
                    throw new Exception('model_id is required');
                }
                
                $stmt = $db->prepare("
                    SELECT id, model_id, x, y, z, screen_x, screen_y, comment, 
                           feedback_type, status, created_at
                    FROM feedbacks 
                    WHERE model_id = ?
                    ORDER BY created_at DESC
                ");
                $stmt->execute([$model_id]);
                $feedbacks = $stmt->fetchAll(PDO::FETCH_ASSOC);
                
                echo json_encode([
                    'success' => true,
                    'feedbacks' => $feedbacks,
                    'count' => count($feedbacks)
                ]);
                
            } else {
                throw new Exception('Invalid action for GET');
            }
            break;
            
        case 'PUT':
            if ($action === 'update_status') {
                // 피드백 상태 업데이트
                $input = json_decode(file_get_contents('php://input'), true);
                if (!$input || !isset($input['id']) || !isset($input['status'])) {
                    throw new Exception('Missing id or status');
                }
                
                $stmt = $db->prepare("
                    UPDATE feedbacks 
                    SET status = ? 
                    WHERE id = ?
                ");
                $stmt->execute([$input['status'], $input['id']]);
                
                echo json_encode([
                    'success' => true,
                    'message' => 'Feedback status updated'
                ]);
                
            } else {
                throw new Exception('Invalid action for PUT');
            }
            break;
            
        case 'DELETE':
            // 피드백 삭제
            $feedback_id = $_GET['id'] ?? '';
            if (!$feedback_id) {
                throw new Exception('feedback id is required');
            }
            
            $stmt = $db->prepare("DELETE FROM feedbacks WHERE id = ?");
            $stmt->execute([$feedback_id]);
            
            echo json_encode([
                'success' => true,
                'message' => 'Feedback deleted successfully'
            ]);
            break;
            
        default:
            throw new Exception('Method not allowed');
    }
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Database error: ' . $e->getMessage()
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
