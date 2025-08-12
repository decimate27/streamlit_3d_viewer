import streamlit as st
import requests
import json
from urllib.parse import urlencode

def proxy_request():
    """피드백 API 프록시 함수"""
    
    # URL 파라미터에서 피드백 데이터 추출
    if 'feedback_action' in st.query_params and st.query_params['feedback_action'] == 'proxy_save':
        try:
            # 피드백 데이터 파싱
            feedback_json = st.query_params.get('feedback_data', '{}')
            feedback_data = json.loads(feedback_json)
            
            # 웹서버 API 호출
            response = requests.post(
                'http://decimate27.dothome.co.kr/streamlit_data/feedback_api.php?action=save',
                json=feedback_data,
                headers={'Content-Type': 'application/json'},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    st.success(f"✅ 피드백 저장 성공! ID: {result.get('feedback_id')}")
                    return result
                else:
                    st.error(f"❌ 피드백 저장 실패: {result.get('error')}")
                    return None
            else:
                st.error(f"서버 오류: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"프록시 오류: {str(e)}")
            return None
    
    return None

# 페이지 로드 시 프록시 요청 처리
if 'feedback_action' in st.query_params:
    proxy_result = proxy_request()
    if proxy_result:
        # JavaScript로 성공 결과 전달
        st.markdown(f"""
        <script>
        if (window.parent) {{
            window.parent.postMessage({{
                type: 'feedback_proxy_result',
                success: true,
                data: {json.dumps(proxy_result)}
            }}, '*');
        }}
        </script>
        """, unsafe_allow_html=True)
    else:
        # 실패 결과 전달
        st.markdown(f"""
        <script>
        if (window.parent) {{
            window.parent.postMessage({{
                type: 'feedback_proxy_result', 
                success: false,
                error: '피드백 저장에 실패했습니다.'
            }}, '*');
        }}
        </script>
        """, unsafe_allow_html=True)
    
    st.stop()
