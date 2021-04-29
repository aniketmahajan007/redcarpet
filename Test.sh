## Bad Request
## Since required field not passed
curl "https://redcarpetloan.herokuapp.com/register"

## Required Fields past
## Password should be min 8 length
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"name":"Test","password":"testing","email":"tester@gmail.com", "cpassword":"testing","mob_number":"1234567890","state":"Delhi","city":"Delhi"}' \
  "https://redcarpetloan.herokuapp.com/register"


curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"name":"Test","password":"testing12345","email":"tester@gmail.com", "cpassword":"testing12345","mob_number":"1234567890","state":"Delhi","city":"Delhi"}' \
  "https://redcarpetloan.herokuapp.com/register"


# if email and password is correct token will be provided to access restricted data
# Since email and password is not correct it will return invalid
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"email":"tester@gmail.com", "password":"testing12345"}' \
  "https://redcarpetloan.herokuapp.com/login"


# Since email and password is correct token will provided
# Email and password has been taken from dummy data mention in README
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"email": "mohit@gmail.com", "password": "mohit12345"}' \
  "https://redcarpetloan.herokuapp.com/login"

# Will return restrict if user role is not agent since agent can create loan
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request POST \
  --data '{"loan_quantity":"100000","loan_interest":"5.2","tenture":"6","ofuser":"bbe80ac1-a801-11eb-aab1-002b67f87a8f"]}' \
  "https://redcarpetloan.herokuapp.com/agent/gen_loan"

# Will return restrict if user role is not agent since agent can edit loan
# Edit loan will fail if it is already approve by admin since approve loan cannot be edited
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request POST \
  --data '{"loan_quantity":"100000","loan_interest":"5.2","tenture":"6","ofuser":"bbe80ac1-a801-11eb-aab1-002b67f87a8f"]}' \
  "https://redcarpetloan.herokuapp.com/agent/edit_loan"

# Will return restrict if user role is not agent or admin
# Since only agent and admin can see all users
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request GET \
  "https://redcarpetloan.herokuapp.com/agent/listuser"

# Will return restrict if user role is not customer
# will return loans based on filtering
# Sortin 1 means DESC date 0 means ASC date
# loan_state - 1 means NEW ,2 means Rejected, 3 means Approve, 4 mean ANY
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request GET \
  "https://redcarpetloan.herokuapp.com/customer/viewloan?sortin=1&loan_state=4"

curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request GET \
  "https://redcarpetloan.herokuapp.com/customer/viewloan?sortin=1&loan_state=2"


# Will return restrict if user role is customer
# will return all loans based on filtering
# Sortin 1 means DESC date 0 means ASC date
# loan_state - 1 means NEW ,2 means Rejected, 3 means Approve, 4 mean ANY
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request GET \
  "https://redcarpetloan.herokuapp.com/agent/viewloan?sortin=1&loan_state=4"

curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request GET \
  "https://redcarpetloan.herokuapp.com/agent/viewloan?sortin=1&loan_state=2"

# Will return restrict if user role is not admin
# Since only admin can reject and approve loan
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request POST \
  --data '{"loan_id":"4","loan_state":"3"]}' \
  "https://redcarpetloan.herokuapp.com/admin/loan_approve"

# Will return restrict if user role is not admin
# Since only admin view all loan logs
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request GET \
  "https://redcarpetloan.herokuapp.com/admin/Loan_logs"

# Will return restrict if user role is not admin
# Since only admin view all edit roles of users
curl --header "Content-Type: application/json" --header "App-Token: --ADD--TOKEN--HERE" \
  --request POST \
  --data '{"user_role":"1","public_id":"bbe80ac1-a801-11eb-aab1-002b67f87a8f"]}' \
  "https://redcarpetloan.herokuapp.com/admin/edit_roles"