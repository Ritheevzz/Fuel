import streamlit as st
from datetime import date
from sqlalchemy import text
from utils.db import get_connection

# === CONFIG ===
st.set_page_config(layout="wide", page_title="Fuel Station Dashboard")

engine = get_connection()

# === HERO BANNER ===
from PIL import Image
import streamlit as st

hero = Image.open("assets/hero.jpeg")

st.image(hero, use_container_width=True)
st.title("⛽ Fuel Station Operations Dashboard")
st.caption("Displays fuel sales performance and revenue trends.")

st.markdown("---")
st.subheader("📌 Overview")
st.write(
    "This platform provides a unified interface for managing **daily sales**, "
    "**fuel stock**, **operational buying price**, and **expenses**, enabling "
    "**accurate financial profit & cost tracking** for fuel stations."
)


# ============================================
# FEATURE MODULES
# ============================================
st.markdown("---")
st.subheader("🧩 Platform Modules")

cols = st.columns(3)

with cols[0]:
    st.markdown("### ⛽ Fuel Stock Management")
    st.write("Track opening/closing stock, tanker receipts & reconciliation.")

with cols[1]:
    st.markdown("### 🏷 Fuel Sales & Billing")
    st.write("Log daily fuel sales, selling prices & customer billing.")

with cols[2]:
    st.markdown("### 💰 Expense Management")
    st.write("Capture EB bills, salaries, maintenance, AMC & operating costs.")

cols2 = st.columns(3)

with cols2[0]:
    st.markdown("### 📉 Buying Price Tracking")
    st.write("Log daily buying price changes for operational tracking.")

with cols2[1]:
    st.markdown("### 📊 Profit & Margin Analytics")
    st.write("Automated margin & profit calculation based on input data.")

with cols2[2]:
    st.markdown("### 🤖 AI Forecasting (Beta)")
    st.write("Predict future fuel demand & selling price trends.")

st.markdown("---")

# === EXPANDER SECTIONS ===
st.title("📥 Daily Operations – Data Entry")

# 1. STOCK ENTRY
from PIL import Image
import streamlit as st

hero = Image.open("assets/STOCK.jpeg")

st.image(hero, use_container_width=True)
with st.expander("📦 Fuel Stock Entry", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        stock_date = st.date_input("Stock Date", key="stock_date", value=date.today())
        stock_fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel"], key="stock_fuel")

    # Fetch opening dynamically
    with engine.connect() as conn:
        prev = conn.execute(
            text("""
                SELECT closing_stock FROM vw_fuel_stock
                WHERE fuel_type = :fuel AND date < :date
                ORDER BY date DESC LIMIT 1
            """), {"fuel": stock_fuel_type, "date": stock_date}
        ).fetchone()

    opening_stock = prev[0] if prev else 0
    st.info(f"Opening Stock: **{opening_stock} Litres**")

    received = st.number_input("Received Stock (Litres)", min_value=0.0, step=1.0)
    if st.button("Save Stock Entry"):
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO fuel_stock(date,fuel_type,opening_stock,received_stock,closing_stock)
                    VALUES(:d,:f,:o,:r,0)
                """),
                {"d": stock_date, "f": stock_fuel_type, "o": opening_stock, "r": received}
            )
            conn.commit()
        st.cache_data.clear()
        st.success("Stock Entry Saved Successfully ✔")
st.markdown("---")


# 2. SALES ENTRY
from PIL import Image
import streamlit as st

hero = Image.open("assets/SALES.jpeg")

st.image(hero, use_container_width=True)
with st.expander("⛽ Fuel Sales Entry", expanded=False):

    col1, col2, col3 = st.columns(3)
    sale_date = col1.date_input("Date", value=date.today())
    fuel_type = col2.selectbox("Fuel Type", ["Petrol", "Diesel"])
    quantity_sold = col3.number_input("Quantity Sold (Litres)", min_value=0.0, step=1.0)

    col4, col5 = st.columns(2)
    buying_price = col4.number_input("Buying Price (₹/L)", min_value=0.0, step=0.1)
    selling_price = col5.number_input("Selling Price (₹/L)", min_value=0.0, step=0.1)

    if st.button("Save Sales Entry"):
        with engine.connect() as conn:
            # insert sales
            conn.execute(
                text("""
                    INSERT INTO fuel_sales(date,fuel_type,quantity_sold,selling_price,total_amount)
                    VALUES(:d,:f,:q,:s,:t)
                """),
                {"d": sale_date, "f": fuel_type, "q": quantity_sold,
                 "s": selling_price, "t": selling_price * quantity_sold}
            )

            # insert/update buying price
            conn.execute(
                text("""
                    INSERT INTO fuel_price(date,fuel_type,buying_price)
                    VALUES(:d,:f,:b) AS new
                    ON DUPLICATE KEY UPDATE buying_price=new.buying_price
                """),
                {"d": sale_date, "f": fuel_type, "b": buying_price}
            )

            conn.commit()

        st.cache_data.clear()
        st.success("Sales Entry Saved Successfully ✔")
st.markdown("---")


# 3. EXPENSE ENTRY
from PIL import Image
import streamlit as st

hero = Image.open("assets/EXPENSE.jpeg")

st.image(hero, use_container_width=True)
with st.expander("💸 Expense Entry", expanded=False):
    exp_date = st.date_input("Expense Date", value=date.today())
    exp_type = st.text_input("Expense Type", placeholder="Salary, EB, Maintenance...")
    exp_amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)

    if st.button("Save Expense Entry"):
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO expenses(date, expense_type, amount)
                    VALUES(:d, :t, :a)
                """),
                {"d": exp_date, "t": exp_type, "a": exp_amount}
            )
            conn.commit()
        st.cache_data.clear()
        st.success("Expense Entry Saved Successfully ✔")

# ============================================
# ABOUT COMPANY
# ============================================
st.markdown("---")
st.subheader("🏢 About")

st.write(
    "We are a software team focused on solving operational inefficiencies in the fuel "
    "retail sector. Many stations rely on manual paper logs, leading to errors, missing "
    "data, and poor procurement decisions. Our mission is to introduce modern AI-powered "
    "operational management to fuel stations with real-world workflows."
)


# ============================================
# PRODUCT ROADMAP
# ============================================
st.markdown("---")
st.subheader("🛣 Product Roadmap")

roadmap = [
    "AI price & demand forecasting",
    "Crude oil market integration",
    "OMC auto price circular updates (IOCL/BPCL/HPCL)",
    "Mobile application for operators",
    "Multi-station support",
    "Tally + GST invoice integration",
    "Vendor purchase tracking",
    "WhatsApp & SMS alert system",
    "Fleet billing & credit accounts",
]

for item in roadmap:
    st.write(f"✔ {item}")


# ============================================
# CONTACT SECTION
# ============================================
st.markdown("---")
st.subheader("📞 Contact & Support")

st.write("📍 **Address:** XYZ Fuel Software Solutions, Chennai, India")
st.write("📧 **Email:** support@fuel-platform.com")
st.write("📞 **Phone:** +91 98765 43210")
st.write("🕒 **Support Hours:** 09:00 AM – 09:00 PM IST")


# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; opacity:0.6; font-size:14px;'>"
    "© 2026 Fuel Station Operations Platform — All Rights Reserved<br>"
    "Version: v0.1.0-beta"
    "</div>",
    unsafe_allow_html=True
)


