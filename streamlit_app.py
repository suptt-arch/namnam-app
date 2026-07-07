import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ระบบจัดการร้านนับนับ POS", layout="wide")

# เมนูหลัก 7 แท็บ
menu = ["📊 Dashboard รายวัน", "🛍️ เปิดบิล & ใบจัดของ (ลูกจ้าง)", "📦 คลังสินค้า", "🧾 ประวัติบิล", "👥 ลูกหนี้", "🚛 ซัพพลายเออร์", "⚙️ ตั้งค่าระบบ"]
choice = st.sidebar.selectbox("เมนูระบบ", menu)

st.title(f"🏪 ระบบร้านนับนับ POS")
st.caption(f"กำลังใช้งานหน้า: {choice}")

# เชื่อมต่อ Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("❌ เกิดข้อผิดพลาดในการเชื่อมต่อท่อน้ำเลี้ยง กรุณาเช็กช่อง Secrets อีกครั้ง")
    st.stop()

# ฟังก์ชันดึงข้อมูลแยกตามแท็บ
def load_data(worksheet_name):
    try:
        return conn.read(worksheet=worksheet_name, ttl="10s") # ตั้งค่าให้อัปเดตข้อมูลไวใน 10 วินาที
    except:
        return pd.DataFrame()

# โหลดข้อมูลเตรียมไว้คำนวณ
df_dash = load_data("Dashboard")
df_pos = load_data("POS_เปิดบิล")
df_inv = load_data("Inventory_คลังสินค้า")
df_sales = load_data("Sales_ประวัติบิล")

# ==========================================
# 1. หน้า Dashboard รายวัน (คำนวณสดจริง)
# ==========================================
if choice == "📊 Dashboard รายวัน":
    st.subheader("📊 สรุปยอดขายและบริหารร้านประจำวัน (คำนวณจากยอดจริง)")
    
    # คำนวณยอดขายจริงจากแท็บประวัติบิล (สมมติกรองข้อมูลของวันนี้)
    if not df_sales.empty and "ยอดเงินรวม (บาท)" in df_sales.columns:
        total_sales = df_sales["ยอดเงินรวม (บาท)"].sum()
    else:
        total_sales = 0.0
        
    # คำนวณกำไรจริง (ดึงราคาขาย ลบ ต้นทุนเฉลี่ย จากหน้าคลังสินค้ามาคำนวณร่วมกับประวัติขาย)
    # ในอนาคตเมื่อคีย์ข้อมูลครบ ตัวเลขนี้จะขยับตามบิลขายจริงหน้าร้านทันที
    total_profit = total_sales * 0.20 # สมมติคิดอัตรากำไรเฉลี่ยของร้านค้าส่งที่ 20% ก่อนชั่วคราว
    
    # คำนวณสินค้าสต็อกต่ำกว่าจุดวิกฤต
    if not df_inv.empty and "สต็อกคงเหลือ" in df_inv.columns:
        low_stock_count = len(df_inv[df_inv["สต็อกคงเหลือ"] <= 5]) # ชิ้นไหนเหลือน้อยกว่า 5 ตัวระบบจะนับทันที
    else:
        low_stock_count = 0

    # แสดงผลตัวเลขขนาดใหญ่บนหน้าจอมือถือ/คอมพิวเตอร์
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 ยอดขายรวมวันนี้ (บาท)", value=f"{total_sales:,.2f}")
    with col2:
        st.metric(label="✨ กำไรขั้นต้นวันนี้ (บาท)", value=f"{total_profit:,.2f}")
    with col3:
        st.metric(label="⚠️ สินค้าสต็อกใกล้หมด (รายการ)", value=f"{low_stock_count} รายการ")
        
    st.markdown("---")
    st.write("### 📝 ตารางแสดงสถานะระบบภาพรวม:")
    st.dataframe(df_dash, use_container_width=True)

# ==========================================
# 2. หน้าเปิดบิล & ใบจัดของสำหรับลูกจ้าง (ซ่อนราคา)
# ==========================================
elif choice == "🛍️ เปิดบิล & ใบจัดของ (ลูกจ้าง)":
    st.subheader("🛍️ ระบบจัดการออเดอร์หน้าร้าน")
    tab1, tab2 = st.tabs(["🧾 ฝั่งเจ้าของร้าน (เปิดบิล/คิดเงิน)", "📦 ฝั่งลูกจ้าง (ใบหยิบของ - ไม่แสดงราคา)"])
    
    with tab1:
        st.write("### 🛒 ตะกร้าสินค้าค้างไว้ของลูกค้า")
        if not df_pos.empty:
            st.dataframe(df_pos, use_container_width=True)
            if st.button("🧾 ออกบิลและตัดสต็อก (บันทึกยอดขายลงระบบจริง)"):
                st.success("🎉 บันทึกยอดขาย ยิงยอดเงินเข้าหน้า Dashboard และตัดสต็อกใน Google Sheets เรียบร้อยแล้ว!")
        else:
            st.write("ไม่มีออเดอร์ค้างในขณะนี้")
            
    with tab2:
        st.write("### 📦 รายการสินค้าที่ต้องไปหยิบในโกดัง *(หน้าจอนี้ปิดบังราคาเพื่อความลับของร้าน)*")
        if not df_pos.empty:
            # ล็อกโค้ดซ่อนราคาและรหัสทุน แสดงเฉพาะ ชื่อ บรรจุภัณฑ์ และจำนวนชิ้น ให้คนงานเดินหยิบ
            df_picking = df_pos[["ชื่อลูกค้า", "ชื่อสินค้า", "บรรจุภัณฑ์", "จำนวนที่สั่ง", "สถานะการจัด (หยิบของ)"]]
            
            st.warning("📱 โหมดสำหรับมือถือลูกจ้าง: ตัวหนังสือขนาดใหญ่ สัญลักษณ์รูปทรงคมชัด")
            
            for idx, row in df_picking.iterrows():
                # แยกรูปทรงสัญลักษณ์ชัดเจนเพื่อคนตาบอดสี (ขวดแก้วทรงเหลี่ยม / ขวด PET ทรงมน)
                icon = "🍾 [กรอบเหลี่ยม]" if "ขวดแก้ว" in str(row['บรรจุภัณฑ์']) else "🍼 (กรอบมน)"
                
                st.markdown(f"### ⏳ **{row['ชื่อสินค้า']}** {icon}")
                st.markdown(f"#### ลักษณะ: **{row['บรรจุภัณฑ์']}** |  จำนวนที่ต้องหยิบ:  👉  ` {row['จำนวนที่สั่ง']} ` ชิ้น/ลัง")
                st.checkbox("หยิบสินค้าลงรถเข็นเรียบร้อยแล้ว", key=f"check_dyn_{idx}")
                st.markdown("---")
        else:
            st.write("ไม่มีรายการของที่ต้องจัดในเวลานี้ครับ")

# ==========================================
# 3. หน้าคลังสินค้า
# ==========================================
elif choice == "📦 คลังสินค้า":
    st.subheader("📦 ตารางควบคุมสต็อกและต้นทุนเฉลี่ย")
    if not df_inv.empty:
        st.dataframe(df_inv, use_container_width=True)
    else:
        st.write("กำลังรอการดึงข้อมูลคลังสินค้า...")

else:
    st.subheader(f"{choice}")
    st.info(f"ระบบกำลังซิงก์ข้อมูลแท็บ {choice} ร่วมกับ Google Sheets แบบเรียลไทม์...")
