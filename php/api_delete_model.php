<?php
/**
 * 모델 삭제 API
 * 웹서버 DB와 파일 시스템에서 모델 삭제
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, DELETE');
header('Content-Type: application/json');

// 재귀적 디렉토리 삭제 함수
function deleteDirectory($dir) {
    if (!file_exists($dir)) {
        return true;
    }
    
    if (!is_dir($dir)) {
        return unlink($dir);
    }
    
    foreach (scandir($dir) as $item) {
        if ($item == '.' || $item == '..') {
            continue;
        }
        
        if (!deleteDirectory($dir . DIRECTORY_SEPARATOR . $item)) {
            return false;
        }
    }
    
    return rmdir($dir);
}

try {
    // POST 데이터 받기
    $input = json_decode(file_get_contents('php://input'), true);
    $model_id = $input['model_id'] ?? $_POST['model_id'] ?? null;
    
    if (!$model_id) {
        throw new Exception('model_id is required');
    }
    
    // DB에서 삭제
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 먼저 모델 존재 확인
    $stmt = $db->prepare("SELECT id FROM models WHERE id = ?");
    $stmt->execute([$model_id]);
    $model = $stmt->fetch();
    
    if (!$model) {
        throw new Exception('Model not found');
    }
    
    // DB에서 삭제
    $stmt = $db->prepare("DELETE FROM models WHERE id = ?");
    $stmt->execute([$model_id]);
    
    // 파일 시스템에서 삭제
    $model_dir = "files/{$model_id}";
    if (is_dir($model_dir)) {
        if (deleteDirectory($model_dir)) {
            $file_deleted = true;
        } else {
            $file_deleted = false;
        }
    } else {
        $file_deleted = false;
    }
    
    echo json_encode([
        'status' => 'success',
        'message' => 'Model deleted successfully',
        'model_id' => $model_id,
        'db_deleted' => true,
        'files_deleted' => $file_deleted
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>