<?php
/**
 * 모델 관리 API (목록 조회, 카운트, 삭제 등)
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    // 데이터베이스 연결
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    $action = $_GET['action'] ?? '';
    
    switch ($action) {
        case 'count':
            // 모델 수 조회
            $stmt = $db->query("SELECT COUNT(*) as count FROM models");
            $result = $stmt->fetch(PDO::FETCH_ASSOC);
            
            echo json_encode([
                'status' => 'success',
                'count' => intval($result['count'])
            ]);
            break;
            
        case 'list':
            // 모델 목록 조회
            $stmt = $db->query("
                SELECT id, name, author, description, access_count, created_at, storage_type
                FROM models 
                ORDER BY created_at DESC
            ");
            $models = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            echo json_encode([
                'status' => 'success',
                'models' => $models,
                'count' => count($models)
            ]);
            break;
            
        case 'delete':
            // 모델 삭제
            $model_id = $_GET['model_id'] ?? '';
            if (!$model_id) {
                throw new Exception('model_id is required');
            }
            
            // 모델 정보 조회 (파일 경로 확인용)
            $stmt = $db->prepare("SELECT obj_path, mtl_path, texture_paths FROM models WHERE id = ?");
            $stmt->execute([$model_id]);
            $model = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($model) {
                // 파일들 삭제
                if ($model['obj_path'] && file_exists($model['obj_path'])) {
                    unlink($model['obj_path']);
                }
                if ($model['mtl_path'] && file_exists($model['mtl_path'])) {
                    unlink($model['mtl_path']);
                }
                
                $texture_paths = json_decode($model['texture_paths'], true) ?: [];
                foreach ($texture_paths as $texture_path) {
                    if (file_exists($texture_path)) {
                        unlink($texture_path);
                    }
                }
                
                // 모델 디렉토리 삭제
                $model_dir = "files/{$model_id}";
                if (is_dir($model_dir)) {
                    rmdir($model_dir);
                }
                
                // 데이터베이스에서 삭제
                $stmt = $db->prepare("DELETE FROM models WHERE id = ?");
                $stmt->execute([$model_id]);
                
                // 관련 피드백도 삭제
                $stmt = $db->prepare("DELETE FROM feedbacks WHERE model_id = ?");
                $stmt->execute([$model_id]);
                
                echo json_encode([
                    'status' => 'success',
                    'message' => 'Model deleted successfully'
                ]);
            } else {
                throw new Exception('Model not found');
            }
            break;
            
        default:
            throw new Exception('Invalid action');
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
        'message' => $e->getMessage()
    ]);
}
?>
