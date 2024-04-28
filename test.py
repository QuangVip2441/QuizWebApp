from flask import Flask, render_template, url_for,  request, redirect, session
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from jinja2 import Environment, FileSystemLoader
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Qh2410.2'

firebaseConfig = {
        'apiKey': "AIzaSyCH5xDaEk35SaFAZn7GO7x0tX2OE4DNySA",
        'authDomain': "quizapp-e4741.firebaseapp.com",
        'databaseURL': "https://quizapp-e4741-default-rtdb.firebaseio.com",
        'projectId': "quizapp-e4741",
        'storageBucket': "quizapp-e4741.appspot.com",
        'messagingSenderId': "119471279793",
        'appId': "1:119471279793:web:917393a11faa680aff5c90"
    }

# Firebase auth
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()



def insertUser(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        print("User created successfully!")
        print("User object:", user)
        user_id = user.localId
        print("User ID:", user_id)
    except Exception as e:
        print("Error creating user:", e)


insertUser("tan123@gmail.com", "Tan123")