from flask import Flask, render_template, url_for,  request, redirect, session
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from jinja2 import Environment, FileSystemLoader


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

# Firestore
cred = credentials.Certificate("service-account-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()



@app.route('/user')
def indexUser():
    collection_name = 'user'
    docs = db.collection(collection_name).stream()  # Add parentheses to call the stream() method

    data = []
    for i, doc in enumerate(docs, start=1):
        data.append({'row_number': i, **doc.to_dict()})

    return render_template('user.html', data=data)



@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            login = auth.sign_in_with_email_and_password(email,password)
            session['logged_in'] = True
            session['email'] = email                
            # return redirect(url_for('index'))
            return render_template('index.html')
        except:
            return 'Sai thông tin đăng nhập'
    return render_template('login.html')
       

@app.route('/logout')
def logout():
    return "<p> logout </p>"

@app.route('/home')
def Home():
    return "Home page"




if __name__ == '__main__':
    app.run(debug=True)



