<?php
/**
 * Annotations (수정점) API
 * 수정점 저장, 조회, 수정, 삭제 기능
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
    
    // annotations 테이블 생성 (없는 경우)
    $db->exec("
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_token TEXT NOT NULL,
            position_x REAL NOT NULL,
            position_y REAL NOT NULL,
            position_z REAL NOT NULL,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_token) REFERENCES models (share_token)
        )
    ");
    
    $method = $_SERVER['REQUEST_METHOD'];
    $action = $_GET['action'] ?? '';
    
    switch ($method) {
        case 'POST':
            if ($action === 'save') {
                // 단일 수정점 저장
                $input = json_decode(file_get_contents('php://input'), true);
                if (!$input) {
                    throw new Exception('Invalid JSON data');
                }
                
                $stmt = $db->prepare("
                    INSERT INTO annotations 
                    (model_token, position_x, position_y, position_z, text, completed)
                    VALUES (?, ?, ?, ?, ?, 0)
                ");
                
                $stmt->execute([
                    $input['model_token'],
                    floatval($input['position']['x']),
                    floatval($input['position']['y']),
                    floatval($input['position']['z']),
                    $input['text']
                ]);
                
                $annotation_id = $db->lastInsertId();
                
                echo json_encode([
                    'status' => 'success',
                    'annotation_id' => $annotation_id,
                    'message' => 'Annotation saved successfully'
                ]);
                
            } elseif ($action === 'save_batch') {
                // 여러 수정점 일괄 저장
                $input = json_decode(file_get_contents('php://input'), true);
                if (!$input) {
                    throw new Exception('Invalid JSON data');
                }
                
                $model_token = $input['model_token'] ?? '';
                $annotations = $input['annotations'] ?? [];
                $changes = $input['changes'] ?? [];
                
                if (!$model_token) {
                    throw new Exception('model_token is required');
                }
                
                $saved_count = 0;
                $changed_count = 0;
                
                // 새 수정점 저장
                foreach ($annotations as $ann) {
                    $stmt = $db->prepare("
                        INSERT INTO annotations 
                        (model_token, position_x, position_y, position_z, text, completed)
                        VALUES (?, ?, ?, ?, ?, 0)
                    ");
                    
                    $stmt->execute([
                        $model_token,
                        floatval($ann['position']['x']),
                        floatval($ann['position']['y']),
                        floatval($ann['position']['z']),
                        $ann['text']
                    ]);
                    $saved_count++;
                }
                
                // 기존 수정점 변경사항 처리
                foreach ($changes as $change) {
                    if ($change['action'] === 'complete') {
                        $stmt = $db->prepare("UPDATE annotations SET completed = 1 WHERE id = ?");
                        $stmt->execute([$change['id']]);
                        $changed_count++;
                    } elseif ($change['action'] === 'delete') {
                        $stmt = $db->prepare("DELETE FROM annotations WHERE id = ?");
                        $stmt->execute([$change['id']]);
                        $changed_count++;
                    }
                }
                
                echo json_encode([
                    'status' => 'success',
                    'saved_count' => $saved_count,
                    'changed_count' => $changed_count,
                    'message' => "Saved $saved_count new annotations, processed $changed_count changes"
                ]);
                
            } else {
                throw new Exception('Invalid action for POST');
            }
            break;
            
        case 'GET':
            if ($action === 'list') {
                // 특정 모델의 수정점 목록 조회
                $model_token = $_GET['model_token'] ?? '';
                if (!$model_token) {
                    throw new Exception('model_token is required');
                }
                
                $stmt = $db->prepare("
                    SELECT id, position_x, position_y, position_z, text, completed, created_at
                    FROM annotations 
                    WHERE model_token = ?
                    ORDER BY created_at ASC
                ");
                $stmt->execute([$model_token]);
                
                $annotations = [];
                while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                    $annotations[] = [
                        'id' => $row['id'],
                        'position' => [
                            'x' => floatval($row['position_x']),
                            'y' => floatval($row['position_y']),
                            'z' => floatval($row['position_z'])
                        ],
                        'text' => $row['text'],
                        'completed' => (bool)$row['completed'],
                        'created_at' => $row['created_at']
                    ];
                }
                
                echo json_encode([
                    'status' => 'success',
                    'annotations' => $annotations,
                    'count' => count($annotations)
                ]);
                
            } else {
                throw new Exception('Invalid action for GET');
            }
            break;
            
        case 'PUT':
            if ($action === 'update_status') {
                // 수정점 상태 업데이트
                $input = json_decode(file_get_contents('php://input'), true);
                if (!$input || !isset($input['id']) || !isset($input['completed'])) {
                    throw new Exception('Missing id or completed status');
                }
                
                $stmt = $db->prepare("
                    UPDATE annotations 
                    SET completed = ? 
                    WHERE id = ?
                ");
                $stmt->execute([$input['completed'] ? 1 : 0, $input['id']]);
                
                echo json_encode([
                    'status' => 'success',
                    'message' => 'Annotation status updated'
                ]);
                
            } else {
                throw new Exception('Invalid action for PUT');
            }
            break;
            
        case 'DELETE':
            // 수정점 삭제
            $annotation_id = $_GET['id'] ?? '';
            if (!$annotation_id) {
                throw new Exception('annotation id is required');
            }
            
            $stmt = $db->prepare("DELETE FROM annotations WHERE id = ?");
            $stmt->execute([$annotation_id]);
            
            echo json_encode([
                'status' => 'success',
                'message' => 'Annotation deleted successfully'
            ]);
            break;
            
        default:
            throw new Exception('Method not allowed');
    }
    
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'error' => 'Database error: ' . $e->getMessage()
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'error' => $e->getMessage()
    ]);
}
?>