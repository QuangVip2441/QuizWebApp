from flask import Flask, render_template, url_for
import pyrebase
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


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


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Qh2410.2'


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min = 4, max=20)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min = 4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    return "<p> logout </p>"

@app.route('/home')
def Home():
    return "Home page"