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
        
        // 삭제 요청 처리
        if (isset($_POST['action']) && $_POST['action'] === 'delete') {
            $model_id = $_POST['model_id'] ?? '';
            
            if (empty($model_id)) {
                $response['message'] = 'Model ID가 필요합니다.';
                echo json_encode($response);
                exit;
            }
            
            $model_dir = __DIR__ . '/files/' . $model_id;
            
            if (is_dir($model_dir)) {
                // 폴더와 내용 삭제
                function deleteDirectory($dir) {
                    if (!file_exists($dir)) return true;
                    if (!is_dir($dir)) return unlink($dir);
                    foreach (scandir($dir) as $item) {
                        if ($item == '.' || $item == '..') continue;
                        if (!deleteDirectory($dir . DIRECTORY_SEPARATOR . $item)) return false;
                    }
                    return rmdir($dir);
                }
                
                if (deleteDirectory($model_dir)) {
                    $response['status'] = 'success';
                    $response['message'] = '모델이 삭제되었습니다.';
                } else {
                    $response['message'] = '모델 삭제에 실패했습니다.';
                }
            } else {
                $response['status'] = 'success';
                $response['message'] = '삭제할 모델이 없습니다.';
            }
            
            echo json_encode($response);
            exit;
        }
        
        // 파일 업로드 처리
        if (isset($_FILES['file']) && isset($_POST['model_id'])) {
            $model_id = $_POST['model_id'];
            $uploaded_file = $_FILES['file'];
            
            // 입력값 검증
            if (empty($model_id) || !preg_match('/^[a-zA-Z0-9-]+$/', $model_id)) {
                $response['message'] = '유효하지 않은 Model ID입니다.';
                echo json_encode($response);
                exit;
            }
            
            if ($uploaded_file['error'] !== UPLOAD_ERR_OK) {
                $response['message'] = '파일 업로드 중 오류가 발생했습니다: ' . $uploaded_file['error'];
                echo json_encode($response);
                exit;
            }
            
            // 파일 크기 제한 (100MB)
            if ($uploaded_file['size'] > 100 * 1024 * 1024) {
                $response['message'] = '파일 크기가 너무 큽니다. (최대 100MB)';
                echo json_encode($response);
                exit;
            }
            
            // 허용된 확장자 확인
            $allowed_extensions = array('obj', 'mtl', 'png', 'jpg', 'jpeg');
            $file_extension = strtolower(pathinfo($uploaded_file['name'], PATHINFO_EXTENSION));
            
            if (!in_array($file_extension, $allowed_extensions)) {
                $response['message'] = '허용되지 않은 파일 형식입니다.';
                echo json_encode($response);
                exit;
            }
            
            // 업로드 디렉토리 생성
            $upload_dir = __DIR__ . '/files/' . $model_id;
            if (!is_dir($upload_dir)) {
                if (!mkdir($upload_dir, 0755, true)) {
                    $response['message'] = '업로드 디렉토리를 생성할 수 없습니다.';
                    echo json_encode($response);
                    exit;
                }
            }
            
            // 파일명 정리 (보안)
            $safe_filename = basename($uploaded_file['name']);
            $safe_filename = preg_replace('/[^a-zA-Z0-9._-]/', '', $safe_filename);
            
            $destination = $upload_dir . '/' . $safe_filename;
            
            // 파일 이동
            if (move_uploaded_file($uploaded_file['tmp_name'], $destination)) {
                $relative_path = $model_id . '/' . $safe_filename;
                $response['status'] = 'success';
                $response['message'] = '파일이 성공적으로 업로드되었습니다.';
                $response['file_path'] = $relative_path;
            } else {
                $response['message'] = '파일을 저장할 수 없습니다.';
            }
            
        } else {
            $response['message'] = '필수 매개변수가 누락되었습니다.';
        }
        
    } else {
        $response['message'] = 'POST 요청만 허용됩니다.';
    }
    
} catch (Exception $e) {
    $response['message'] = '서버 오류: ' . $e->getMessage();
}

echo json_encode($response);
?>
