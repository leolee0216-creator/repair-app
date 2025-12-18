import streamlit as st

# 設定網頁
st.set_page_config(page_title="社宅管理系統", layout="wide", initial_sidebar_state="collapsed")

# --- 🚫 隱藏側邊欄的 CSS 魔法 ---
# 這段會把左邊原本自動跑出來的選單藏起來，強迫使用者走大按鈕導航
no_sidebar_style = """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)

# --- Session State 初始化 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# 🔐 登入畫面
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center;'>🔒 社宅管理系統</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            password = st.text_input("輸入密碼", type="password", placeholder="請輸入密碼...")
            submitted = st.form_submit_button("登入系統", type="primary", use_container_width=True)
            
            if submitted:
                if password == "MVP88888":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ 密碼錯誤")
    st.stop()

# ==========================================
# 🏠 主目錄 (登入後顯示)
# ==========================================
st.title("🏠 歡迎使用社宅管理系統")
st.success("✅ 您已成功登入！請選擇功能：")

# 使用 2x2 排版按鈕
c1, c2 = st.columns(2)

with c1:
    # 跳轉到修繕系統
    if st.button("🛠️ 1. 社宅申請修繕系統", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Repair_System.py")
    
    if st.button("📊 3. 社宅租金評定系統 (建置中)", use_container_width=True):
        st.switch_page("pages/3_Rent_Assessment.py")

with c2:
    if st.button("🏠 2. 社宅申請屋況系統 (建置中)", use_container_width=True):
        st.switch_page("pages/2_Housing_Condition.py")
        
    if st.button("🔗 4. 社宅相關連結目錄 (建置中)", use_container_width=True):
        st.toast("🚧 連結目錄尚未建立頁面")

st.markdown("---")
if st.button("🚪 登出系統"):
    st.session_state.logged_in = False
    st.rerun()