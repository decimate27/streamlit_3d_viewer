<?php
/**
 * 모든 모델 데이터를 JSON으로 반환하는 API
 * 로컬 DB와 동기화를 위해 사용됨
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Content-Type: application/json');

try {
    // 데이터베이스 연결
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 모든 모델 조회
    $stmt = $db->prepare("
        SELECT id, name, author, description, share_token, 
               obj_path, mtl_path, texture_paths, storage_type, 
               access_count, created_at 
        FROM models
        ORDER BY created_at
    ");
    
    $stmt->execute();
    $models = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // 성공 응답
    echo json_encode([
        'status' => 'success',
        'count' => count($models),
        'models' => $models
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
        'message' => 'Server error: ' . $e->getMessage()
    ]);
}
?>