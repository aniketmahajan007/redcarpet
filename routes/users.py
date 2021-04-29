from core.conn import POSTGRESQL_URI, SECRET
import datetime
import re
from main import app
from flask import request
import psycopg2
import json
import bcrypt
from module.email_regix import email_regix
import uuid
import jwt


def validate_reg(name, email, password, cpassword, mob_number, state, city):
    if name is None or email is None or password is None or cpassword is None or state is None or city is None:
        return False
    elif len(mob_number) != 10:
        return False
    if len(name) < 3 or len(email) < 10:
        return False
    return True


def validate_login(email, password):
    if email is None:
        return False
    elif password is None:
        return False
    elif len(email) < 10:
        return False
    return True


@app.route('/register', methods=['POST'])
def register():
    form_data = request.get_json()
    try:
        name = form_data['name']
        email = form_data["email"]
        password = form_data["password"]
        cpassword = form_data["cpassword"]
        mob_number = form_data["mob_number"]
        state = form_data["state"]
        city = form_data["city"]
    except:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    # Validation
    if not validate_reg(name, email, password, cpassword, mob_number, state, city):
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    if len(password) < 8:
        return json.dumps({"status": "pass_weak"}), 200, {'Access-Control-Allow-Origin': '*',
                                                          'Content-Type': 'application/json'}
    if password != cpassword:
        return json.dumps({"status": "pass_fail"}), 200, {'Access-Control-Allow-Origin': '*',
                                                          'Content-Type': 'application/json'}
    if not re.search(email_regix, email):
        return json.dumps({"status": "email_fail"}), 200, {'Access-Control-Allow-Origin': '*',
                                                           'Content-Type': 'application/json'}
    mob_number = int(mob_number)
    # Validation Complete
    # Email Validation currently weak since its always better to send confirmation mail to confirm mail
    # Inserting into database using prepared statement to prevent SQL injection
    connection = psycopg2.connect(POSTGRESQL_URI)
    # To prevent duplicate email
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM register WHERE email=%s LIMIT 1", [email])
            result = cursor.fetchall()
    if len(result) > 0:
        return json.dumps({"status": "already_register"}), 200, {'Access-Control-Allow-Origin': '*',
                                                                 'Content-Type': 'application/json'}
    datecreated = datetime.datetime.now()
    # Encrypting Password
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password = password.decode('utf-8')
    # public id
    public_id = str(uuid.uuid1())
    # Default 1 for customer
    userrole = 1
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO register (name, email, password, datecreated, userrole, public_id, mob_number, state, city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (name, email, password, datecreated, userrole, public_id, mob_number, state, city))
    connection.close()
    return json.dumps({"status": "success"}), 200, {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'}


@app.route('/login', methods=['POST'])
def login():
    form_data = request.get_json()
    try:
        email = form_data["email"]
        password = form_data["password"]
    except:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    # Validation
    if not validate_login(email, password):
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    if len(password) < 8:
        return json.dumps({"status": "pass_weak"}), 200, {'Access-Control-Allow-Origin': '*',
                                                          'Content-Type': 'application/json'}

    if not re.search(email_regix, email):
        return json.dumps({"status": "email_fail"}), 200, {'Access-Control-Allow-Origin': '*',
                                                           'Content-Type': 'application/json'}
    # Validation Complete
    # Email Validation currently weak since its always better to send confirmation mail to confirm mail
    # Inserting into database using prepared statement to prevent SQL injection
    connection = psycopg2.connect(POSTGRESQL_URI)
    # To prevent duplicate email
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name, userrole, public_id, password FROM register WHERE email=%s LIMIT 1", [email])
            result = cursor.fetchall()
    connection.close()
    if len(result) < 1:
        return json.dumps({"status": "invalid"}), 200, {'Access-Control-Allow-Origin': '*',
                                                        'Content-Type': 'application/json'}

    if not bcrypt.checkpw(password.encode('utf-8'), result[0][3].encode('utf-8')):
        return json.dumps({"status": "invalid"}), 200, {'Access-Control-Allow-Origin': '*',
                                                        'Content-Type': 'application/json'}
    token_gen = jwt.encode(
        {'public_id': result[0][2], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=(60 * 3))}, SECRET)
    if result[0][1] == 1:
        user_role = "Customer"
    elif result[0][1] == 2:
        user_role = "Agent"
    else:
        user_role = "Admin"
    return json.dumps({"status": "success", "token": token_gen, "name": result[0][0], "Role": user_role}), 200, {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'}


@app.errorhandler(404)
def page_not_found(e):
    return "Bad Request", 200
