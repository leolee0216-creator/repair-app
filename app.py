import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image, ImageOps
import io
import os
from streamlit_cropper import st_cropper

# --- 設定網頁 ---
st.set_page_config(page_title="社宅管理系統 (阿任版)", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🔄 Session State 管理 (控制頁面切換)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login" # 預設在登入頁

# ==========================================
# 🔐 1. 登入系統 (Login)
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
                    st.session_state.current_page = "menu" # 登入成功去目錄
                    st.rerun()
                else:
                    st.error("❌ 密碼錯誤")
    st.stop() # 停止執行後面的程式

# ==========================================
# 📂 2. 主目錄 (Main Menu)
# ==========================================
if st.session_state.current_page == "menu":
    st.markdown("<h1 style='text-align: center;'>🏠 社宅管理系統主目錄</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # 使用 2x2 排版按鈕
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("🛠️ 1. 社宅申請修繕系統", use_container_width=True, type="primary"):
            st.session_state.current_page = "repair_system"
            st.rerun()
        
        if st.button("📊 3. 社宅租金評定系統 (建置中)", use_container_width=True):
            st.toast("🚧 系統建置中...")

    with c2:
        if st.button("🏠 2. 社宅申請屋況系統 (建置中)", use_container_width=True):
            st.toast("🚧 系統建置中...")
            
        if st.button("🔗 4. 社宅相關連結目錄 (建置中)", use_container_width=True):
            st.toast("🚧 系統建置中...")
            
    # 登出按鈕
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 登出系統"):
        st.session_state.logged_in = False
        st.session_state.current_page = "login"
        st.rerun()

    st.stop() # 停在這裡，不要執行下面的修繕系統

# ==========================================
# 🛠️ 3. 社宅申請修繕系統 (Repair System)
# ==========================================
if st.session_state.current_page == "repair_system":
    
    # --- 頂部導航 ---
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("⬅️ 回主目錄"):
            st.session_state.current_page = "menu"
            st.rerun()
    with col_title:
        st.markdown("## 🛠️ 社宅申請修繕系統")

    # --- 操作說明 (更新版) ---
    with st.expander("📖 操作說明與發票須知 (點此展開)"):
        st.info("""
        **1. 基本資料**：填寫地址與修繕品項。
        **2. 照片紀錄**：發票為正方形(17x17cm)，其餘為橫式(4:3)。
        
        ---
        **【電子發票注意事項 (MOMO/蝦皮等)】**
        須上電子發票整合服務平台查詢：
        [👉 點此前往財政部電子發票平台](https://www.einvoice.nat.gov.tw/portal/btc/audit/btc601w/search)
        
        **平台查詢截圖須包含以下 5 點資訊：**
        1. 發票號碼
        2. 發票日期
        3. 發票金額
        4. 廠商統編與名稱
        5. 消費明細內容
        """)

    taiwan_districts = {
        "台北市": ["中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"],
        "新北市": ["板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區", "樹林區", "鶯歌區", "三峽區", "淡水區", "汐止區", "瑞芳區", "土城區", "蘆洲區", "五股區", "泰山區", "林口區", "深坑區", "石碇區", "坪林區", "三芝區", "石門區", "八里區", "平溪區", "雙溪區", "貢寮區", "金山區", "萬里區", "烏來區"],
        "桃園市": ["桃園區", "中壢區", "大溪區", "楊梅區", "蘆竹區", "大園區", "龜山區", "八德區", "龍潭區", "平鎮區", "新屋區", "觀音區", "復興區"],
    }

    # --- 步驟 1: 基本資料 ---
    st.subheader("1️⃣ 基本資料")

    with st.container(border=True):
        c1, c2 = st.columns([1, 1])
        with c1:
            city = st.selectbox("縣市", list(taiwan_districts.keys()), index=None, placeholder="選擇縣市")
        with c2:
            dist_options = taiwan_districts[city] if city else []
            district = st.selectbox("行政區", dist_options, index=None, placeholder="選擇區域", disabled=not city)
        
        street_address = st.text_input("詳細地址", placeholder="例如：南京東路五段356號13樓之1")
        
        if city and district and street_address:
            full_address = f"{city}{district}{street_address}"
            st.markdown(f"📍 **{full_address}**")
        else:
            full_address = None

        st.markdown("---")
        
        repair_options = {
            "防水工程": "浴室外牆滲水，故做防水工程",
            "壁癌處理": "牆面油漆剝落與壁癌生成，需刮除並重漆",
            "其他": ""
        }
        
        item_col, reason_col = st.columns([1, 1])
        with item_col:
            selected_item = st.selectbox("修繕品項", list(repair_options.keys()), index=None)
            if selected_item == "其他":
                final_item_name = st.text_input("輸入自訂品項")
            else:
                final_item_name = selected_item

        with reason_col:
            default_reason = repair_options.get(selected_item, "") if selected_item != "其他" else ""
            reason = st.text_area("修繕緣由", value=default_reason, height=100)

    # --- 步驟 2: 照片處理 (修正原圖顯示問題) ---
    st.subheader("2️⃣ 現場照片")

    def render_photo_card(title, key_prefix, icon, is_invoice=False):
        if is_invoice:
            aspect = (1, 1) # 發票正方形
            ratio_msg = "正方形 17x17 cm (發票專用)"
        else:
            aspect = (4, 3) # 一般照片
            ratio_msg = "橫式 4:3"

        with st.container(border=True):
            st.markdown(f"**{icon} {title}** <small style='color:gray'>({ratio_msg})</small>", unsafe_allow_html=True)
            
            t1, t2, t3 = st.tabs(["照片 1", "照片 2", "照片 3"])
            image_list = []
            
            for i, tab in enumerate([t1, t2, t3]):
                with tab:
                    u_key = f"{key_prefix}_{i+1}"
                    uploaded = st.file_uploader(f"上傳第 {i+1} 張", type=['jpg', 'jpeg', 'png'], key=u_key, label_visibility="collapsed")
                    
                    if uploaded:
                        # 1. 讀取並轉正照片
                        img = Image.open(uploaded)
                        img = ImageOps.exif_transpose(img)
                        
                        # 2. 顯示說明
                        st.write("👇 **請拖拉紅色框框選擇範圍 (支援縮放)**")
                        
                        # 3. 裁切器
                        # 這裡不做 resize，讓 st_cropper 自己處理，確保不會因為預先縮小而畫質變差
                        # 但如果覺得圖片太大，可以設定 width 參數，這裡我們保持原樣以求最高解析度
                        cropped = st_cropper(
                            img, 
                            realtime_update=True, 
                            box_color='#FF0000', 
                            aspect_ratio=aspect,
                            key=f"crop_{u_key}"
                        )
                        
                        with st.expander("👁️ 預覽裁切結果"):
                            st.image(cropped, use_container_width=True)
                        
                        image_list.append(cropped)
                    else:
                        st.caption("尚未上傳")
                        image_list.append(None)
            return image_list

    row1_a, row1_b = st.columns(2)
    with row1_a:
        imgs_before = render_photo_card("修繕前", "before", "🏚️")
    with row1_b:
        imgs_during = render_photo_card("修繕中", "during", "🚧")

    row2_a, row2_b = st.columns(2)
    with row2_a:
        imgs_after = render_photo_card("修繕後", "after", "✨")
    with row2_b:
        imgs_invoice = render_photo_card("發票/收據", "invoice", "🧾", is_invoice=True)

    # --- 步驟 3: 匯出 ---
    st.subheader("3️⃣ 報告生成")

    can_submit = full_address and final_item_name and os.path.exists("template.docx")

    if st.button("🚀 立即生成 Word 報告", type="primary", use_container_width=True, disabled=not can_submit):
        if not can_submit:
            st.error("資料不完整或找不到模板檔案")
        else:
            try:
                doc = DocxTemplate("template.docx")
                context = { 'address': full_address, 'item': final_item_name, 'reason': reason }
                
                def process_img(img_obj, is_invoice_img=False):
                    if img_obj is None: return ""
                    buf = io.BytesIO()
                    img_obj = img_obj.convert('RGB')
                    img_obj.save(buf, format='JPEG', quality=95)
                    buf.seek(0)
                    
                    if is_invoice_img:
                        # 發票：17x17 cm
                        return InlineImage(doc, buf, width=Mm(170), height=Mm(170))
                    else:
                        # 一般：8x6 cm (4:3)
                        return InlineImage(doc, buf, width=Mm(80))

                # 處理圖片
                for prefix, img_list in {"img_before": imgs_before, "img_during": imgs_during, "img_after": imgs_after}.items():
                    for idx, img_obj in enumerate(img_list):
                        context[f"{prefix}_{idx+1}"] = process_img(img_obj, is_invoice_img=False)

                for idx, img_obj in enumerate(imgs_invoice):
                    context[f"img_invoice_{idx+1}"] = process_img(img_obj, is_invoice_img=True)

                doc.render(context)
                bio = io.BytesIO()
                doc.save(bio)
                
                filename = f"{full_address}-{final_item_name}.docx"
                st.success(f"🎉 成功！檔名：{filename}")
                st.download_button("📥 下載 Word 檔", bio.getvalue(), filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary")
                
            except Exception as e:
                st.error(f"發生錯誤：{e}")