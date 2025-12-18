import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image, ImageOps
import io
import os
from streamlit_cropper import st_cropper
from repair_data import REPAIR_DATABASE 

# --- 隱藏側邊欄 CSS ---
st.set_page_config(page_title="修繕系統", layout="wide", initial_sidebar_state="collapsed")
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

# --- 標題區 ---
col_logo, col_header = st.columns([1, 6])
with col_header:
    st.subheader("🛠️ 社宅申請修繕系統")

# --- 操作說明 (收合) ---
with st.expander("📖 操作指南 (點此展開)"):
    st.markdown("""
    * **地址與品項**：選擇縣市後自動帶出區域；選擇品項後自動帶出理由。
    * **照片處理**：
        * **一般照片**：上傳後請拖拉 <span style='color:red'>紅色框框</span>，框選範圍即為匯出結果 (4:3比例)。
        * **發票/收據**：不需裁切，系統自動處理為 17x17cm 原圖。
                
        ---
        **【電子發票注意事項 (MOMO/蝦皮等)】**
        須上電子發票整合服務平台查詢：
        [👉 前往財政部電子發票平台](https://www.einvoice.nat.gov.tw/portal/btc/audit/btc601w/search)
        
        **平台查詢資訊須包含：**
        1. 發票號碼
        2. 發票日期
        3. 發票金額
        4. 廠商統編與名稱
        5. 消費明細內容
    """, unsafe_allow_html=True)

taiwan_districts = {
    "台北市": ["中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"],
    "新北市": ["板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區", "樹林區", "鶯歌區", "三峽區", "淡水區", "汐止區", "瑞芳區", "土城區", "蘆洲區", "五股區", "泰山區", "林口區", "深坑區", "石碇區", "坪林區", "三芝區", "石門區", "八里區", "平溪區", "雙溪區", "貢寮區", "金山區", "萬里區", "烏來區"],
    "桃園市": ["桃園區", "中壢區", "大溪區", "楊梅區", "蘆竹區", "大園區", "龜山區", "八德區", "龍潭區", "平鎮區", "新屋區", "觀音區", "復興區"],
}

# --- 步驟 1: 基本資料 (極簡化設計) ---
st.markdown("#### 1️⃣ 資料填寫")

with st.container(border=True):
    # 第一行：地址選擇
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        city = st.selectbox("縣市", list(taiwan_districts.keys()), index=None, label_visibility="collapsed", placeholder="縣市")
    with c2:
        dist_options = taiwan_districts[city] if city else []
        district = st.selectbox("行政區", dist_options, index=None, label_visibility="collapsed", placeholder="行政區", disabled=not city)
    with c3:
        street_address = st.text_input("地址", placeholder="街道巷弄號樓", label_visibility="collapsed")
    
    # 顯示確認地址
    if city and district and street_address:
        full_address = f"{city}{district}{street_address}"
        st.caption(f"📍 地址確認：{full_address}")
    else:
        full_address = None

    st.divider() # 分隔線
    
    # 第二行：品項與理由
    item_col, reason_col = st.columns([1, 2])
    
    with item_col:
        main_options = ["其他"] + list(REPAIR_DATABASE.keys())
        selected_category = st.selectbox("修繕品項", main_options, index=None)
        
        if selected_category == "其他":
            final_item_name = st.text_input("輸入名稱")
        else:
            final_item_name = selected_category

    with reason_col:
        if selected_category == "其他":
            reason = st.text_area("修繕理由", placeholder="請自行輸入...", height=100)
        elif selected_category:
            reason_options = REPAIR_DATABASE[selected_category]
            selected_reason = st.selectbox("常見理由 (可修改)", reason_options, index=None, label_visibility="collapsed", placeholder="選擇理由...")
            reason = st.text_area("詳細理由", value=selected_reason if selected_reason else "", height=100, label_visibility="collapsed")
        else:
            reason = st.text_area("修繕理由", disabled=True, placeholder="👈 請先選擇品項", height=100)

# --- 步驟 2: 照片處理 ---
st.markdown("#### 2️⃣ 影像紀錄")

def render_photo_card(title, key_prefix, icon, is_invoice=False):
    # 決定提示文字與裁切比例
    if is_invoice:
        aspect = None # 發票不鎖定比例，也不裁切
        help_text = "發票模式：直接顯示原圖 (匯出 17x17cm)"
    else:
        aspect = (4, 3) # 一般照片鎖定 4:3
        help_text = "修繕模式：請調整紅框 (匯出 4:3 比例)"

    with st.container(border=True):
        st.markdown(f"**{icon} {title}**")
        st.caption(help_text)
        
        t1, t2, t3 = st.tabs(["📸 1", "📸 2", "📸 3"])
        image_list = []
        
        for i, tab in enumerate([t1, t2, t3]):
            with tab:
                u_key = f"{key_prefix}_{i+1}"
                uploaded = st.file_uploader(f"上傳照片 {i+1}", type=['jpg', 'jpeg', 'png'], key=u_key, label_visibility="collapsed")
                
                if uploaded:
                    # 1. 讀取並轉正 (解決手機照片旋轉問題)
                    img = Image.open(uploaded)
                    img = ImageOps.exif_transpose(img)
                    
                    if is_invoice:
                        # 發票模式：直接顯示原圖
                        st.image(img, use_container_width=True)
                        image_list.append(img)
                    else:
                        # 一般模式：裁切器
                        # box_color: 紅框
                        # aspect_ratio: (4,3) 鎖定比例，確保匯出一致
                        cropped = st_cropper(
                            img, 
                            realtime_update=True, 
                            box_color='#FF0000', 
                            aspect_ratio=aspect, 
                            key=f"crop_{u_key}"
                        )
                        # 預覽區 (放在下面比較好對照)
                        with st.expander("查看裁切結果"):
                            st.image(cropped, caption="將匯出的畫面", use_container_width=True)
                        image_list.append(cropped)
                else:
                    image_list.append(None)
        return image_list

# 2x2 照片佈局
r1c1, r1c2 = st.columns(2)
with r1c1: imgs_before = render_photo_card("修繕前", "before", "🏚️")
with r1c2: imgs_during = render_photo_card("修繕中", "during", "🚧")

r2c1, r2c2 = st.columns(2)
with r2c1: imgs_after = render_photo_card("修繕後", "after", "✨")
with r2c2: imgs_invoice = render_photo_card("發票/收據", "invoice", "🧾", is_invoice=True)

# --- 步驟 3: 匯出 ---
st.markdown("#### 3️⃣ 輸出報告")

can_submit = full_address and final_item_name and os.path.exists("template.docx")

if st.button("🚀 生成 Word 報告", type="primary", use_container_width=True, disabled=not can_submit):
    if not can_submit:
        st.error("資料不完整或找不到模板")
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
                    # 發票強制 170mm x 170mm (17cm)
                    return InlineImage(doc, buf, width=Mm(170), height=Mm(170))
                else:
                    # 一般照片：寬度 80mm。因為裁切器鎖定 4:3，所以高度會自動變成 60mm
                    # 這樣就保證了「只依照紅框呈現」且「比例不跑掉」
                    return InlineImage(doc, buf, width=Mm(80))

            # 處理一般照片
            for prefix, img_list in {"img_before": imgs_before, "img_during": imgs_during, "img_after": imgs_after}.items():
                for idx, img_obj in enumerate(img_list):
                    context[f"{prefix}_{idx+1}"] = process_img(img_obj, is_invoice_img=False)

            # 處理發票
            for idx, img_obj in enumerate(imgs_invoice):
                context[f"img_invoice_{idx+1}"] = process_img(img_obj, is_invoice_img=True)

            doc.render(context)
            bio = io.BytesIO()
            doc.save(bio)
            
            filename = f"{full_address}-{final_item_name}.docx"
            st.success(f"🎉 報告已生成！")
            st.download_button("📥 下載 Word 檔", bio.getvalue(), filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary")
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")

# --- 底部返回按鈕 ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("⬅️ 回主目錄", use_container_width=True):
    st.switch_page("app.py")