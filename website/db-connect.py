import pyrebase


firebaseConfig = {
        'apiKey': "AIzaSyCH5xDaEk35SaFAZn7GO7x0tX2OE4DNySA",
        'authDomain': "quizapp-e4741.firebaseapp.com",
        'databaseURL': "https://quizapp-e4741-default-rtdb.firebaseio.com",
        'projectId': "quizapp-e4741",
        'storageBucket': "quizapp-e4741.appspot.com",
        'messagingSenderId': "119471279793",
        'appId': "1:119471279793:web:917393a11faa680aff5c90"
    }
    
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def login():
    print("Login....")
    email = input("Enter Email: ")
    password = input("Enter password: ")
    try:
        login = auth.sign_in_with_email_and_password(email,password)
        print("successfully logged in!")
    except:
        print("Invalid email and password")
    return 
    

def signup():
    print("Sign up...")
    email = input("Enter Email: ")
    password = input("Enter password: ")
    try:
        user = auth.create_user_with_email_and_password(email,password)
    except:
        print("Email already exists")
    return
    

ans = input("Are you a new user?[y/n]")

if ans == 'n':
    login()
elif ans == 'y':
    signup()
   