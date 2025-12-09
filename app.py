from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import dicttoxml
from xml.dom.minidom import parseString
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678joel'
app.config['MYSQL_DB'] = 'init_db'
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=2)

mysql = MySQL(app)
jwt = JWTManager(app)

def to_format(data, fmt='json'):
    if fmt == 'xml':
        xml = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
        pretty = parseString(xml).toprettyxml()
        resp = make_response(pretty)
        resp.headers['Content-Type'] = 'application/xml'
        return resp
    else:
        return jsonify(data)

@app.route('/auth/register', methods=['POST'])
def register():
    body = request.json or {}
    username = body.get('username')
    password = body.get('password')
    role = body.get('role', 'user')
    if not username or not password:
        return jsonify({'msg':'username & password required'}), 400
    cur = mysql.connection.cursor()
    hashed = generate_password_hash(password)
    try:
        cur.execute("INSERT INTO users (username,password,role) VALUES (%s,%s,%s)", (username, hashed, role))
        mysql.connection.commit()
    except Exception as e:
        return jsonify({'msg':'user exists or db error', 'err': str(e)}), 400
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
        return jsonify({'msg':'invalid credentials'}), 401
    user_id, uname, pw_hash, role = row
    if not check_password_hash(pw_hash, password):
        return jsonify({'msg':'invalid credentials'}), 401
    access = create_access_token(identity={'id': user_id, 'username': uname, 'role': role})
    return jsonify({'access_token': access}), 200

@app.route('/employees', methods=['GET','POST'])
def employees_collection():
    fmt = (request.args.get('format') or 'json').lower()
    if request.method == 'GET':
        q = request.args.get('q')
        cur = mysql.connection.cursor()
        if q:
            like = f"%{q}%"
            cur.execute("SELECT e.*, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id=d.id WHERE first_name LIKE %s OR last_name LIKE %s OR birth_city LIKE %s", (like, like, like))
        else:
            cur.execute("SELECT e.*, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id=d.id")
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        return to_format({'employees': rows}, fmt)

    @jwt_required()
    def create_employee():
        data = request.json or {}
        required = ['first_name','last_name']
        for f in required:
            if not data.get(f):
                return jsonify({'msg': f'{f} required'}), 400
        cur = mysql.connection.cursor()
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
    return create_employee()

@app.route('/employees/<int:emp_id>', methods=['GET','PUT','DELETE'])
def employee_item(emp_id):
    fmt = (request.args.get('format') or 'json').lower()
    cur = mysql.connection.cursor()
    if request.method == 'GET':
        cur.execute("SELECT e.*, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id=d.id WHERE e.id=%s", (emp_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({'msg':'not found'}), 404
        cols = [d[0] for d in cur.description]
        return to_format(dict(zip(cols,row)), fmt)

    if request.method == 'PUT':
        @jwt_required()
        def update():
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
            cur.execute(sql, tuple(vals))
            mysql.connection.commit()
            return jsonify({'msg':'updated'}), 200
        return update()

    if request.method == 'DELETE':
        @jwt_required()
        def delete():
            cur.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
            mysql.connection.commit()
            return jsonify({'msg':'deleted'}), 200
        return delete()

@app.route('/departments', methods=['GET','POST'])
def departments_collection():
    fmt = (request.args.get('format') or 'json').lower()
    cur = mysql.connection.cursor()
    if request.method == 'GET':
        cur.execute("SELECT * FROM departments")
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        return to_format({'departments': rows}, fmt)

    @jwt_required()
    def create_dept():
        data = request.json or {}
        if not data.get('name'):
            return jsonify({'msg':'name required'}), 400
        try:
            cur.execute("INSERT INTO departments (name,description) VALUES (%s,%s)", (data.get('name'), data.get('description')))
            mysql.connection.commit()
        except Exception as e:
            return jsonify({'msg':'db error', 'err': str(e)}), 400
        return jsonify({'msg':'created'}), 201
    return create_dept()

@app.route('/departments/<int:d_id>', methods=['GET','PUT','DELETE'])
def department_item(d_id):
    cur = mysql.connection.cursor()
    fmt = (request.args.get('format') or 'json').lower()
    if request.method == 'GET':
        cur.execute("SELECT * FROM departments WHERE id=%s", (d_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({'msg':'not found'}), 404
        cols = [d[0] for d in cur.description]
        return to_format(dict(zip(cols,row)), fmt)

    @jwt_required()
    def update_dept():
        data = request.json or {}
        if not data.get('name'):
            return jsonify({'msg':'name required'}), 400
        cur.execute("UPDATE departments SET name=%s, description=%s WHERE id=%s", (data.get('name'), data.get('description'), d_id))
        mysql.connection.commit()
        return jsonify({'msg':'updated'}), 200

    @jwt_required()
    def delete_dept():
        cur.execute("DELETE FROM departments WHERE id=%s", (d_id,))
        mysql.connection.commit()
        return jsonify({'msg':'deleted'}), 200

    if request.method == 'PUT':
        return update_dept()
    else:
        return delete_dept()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)