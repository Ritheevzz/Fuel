import sys
import os

# This automatically finds the project root (NO hardcoded path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from sqlalchemy import text
from utils.db import get_connection

st.set_page_config(layout="wide")
st.title("📥 Daily Operations – Data Entry")

engine = get_connection()

# ===============================
# 📦 STOCK ENTRY (AUTO OPENING STOCK)
# ===============================
from PIL import Image
import streamlit as st

hero = Image.open("assets/hero.jpeg")
st.subheader("📦 Fuel Stock Entry")

stock_date = st.date_input("Stock Date", key="stock_date")
stock_fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel"], key="stock_fuel")

# Get opening stock from last day
with engine.connect() as conn:
    result = conn.execute(
        text("""
            SELECT closing_stock
            FROM vw_fuel_stock
            WHERE fuel_type = :fuel
              AND date < :date
            ORDER BY date DESC
            LIMIT 1
        """),
        {"fuel": stock_fuel_type, "date": stock_date}
    ).fetchone()

if result:
    opening_stock = result[0]
    st.success(f"Opening Stock (Auto): {opening_stock} Litres")
else:
    opening_stock = 0
    st.warning("⚠️ No previous stock data found. Opening stock set to 0.")

with st.form("fuel_stock_form"):
    received_stock = st.number_input("Received Stock (Litres)", min_value=0.0, step=1.0)
    save_stock = st.form_submit_button("Save Stock Details")

if save_stock:
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO fuel_stock (date, fuel_type, opening_stock, received_stock, closing_stock)
                VALUES (:date, :fuel, :opening, :received, 0)
            """),
            {"date": stock_date, "fuel": stock_fuel_type, "opening": opening_stock, "received": received_stock}
        )
        conn.commit()

    st.cache_data.clear()
    st.success("✅ Stock saved successfully")

st.markdown("---")

# ===============================
# ⛽ FUEL SALES ENTRY
# ===============================
st.subheader("⛽ Fuel Sales Entry")
from PIL import Image
import streamlit as st

hero = Image.open("assets/hero.jpeg")


with st.form("fuel_sales_form"):
    sale_date = st.date_input("Date")
    fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel"])

    buying_price = st.number_input("Buying Price per Litre (₹)", min_value=0.0, step=0.1)
    quantity_sold = st.number_input("Quantity Sold (Litres)", min_value=0.0, step=1.0)
    selling_price = st.number_input("Selling Price per Litre (₹)", min_value=0.0, step=0.1)

    save_sales = st.form_submit_button("Save Fuel Sales")

if save_sales:
    if quantity_sold > 0 and selling_price > 0 and buying_price > 0:
        with engine.connect() as conn:

            # Insert sales transaction
            conn.execute(
                text("""
                    INSERT INTO fuel_sales (date, fuel_type, quantity_sold, selling_price, total_amount)
                    VALUES (:date, :fuel, :qty, :price, :total)
                """),
                {
                    "date": sale_date,
                    "fuel": fuel_type,
                    "qty": quantity_sold,
                    "price": selling_price,
                    "total": quantity_sold * selling_price
                }
            )

            # Insert or update daily buying price
            conn.execute(
                text("""
                    INSERT INTO fuel_price (date, fuel_type, buying_price)
                    VALUES (:date, :fuel, :buy)
                    AS new
                    ON DUPLICATE KEY UPDATE buying_price = new.buying_price
                """),
                {"date": sale_date, "fuel": fuel_type, "buy": buying_price}
            )

            conn.commit()

        st.cache_data.clear()
        st.success("✅ Fuel sales & buying price saved successfully")
    else:
        st.warning("⚠️ Quantity, selling price and buying price must be greater than zero")

st.markdown("---")

# ===============================
# 💸 EXPENSE ENTRY
# ===============================
st.subheader("💸 Expense Entry")

with st.form("expense_form"):
    expense_date = st.date_input("Expense Date", key="expense_date")
    expense_type = st.text_input("Expense Type (Salary, EB, Maintenance, etc.)")
    expense_amount = st.number_input("Expense Amount (₹)", min_value=0.0, step=10.0)

    save_expense = st.form_submit_button("Save Expense")

if save_expense:
    if expense_type.strip() and expense_amount > 0:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO expenses (date, expense_type, amount)
                    VALUES (:date, :type, :amount)
                """),
                {"date": expense_date, "type": expense_type, "amount": expense_amount}
            )
            conn.commit()

        st.cache_data.clear()
        st.success("✅ Expense saved successfully")
    else:
        st.warning("⚠️ Enter valid expense type and amount")

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

