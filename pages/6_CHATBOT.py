import streamlit as st
import mysql.connector
import re
import pandas as pd

# ========== DB ==========
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="fast",
        database="petrol_db"
    )

def query(sql, params=None):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or [])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ========== NLP HELPERS ==========

MONTHS = {
    "january":1, "jan":1,
    "february":2, "feb":2,
    "march":3, "mar":3,
    "april":4, "apr":4,
    "may":5,
    "june":6, "jun":6,
    "july":7, "jul":7,
    "august":8, "aug":8,
    "september":9, "sep":9,
    "october":10, "oct":10,
    "november":11, "nov":11,
    "december":12, "dec":12
}

def extract_year(text):
    m = re.search(r"(20\d{2})", text)
    return int(m.group(1)) if m else None

def extract_date(text):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    return m.group(1) if m else None

def extract_month(text):
    for k,v in MONTHS.items():
        if k in text:
            return v
    return None

def extract_fuel(text):
    if "diesel" in text: return "Diesel"
    if "petrol" in text: return "Petrol"
    return None

def extract_metric(text):
    if "profit" in text: return "profit"
    if "revenue" in text: return "revenue"
    if "sale" in text or "sold" in text: return "sales"
    if "expense" in text or "cost" in text: return "expenses"
    if "stock" in text: return "stock"
    return None

# ========== QUERY HANDLER ==========

def handle_query(text):
    t = text.lower().strip()

    metric = extract_metric(t)
    fuel = extract_fuel(t)
    year = extract_year(t)
    month = extract_month(t)
    date = extract_date(t)

    # ----------- DAILY MODE -----------
    if date and metric:
        if metric == "profit":
            sql = "SELECT profit FROM vw_profit_analysis WHERE date=%s"
            params=[date]
            if fuel:
                sql+=" AND fuel_type=%s"
                params.append(fuel)
            data=query(sql, params)
            if not data:
                return f"No profit data on {date}."
            value=data[0]['profit']
            return f"Profit on {date}: ₹{value:,.0f}"

        if metric == "sales":
            sql = """
                SELECT SUM(quantity_sold) AS vol 
                FROM fuel_sales 
                WHERE date=%s
            """
            params=[date]
            if fuel:
                sql+=" AND fuel_type=%s"
                params.append(fuel)
            data=query(sql, params)
            value = data[0]['vol'] if data else None
            if not value:
                return f"No sales data on {date}."
            return f"Fuel sold on {date}: {value:,.0f} litres"

        if metric == "revenue":
            sql = """
                SELECT SUM(fs.quantity_sold * fp.selling_price) AS rev
                FROM fuel_sales fs
                JOIN fuel_price fp ON fs.date=fp.date AND fs.fuel_type=fp.fuel_type
                WHERE fs.date=%s
            """
            params=[date]
            if fuel:
                sql+=" AND fs.fuel_type=%s"
                params.append(fuel)
            data=query(sql, params)
            value=data[0]['rev'] if data else None
            if not value:
                return f"No revenue data on {date}."
            return f"Revenue on {date}: ₹{value:,.0f}"

        if metric == "expenses":
            sql="SELECT SUM(amount) AS total FROM expenses WHERE date=%s"
            data=query(sql,[date])
            value=data[0]['total'] if data else None
            return f"Expenses on {date}: ₹{value or 0:,.0f}"

        if metric == "stock":
            sql="SELECT closing_stock FROM vw_fuel_stock WHERE date=%s"
            params=[date]
            if fuel:
                sql+=" AND fuel_type=%s"
                params.append(fuel)
            data=query(sql,params)
            if not data:
                return f"No stock data on {date}."
            return f"Closing stock on {date}: {data[0]['closing_stock']} litres"

    # ----------- MONTHLY MODE -----------
    if month and year and metric:
        if metric == "profit":
            sql="""
                SELECT SUM(profit) AS val FROM vw_profit_analysis
                WHERE YEAR(date)=%s AND MONTH(date)=%s
            """
            params=[year,month]
            if fuel:
                sql+=" AND fuel_type=%s"
                params.append(fuel)
            data=query(sql,params)
            v=data[0]['val'] if data else None
            return f"Profit in {year}-{month:02d}: ₹{v or 0:,.0f}"

        if metric == "sales":
            sql="SELECT SUM(quantity_sold) AS vol FROM fuel_sales WHERE YEAR(date)=%s AND MONTH(date)=%s"
            params=[year,month]
            if fuel:
                sql+=" AND fuel_type=%s"
                params.append(fuel)
            data=query(sql,params)
            v=data[0]['vol'] if data else None
            return f"Sales in {year}-{month:02d}: {v or 0:,.0f} litres"

        if metric == "revenue":
            sql="""
                SELECT SUM(fs.quantity_sold * fp.selling_price) AS rev
                FROM fuel_sales fs
                JOIN fuel_price fp ON fs.date=fp.date AND fs.fuel_type=fp.fuel_type
                WHERE YEAR(fs.date)=%s AND MONTH(fs.date)=%s
            """
            params=[year,month]
            if fuel:
                sql+=" AND fs.fuel_type=%s"
                params.append(fuel)
            data=query(sql,params)
            v=data[0]['rev'] if data else None
            return f"Revenue in {year}-{month:02d}: ₹{v or 0:,.0f}"

        if metric == "expenses":
            sql="SELECT SUM(amount) AS total FROM expenses WHERE YEAR(date)=%s AND MONTH(date)=%s"
            data=query(sql,[year,month])
            v=data[0]['total'] if data else None
            return f"Expenses in {year}-{month:02d}: ₹{v or 0:,.0f}"

    # ----------- YEARLY MODE -----------
    if year and metric:
        if metric == "profit":
            sql="SELECT SUM(profit) AS val FROM vw_profit_analysis WHERE YEAR(date)=%s"
            params=[year]
            if fuel:
                sql+=" AND fuel_type=%s"
                params.append(fuel)
            data=query(sql,params)
            v=data[0]['val'] if data else None
            return f"Profit in {year}: ₹{v or 0:,.0f}"

        if metric == "sales":
            sql="SELECT SUM(quantity_sold) AS vol FROM fuel_sales WHERE YEAR(date)=%s"
            params=[year]
            if fuel:
                sql+=" AND fuel_type=%s"
                params.append(fuel)
            data=query(sql,params)
            v=data[0]['vol'] if data else None
            return f"Sales in {year}: {v or 0:,.0f} litres"

        if metric == "revenue":
            sql="""
                SELECT SUM(fs.quantity_sold * fp.selling_price) AS rev
                FROM fuel_sales fs
                JOIN fuel_price fp ON fs.date=fp.date AND fs.fuel_type=fp.fuel_type
                WHERE YEAR(fs.date)=%s
            """
            params=[year]
            if fuel:
                sql+=" AND fs.fuel_type=%s"
                params.append(fuel)
            data=query(sql,params)
            v=data[0]['rev'] if data else None
            return f"Revenue in {year}: ₹{v or 0:,.0f}"

        if metric == "expenses":
            sql="SELECT SUM(amount) AS total FROM expenses WHERE YEAR(date)=%s"
            data=query(sql,[year])
            v=data[0]['total'] if data else None
            return f"Expenses in {year}: ₹{v or 0:,.0f}"

    return "I couldn't understand your query. Try: profit in 2025"
    

# ========== STREAMLIT UI ==========

st.title("⛽ Fuel Bunk Query Assistant")

q = st.chat_input("Ask (e.g., profit in 2025, diesel sales on 2024-02-10)")

if q:
    ans = handle_query(q)
    with st.chat_message("assistant"):
        st.markdown(ans)
