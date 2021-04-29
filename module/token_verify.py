import psycopg2
import jwt
from flask import request

from core.conn import POSTGRESQL_URI, SECRET, ALGO


def verify_token(token):
    # checking App token in headers
    if 'App-Token' in request.headers:
        token = request.headers['App-Token']
    if not token or token is None:
        return None
    try:
        # Decoding token
        token_dec = jwt.decode(token, SECRET, ALGO)
    except:
        return None

    public_id = token_dec['public_id']
    # User Validating
    connection = psycopg2.connect(POSTGRESQL_URI)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT sno, public_id, name, email, userrole, mob_number, state, city FROM register WHERE public_id=%s LIMIT 1", [public_id])
            result = cursor.fetchall()
    connection.close()
    if len(result) < 1:
        return None
    return result
