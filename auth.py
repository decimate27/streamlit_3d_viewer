# auth.py - 개선된 세션 관리 (Streamlit Cloud 호환)
import streamlit as st
import hashlib
import os
import time
import sqlite3
import uuid
import json
from datetime import datetime, timedelta

# 환경 변수에서 설정 가져오기
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "palbong211!")
SECRET_KEY = os.getenv("SECRET_KEY", "3d-viewer-secret-2024")

# 보안 설정
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5분
SESSION_TIMEOUT = 3600  # 60분 (1시간)
SESSION_DB_PATH = "data/sessions.db"

def hash_password(password):
    """비밀번호 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_session_db():
    """세션 데이터베이스 초기화"""
    os.makedirs(os.path.dirname(SESSION_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SESSION_DB_PATH)
    cursor = conn.cursor()
    
    # 세션 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            login_time REAL NOT NULL,
            last_activity REAL NOT NULL,
            browser_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 만료된 세션 정리
    cursor.execute('''
        DELETE FROM sessions 
        WHERE last_activity < ?
    ''', (time.time() - SESSION_TIMEOUT,))
    
    conn.commit()
    conn.close()

def get_browser_id():
    """브라우저별 고유 ID 생성/가져오기"""
    # URL 파라미터에서 브라우저 ID 확인
    query_params = st.query_params
    browser_id = query_params.get("sid", None)
    
    if not browser_id:
        # 세션 상태에서 확인
        if "browser_id" not in st.session_state:
            st.session_state["browser_id"] = str(uuid.uuid4())
        browser_id = st.session_state["browser_id"]
    else:
        st.session_state["browser_id"] = browser_id
    
    return browser_id

def create_db_session(user_id="admin"):
    """데이터베이스에 세션 생성"""
    init_session_db()
    session_id = str(uuid.uuid4())
    browser_id = get_browser_id()
    
    conn = sqlite3.connect(SESSION_DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, login_time, last_activity, browser_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, time.time(), time.time(), browser_id))
        conn.commit()
    except Exception as e:
        print(f"세션 생성 오류: {e}")
        session_id = None
    finally:
        conn.close()
    
    return session_id

def validate_db_session(browser_id):
    """데이터베이스에서 세션 유효성 검증"""
    if not browser_id:
        return None
    
    init_session_db()
    conn = sqlite3.connect(SESSION_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT session_id, login_time, last_activity 
        FROM sessions
        WHERE browser_id = ?
        ORDER BY last_activity DESC
        LIMIT 1
    ''', (browser_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    session_id, login_time, last_activity = result
    
    # 세션 타임아웃 확인
    if time.time() - last_activity > SESSION_TIMEOUT:
        delete_db_session(session_id)
        return None
    
    # 활동 시간 업데이트
    update_db_session_activity(session_id)
    
    return {
        'session_id': session_id,
        'login_time': login_time,
        'last_activity': last_activity
    }

def update_db_session_activity(session_id):
    """세션 활동 시간 업데이트"""
    conn = sqlite3.connect(SESSION_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE sessions 
        SET last_activity = ?
        WHERE session_id = ?
    ''', (time.time(), session_id))
    
    conn.commit()
    conn.close()

def delete_db_session(session_id):
    """세션 삭제"""
    conn = sqlite3.connect(SESSION_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    
    conn.commit()
    conn.close()

def delete_browser_sessions(browser_id):
    """특정 브라우저의 모든 세션 삭제"""
    if not browser_id:
        return
    
    conn = sqlite3.connect(SESSION_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE browser_id = ?', (browser_id,))
    
    conn.commit()
    conn.close()

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
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None

def update_activity_time():
    """활동 시간 업데이트"""
    st.session_state["last_activity_time"] = time.time()
    
    # DB 세션도 업데이트
    if st.session_state.get("session_id"):
        update_db_session_activity(st.session_state["session_id"])

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
    """세션 유효성 확인 (DB 기반)"""
    init_session_state()
    
    # 먼저 DB에서 세션 확인
    browser_id = get_browser_id()
    db_session = validate_db_session(browser_id)
    
    if db_session:
        # DB 세션이 유효하면 메모리 세션 복원
        st.session_state["password_correct"] = True
        st.session_state["session_id"] = db_session['session_id']
        st.session_state["login_time"] = db_session['login_time']
        st.session_state["last_activity_time"] = db_session['last_activity']
        
        # URL에 브라우저 ID 추가 (세션 유지용)
        if "sid" not in st.query_params:
            st.query_params["sid"] = browser_id
        
        return True
    
    # 메모리 세션 확인
    if not st.session_state.get("password_correct", False):
        return False
    
    if st.session_state.get("login_time", 0) == 0:
        return False
    
    # 활동 시간 기준 세션 만료 체크
    time_since_activity = time.time() - st.session_state.get("last_activity_time", 0)
    
    if time_since_activity < SESSION_TIMEOUT:
        update_activity_time()
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
    
    # DB에 세션 생성
    session_id = create_db_session()
    if session_id:
        st.session_state["session_id"] = session_id
        
        # URL에 브라우저 ID 추가
        browser_id = get_browser_id()
        st.query_params["sid"] = browser_id

def check_password():
    """비밀번호 확인 함수"""
    init_session_state()
    
    # 로그아웃 처리
    if st.session_state.get("logout_clicked", False):
        del st.session_state["logout_clicked"]
        st.success("👋 로그아웃되었습니다.")
        time.sleep(0.5)
        st.rerun()
    
    # 세션 유효성 확인 (DB 포함)
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
                st.caption("🔒 새로고침 후에도 세션 유지")
            
            # 로그아웃 버튼
            if st.button("🚪 로그아웃", key="sidebar_logout"):
                logout()
                st.rerun()
        
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
            st.session_state["just_logged_in"] = True
        else:
            st.session_state["password_correct"] = False
            record_failed_attempt()
    
    # 로그인 성공 처리
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
    
    st.info("💡 로그인 후 60분 동안 세션이 유지됩니다. (새로고침 후에도 유지)")
    
    # 보안 정보 표시
    with st.expander("🛡️ 보안 정보"):
        st.write(f"**최대 로그인 시도**: {MAX_LOGIN_ATTEMPTS}회")
        st.write(f"**계정 잠금 시간**: {LOCKOUT_DURATION//60}분")
        st.write(f"**세션 유지 시간**: {SESSION_TIMEOUT//60}분")
        st.write("**세션 정책**: 페이지 새로고침 후에도 유지 (DB 저장)")
        st.write("**개선사항**: SQLite DB를 통한 영구 세션 관리")
        
        # 디버그 정보
        if st.checkbox("디버그 정보 보기"):
            browser_id = get_browser_id()
            st.json({
                "password_correct": st.session_state.get("password_correct", False),
                "browser_id": browser_id,
                "session_id": st.session_state.get("session_id"),
                "login_time": datetime.fromtimestamp(st.session_state.get("login_time", 0)).strftime('%Y-%m-%d %H:%M:%S') if st.session_state.get("login_time", 0) > 0 else "Not logged in",
                "last_activity": datetime.fromtimestamp(st.session_state.get("last_activity_time", 0)).strftime('%Y-%m-%d %H:%M:%S') if st.session_state.get("last_activity_time", 0) > 0 else "No activity",
                "login_attempts": st.session_state.get("login_attempts", 0),
                "session_valid": is_session_valid()
            })
    
    return False

def logout():
    """로그아웃 함수"""
    # DB에서 세션 삭제
    browser_id = get_browser_id()
    delete_browser_sessions(browser_id)
    
    # 메모리 세션 초기화
    st.session_state["password_correct"] = False
    st.session_state["login_time"] = 0
    st.session_state["last_activity_time"] = 0
    st.session_state["login_attempts"] = 0
    st.session_state["session_id"] = None
    st.session_state["logout_clicked"] = True
    
    # URL 파라미터 정리
    if "sid" in st.query_params:
        del st.query_params["sid"]

def show_logout_button():
    """로그아웃 버튼 표시 (메인 영역용)"""
    if st.button("🚪 로그아웃", key="main_logout"):
        logout()
        st.rerun()

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
