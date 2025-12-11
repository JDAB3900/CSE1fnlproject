# models.py
from db import get_db_connection

def fetch_all_employees(filters=None, limit=100, offset=0):
    conn = get_db_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM employees"
    params = []
    if filters:
        clauses = []
        for k,v in filters.items():
            clauses.append(f"{k} LIKE %s")
            params.append(f"%{v}%")
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fetch_employee(emp_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE id=%s", (emp_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def create_employee(data):
    conn = get_db_connection()
    cur = conn.cursor()
    keys = ", ".join(data.keys())
    vals_placeholders = ", ".join(["%s"] * len(data))
    sql = f"INSERT INTO employees ({keys}) VALUES ({vals_placeholders})"
    cur.execute(sql, tuple(data.values()))
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return fetch_employee(new_id)

def update_employee(emp_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    set_clause = ", ".join([f"{k}=%s" for k in data.keys()])
    params = list(data.values()) + [emp_id]
    sql = f"UPDATE employees SET {set_clause} WHERE id=%s"
    cur.execute(sql, params)
    cur.close()
    conn.close()
    return fetch_employee(emp_id)

def delete_employee(emp_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
    affected = cur.rowcount
    cur.close()
    conn.close()
    return affected
