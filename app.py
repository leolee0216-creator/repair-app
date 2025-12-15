import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image
import io
import os
from streamlit_cropper import st_cropper

# --- 設定網頁 (設定為 Wide 寬螢幕，但在手機上會自動適配) ---
st.set_page_config(page_title="社宅修繕系統 (阿任版)", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🔐 登入系統 (支援 Enter 鍵)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center;'>🔒 系統鎖定中</h2>", unsafe_allow_html=True)
        # 使用 form 表單，這樣按 Enter 也可以送出
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
# 🏠 主介面
# ==========================================

st.markdown("<h1 style='text-align: center;'>🛠️ 社宅申請修繕系統 <span style='font-size: 0.6em; color: gray;'>(阿任版)</span></h1>", unsafe_allow_html=True)

# 操作說明 (收合)
with st.expander("📖 操作說明 (點此展開)"):
    st.info("""
    1. **基本資料**：填寫地址與修繕品項。
    2. **照片紀錄**：
       - **發票/收據**：會自動鎖定為 **13x17 cm** 的比例 (直式)。
       - **其他照片**：鎖定為 **4:3** 比例 (橫式)。
    3. **手機操作**：照片上傳後，請上下滑動以查看裁切框與預覽結果。
    """)

taiwan_districts = {
    "台北市": ["中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"],
    "新北市": ["板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區", "樹林區", "鶯歌區", "三峽區", "淡水區", "汐止區", "瑞芳區", "土城區", "蘆洲區", "五股區", "泰山區", "林口區", "深坑區", "石碇區", "坪林區", "三芝區", "石門區", "八里區", "平溪區", "雙溪區", "貢寮區", "金山區", "萬里區", "烏來區"],
    "桃園市": ["桃園區", "中壢區", "大溪區", "楊梅區", "蘆竹區", "大園區", "龜山區", "八德區", "龍潭區", "平鎮區", "新屋區", "觀音區", "復興區"],
}

# --- 步驟 1: 基本資料 (手機適配版：用 Container 包覆) ---
st.subheader("1️⃣ 基本資料")

with st.container(border=True):
    # 手機上 col_addr_1, 2, 3 會自動變成直向堆疊，這是 Streamlit 的特性
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
    
    # 修繕品項
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

# --- 步驟 2: 照片處理 (核心修改：支援手機與發票尺寸) ---
st.subheader("2️⃣ 現場照片")

def render_photo_card(title, key_prefix, icon, is_invoice=False):
    """ 
    is_invoice=True 時，裁切比例鎖定為 13:17 (寬13, 高17)
    is_invoice=False 時，裁切比例鎖定為 4:3 
    """
    
    # 設定裁切比例
    if is_invoice:
        aspect = (13, 17) # 發票特規
        ratio_msg = "直式 13:17 (發票專用)"
    else:
        aspect = (4, 3)   # 一般照片
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
                    img = Image.open(uploaded)
                    
                    # 手機優化：不要左右並排，改為上下排列
                    # 這樣在手機窄螢幕上，裁切框才會夠大
                    st.write("👇 **請調整紅色框框**")
                    cropped = st_cropper(
                        img, 
                        realtime_update=True, 
                        box_color='#FF0000', 
                        aspect_ratio=aspect, # 這裡代入不同的比例
                        key=f"crop_{u_key}"
                    )
                    
                    with st.expander("👁️ 點此預覽裁切結果"):
                        st.image(cropped, use_container_width=True)
                    
                    image_list.append(cropped)
                else:
                    st.caption("尚未上傳")
                    image_list.append(None)
        return image_list

# 排版：手機會自動將 Columns 堆疊，所以這裡保持 Columns 沒關係
# 發票區獨立放一行，因為它比較長
row1_a, row1_b = st.columns(2)
with row1_a:
    imgs_before = render_photo_card("修繕前", "before", "🏚️")
with row1_b:
    imgs_during = render_photo_card("修繕中", "during", "🚧")

row2_a, row2_b = st.columns(2)
with row2_a:
    imgs_after = render_photo_card("修繕後", "after", "✨")
with row2_b:
    # 這裡開啟 is_invoice=True 模式
    imgs_invoice = render_photo_card("發票/收據", "invoice", "🧾", is_invoice=True)

# --- 步驟 3: 匯出 ---
st.subheader("3️⃣ 報告生成")

can_submit = full_address and final_item_name and os.path.exists("template.docx")

if st.button("🚀 立即生成 Word 報告", type="primary", use_container_width=True, disabled=not can_submit):
    if not can_submit:
        st.error("資料不完整 (地址、品項) 或找不到模板檔案")
    else:
        try:
            doc = DocxTemplate("template.docx")
            context = { 'address': full_address, 'item': final_item_name, 'reason': reason }
            
            # 圖片處理函數 (加入尺寸判斷)
            def process_img(img_obj, is_invoice_img=False):
                if img_obj is None: return ""
                buf = io.BytesIO()
                img_obj = img_obj.convert('RGB')
                img_obj.save(buf, format='JPEG', quality=95)
                buf.seek(0)
                
                # 判斷是否為發票，給予不同尺寸
                if is_invoice_img:
                    # 發票特規：寬 130mm, 高 170mm (即 13x17 cm)
                    return InlineImage(doc, buf, width=Mm(130), height=Mm(170))
                else:
                    # 一般照片：寬 80mm (高度會隨比例自動調整)
                    return InlineImage(doc, buf, width=Mm(80))

            # 彙整所有圖片
            # 1. 一般照片
            for prefix, img_list in {"img_before": imgs_before, "img_during": imgs_during, "img_after": imgs_after}.items():
                for idx, img_obj in enumerate(img_list):
                    key_name = f"{prefix}_{idx+1}"
                    context[key_name] = process_img(img_obj, is_invoice_img=False)

            # 2. 發票照片 (特別處理)
            for idx, img_obj in enumerate(imgs_invoice):
                key_name = f"img_invoice_{idx+1}"
                context[key_name] = process_img(img_obj, is_invoice_img=True)

            doc.render(context)
            bio = io.BytesIO()
            doc.save(bio)
            
            filename = f"{full_address}-{final_item_name}.docx"
            st.success(f"🎉 成功！檔名：{filename}")
            st.download_button("📥 下載 Word 檔", bio.getvalue(), filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary")
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")