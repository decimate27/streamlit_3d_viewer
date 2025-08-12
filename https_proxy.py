#!/usr/bin/env python3
"""
HTTPS Proxy Server
HTTPS 페이지에서 HTTP API를 호출할 수 있도록 프록시 역할을 합니다.
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import logging

# Flask 앱 생성
app = Flask(__name__)
CORS(app)  # CORS 허용

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 원본 서버 URL (HTTP)
ORIGINAL_BASE_URL = "http://decimate27.dothome.co.kr/streamlit_data"

@app.route('/proxy/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_request(endpoint):
    """모든 요청을 원본 HTTP 서버로 프록시"""
    
    # CORS preflight 요청 처리
    if request.method == 'OPTIONS':
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response
    
    try:
        # 원본 URL 구성
        target_url = f"{ORIGINAL_BASE_URL}/{endpoint}"
        
        # 쿼리 파라미터 추가
        if request.args:
            query_string = request.query_string.decode('utf-8')
            target_url += f"?{query_string}"
        
        logger.info(f"🔄 Proxying {request.method} {target_url}")
        
        # 요청 데이터 준비
        headers = {'User-Agent': 'HTTPS-Proxy/1.0'}
        data = None
        
        if request.method in ['POST', 'PUT'] and request.is_json:
            data = request.get_json()
            headers['Content-Type'] = 'application/json'
        
        # 원본 서버로 요청 전송
        if request.method == 'GET':
            response = requests.get(target_url, headers=headers, timeout=30, verify=False)
        elif request.method == 'POST':
            response = requests.post(target_url, json=data, headers=headers, timeout=30, verify=False)
        elif request.method == 'PUT':
            response = requests.put(target_url, json=data, headers=headers, timeout=30, verify=False)
        elif request.method == 'DELETE':
            response = requests.delete(target_url, headers=headers, timeout=30, verify=False)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        # 응답 반환
        response_data = response.text
        
        try:
            # JSON 응답인지 확인
            json_data = response.json()
            flask_response = jsonify(json_data)
        except:
            # 일반 텍스트 응답
            flask_response = Response(response_data)
        
        flask_response.status_code = response.status_code
        flask_response.headers['Access-Control-Allow-Origin'] = '*'
        
        logger.info(f"✅ Proxy response: {response.status_code}")
        return flask_response
        
    except Exception as e:
        logger.error(f"❌ Proxy error: {str(e)}")
        return jsonify({'error': f'Proxy error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """프록시 서버 상태 확인"""
    return jsonify({
        'status': 'healthy', 
        'message': 'HTTPS Proxy Server is running',
        'target': ORIGINAL_BASE_URL
    })

if __name__ == '__main__':
    print("🔒 HTTPS 프록시 서버 시작 중...")
    print(f"🎯 원본 서버: {ORIGINAL_BASE_URL}")
    print("📡 프록시 엔드포인트: https://localhost:5003/proxy/[endpoint]")
    print("🔍 상태 확인: https://localhost:5003/health")
    
    # SSL 인증서 없이 HTTPS로 실행 (개발용)
    app.run(
        host='0.0.0.0', 
        port=5003, 
        debug=True,
        ssl_context='adhoc'  # 자체 서명 인증서 생성
    )
