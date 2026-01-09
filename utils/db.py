from sqlalchemy import create_engine

def get_connection():
    return create_engine(
        "mysql+pymysql://root:fast@localhost:3306/petrol_db"
    )

def load_sales():
    return pd.read_sql("SELECT * FROM vw_sales ORDER BY date", engine)

def load_stock():
    return pd.read_sql("SELECT * FROM vw_stock ORDER BY date", engine)

def load_financial():
    return pd.read_sql("SELECT * FROM vw_financial ORDER BY date", engine)
