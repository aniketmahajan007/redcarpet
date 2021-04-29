import datetime
import uuid

from main import app
from flask import request
import psycopg2
import json
from core.conn import POSTGRESQL_URI
from module.token_verify import verify_token


def validate_loanreq(loan_quantity, loan_interest, tenture):
    if loan_quantity < 100 or loan_interest < 0 or loan_interest > 80 or tenture < 1:
        return False
    return True


def validate_edit_loanreq(loan_quantity, loan_interest, tenture, loan_id):
    if loan_quantity < 100 or loan_interest < 0 or loan_interest > 80 or tenture < 1 or loan_id < 1:
        return False
    return True


@app.route('/agent/gen_loan', methods=['POST'])
def gen_loan():
    # Only Agent Role Can access This
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 2 stands for Agent
    if token[0][4] != 2:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    form_data = request.get_json()
    try:
        loan_quantity = int(form_data['loan_quantity'])
        loan_interest = float(form_data['loan_interest'])
        tenture = int(form_data['tenture'])
        ofuser = form_data['ofuser']
    except:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    if not validate_loanreq(loan_quantity, loan_interest, tenture):
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    connection = psycopg2.connect(POSTGRESQL_URI)
    # Validating User
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM register WHERE public_id=%s LIMIT 1",
                [ofuser])
            result = cursor.fetchall()
    if len(result) < 1:
        return json.dumps({"status": "invalid_user"}), 200, {'Access-Control-Allow-Origin': '*',
                                                             'Content-Type': 'application/json'}
    datelog = datetime.datetime.now()
    # 1 Means new  2 Means Rejected 3 Means Approve
    loan_state = 1
    # Raising loan request
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO loan_request (loan_quantity, loan_interest, tenture, loan_state, byagent, ofuser, date_request) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING loan_id;",
                [loan_quantity, loan_interest, tenture, loan_state, token[0][1], ofuser, datelog])
            result_id = cursor.fetchone()[0]
    operation_done = "created"
    # Adding loan request to loan logs
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO loan_logs (loan_id, cur_state, changeby, log_date, operation_done, loan_interest, loan_quantity, tenture) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [result_id, loan_state, token[0][1], datelog, operation_done, loan_interest, loan_quantity, tenture])
    connection.close()
    return json.dumps({"status": "success"}), 200, {'Access-Control-Allow-Origin': '*',
                                                    'Content-Type': 'application/json'}


@app.route('/agent/edit_loan', methods=['POST'])
def edit_loan():
    # Only Agent Role Can access This
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 2 stands for Agent
    if token[0][4] != 2:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    form_data = request.get_json()
    try:
        loan_quantity = int(form_data['loan_quantity'])
        loan_interest = float(form_data['loan_interest'])
        tenture = int(form_data['tenture'])
        loan_id = int(form_data['loan_id'])
    except:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    if not validate_edit_loanreq(loan_quantity, loan_interest, tenture, loan_id):
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    connection = psycopg2.connect(POSTGRESQL_URI)
    # Checking Loan Exisr
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT loan_state FROM loan_request WHERE loan_id=%s AND byagent=%s LIMIT 1",
                [loan_id, token[0][1]])
            result = cursor.fetchall()
    if len(result) < 1:
        connection.close()
        return json.dumps({"status": "invalid_loan"}), 200, {'Access-Control-Allow-Origin': '*',
                                                             'Content-Type': 'application/json'}
    # Approve loan cannot be edited | 1. New , 2. Rejected, 3. Approved
    if result[0][0] == 3:
        connection.close()
        return json.dumps({"status": "approved"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE loan_request SET loan_quantity = %s, loan_interest = %s, tenture = %s WHERE loan_id = %s AND byagent = %s",
                [loan_quantity, loan_interest, tenture, loan_id, token[0][1]])

    # Updated Dates for Logs
    datelog = datetime.datetime.now()
    operation_done = "agentupdate"
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO loan_logs (loan_id, cur_state, changeby, log_date, operation_done, loan_interest, loan_quantity, tenture) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [loan_id, result[0][0], token[0][1], datelog, operation_done, loan_interest, loan_quantity, tenture])
    connection.close()
    return json.dumps({"status": "success"}), 200, {'Access-Control-Allow-Origin': '*',
                                                    'Content-Type': 'application/json'}
