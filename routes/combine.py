from main import app
from flask import request
import psycopg2
import json
from core.conn import POSTGRESQL_URI
from module.token_verify import verify_token


@app.route('/agent/gen_new_pub_id', methods=['POST'])
def gen_new_pub_id():
    # Token Verification
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 2 stands for Agent , 3 for Admin
    if token[0][4] < 2 or token[0][4] > 3:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    form_data = request.get_json()
    try:
        public_id = form_data['public_id']
    except:
        return json.dumps({"status": "field_empty"}), 200, {'Access-Control-Allow-Origin': '*',
                                                            'Content-Type': 'application/json'}
    # Generating new Public id
    new_public_id = str(uuid.uuid1())
    connection = psycopg2.connect(POSTGRESQL_URI)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE register SET public_id=%s WHERE public_id=%s", [new_public_id, public_id])
    connection.close()
    return json.dumps({"status": "success"}), 200, {'Access-Control-Allow-Origin': '*',
                                                    'Content-Type': 'application/json'}


@app.route('/agent/listuser', methods=['GET'])
def listuser():
    # Token Verification
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 2 stands for Agent, 3 stands for Admin
    if token[0][4] < 2 or token[0][4] > 3:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    # Fetching Data with users role
    connection = psycopg2.connect(POSTGRESQL_URI)
    # Fetching Users
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT public_id, name, email, mob_number, state, city FROM register WHERE userrole = 1")
            result = cursor.fetchall()
    connection.close()
    finalresult = []
    # Prettifying Result
    for temp in result:
        token = {
            'public_id': temp[0],
            'name': temp[1],
            'email': temp[2],
            'mob_number': temp[3],
            'state': temp[4],
            'city': temp[5]
        }
        finalresult.append(token)
    return json.dumps(finalresult), 200, {'Access-Control-Allow-Origin': '*',
                                          'Content-Type': 'application/json'}


@app.route('/customer/viewloan', methods=['GET'])
def cus_viewloan():
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 1 stands for Customer
    if token[0][4] != 1:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    # Filters
    # 0 stands for ASC 1 for Des
    sortin = request.args.get("sortin")
    loan_state = request.args.get("loan_state")
    if sortin is None:
        sortin = 1
    else:
        sortin = int(sortin)
    # Loan state 1 for created 2. Rejected 3. Approve 4. Any
    if loan_state is None:
        loan_state = 4
    else:
        loan_state = int(loan_state)
    connection = psycopg2.connect(POSTGRESQL_URI)
    # Filter in Action
    with connection:
        with connection.cursor() as cursor:
            if loan_state == 4:
                if sortin == 1:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request FROM loan_request WHERE ofuser=%s ORDER BY loan_id DESC",
                        [token[0][1]])
                else:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request FROM loan_request WHERE ofuser=%s",
                        [token[0][1]])
            else:
                if sortin == 1:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request FROM loan_request WHERE ofuser=%s AND loan_state=%s  ORDER BY loan_id DESC",
                        [token[0][1], loan_state])
                else:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request FROM loan_request WHERE ofuser=%s AND loan_state=%s",
                        [token[0][1], loan_state])
            result = cursor.fetchall()
    connection.close()
    finalresult = []
    # Prettifying Result
    for temp in result:
        if temp[3] == 1:
            token = "Queue"
        elif temp[3] == 2:
            token = "Rejected"
        else:
            token = "Approved"
        temp = {
            'Amount': temp[0],
            'State': token,
            'Interest': str(temp[1]),
            'Tenture': temp[2],
            'date': str(temp[4])[:-7],
        }
        finalresult.append(temp)
    return json.dumps(finalresult), 200, {'Access-Control-Allow-Origin': '*',
                                          'Content-Type': 'application/json'}


@app.route('/agent/viewloan', methods=['GET'])
def agent_viewloan():
    token = None
    token = verify_token(token)
    if token is None:
        return json.dumps({"status": "Token Missing"}), 200, {'Access-Control-Allow-Origin': '*',
                                                              'Content-Type': 'application/json'}
    # Userrole 1 stands for Customer which cannot access all loans
    if token[0][4] == 1:
        return json.dumps({"status": "Restrict"}), 200, {'Access-Control-Allow-Origin': '*',
                                                         'Content-Type': 'application/json'}
    # Filters
    # 0 stands for ASC 1 for Des
    sortin = request.args.get("sortin")
    loan_state = request.args.get("loan_state")
    if sortin is None:
        sortin = 1
    else:
        sortin = int(sortin)
    # Loan state 1 for created 2. Rejected 3. Approve 4. Any
    if loan_state is None:
        loan_state = 4
    else:
        loan_state = int(loan_state)
    connection = psycopg2.connect(POSTGRESQL_URI)
    # Filter in Action
    with connection:
        with connection.cursor() as cursor:
            if loan_state == 4:
                if sortin == 1:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request, ofuser FROM loan_request ORDER BY loan_id DESC")
                else:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request, ofuser FROM loan_request")
            else:
                if sortin == 1:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request, ofuser FROM loan_request WHERE loan_state=%s  ORDER BY loan_id DESC",
                        [loan_state])
                else:
                    cursor.execute(
                        "SELECT loan_quantity, loan_interest, tenture, loan_state, date_request, ofuser FROM loan_request WHERE loan_state=%s",
                        [loan_state])
            result = cursor.fetchall()
    connection.close()
    finalresult = []
    # Prettifying Result
    for temp in result:
        if temp[3] == 1:
            token = "Queue"
        elif temp[3] == 2:
            token = "Rejected"
        else:
            token = "Approved"
        temp = {
            'Amount': temp[0],
            'State': token,
            'Interest': str(temp[1]),
            'Tenture': temp[2],
            'date': str(temp[4])[:-7],
            'Customer': temp[5]
        }
        finalresult.append(temp)
    return json.dumps(finalresult), 200, {'Access-Control-Allow-Origin': '*',
                                          'Content-Type': 'application/json'}
