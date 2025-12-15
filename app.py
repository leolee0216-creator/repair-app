import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image
import io
import os
from streamlit_cropper import st_cropper

# --- 設定網頁 ---
st.set_page_config(page_title="社宅修繕系統 (阿任版)", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🔐 登入系統
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center;'>🔒 系統鎖定中</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>請輸入管理員密碼以存取社宅修繕系統</p>", unsafe_allow_html=True)
        password = st.text_input("輸入密碼", type="password", label_visibility="collapsed", placeholder="請輸入密碼...")
        if st.button("登入系統", use_container_width=True, type="primary"):
            if password == "MVP88888":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ 密碼錯誤，請重新輸入")
    st.stop()

# ==========================================
# 🏠 主介面設計
# ==========================================

# 標題區
st.markdown("<h1 style='text-align: center;'>🛠️ 社宅申請修繕系統 <span style='font-size: 0.6em; color: gray;'>(阿任版)</span></h1>", unsafe_allow_html=True)

# 操作指引 (預設收合，保持畫面乾淨)
with st.expander("📖 點此查看操作說明 (新手必讀)"):
    st.markdown("""
    1. **基本資料**：請依序選擇縣市、區域，並輸入詳細地址。
    2. **照片上傳**：
       - 四大區域 (前/中/後/發票) 皆可上傳。
       - 每個區域最多支援 **3 張** 照片。
       - 上傳後請在左側 **拖拉紅色框框** 進行裁切與特寫。
    3. **匯出**：確認資料無誤後，點擊最下方按鈕生成 Word 檔。
    """)

# 資料庫
taiwan_districts = {
    "台北市": ["中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"],
    "新北市": ["板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區", "樹林區", "鶯歌區", "三峽區", "淡水區", "汐止區", "瑞芳區", "土城區", "蘆洲區", "五股區", "泰山區", "林口區", "深坑區", "石碇區", "坪林區", "三芝區", "石門區", "八里區", "平溪區", "雙溪區", "貢寮區", "金山區", "萬里區", "烏來區"],
    "桃園市": ["桃園區", "中壢區", "大溪區", "楊梅區", "蘆竹區", "大園區", "龜山區", "八德區", "龍潭區", "平鎮區", "新屋區", "觀音區", "復興區"],
}

# --- 步驟 1: 基本資料 ---
st.markdown("### 1️⃣ 基本資料與緣由")

with st.container(border=True): # 加上邊框讓視覺更集中
    col_addr_1, col_addr_2, col_addr_3 = st.columns([1, 1, 2])
    
    with col_addr_1:
        city = st.selectbox("縣市", list(taiwan_districts.keys()), index=None, placeholder="選擇縣市")
    with col_addr_2:
        dist_options = taiwan_districts[city] if city else []
        district = st.selectbox("行政區", dist_options, index=None, placeholder="選擇區域", disabled=not city)
    with col_addr_3:
        street_address = st.text_input("地址", placeholder="例如：南京東路五段356號13樓之1")
        
    # 自動顯示完整地址確認
    if city and district and street_address:
        full_address = f"{city}{district}{street_address}"
        st.caption(f"📍 完整地址確認： :blue[{full_address}]")
    else:
        full_address = None

    st.markdown("---")
    
    # 修繕項目
    c1, c2 = st.columns([1, 2])
    repair_options = {
        "防水工程": "浴室外牆滲水，故做防水工程",
        "壁癌處理": "牆面油漆剝落與壁癌生成，需刮除並重漆",
        "其他": ""
    }
    
    with c1:
        selected_item = st.selectbox("修繕品項", list(repair_options.keys()), index=None, placeholder="請選擇品項")
        if selected_item == "其他":
            final_item_name = st.text_input("輸入自訂品項名稱", placeholder="ex: 馬桶更換")
        else:
            final_item_name = selected_item

    with c2:
        default_reason = repair_options.get(selected_item, "") if selected_item != "其他" else ""
        reason = st.text_area("修繕緣由 (可編輯)", value=default_reason, placeholder="請詳細說明損壞狀況...", height=100)

# --- 步驟 2: 照片處理 ---
st.markdown("### 2️⃣ 現場照片紀錄")
st.info("💡 每個區塊最多 3 張。上傳後請**拖拉紅色框框**選取重點範圍 (即裁切與放大功能)。")

def render_photo_card(title, key_prefix, icon="📸"):
    """ 產生一個帶有邊框的照片區塊卡片 """
    with st.container(border=True):
        st.markdown(f"#### {icon} {title}")
        
        # 使用 Tabs 分頁
        t1, t2, t3 = st.tabs(["照片 1", "照片 2", "照片 3"])
        image_list = []
        
        for i, tab in enumerate([t1, t2, t3]):
            with tab:
                u_key = f"{key_prefix}_{i+1}"
                uploaded = st.file_uploader(f"上傳第 {i+1} 張", type=['jpg', 'jpeg', 'png'], key=u_key, label_visibility="collapsed")
                
                if uploaded:
                    img = Image.open(uploaded)
                    # 裁切器
                    cropped = st_cropper(img, realtime_update=True, box_color='#FF0000', aspect_ratio=(4, 3), key=f"crop_{u_key}")
                    st.caption("✅ 預覽 (將匯入此範圍)")
                    st.image(cropped, use_container_width=True)
                    image_list.append(cropped)
                else:
                    st.markdown("<div style='text-align: center; color: #ccc; padding: 20px;'>尚未上傳</div>", unsafe_allow_html=True)
                    image_list.append(None)
        return image_list

# 2x2 排版
row1_a, row1_b = st.columns(2)
with row1_a:
    imgs_before = render_photo_card("修繕前", "before", "🏚️")
with row1_b:
    imgs_during = render_photo_card("修繕中", "during", "🚧")

row2_a, row2_b = st.columns(2)
with row2_a:
    imgs_after = render_photo_card("修繕後", "after", "✨")
with row2_b:
    imgs_invoice = render_photo_card("發票/收據", "invoice", "🧾")

# --- 步驟 3: 匯出 ---
st.markdown("### 3️⃣ 報告生成")

# 檢查按鈕狀態
can_submit = full_address and final_item_name and os.path.exists("template.docx")

if st.button("🚀 立即生成 Word 報告", type="primary", use_container_width=True, disabled=not can_submit):
    if not can_submit:
        st.error("資料不完整，請檢查地址、品項或確認模板檔案是否存在。")
    else:
        try:
            doc = DocxTemplate("template.docx")
            context = {
                'address': full_address,
                'item': final_item_name,
                'reason': reason
            }
            
            # 圖片處理函數
            def process_img(img_obj):
                if img_obj is None: return ""
                buf = io.BytesIO()
                img_obj = img_obj.convert('RGB')
                img_obj.save(buf, format='JPEG', quality=95)
                buf.seek(0)
                return InlineImage(doc, buf, width=Mm(80))

            # 彙整所有圖片
            all_sections = {
                "img_before": imgs_before,
                "img_during": imgs_during,
                "img_after": imgs_after,
                "img_invoice": imgs_invoice
            }

            for prefix, img_list in all_sections.items():
                for idx, img_obj in enumerate(img_list):
                    key_name = f"{prefix}_{idx+1}"
                    context[key_name] = process_img(img_obj) if img_obj else ""

            doc.render(context)
            bio = io.BytesIO()
            doc.save(bio)
            
            filename = f"{full_address}-{final_item_name}.docx"
            st.success(f"🎉 報告已生成！檔名：{filename}")
            st.download_button("📥 點此下載 Word 檔", bio.getvalue(), filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary")
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")