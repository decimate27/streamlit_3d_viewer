import streamlit as st
from auth import check_password, logout, update_activity_time

# 페이지 설정
st.set_page_config(
    page_title="3D Model Manager - 쿠키 테스트",
    page_icon="🍪",
    layout="wide"
)

# 인증 확인
if not check_password():
    st.stop()

# 인증 성공 후 활동 시간 업데이트
update_activity_time()

# 메인 컨텐츠
st.title("🍪 쿠키 기반 세션 테스트")
st.success("✅ 로그인 성공!")

st.markdown("""
### 테스트 항목:
1. 브라우저 새로고침 (F5) 해도 로그인 유지 확인
2. 새 탭에서 동일 URL 접속 시 로그인 유지 확인
3. 브라우저 종료 후 재시작해도 7일간 로그인 유지 확인

### 현재 상태:
- 쿠키 기반 세션 관리 활성화 ✅
- 세션 만료 시간: 60분 (활동 시 자동 연장)
- 쿠키 유효 기간: 7일
""")

# 로그아웃 버튼
if st.button("🚪 로그아웃"):
    logout()
    st.rerun()

st.info("💡 브라우저를 새로고침(F5)해보세요. 로그인이 유지되어야 합니다.")
