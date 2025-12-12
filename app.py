# app.py - Fixed and improved version
from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager, create_access_token, verify_jwt_in_request, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import dicttoxml
from xml.dom.minidom import parseString
import os
import sys

print(">>> RUNNING FROM:", __file__)

app = Flask(__name__)

# --- Config (match your provided values) ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678joel'
app.config['MYSQL_DB'] = 'init_db'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=2)

# --- Extensions ---
mysql = MySQL(app)
jwt = JWTManager(app)

@app.route("/_dbdebug")
def db_debug():
    try:
        print(">>> MySQL object:", mysql)
        print(">>> mysql.connection:", mysql.connection)
        if mysql.connection is None:
            return "ERROR: mysql.connection is None — Database handle FAILED to initialize", 500

        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE()")
        db = cur.fetchone()
        return f"DB CONNECTED OK — Current DB: {db}", 200

    except Exception as e:
        return f"DB ERROR: {e}", 500

# --- Helpers ---
def to_format(data, fmt='json'):
    """
    Return data as JSON (default) or XML if fmt == 'xml'.
    Accepts dicts and lists.
    """
    if fmt == 'xml':
        try:
            xml = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
            pretty = parseString(xml).toprettyxml()
            resp = make_response(pretty)
            resp.headers['Content-Type'] = 'application/xml'
            return resp
        except Exception as e:
            # Fallback to JSON if xml conversion fails
            return jsonify({'error': 'xml conversion failed', 'detail': str(e)})
    else:
        return jsonify(data)

def fetch_rows_as_dicts(cur):
    """
    Convert cursor.fetchall() results into list of dicts using cursor.description
    """
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    return [dict(zip(cols, r)) for r in rows]

def fetch_one_as_dict(cur):
    row = cur.fetchone()
    cols = [d[0] for d in cur.description] if cur.description else []
    return dict(zip(cols, row)) if row else None

# --- Auth ---
@app.route('/auth/register', methods=['POST'])
def register():
    body = request.json or {}
    username = body.get('username')
    password = body.get('password')
    role = body.get('role', 'user')
    if not username or not password:
        return jsonify({'msg':'username & password required'}), 400

    hashed = generate_password_hash(password)
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username,password,role) VALUES (%s,%s,%s)", (username, hashed, role))
        mysql.connection.commit()
    except Exception as e:
        # likely duplicate username or DB error
        return jsonify({'msg':'user exists or db error', 'err': str(e)}), 400
    finally:
        try:
            cur.close()
        except:
            pass

    return jsonify({'msg':'user created'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    body = request.json or {}
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        return jsonify({'msg':'username & password required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    if not row:
        cur.close()
        return jsonify({'msg':'invalid credentials'}), 401

    user_id, uname, pw_hash, role = row
    cur.close()

    if not check_password_hash(pw_hash, password):
        return jsonify({'msg':'invalid credentials'}), 401

    access = create_access_token(identity={'id': user_id, 'username': uname, 'role': role})
    return jsonify({'access_token': access}), 200

# --- Employees CRUD ---
@app.route('/employees', methods=['GET','POST'])
def employees_collection():
    fmt = (request.args.get('format') or 'json').lower()

    if request.method == 'GET':
        q = request.args.get('q')
        cur = mysql.connection.cursor()
        try:
            if q:
                like = f"%{q}%"
                cur.execute(
                    "SELECT e.*, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id=d.id "
                    "WHERE first_name LIKE %s OR last_name LIKE %s OR birth_city LIKE %s",
                    (like, like, like)
                )
            else:
                cur.execute("SELECT e.*, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id=d.id")
            rows = fetch_rows_as_dicts(cur)
            return to_format({'employees': rows}, fmt)
        finally:
            cur.close()

    # POST - create (protected)
    if request.method == 'POST':
        # require JWT
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({'msg': 'missing or invalid token', 'err': str(e)}), 401

        data = request.json or {}
        required = ['first_name','last_name']
        for f in required:
            if not data.get(f):
                return jsonify({'msg': f'{f} required'}), 400

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                """
                INSERT INTO employees (first_name,middle_name,last_name,name_extension,birthdate,birth_city,birth_province,birth_country,sex,civil_status,department_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    data.get('first_name'), data.get('middle_name'), data.get('last_name'), data.get('name_extension'),
                    data.get('birthdate'), data.get('birth_city'), data.get('birth_province'), data.get('birth_country'),
                    data.get('sex'), data.get('civil_status'), data.get('department_id')
                )
            )
            mysql.connection.commit()
            return jsonify({'msg':'employee created'}), 201
        except Exception as e:
            return jsonify({'msg':'db error', 'err': str(e)}), 400
        finally:
            cur.close()

@app.route('/employees/<int:emp_id>', methods=['GET','PUT','DELETE'])
def employee_item(emp_id):
    fmt = (request.args.get('format') or 'json').lower()
    cur = mysql.connection.cursor()
    try:
        if request.method == 'GET':
            cur.execute("SELECT e.*, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id=d.id WHERE e.id=%s", (emp_id,))
            row = fetch_one_as_dict(cur)
            if not row:
                return jsonify({'msg':'not found'}), 404
            return to_format(row, fmt)

        if request.method == 'PUT':
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'msg': 'missing or invalid token', 'err': str(e)}), 401

            data = request.json or {}
            allowed = ['first_name','middle_name','last_name','name_extension','birthdate','birth_city','birth_province','birth_country','sex','civil_status','department_id']
            sets = []
            vals = []
            for k in allowed:
                if k in data:
                    sets.append(f"{k}=%s")
                    vals.append(data[k])
            if not sets:
                return jsonify({'msg':'no updatable fields provided'}), 400
            vals.append(emp_id)
            sql = f"UPDATE employees SET {', '.join(sets)} WHERE id=%s"
            try:
                cur.execute(sql, tuple(vals))
                mysql.connection.commit()
                return jsonify({'msg':'updated'}), 200
            except Exception as e:
                return jsonify({'msg':'db error', 'err': str(e)}), 400

        if request.method == 'DELETE':
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'msg': 'missing or invalid token', 'err': str(e)}), 401
            try:
                cur.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
                mysql.connection.commit()
                return jsonify({'msg':'deleted'}), 200
            except Exception as e:
                return jsonify({'msg':'db error', 'err': str(e)}), 400
    finally:
        cur.close()

# --- Departments CRUD ---
@app.route('/departments', methods=['GET','POST'])
def departments_collection():
    fmt = (request.args.get('format') or 'json').lower()
    cur = mysql.connection.cursor()
    try:
        if request.method == 'GET':
            cur.execute("SELECT * FROM departments")
            rows = fetch_rows_as_dicts(cur)
            return to_format({'departments': rows}, fmt)

        if request.method == 'POST':
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'msg': 'missing or invalid token', 'err': str(e)}), 401
            data = request.json or {}
            if not data.get('name'):
                return jsonify({'msg':'name required'}), 400
            try:
                cur.execute("INSERT INTO departments (name,description) VALUES (%s,%s)", (data.get('name'), data.get('description')))
                mysql.connection.commit()
                return jsonify({'msg':'created'}), 201
            except Exception as e:
                return jsonify({'msg':'db error', 'err': str(e)}), 400
    finally:
        cur.close()

@app.route('/departments/<int:d_id>', methods=['GET','PUT','DELETE'])
def department_item(d_id):
    cur = mysql.connection.cursor()
    fmt = (request.args.get('format') or 'json').lower()
    try:
        if request.method == 'GET':
            cur.execute("SELECT * FROM departments WHERE id=%s", (d_id,))
            row = fetch_one_as_dict(cur)
            if not row:
                return jsonify({'msg':'not found'}), 404
            return to_format(row, fmt)

        if request.method == 'PUT':
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'msg': 'missing or invalid token', 'err': str(e)}), 401
            data = request.json or {}
            if not data.get('name'):
                return jsonify({'msg':'name required'}), 400
            try:
                cur.execute("UPDATE departments SET name=%s, description=%s WHERE id=%s", (data.get('name'), data.get('description'), d_id))
                mysql.connection.commit()
                return jsonify({'msg':'updated'}), 200
            except Exception as e:
                return jsonify({'msg':'db error', 'err': str(e)}), 400

        if request.method == 'DELETE':
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'msg': 'missing or invalid token', 'err': str(e)}), 401
            try:
                cur.execute("DELETE FROM departments WHERE id=%s", (d_id,))
                mysql.connection.commit()
                return jsonify({'msg':'deleted'}), 200
            except Exception as e:
                return jsonify({'msg':'db error', 'err': str(e)}), 400
    finally:
        cur.close()

# --- Health ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'}), 200

# --- App runner ---
if __name__ == '__main__':
    # optionally allow host/port via env vars in the future
    app.run(debug=True)
