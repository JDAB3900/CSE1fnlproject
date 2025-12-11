# db.py
from flask import current_app
import MySQLdb
import MySQLdb.cursors

def get_db_connection():
    cfg = current_app.config
    conn = MySQLdb.connect(
        host=cfg['localhost'],
        user=cfg['root'],
        passwd=cfg['12345678joel'],
        db=cfg['init_db'],
        cursorclass=MySQLdb.cursors.DictCursor,
        autocommit=True
    )
    return conn
