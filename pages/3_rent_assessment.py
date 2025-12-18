import streamlit as st

st.set_page_config(page_title="租金系統", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- 權限檢查 ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ 請先在首頁登入")
    if st.button("回首頁登入"):
        st.switch_page("app.py")
    st.stop()

st.title("📊 社宅租金評定系統")
st.info("🚧 此系統尚在建置中，敬請期待！")

st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("⬅️ 回主目錄", use_container_width=True):
    st.switch_page("app.py")