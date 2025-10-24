import psycopg2
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port":os.getenv("PORT")
}

def query_database(query: str):
    """Execute a SQL query and return the results"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def get_schema():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """)
        tables = cursor.fetchall()
        schema = {}
        for table_name_tuple in tables:
            table = table_name_tuple[0]
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name='{table}'
            """)
            columns = cursor.fetchall()
            schema[table] = [{"column_name": c[0], "data_type": c[1]} for c in columns]
        conn.close()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))