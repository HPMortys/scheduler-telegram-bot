import sqlite3
from db.constants import DB_FILE


class Database:
    class Tables:
        user = 'user'
        scheduler_test = 'scheduler_test'

    def __init__(self, db_file=DB_FILE):
        print(db_file)
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        # columns should be a dictionary of column names and types
        columns_str = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")
        self.conn.commit()

    def insert_row(self, table_name, values):
        # values should be a dictionary of column names and values
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["?" for _ in values])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(values.values()))
        self.conn.commit()

    def update_row(self, table_name, values, where):
        # values should be a dictionary of column names and values to update
        # where should be a dictionary of column names and values to filter by
        set_values = ", ".join([f"{col_name} = ?" for col_name in values])
        where_clause = " AND ".join([f"{col_name} = ?" for col_name in where])
        query = f"UPDATE {table_name} SET {set_values} WHERE {where_clause}"
        self.cursor.execute(query, tuple(values.values()) + tuple(where.values()))
        self.conn.commit()

    def delete_row(self, table_name, where, operator):
        # where should be a dictionary of column names and values to filter by
        where_clause = " AND ".join([f"{col_name} = ?" for col_name in where])
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        self.cursor.execute(query, tuple(where.values()))
        self.conn.commit()

    def select_rows(self, table_name, columns=None, where=None, order_by=None):
        # columns should be a list of column names to select (or None for all columns)
        # where should be a dictionary of column names and values to filter by (or None for no filter)
        # order_by should be a list of column names to order by (or None for no order)
        columns_str = "*" if columns is None else ", ".join(columns)
        where_clause = "" if where is None else "WHERE " + " AND ".join([f"{col_name} = ?" for col_name in where])
        order_by_clause = "" if order_by is None else "ORDER BY " + ", ".join(order_by)
        query = f"SELECT {columns_str} FROM {table_name} {where_clause} {order_by_clause}"
        params = [] if where is None else tuple(where.values())
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        print('closed')
        self.cursor.close()
        self.conn.close()

    def __del__(self):
        self.close()
