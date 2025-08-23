<?php
/**
 * 단일 모델 조회 API
 * share_token으로 특정 모델 정보 가져오기
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Content-Type: application/json');

try {
    $share_token = $_GET['token'] ?? null;
    
    if (!$share_token) {
        throw new Exception('share_token is required');
    }
    
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 모델 조회 및 조회수 증가
    $stmt = $db->prepare("
        UPDATE models 
        SET access_count = access_count + 1 
        WHERE share_token = ?
    ");
    $stmt->execute([$share_token]);
    
    // 모델 정보 가져오기
    $stmt = $db->prepare("
        SELECT id, name, author, description, share_token, 
               obj_path, mtl_path, texture_paths, storage_type, 
               access_count, created_at 
        FROM models
        WHERE share_token = ?
    ");
    
    $stmt->execute([$share_token]);
    $model = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$model) {
        http_response_code(404);
        echo json_encode([
            'status' => 'error',
            'message' => 'Model not found'
        ]);
        exit;
    }
    
    // texture_paths JSON 디코딩
    $texture_paths = [];
    if ($model['texture_paths']) {
        $decoded = json_decode($model['texture_paths'], true);
        if ($decoded) {
            $texture_paths = $decoded;
        }
    }
    
    // file_paths 형식으로 변환
    $file_paths = [
        'obj_path' => str_replace('files/', '', $model['obj_path']),
        'mtl_path' => str_replace('files/', '', $model['mtl_path']),
        'texture_paths' => array_map(function($path) {
            return str_replace('files/', '', $path);
        }, $texture_paths)
    ];
    
    $processed_model = [
        'id' => $model['id'],
        'name' => $model['name'],
        'author' => $model['author'],
        'description' => $model['description'],
        'share_token' => $model['share_token'],
        'file_paths' => json_encode($file_paths),
        'storage_type' => 'web',
        'access_count' => $model['access_count'],
        'created_at' => $model['created_at'],
        'real_height' => 1.0
    ];
    
    echo json_encode([
        'status' => 'success',
        'model' => $processed_model
    ], JSON_UNESCAPED_UNICODE);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>