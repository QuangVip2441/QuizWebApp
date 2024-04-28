from flask import Flask, render_template, url_for,  request, redirect, session
import pyrebase
import firebase_admin 
from firebase_admin import credentials, firestore, auth
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

# Firestore
cred = credentials.Certificate("service-account-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


# Tạo số thứ tự trang user
@app.route('/user')
def indexUser():
    collection_name = 'user'
    docs = db.collection(collection_name).stream()  # Add parentheses to call the stream() method

    data = []
    for i, doc in enumerate(docs, start=1):
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id  # Add the document ID to the data dictionary
        data.append({'row_number': i, **doc_data})

    return render_template('user.html', data=data)

# gọi trang thêm người dùng
@app.route('/register')
def register():
    return render_template('insertUser.html')

#xử lý thêm người dùng
@app.route('/registered', methods=['POST'])
def insertUser():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    mssv = request.form['mssv']
    phone = request.form['phone']

  
    if CheckexistsEmailandMSSV(email, mssv) != True:
        return render_template('notify.html', message='Email hoặc mã số sinh viên đã tồn tại')
    else:
         
            user = auth.create_user_with_email_and_password(email, password)
            user_id = user.get("localId")

            user_data = {
                'username': username,
                'email': email,
                'mssv': mssv,
                'phone': phone
            }
            # Save user data to Firestore
            db.collection('user').document(user_id).set(user_data)
            # Redirect to indexUser or any other route after successful insertion
            return redirect(url_for('indexUser'))


            

            
            
       



# thông báo sự tồn tại của email và mssv
@app.route('/notify')
def notifyexistsEmailandMSSV():
    return render_template('notify.html', message='Email hoặc mã số sinh viên đã tồn tại')

# kiếm tra sự tồn tại của email và mssv
def CheckexistsEmailandMSSV(email,mssv):
    mssv_query = db.collection('user').where('mssv', '==', mssv)
    mssv_docs = mssv_query.stream()

    # Check if email is already registered
    email_query = db.collection('user').where('email', '==', email)
    email_docs = email_query.stream()
    if len(list(email_docs)) > 0:
        return False
    elif len(list(mssv_docs)) > 0:
        return False
    return True

# xử lý login
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
           return render_template('notify.html', message='Sai thông tin đăng nhập')
    return render_template('login.html')
       
#Xử lý logout
@app.route('/logout')
def logout():
    return render_template('login.html')


# gọi trang chủ
@app.route('/home')
def Home():
    return "Home page"


# gọi trang sửa người dùng và xử lý sửa người dùng
@app.route("/user/<id>/edit" , methods=['GET', 'POST'])
def user_edit(id):
    if request.method == 'GET':
        user_ref = db.collection("user").document(id)
        user_data = user_ref.get().to_dict()

        user = auth.get_user(id)
        password_hash = user.tokens_valid_after_timestamp
        

        if user_data:
            user_data['password_hash'] = password_hash
            return render_template("editUser.html", user = user_data)
        else:
            return render_template('notify.html', message='Tài khoản không tồn tại')
    elif request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        mssv = request.form["mssv"]
        phone = request.form["phone"]

        # Validate form data
        if not username or not email or not password or not mssv or not phone:
           return render_template('notify.html', message='Nội dung chưa đủ')

        # Update user data in Firestore
        try:
            user = auth.get_user_by_email(id)
            user.update_email(email)
            user.update_password(password)
            print("User updated successfully!")
        except Exception as e:
            print("Error updating user:", e)

        user_data = {
            'username': username,
            'email': email,
            'mssv': mssv,
            'phone': phone
        }

        db.collection('user').document(id).set(user_data)
        return indexUser()


    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    mssv = request.form["mssv"]
    phone = request.form["phone"]

    # Validate form data
    if not username or not email or not password or not mssv or not phone:
        return "Invalid form data", 400

    # Update user data in Firestore
    user_ref = db.collection("users").document(email)
    user_data = {
        "email": email,
        "password": password,
        "mssv": mssv,
        "phone": phone
    }
    user_ref.set(user_data)

    return redirect(url_for("user", username=email))

# HÀM NÀY XỬ LÝ BẮT BUỘC PHẢI LOGIN ,NẾU KHÔNG SẼ KHÔNG VÀO ĐƯỢC HỆ THỐNG
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             Flask('Login required.')
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# Secure Page Route (Example)
# @app.route('/secure_page')
# def secure_page():
#     if 'user_id' in session:
#         # This route is accessible only for logged-in users
#         return render_template('navbar.html')
#     else:
#         flash('Login required.')
#         return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)



