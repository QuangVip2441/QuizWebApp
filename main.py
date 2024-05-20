from flask import Flask, render_template, url_for,  request, redirect, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from uuid import uuid4
import pyrebase
import firebase_admin 
from firebase_admin import credentials, firestore, auth
from jinja2 import Environment, FileSystemLoader
from functools import wraps



app = Flask(__name__)
app.config['SECRET_KEY'] = 'Qh2410.2'
login_manager = LoginManager(app)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id
    
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Hàm kiểm tra đăng nhập
def is_logged_in():
    return 'user_id' in session

# Hàm đăng nhập
def login_user(user_id):
    session['user_id'] = user_id

# Hàm đăng xuất
def logout_user():
    session.pop('user_id', None)

# Đánh dấu một route là cần phải đăng nhập
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
@login_required
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
@login_required
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
@login_required
def insert_questions(moduleid):
    if request.method == 'GET':
        module_ref = db.collection("module").document(moduleid)
        module_data = module_ref.get().to_dict()

        if module_data:
            module_data['id'] = moduleid
            return render_template("insertquestions.html", module=module_data, module_id=moduleid)
        else:
            return render_template('notify.html', message='Module không tồn tại')
       
# Xử lý thêm câu hỏi======================================================
@app.route('/insertquestions/<moduleid>', methods=['POST'])
@login_required
def insert_questions_process(moduleid):
    content = request.form['content']
    answerA = request.form['answerA']
    answerB = request.form['answerB']
    answerC = request.form['answerC']
    answerD = request.form['answerD']
    correct = request.form['correct']

    if request.method == 'POST':
        question_data = {
            'id'      : str(uuid4()),  # Generate a random UUID
            'content' : content,
            'correct' : correct,
            'choices' : [
                {'id' : 'A', 'answer' : answerA},
                {'id' : 'B', 'answer' : answerB},
                {'id' : 'C', 'answer' : answerC},
                {'id' : 'D', 'answer' : answerD}
            ]
        }

        question_ref = db.collection("module").document(moduleid).collection('questions').document(question_data['id']) # Tạo một document mới trong collection 'questions'
        question_ref.set(question_data)

        module_ref = db.collection("module").document(moduleid)
        current_number_questions = module_ref.get().get('numberQuestions') or 0

        new_number_questions = int(current_number_questions) + 1
        new_number_questions_str = str(new_number_questions)
        module_ref.update({'numberQuestions': new_number_questions_str})

        return redirect(url_for('list_question', id=moduleid))

# gọi trang thêm người dùng============================================================================================
@app.route('/register')
def register(): 
    return render_template('insertUser.html')

#xử lý thêm người dùng============================================================================================
@app.route('/registered', methods=['POST'])
@login_required
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
# Kiểm tra sự tồn tại của email và mssv người dùng khác============================================
def check_exists_email_and_mssv(id, email, mssv):
    # Check if the email is already registered
    email_query = db.collection('user').where('email', '==', email)
    email_docs = email_query.stream()
    
    for doc in email_docs:
        # If email exists and it does not belong to the current user
        if doc.id != id:
            return False

    # Check if MSSV is already registered
    mssv_query = db.collection('user').where('mssv', '==', mssv)
    mssv_docs = mssv_query.stream()
    
    for doc in mssv_docs:
        # If MSSV exists and it does not belong to the current user
        if doc.id != id:
            return False

    return True

# xử lý login============================================================================================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Kiểm tra xem email và mật khẩu có phù hợp với tài khoản admin hay không
        if email == 'Admin1234@gmail.com' and password == 'Admin1234':
            try:
                login = auth.sign_in_with_email_and_password(email, password)
                session['logged_in'] = True
                session['email'] = email
                login_user(login['localId'])  # Đăng nhập bằng localId
                return redirect(url_for('indexModule'))
            except:
                return render_template('notify.html', message='Sai thông tin đăng nhập')
        else:
            return render_template('notify.html', message='Tài khoản hoặc mật khẩu không đúng')

    return render_template('login.html')

       
#Xử lý logout============================================================================================
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Đăng xuất
    session.clear()  # Xóa phiên đăng nhập
    return redirect(url_for('login'))

# xử lý sửa user=====================================================================================
@app.route('/user/<id>', methods=['POST'])
@login_required
def user_edit_process(id):
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        mssv = request.form["mssv"]
        phone = request.form["phone"]

        # Validate form data
        if not username or not email or not password or not mssv or not phone:
           return render_template('notify.html', message='Nội dung chưa đủ')
        elif check_exists_email_and_mssv(id, email, mssv)!= True:
            return render_template('notify.html', message='Email hoặc mã số sinh viên đã tồn tại')
    

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
@login_required
def delete_user(id):
    return '''
        <script>
            if (confirm("Are you sure you want to delete user {0}?")) {{
                window.location.href = "/delete_confirm/{0}";
            }} else {{
                window.location.href = "/user";
            }}
        </script>
    '''.format(id)

@app.route('/delete_confirm/<id>', methods=['GET'])
@login_required
def delete_user_confirm(id):
    try:
        firebase_admin.auth.delete_user(id)
        db.collection('user').document(id).delete()
        return indexUser()
    except Exception as e:
        return 'Error deleting user: {}'.format(e)
# gọi trang sửa người dùng và xử lý sửa người dùng============================================================================================
@app.route('/user/<id>' , methods=['GET'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
# gọi trang sửa questions =============================================================
@app.route('/editquestion/<module_id>/<idquestion>', methods=['GET'])
@login_required
def question_edit(module_id, idquestion):
    # Lấy dữ liệu câu hỏi từ Firestore
    question_ref = db.collection("module").document(module_id).collection('questions').document(idquestion)
    question_data = question_ref.get().to_dict()

    if question_data:
        question_data['id'] = idquestion
        return render_template("editQuestions.html", questions=question_data, module_id=module_id)
    else:
        return render_template('notify.html', message='Câu hỏi không tồn tại')

# Xử lý sửa questions ======================================================================
@app.route('/editquestion/<module_id>/<idquestion>', methods=['POST'])
@login_required
def question_edit_process(module_id, idquestion):
    # Lấy dữ liệu từ form
    content = request.form['content']
    answerA = request.form['answerA']
    answerB = request.form['answerB']
    answerC = request.form['answerC']
    answerD = request.form['answerD']
    correct = request.form['correct']

    # Tạo dữ liệu mới cho câu hỏi
    question_data = {
        'content': content,
        'correct': correct,
        'choices': [
            {'id': 'A', 'answer': answerA},
            {'id': 'B', 'answer': answerB},
            {'id': 'C', 'answer': answerC},
            {'id': 'D', 'answer': answerD}
        ]
    }

    # Cập nhật dữ liệu vào Firestore
    module_ref = db.collection("module").document(module_id).collection('questions').document(idquestion)
    module_ref.set(question_data, merge=True)

    # Chuyển hướng về trang danh sách câu hỏi
    return redirect(url_for('list_question', id=module_id))
# Xóa câu hỏi==========================================================================================
@app.route('/deletequestion_confirm/<module_id>/<idquestion>', methods=['GET'])
@login_required
def delete_question_confirm(module_id, idquestion):
    try:
        db.collection("module").document(module_id).collection('questions').document(idquestion).delete()
        module_ref = db.collection("module").document(module_id)
        current_number_questions = module_ref.get().get('numberQuestions') or 0

        new_number_questions = int(current_number_questions) - 1
        new_number_questions_str = str(new_number_questions)
        module_ref.update({'numberQuestions': new_number_questions_str})

        return redirect(url_for('list_question', id=module_id))
    except Exception as e:
        return 'Error deleting question: {}'.format(e)

@app.route('/deletequestion/<module_id>/<idquestion>', methods=['GET'])
@login_required
def delete_question(module_id, idquestion):
    return '''
        <script>
            if (confirm("Bạn chắc chắn muốn xóa câu hỏi này?")) {{
                window.location.href = "/deletequestion_confirm/{0}/{1}";
            }} else {{
                window.location.href = "/questions/{0}";
            }}
        </script>
    '''.format(module_id, idquestion) 
# xử lý danh sách quản lí bài kiểm tra===================================================================
@app.route('/testadmin')
@login_required
def indexTestAdmin():
    collection_name = 'testadmin'
    docs = db.collection(collection_name).stream()

    data = []
    for i, doc in enumerate(docs, start=1):
        doc_data = doc.to_dict()
        doc_data['moduleid'] = doc.id  # Add the document ID to the data dictionary
        data.append({'row_number': i, **doc_data})

    return render_template('testAdmin.html', data=data)
# Sửa danh sách quản lí bài kiểm tra==============================================================
@app.route('/testadmin/<moduleid>', methods=['GET'])
@login_required
def testadmin_edit(moduleid):
    if request.method == 'GET':
        try:
            module_ref = db.collection("testadmin").document(moduleid)
            module_data = module_ref.get().to_dict()
            
            if module_data:
                module_data['moduleid'] = moduleid

                # Nếu moduleid là yPcUWum0mjuL7mld9Yhy thì tính toán test_get_numberQuestions
                if moduleid == 'yPcUWum0mjuL7mld9Yhy':
                    all_modules = db.collection('testadmin').stream()
                    total_questions = 0
                    for module in all_modules:
                        if module.id != moduleid:
                            # Convert to int if possible, otherwise use 0
                            total_questions += int(module.to_dict().get('test_get_numberQuestions', 0))
                    test_get_numberQuestions_calculated = 50 - total_questions
                    return render_template("editTestAdmin.html", module=module_data, test_get_numberQuestions_calculated=test_get_numberQuestions_calculated)
                elif moduleid == 'ZayqBjRnPr1GXBoyPdOh':  # Nếu moduleid là ZayqBjRnPr1GXBoyPdOh, gán giá trị 0 cho test_get_numberQuestions
                    module_data['test_get_numberQuestions'] = 0
                    return render_template("editTestAdmin.html", module=module_data, test_get_numberQuestions_calculated = 0)
                else:
                    return render_template("editTestAdmin.html", module=module_data)
            else:
                return render_template('notify.html', message='Phần thi không tồn tại')
        except Exception as e:
            print(f"Error in testadmin_edit GET: {e}")
            return render_template('notify.html', message='Đã xảy ra lỗi khi truy xuất dữ liệu')


@app.route('/testadmin/<moduleid>', methods=['POST'])
@login_required
def testadmin_editprocess(moduleid):
    test_name = request.form["test_name"]
    numberquestion = request.form["numberquestion"]
    timeAllowed = request.form["timeAllowed"]

    # Validate form data
    if not test_name or not numberquestion or not timeAllowed:
       return render_template('notify.html', message='Nội dung chưa đủ')

    # Khi moduleid là yPcUWum0mjuL7mld9Yhy thì tính test_get_numberQuestions
    if moduleid == 'yPcUWum0mjuL7mld9Yhy':
        all_modules = db.collection('testadmin').stream()
        total_questions = 0
        for module in all_modules:
            if module.id != moduleid:
                # Convert to int if possible, otherwise use 0
                total_questions += int(module.to_dict().get('test_get_numberQuestions', 0))
        test_get_numberQuestions = 50 - total_questions
    else:
        test_get_numberQuestions = int(request.form["test_get_numberQuestions"])  # Ensure this is an int

    # Update user data in Firestore
    module_data = {
        'test_name': test_name,
        'numberquestion': int(numberquestion),  # Ensure this is an int
        'test_get_numberQuestions': test_get_numberQuestions,  # Already an int
        'timeAllowed': int(timeAllowed)  # Ensure this is an int
    }

    db.collection('testadmin').document(moduleid).set(module_data)
    return indexTestAdmin()
# Tìm kiếm sinh viên theo mã số sinh viên================================================
@app.route('/search', methods=['POST'])
@login_required
def search_student():
    mssv = request.form['mssv']
    collection_name = 'user'
    docs = db.collection(collection_name).where('mssv', '==', mssv).stream()

    data = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        data.append(doc_data)

    if len(data) == 0:
        return render_template('notify.html', message='Không tìm thấy sinh viên với mã số sinh viên này')
    else:
        return render_template('user.html', data=data)
# Tìm kiếm câu hỏi thuộc từng mô đun ==================================================================
@app.route('/search', methods=['POST'])
@login_required
def search():
    content = request.form['content']
    collection_name = 'questions'
    docs = db.collection(collection_name).where('content', '==', content).stream()

    data = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        data.append(doc_data)

    if len(data) == 0:
        return render_template('notify.html', message='Không tìm thấy câu hỏi với nội dung này')
    else:
        return render_template('questions.html', data=data, module_id=module_id)

if __name__ == '__main__':
    app.run(debug=True)



