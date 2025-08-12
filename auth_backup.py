# auth.py - 간단한 인증 관리 모듈, 메모리에 기반한 세션 관리. 그래서 refresh 해도 로그인 풀려버림.
import streamlit as st
import hashlib
import os
import time
from datetime import datetime, timedelta

# 관리자 비밀번호 설정 (환경변수에서 가져오거나 기본값 사용)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "palbong211!")  # 실제 사용시 반드시 변경하세요!

# 보안 설정
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5분 (초)
SESSION_TIMEOUT = 3600  # 60분 (초) - 1시간 세션 유지

def hash_password(password):
    """비밀번호 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_session_state():
    """세션 상태 초기화"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0
    if "last_attempt_time" not in st.session_state:
        st.session_state["last_attempt_time"] = 0
    if "login_time" not in st.session_state:
        st.session_state["login_time"] = 0
    if "last_activity_time" not in st.session_state:
        st.session_state["last_activity_time"] = time.time()

def update_activity_time():
    """활동 시간 업데이트 - 페이지 새로고침시에도 세션 연장"""
    st.session_state["last_activity_time"] = time.time()

def is_locked_out():
    """계정 잠금 상태 확인"""
    init_session_state()
    
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        time_since_last_attempt = time.time() - st.session_state["last_attempt_time"]
        if time_since_last_attempt < LOCKOUT_DURATION:
            return True, LOCKOUT_DURATION - int(time_since_last_attempt)
        else:
            # 잠금 해제
            st.session_state["login_attempts"] = 0
    return False, 0

def is_session_valid():
    """세션 유효성 확인 - 활동 기반으로 체크"""
    init_session_state()
    
    # 로그인하지 않은 경우
    if not st.session_state.get("password_correct", False):
        return False
    
    # 로그인 시간이 없는 경우
    if st.session_state.get("login_time", 0) == 0:
        return False
    
    # 마지막 활동 시간 기준으로 세션 만료 체크
    time_since_activity = time.time() - st.session_state.get("last_activity_time", 0)
    
    # 60분 이내 활동이 있었으면 세션 유지
    if time_since_activity < SESSION_TIMEOUT:
        update_activity_time()  # 활동 시간 갱신
        return True
    
    return False

def record_failed_attempt():
    """로그인 실패 기록"""
    init_session_state()
    st.session_state["login_attempts"] += 1
    st.session_state["last_attempt_time"] = time.time()

def record_successful_login():
    """로그인 성공 기록"""
    init_session_state()
    st.session_state["login_attempts"] = 0
    st.session_state["login_time"] = time.time()
    st.session_state["last_activity_time"] = time.time()
    st.session_state["password_correct"] = True

def check_password():
    """비밀번호 확인 함수"""
    init_session_state()
    
    # 로그아웃 처리 (callback 밖에서)
    if st.session_state.get("logout_clicked", False):
        del st.session_state["logout_clicked"]
        st.success("👋 로그아웃되었습니다.")
        time.sleep(0.5)
        st.rerun()
    
    # 이미 로그인되어 있고 세션이 유효한 경우
    if is_session_valid():
        # 세션 정보 사이드바에 표시
        with st.sidebar:
            st.success("✅ 로그인 상태")
            
            # 남은 세션 시간 계산
            time_since_activity = time.time() - st.session_state.get("last_activity_time", 0)
            remaining_time = SESSION_TIMEOUT - time_since_activity
            
            if remaining_time > 0:
                mins = int(remaining_time // 60)
                secs = int(remaining_time % 60)
                st.info(f"⏱️ 세션 만료까지: {mins}분 {secs}초")
                st.caption("페이지 활동시 자동 연장됩니다")
            
            # 로그아웃 버튼
            if st.button("🚪 로그아웃", key="sidebar_logout"):
                logout()
                st.rerun()  # 버튼 클릭 후 리런
        
        return True
    
    # 세션이 만료된 경우
    if st.session_state.get("password_correct", False) and not is_session_valid():
        st.warning("⏰ 세션이 만료되었습니다. 다시 로그인해주세요.")
        st.session_state["password_correct"] = False
        st.session_state["login_time"] = 0
    
    def password_entered():
        """비밀번호가 입력되었을 때 호출"""
        # 계정 잠금 확인
        is_locked, remaining_time = is_locked_out()
        if is_locked:
            st.error(f"🔒 계정이 잠금되었습니다. {remaining_time}초 후 다시 시도하세요.")
            return
        
        if hash_password(st.session_state["password"]) == hash_password(ADMIN_PASSWORD):
            record_successful_login()
            del st.session_state["password"]  # 입력된 비밀번호는 즉시 삭제
            st.session_state["just_logged_in"] = True  # 로그인 성공 플래그
            # st.rerun() 제거 - callback 내에서는 사용하지 않음
        else:
            st.session_state["password_correct"] = False
            record_failed_attempt()
    
    # 로그인 성공 처리 (callback 밖에서)
    if st.session_state.get("just_logged_in", False):
        del st.session_state["just_logged_in"]
        st.success("✅ 로그인 성공! 60분 동안 세션이 유지됩니다.")
        time.sleep(0.5)
        st.rerun()
    
    # 로그인 폼 표시
    st.markdown("### 🔐 관리자 인증")
    
    # 계정 잠금 확인
    is_locked, remaining_time = is_locked_out()
    if is_locked:
        st.error(f"🔒 너무 많은 로그인 시도로 계정이 잠금되었습니다.")
        st.warning(f"⏱️ {remaining_time}초 후 다시 시도할 수 있습니다.")
        return False
    
    # 로그인 시도 횟수 표시
    if st.session_state.get("login_attempts", 0) > 0:
        remaining_attempts = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
        st.warning(f"⚠️ 남은 로그인 시도: {remaining_attempts}회")
    
    # 비밀번호 입력
    st.text_input(
        "관리자 비밀번호를 입력하세요",
        type="password",
        on_change=password_entered,
        key="password",
        placeholder="비밀번호 입력"
    )
    
    if st.session_state.get("password_correct", None) == False and st.session_state.get("login_attempts", 0) > 0:
        st.error("❌ 비밀번호가 틀렸습니다.")
    
    st.info("💡 로그인 후 60분 동안 세션이 유지됩니다.")
    
    # 보안 정보 표시
    with st.expander("🛡️ 보안 정보"):
        st.write(f"**최대 로그인 시도**: {MAX_LOGIN_ATTEMPTS}회")
        st.write(f"**계정 잠금 시간**: {LOCKOUT_DURATION//60}분")
        st.write(f"**세션 유지 시간**: {SESSION_TIMEOUT//60}분")
        st.write("**세션 정책**: 페이지 새로고침 및 활동시 자동 연장")
        
        # 디버그 정보
        if st.checkbox("디버그 정보 보기"):
            st.json({
                "password_correct": st.session_state.get("password_correct", False),
                "login_time": datetime.fromtimestamp(st.session_state.get("login_time", 0)).strftime('%Y-%m-%d %H:%M:%S') if st.session_state.get("login_time", 0) > 0 else "Not logged in",
                "last_activity": datetime.fromtimestamp(st.session_state.get("last_activity_time", 0)).strftime('%Y-%m-%d %H:%M:%S') if st.session_state.get("last_activity_time", 0) > 0 else "No activity",
                "login_attempts": st.session_state.get("login_attempts", 0),
                "session_valid": is_session_valid()
            })
    
    return False

def logout():
    """로그아웃 함수"""
    st.session_state["password_correct"] = False
    st.session_state["login_time"] = 0
    st.session_state["last_activity_time"] = 0
    st.session_state["login_attempts"] = 0
    st.session_state["logout_clicked"] = True  # 로그아웃 플래그

def show_logout_button():
    """로그아웃 버튼 표시 (메인 영역용)"""
    if st.button("🚪 로그아웃", key="main_logout"):
        logout()
        st.rerun()  # 버튼 클릭 후 리런

# 세션 상태 디버깅용 함수
def show_session_info():
    """현재 세션 정보 표시 (디버깅용)"""
    if st.session_state.get("password_correct", False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            login_time = datetime.fromtimestamp(st.session_state.get("login_time", 0))
            st.metric("로그인 시간", login_time.strftime('%H:%M:%S'))
        
        with col2:
            last_activity = datetime.fromtimestamp(st.session_state.get("last_activity_time", 0))
            st.metric("마지막 활동", last_activity.strftime('%H:%M:%S'))
        
        with col3:
            time_since_activity = time.time() - st.session_state.get("last_activity_time", 0)
            remaining = SESSION_TIMEOUT - time_since_activity
            st.metric("남은 시간", f"{int(remaining//60)}분")
