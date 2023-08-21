# sqlite dadtabase connection
import sqlite3
def connect_to_db():
    conn = sqlite3.connect('gitlab.sqlite')
    return conn

from sqlalchemy import create_engine

# sqlite database connection
def connect_to_db_engine():
    DATABASE_URL = "sqlite:///gitlab.sqlite"
    engine = create_engine(DATABASE_URL, echo=True)  # echo=True will log SQL statements, turn it off in production
    return engine


def get_table_info():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"Table: {table_name}")
        for column in columns:
            print(column)
        print("\n")
    conn.close()

if __name__ == "__main__":
    get_table_info()