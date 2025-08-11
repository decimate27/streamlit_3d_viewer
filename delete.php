<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// OPTIONS 요청 처리
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    exit(0);
}

$response = array('status' => 'error', 'message' => '');

try {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        
        // 모델 삭제 요청 처리
        if (isset($_POST['action']) && $_POST['action'] === 'delete') {
            $model_id = $_POST['model_id'] ?? '';
            
            if (empty($model_id)) {
                $response['message'] = 'Model ID가 필요합니다.';
                echo json_encode($response);
                exit;
            }
            
            // Model ID 유효성 검사 (보안)
            if (!preg_match('/^[a-zA-Z0-9]+$/', $model_id)) {
                $response['message'] = '유효하지 않은 Model ID입니다.';
                echo json_encode($response);
                exit;
            }
            
            $model_dir = __DIR__ . '/files/' . $model_id;
            
            if (is_dir($model_dir)) {
                // 폴더와 내용 재귀적으로 삭제
                function deleteDirectory($dir) {
                    if (!file_exists($dir)) return true;
                    if (!is_dir($dir)) return unlink($dir);
                    
                    foreach (scandir($dir) as $item) {
                        if ($item == '.' || $item == '..') continue;
                        if (!deleteDirectory($dir . DIRECTORY_SEPARATOR . $item)) {
                            return false;
                        }
                    }
                    return rmdir($dir);
                }
                
                if (deleteDirectory($model_dir)) {
                    $response['status'] = 'success';
                    $response['message'] = '모델이 성공적으로 삭제되었습니다.';
                    $response['deleted_path'] = $model_id;
                } else {
                    $response['message'] = '모델 삭제에 실패했습니다.';
                }
            } else {
                // 디렉토리가 없어도 성공으로 처리 (이미 삭제됨)
                $response['status'] = 'success';
                $response['message'] = '모델이 이미 삭제되었거나 존재하지 않습니다.';
                $response['deleted_path'] = $model_id;
            }
            
            echo json_encode($response);
            exit;
        }
        
        // 파일 목록 조회 (디버깅용)
        if (isset($_POST['action']) && $_POST['action'] === 'list') {
            $files_dir = __DIR__ . '/files';
            
            if (is_dir($files_dir)) {
                $models = array();
                $dirs = scandir($files_dir);
                
                foreach ($dirs as $dir) {
                    if ($dir != '.' && $dir != '..' && is_dir($files_dir . '/' . $dir)) {
                        $model_files = scandir($files_dir . '/' . $dir);
                        $file_list = array();
                        
                        foreach ($model_files as $file) {
                            if ($file != '.' && $file != '..') {
                                $file_path = $files_dir . '/' . $dir . '/' . $file;
                                $file_list[] = array(
                                    'name' => $file,
                                    'size' => filesize($file_path),
                                    'modified' => filemtime($file_path)
                                );
                            }
                        }
                        
                        $models[] = array(
                            'model_id' => $dir,
                            'files' => $file_list
                        );
                    }
                }
                
                $response['status'] = 'success';
                $response['models'] = $models;
            } else {
                $response['message'] = 'files 디렉토리가 존재하지 않습니다.';
            }
            
            echo json_encode($response);
            exit;
        }
        
        $response['message'] = '지원되지 않는 액션입니다.';
        
    } else {
        $response['message'] = 'POST 요청만 허용됩니다.';
    }
    
} catch (Exception $e) {
    $response['message'] = '서버 오류: ' . $e->getMessage();
}

echo json_encode($response);
?>
