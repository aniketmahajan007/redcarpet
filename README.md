# RedCarpet 

# Minimal loan management system - API

Code: https://github.com/aniketmahajan007/redcarpet

Hosted : https://redcarpetloan.herokuapp.com/ 

You can also use Docker image to run on local machine

# Stack:
Python , Flask, PostgreSQL

===================================================

Why backend in Python?

There were multiple options for backend like PHP, NodeJS, Python but since your company is already using python for development that's the reason i choose.

# Database Structure

1. It contains three tables  which is used for storing data.
 - Register

    It stores information of all types of users (Customer, Agent, Admin) a userrole column defined what type of users is accessing services.

    
    User Roles
    1 stands for Customer
    2 stands for Agent
    3 stands for Admin
 - Loans
    
    It stores all loans data and its states and which customer initiated the request and which agent is fulfilling the request etc
   
- Loan log

    It stores all logs of loans whenever a change is occurred in loans like state changes etc is stored here to easily rollback if any disaster occurred

# API Endpoints

- /register

        Required POST Data:
        name
        email
        password
        cpassword
        mob_number
        state
        city

    Which can access by everyone used to registered customers and its details.
  
    (All data which is sent first get validated like email is valid, password is strong, email is already in use etc. after validating password get hashed using bcrypt technique and public_id is also generated which is unique)

  
- /login
        
        Rquired POST Data:
        email
        password
 
    
Which can access by everyone used to login and access services after registering.

(All data which is sent first get validated after that JWT token is provided which can be used to access restricted data)

  
- /agent/gen_loan
    
    This endpoint can only access by user role - 2 which means agent and is used to generate loan
  
  (Token is decrypted to check user is agent or not after that validation takes place after that loan is added in loan request table and loan_logs table with current state NEW)

            Loan States
            1 stands for NEW
            2 stands for REJECTED
            3 stands for APPROVE
    
- /agent/edit_loan

    
        Required POST data: 
        loan_quantity
        loan_interest
        tenture
        ofuser
        
        Required Header:
        App-token
    

This endpoint can only access by user role - 2 which means agent and is used to edit loan

(Token is decrypted to check user is agent or not after that validation takes place and if loan is not in APPROVE state its gets updated and entry in logs_loan table is filled)
  

- /agent/gen_new_pub_id


        Required POST data: 
        public_id
        
        Required Header:
        App-token
    
This endpoint can only access by user role - 2,3 which means agent and admin

(Token is decrypted to check user is agent, admin or not after that validation takes place and customer public_id is updated)
  

-  /agent/listuser

        Required headers data:
        App-token

   

This endpoint can only access by user role - 2,3 which means agent and admin and use to show all users

(Token is decrypted to check user is agent, admin or not after that all the users is fetch from database and return in JSON format)
   

-   /customer/viewloan

        Required GET data:
        sortin ( 0 for ASC date, 1 for DES date )
        loan_state ( 1 - New, 2- Rejected, 3- Approve, 4- Any )
        
        Required Header:
        App-token

This endpoint can only access by user role - 1 which means customer and used to show all loans of that customer

(Token is decrypted to check user is customer, or not after that all the loans of customer is fetch based on filters like sortin, loan_state from database and return in JSON format)
    

-   /agent/viewloan

        Required GET data:
        sortin ( 0 for ASC date, 1 for DES date )
        loan_state ( 1 - New, 2- Rejected, 3- Approve, 4- Any )
        
        Required Header:
        App-token
    
This endpoint can only access by user role - 2,3 which means agent,admin and used to show all loans 

(Token is decrypted to check user is agent, admin, or not after that all the loans is fetch from database and return in JSON format)

-   /admin/loan_approve

        Required POST data:
        loan_id
        loan_state
        
        Required Header:
        App-token

This endpoint can only access by user role - 3 which means admin and used to approve or reject loans 

(Token is decrypted to check user is admin, or not after that loan is validated if its valid then loan current state get changed and entry in loan_log table gets added)

- /admin/loan_logs

        Required Header:
        App-token

This endpoint can only access by user role - 3 which means admin and used to access all loan logs

(Token is decrypted to check user is admin, or not after that all logs gets fetched from database.)

- /agent/edit_roles

        Required POST data:
        user_role
        public_id

        Required Header:
        App-token

This endpoint can only access by user role - 3 which means admin and used to change role of users

(Token is decrypted to check user is admin, or not after that user role state get changed and updated in database.)


Note: App-Token is given after successfully login
      
If App-token is not added on required endpoints , Token missing response will be sent.