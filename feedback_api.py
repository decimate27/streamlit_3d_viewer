#!/usr/bin/env python3
"""
피드백 저장용 Flask API 서버
Streamlit과 별도로 실행되어 JavaScript에서 직접 피드백을 전송받습니다.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import ModelDatabase
import json
import logging

# Flask 앱 생성
app = Flask(__name__)
CORS(app)  # CORS 허용

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/save_feedback', methods=['POST', 'OPTIONS'])
def save_feedback():
    """피드백 저장 API"""
    
    # CORS preflight 요청 처리
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        # JSON 데이터 받기
        feedback_data = request.get_json()
        
        if not feedback_data:
            return jsonify({'error': 'No data provided'}), 400
        
        logger.info(f"📝 피드백 데이터 수신: {feedback_data}")
        
        # 필수 필드 확인
        required_fields = ['model_id', 'x', 'y', 'z', 'screen_x', 'screen_y', 'comment']
        for field in required_fields:
            if field not in feedback_data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # 데이터베이스에 저장
        db = ModelDatabase()
        feedback_id = db.add_feedback(
            model_id=feedback_data['model_id'],
            x=float(feedback_data['x']),
            y=float(feedback_data['y']),
            z=float(feedback_data['z']),
            screen_x=float(feedback_data['screen_x']),
            screen_y=float(feedback_data['screen_y']),
            comment=str(feedback_data['comment']),
            feedback_type=feedback_data.get('feedback_type', 'point')
        )
        
        if feedback_id:
            logger.info(f"✅ 피드백 저장 성공 - ID: {feedback_id}")
            return jsonify({
                'success': True, 
                'feedback_id': feedback_id,
                'message': '피드백이 성공적으로 저장되었습니다.'
            }), 200
        else:
            logger.error("❌ 피드백 저장 실패")
            return jsonify({'error': 'Failed to save feedback'}), 500
            
    except Exception as e:
        logger.error(f"❌ 피드백 저장 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({'status': 'healthy', 'message': 'Feedback API server is running'})

if __name__ == '__main__':
    print("🚀 피드백 API 서버 시작 중...")
    print("📡 엔드포인트: http://localhost:5001/save_feedback")
    print("🔍 상태 확인: http://localhost:5001/health")
    app.run(host='0.0.0.0', port=5001, debug=True)
