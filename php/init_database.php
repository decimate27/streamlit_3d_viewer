<?php
/**
 * SQLite 데이터베이스 초기화 스크립트
 * 웹서버에 업로드하여 실행합니다.
 */

// CORS 헤더 설정
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// OPTIONS 요청 처리 (CORS preflight)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

try {
    // SQLite 데이터베이스 파일 생성
    $db = new PDO('sqlite:streamlit_3d.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // 모델 테이블 생성
    $db->exec("
        CREATE TABLE IF NOT EXISTS models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            author TEXT,
            description TEXT,
            share_token TEXT UNIQUE NOT NULL,
            obj_path TEXT,
            mtl_path TEXT,
            texture_paths TEXT,
            storage_type TEXT DEFAULT 'web',
            access_count INTEGER DEFAULT 0,
            real_height REAL DEFAULT 1.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ");
    
    // 기존 테이블에 real_height 컬럼 추가 (없는 경우)
    try {
        $db->exec("ALTER TABLE models ADD COLUMN real_height REAL DEFAULT 1.0");
    } catch (PDOException $e) {
        // 컬럼이 이미 존재하는 경우 무시
    }
    
    // 피드백 테이블 생성
    $db->exec("
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL,
            z REAL NOT NULL,
            screen_x REAL NOT NULL,
            screen_y REAL NOT NULL,
            comment TEXT NOT NULL,
            feedback_type TEXT DEFAULT 'point',
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
    ");
    
    // 인덱스 생성
    $db->exec("CREATE INDEX IF NOT EXISTS idx_models_share_token ON models (share_token)");
    $db->exec("CREATE INDEX IF NOT EXISTS idx_feedbacks_model_id ON feedbacks (model_id)");
    $db->exec("CREATE INDEX IF NOT EXISTS idx_feedbacks_status ON feedbacks (status)");
    
    echo json_encode([
        'status' => 'success',
        'message' => 'Database initialized successfully',
        'tables_created' => ['models', 'feedbacks'],
        'db_file' => 'streamlit_3d.db'
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
        'message' => 'Error: ' . $e->getMessage()
    ]);
}
?>
