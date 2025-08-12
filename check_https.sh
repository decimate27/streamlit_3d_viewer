#!/bin/bash
# HTTPS 적용 확인 스크립트

echo "🔒 HTTPS 서비스 확인 중..."
echo "======================================"

# 1. HTTPS 접속 테스트
echo "1. HTTPS 접속 테스트:"
curl -s -I "https://decimate27.dothome.co.kr/streamlit_data/init_database.php" | head -n 1

# 2. SSL 인증서 확인  
echo -e "\n2. SSL 인증서 정보:"
echo | openssl s_client -connect decimate27.dothome.co.kr:443 -servername decimate27.dothome.co.kr 2>/dev/null | openssl x509 -noout -dates

# 3. API 테스트
echo -e "\n3. HTTPS API 테스트:"
curl -s -X GET "https://decimate27.dothome.co.kr/streamlit_data/init_database.php" | jq '.' 2>/dev/null || echo "JSON 파싱 실패 - 응답 확인 필요"

echo -e "\n======================================"
echo "✅ HTTPS 서비스가 정상 작동하면 위 명령들이 모두 성공해야 합니다."
