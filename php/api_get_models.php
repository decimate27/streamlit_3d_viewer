<?php
/**
 * 모든 모델 조회 API
 * 웹서버 DB에서 직접 모든 모델 정보를 가져옴
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Content-Type: application/json');

try {
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 모든 모델 조회 (real_height 포함)
    $stmt = $db->prepare("
        SELECT id, name, author, description, share_token, 
               obj_path, mtl_path, texture_paths, storage_type, 
               access_count, real_height, created_at 
        FROM models
        ORDER BY created_at DESC
    ");
    
    $stmt->execute();
    $models = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    // 경로 정보를 정리하여 반환
    $processed_models = [];
    foreach ($models as $model) {
        // texture_paths JSON 디코딩
        $texture_paths = [];
        if ($model['texture_paths']) {
            $decoded = json_decode($model['texture_paths'], true);
            if ($decoded) {
                $texture_paths = $decoded;
            }
        }
        
        // file_paths 형식으로 변환 (Python 코드와 호환)
        $file_paths = [
            'obj_path' => str_replace('files/', '', $model['obj_path']),
            'mtl_path' => str_replace('files/', '', $model['mtl_path']),
            'texture_paths' => array_map(function($path) {
                return str_replace('files/', '', $path);
            }, $texture_paths)
        ];
        
        $processed_models[] = [
            'id' => $model['id'],
            'name' => $model['name'],
            'author' => $model['author'],
            'description' => $model['description'],
            'share_token' => $model['share_token'],
            'file_paths' => json_encode($file_paths),
            'storage_type' => 'web',
            'access_count' => $model['access_count'],
            'created_at' => $model['created_at'],
            'real_height' => isset($model['real_height']) ? floatval($model['real_height']) : 1.0
        ];
    }
    
    echo json_encode([
        'status' => 'success',
        'count' => count($processed_models),
        'models' => $processed_models
    ], JSON_UNESCAPED_UNICODE);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>