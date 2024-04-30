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

# Firebase auth============================================================================================
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Firestore============================================================================================
cred = credentials.Certificate("service-account-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

#Trang danh sách module =================================================================================
@app.route('/module')
def indexModule():
    collection_name = 'module'
    docs = db.collection(collection_name).stream()

    data = []
    for i, doc in enumerate(docs, start=1):
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id  # Add the document ID to the data dictionary
        data.append({'row_number': i, **doc_data})

    return render_template('module.html', data=data)


# Tạo số thứ tự trang user============================================================================================
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


#Thêm câu hỏi trắc nghiệm=========================================================================
@app.route('/insertquestions/<moduleid>', methods=['GET'])
def insert_questions(moduleid):
    if request.method == 'GET':
        module_ref = db.collection("module").document(moduleid)
        module_data = module_ref.get().to_dict()

        
        if module_data:
            module_data['id'] = moduleid
            return render_template("insertquestions.html", module = module_data)
        else:
            return render_template('notify.html', message='Module không tồn tại')
        
# Xử lý thêm câu hỏi======================================================
@app.route('/insertquestions/<moduleid>', methods=['POST'])
def insert_questions_process(moduleid):
    pass
# gọi trang thêm người dùng============================================================================================
@app.route('/register')
def register(): 
    return render_template('insertUser.html')

#xử lý thêm người dùng============================================================================================
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

# thông báo sự tồn tại của email và mssv============================================================================================
@app.route('/notify')
def notifyexistsEmailandMSSV():
    return render_template('notify.html', message='Email hoặc mã số sinh viên đã tồn tại')

# kiếm tra sự tồn tại của email và mssv============================================================================================
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

# xử lý login============================================================================================
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
       
#Xử lý logout============================================================================================
@app.route('/logout')
def logout():
    return render_template('login.html')

# gọi trang chủ============================================================================================
@app.route('/home')
def Home():
    return "Home page"

# xử lý sửa user=====================================================================================
@app.route('/user/<id>', methods=['POST'])
def user_edit_process(id):
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
            user = firebase_admin.auth.get_user(id)
            firebase_admin.auth.update_user(
            uid=user.uid,
            email=email,
            password=password
    )
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

# Hàm xử lý xóa ============================================
@app.route('/delete/<id>', methods=['GET'])
def delete_user(id):
    return '''
        <script>
            if (confirm("Are you sure you want to delete user {0}?")) {{
                window.location.href = "/delete_confirm/{0}";
            }} else {{
                window.location.href = "/";
            }}
        </script>
    '''.format(id)

@app.route('/delete_confirm/<id>', methods=['GET'])
def delete_user_confirm(id):
    try:
        firebase_admin.auth.delete_user(id)
        db.collection('user').document(id).delete()
        return indexUser()
    except Exception as e:
        return 'Error deleting user: {}'.format(e)
# gọi trang sửa người dùng và xử lý sửa người dùng============================================================================================
@app.route('/user/<id>' , methods=['GET'])
def user_edit(id):
    if request.method == 'GET':
        user = firebase_admin.auth.get_user(id)
        password_hash = user.tokens_valid_after_timestamp
        

        user_ref = db.collection("user").document(id)
        user_data = user_ref.get().to_dict()
        
        if user_data:
            user_data['id'] = id
            user_data['password_hash'] = password_hash
            return render_template("editUser.html", user = user_data)
        else:
            return render_template('notify.html', message='Tài khoản không tồn tại')
# xử lý sửa module=====================================================================================
@app.route('/module/<id>', methods=['POST'])
def module_edit_process(id):
        name = request.form["name"]
        introduction = request.form["introduction"]
        numberQuestions = request.form["numberQuestions"]
        

        # Validate form data
        if not name or not introduction or not numberQuestions:
           return render_template('notify.html', message='Nội dung chưa đủ')

        # Update user data in Firestore

        module_data = {
            'name': name,
            'introduction': introduction,
            'numberQuestions': numberQuestions
        }

        db.collection('module').document(id).set(module_data)
        return indexModule()
# Gọi trang sửa Module và xử lý Module==================================================================
@app.route('/module/<id>' , methods=['GET'])
def module_edit(id):
    if request.method == 'GET':

        module_ref = db.collection("module").document(id)
        module_data = module_ref.get().to_dict()
        
        if module_data:
            module_data['id'] = id
            return render_template("editModule.html", module = module_data)
        else:
            return render_template('notify.html', message='Module không tồn tại')


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
# Gọi trang danh sách các câu hỏi=================================================================
@app.route('/questions/<id>', methods=['GET'])
def list_question(id):
    if request.method == 'GET':

        collection_name = 'module'
        collection_questions = 'questions'
        
        docs = db.collection(collection_name).document(id).collection(collection_questions).stream()  # Add parentheses to call the stream() method

        data = []
        for i, doc in enumerate(docs, start=1):
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id  # Add the document ID to the data dictionary
            data.append({'row_number': i, **doc_data})

        return render_template('listquestions.html', data=data, module_id=id)

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



