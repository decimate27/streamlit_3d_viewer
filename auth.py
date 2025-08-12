# auth.py - 간단한 인증 관리 모듈
import streamlit as st
import hashlib
import os
import time

# 관리자 비밀번호 설정 (환경변수에서 가져오거나 기본값 사용)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "palbong211!")  # 실제 사용시 반드시 변경하세요!

# 보안 설정
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5분 (초)
SESSION_TIMEOUT = 3600  # 1시간 (초)

def hash_password(password):
    """비밀번호 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_locked_out():
    """계정 잠금 상태 확인"""
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0
    if "last_attempt_time" not in st.session_state:
        st.session_state["last_attempt_time"] = 0
    
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        time_since_last_attempt = time.time() - st.session_state["last_attempt_time"]
        if time_since_last_attempt < LOCKOUT_DURATION:
            return True, LOCKOUT_DURATION - int(time_since_last_attempt)
        else:
            # 잠금 해제
            st.session_state["login_attempts"] = 0
    return False, 0

def is_session_expired():
    """세션 만료 확인"""
    if "login_time" not in st.session_state:
        st.session_state["login_time"] = 0
    
    if st.session_state["login_time"] == 0:
        return False
    
    time_since_login = time.time() - st.session_state["login_time"]
    return time_since_login > SESSION_TIMEOUT

def record_failed_attempt():
    """로그인 실패 기록"""
    st.session_state["login_attempts"] += 1
    st.session_state["last_attempt_time"] = time.time()

def record_successful_login():
    """로그인 성공 기록"""
    st.session_state["login_attempts"] = 0
    st.session_state["login_time"] = time.time()

def check_password():
    """비밀번호 확인 함수"""
    
    # 세션 만료 확인
    if st.session_state.get("password_correct", False) and is_session_expired():
        st.warning("⏰ 세션이 만료되었습니다. 다시 로그인해주세요.")
        if "password_correct" in st.session_state:
            del st.session_state["password_correct"]
        st.rerun()
    
    def password_entered():
        """비밀번호가 입력되었을 때 호출"""
        # 계정 잠금 확인
        is_locked, remaining_time = is_locked_out()
        if is_locked:
            st.error(f"🔒 계정이 잠금되었습니다. {remaining_time}초 후 다시 시도하세요.")
            return
        
        if hash_password(st.session_state["password"]) == hash_password(ADMIN_PASSWORD):
            st.session_state["password_correct"] = True
            record_successful_login()
            del st.session_state["password"]  # 입력된 비밀번호는 즉시 삭제
            st.success("✅ 로그인 성공!")
            time.sleep(1)
            st.rerun()
        else:
            st.session_state["password_correct"] = False
            record_failed_attempt()

    # 세션에 인증 상태가 없거나 인증 실패한 경우
    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        # 계정 잠금 확인
        is_locked, remaining_time = is_locked_out()
        if is_locked:
            st.error(f"🔒 너무 많은 로그인 시도로 계정이 잠금되었습니다.")
            st.warning(f"⏱️ {remaining_time}초 후 다시 시도할 수 있습니다.")
            return False
        
        st.markdown("### 🔐 관리자 인증")
        
        # 로그인 시도 횟수 표시
        if st.session_state.get("login_attempts", 0) > 0:
            remaining_attempts = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
            st.warning(f"⚠️ 남은 로그인 시도: {remaining_attempts}회")
        
        st.text_input(
            "관리자 비밀번호를 입력하세요",
            type="password",
            on_change=password_entered,
            key="password",
            placeholder="비밀번호 입력"
        )
        
        if st.session_state.get("password_correct", None) == False:
            st.error("❌ 비밀번호가 틀렸습니다.")
        
        st.info("💡 이 페이지는 관리자만 접근할 수 있습니다.")
        
        # 보안 정보 표시
        with st.expander("🛡️ 보안 정보"):
            st.write(f"**최대 로그인 시도**: {MAX_LOGIN_ATTEMPTS}회")
            st.write(f"**계정 잠금 시간**: {LOCKOUT_DURATION//60}분")
            st.write(f"**세션 유지 시간**: {SESSION_TIMEOUT//60}분")
            
            # 현재 상태
            if st.session_state.get("password_correct", False):
                from datetime import datetime
                login_time = datetime.fromtimestamp(st.session_state["login_time"])
                st.success(f"✅ 로그인됨 - {login_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                remaining_time = SESSION_TIMEOUT - (time.time() - st.session_state["login_time"])
                if remaining_time > 0:
                    st.info(f"⏱️ 세션 만료까지: {int(remaining_time//60)}분 {int(remaining_time%60)}초")
            
        
        return False
    else:
        # 인증 성공
        return True

def logout():
    """로그아웃 함수"""
    if "password_correct" in st.session_state:
        del st.session_state["password_correct"]
    if "login_time" in st.session_state:
        del st.session_state["login_time"]
    st.rerun()

def show_logout_button():
    """로그아웃 버튼 표시"""
    if st.button("🚪 로그아웃"):
        logout()

def logout():
    """로그아웃 함수"""
    if "password_correct" in st.session_state:
        del st.session_state["password_correct"]
    st.rerun()

def show_logout_button():
    """로그아웃 버튼 표시"""
    if st.button("🚪 로그아웃"):
        logout()
