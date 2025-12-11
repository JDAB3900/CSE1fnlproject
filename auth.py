# auth.py
from flask import Blueprint, request, current_app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def create_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        uid = cur.lastrowid
        cur.close(); conn.close()
        return uid
    except Exception as e:
        cur.close(); conn.close()
        raise

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg":"username and password required"}), 400
    try:
        create_user(username, password)
    except Exception as e:
        return jsonify({"msg":"user creation failed or username taken"}), 400
    return jsonify({"msg":"user created"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg":"username and password required"}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row or not check_password_hash(row['password_hash'], password):
        return jsonify({"msg":"bad username or password"}), 401
    access_token = create_access_token(identity=row['id'])
    return jsonify(access_token=access_token), 200
