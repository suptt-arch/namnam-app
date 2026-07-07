import streamlit as st
import pandas as pd

# ดึงลิงก์ Google Sheets จาก Secrets ที่หยอดไว้
try:
    sheet_url = st.secrets["public_gsheet_url"]
    # แปลงลิงก์ให้เป็นแบบดึงข้อมูล CSV
    csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv").replace("/edit#gid=", "/export?format=csv&gid=")
except:
    st.error("❌ ไม่พบลิงก์ Google Sheets ในระบบ Secrets กรุณาเช็กการตั้งค่าอีกครั้ง")
    st.stop()

st.set_page_config(page_title="ระบบจัดการร้านนับนับ POS", layout="wide")

# เมนูหลัก 7 แท็บภาษาไทย
menu = ["📊 Dashboard", "🛍️ เปิดบิล (POS)", "📦 คลังสินค้า", "🧾 ประวัติบิล", "👥 ลูกหนี้", "🚛 ซัพพลายเออร์", "⚙️ ตั้งค่า"]
choice = st.sidebar.selectbox("เมนูระบบ", menu)

st.title(f"🏪 ระบบร้านนับนับ - หน้า {choice}")

# โหลดข้อมูลจาก Google Sheets (แท็บแรกเป็นตัวอย่างก่อน)
try:
    df = pd.read_csv(csv_url)
    
    if choice == "📊 Dashboard":
        st.subheader("สรุปภาพรวมร้านค้าส่งวันนี้")
        st.dataframe(df)
        
    elif choice == "🛍️ เปิดบิล (POS)":
        st.subheader("หน้าต่างเปิดบิลและจัดสินค้า (รองรับโหมดตาบอดสี/เสียงอ่าน)")
        st.info("ระบบกำลังดึงข้อมูลตะกร้าสินค้า...")
        
    elif choice == "📦 คลังสินค้า":
        st.subheader("จัดการรายการสต็อกสินค้าและราคาทุนเฉลี่ย")
        st.write("รายการสินค้าในคลังปัจจุบัน:")
        st.dataframe(df)
        
    else:
        st.write(f"กำลังโหลดระบบหน้า {choice}...")
except Exception as e:
    st.warning("🔄 กำลังเชื่อมต่อท่อน้ำเลี้ยงข้อมูลกับ Google Sheets ของคุณ...")
    st.caption("หากข้อมูลไม่ขึ้น กรุณาตรวจสอบว่า Google Sheets ตั้งค่าสิทธิ์เป็น 'ทุกคนที่มีลิงก์มีสิทธิ์อ่าน' แล้วหรือยัง")
