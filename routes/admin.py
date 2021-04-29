import datetime

from main import app
from flask import request
import psycopg2
import json
from core.conn import POSTGRESQL_URI
from module.token_verify import verify_token


@app.route('/admin/loan_approve', methods=['POST'])
def loan_approve():
    # Only Admin Role Can access This
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 3 stands for Admin
    if token[0][4] != 3:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    form_data = request.get_json()
    # Checking required fields
    try:
        loan_id = int(form_data['loan_id'])
        loan_state = int(form_data['loan_state'])
    except:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    if loan_id < 1 or loan_state < 1 or loan_state > 3:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    connection = psycopg2.connect(POSTGRESQL_URI)
    # Checking Loan exist if exist fetching details
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT loan_quantity, loan_interest, tenture FROM loan_request WHERE loan_id=%s LIMIT 1",
                [loan_id])
            result = cursor.fetchall()
    if len(result) < 1:
        connection.close()
        return json.dumps({"status": "invalid_loan"}), 200, {'Access-Control-Allow-Origin': '*',
                                                             'Content-Type': 'application/json'}
    # Updating loan status
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE loan_request SET loan_state=%s WHERE loan_id=%s",
                [loan_state, loan_id])
    datelog = datetime.datetime.now()
    if loan_state == 2:
        operation_done = "rejected"
    else:
        operation_done = "approve"
    # inserting this change in loan log table
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO loan_logs (loan_id, cur_state, changeby, log_date, operation_done, loan_interest, loan_quantity, tenture) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [loan_id, loan_state, token[0][1], datelog, operation_done, result[0][1], result[0][0], result[0][2]])
    connection.close()
    return json.dumps({"status": "success"}), 200, {'Access-Control-Allow-Origin': '*',
                                                    'Content-Type': 'application/json'}


@app.route('/admin/loan_logs', methods=['GET'])
def loan_logs():
    # Only Admin Role Can access This
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 3 stands for Admin
    if token[0][4] != 3:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    connection = psycopg2.connect(POSTGRESQL_URI)
    #Fetching All logs
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT loan_id, cur_state, changeby, log_date, operation_done, loan_interest, loan_quantity, tenture FROM loan_logs")
            result = cursor.fetchall()
    connection.close()
    finalresult = []
    # Prettifying Result
    for temp in result:
        temp = {
            'loan_id': temp[0],
            'cur_state': temp[1],
            'Agent': temp[2],
            'date': temp[3],
            'Operation': temp[4],
            'Interest': temp[5],
            'Amount': temp[6],
            'Tenture': temp[7]
        }
        finalresult.append(temp)
    return json.dumps(finalresult), 200, {'Access-Control-Allow-Origin': '*',
                                          'Content-Type': 'application/json'}


@app.route('/agent/edit_roles', methods=['POST'])
def edit_roles():
    # Token Verification
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 3 stands for Admin
    if token[0][4] != 3:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    form_data = request.get_json()
    # Fetching and validaing new role
    try:
        user_role = form_data['user_role']
        public_id = form_data['public_id']
    except:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    if user_role < 1 or user_role > 3:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    connection = psycopg2.connect(POSTGRESQL_URI)
    # Updating new roles to database
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE register SET userrole=%s WHERE public_id=%s", [user_role, public_id])
    connection.close()
    return json.dumps({"status": "success"}), 200, {'Access-Control-Allow-Origin': '*',
                                                    'Content-Type': 'application/json'}
