import os
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pickle
from flask import jsonify
import cv2
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, send_file
from flask_security import SQLAlchemyUserDatastore, Security, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Role, UserRoles
from models import *
from utils import generate_book_id, generate_category_id

app = Flask(__name__)
  
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Library.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "iiytghhgh"
app.config["SECURITY_PASSWORD_SALT"] = "dfswert"
app.config['UPLOAD_FOLDER'] = 'static'
db.init_app(app)

datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, datastore)


with app.app_context():
      db.create_all()

      if not Role.query.filter_by(name="librarian").first():
                  app.security.datastore.create_role(name="librarian")
                  app.security.datastore.create_role(name="student")
                  db.session.commit()

      admin_user = User.query.filter_by(email="librarian@gmail.com").first()

      if not admin_user:
            admin_user = datastore.create_user(name="librarian",email="librarian@gmail.com",password=generate_password_hash("password"), librarian=True, phone=7000707070)
            admin_role = Role.query.filter_by(name="librarian").first()
            datastore.add_role_to_user(admin_user, admin_role)
            db.session.commit()

app.app_context().push()

#### Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
try:
    cap = cv2.VideoCapture(1)
except:
    cap = cv2.VideoCapture(0)

@app.route('/')
def home():
      top_books = Books.query.order_by(Books.Book_rating.desc()).limit(5).all()  # Assuming 'rating' field tracks the rating
      categories = BookCategory.query.limit(5).all()
      return render_template('Home/Home.html', top_books=top_books,categories=categories)

@app.route('/login_page')
def login():
      return render_template('login.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
      if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = app.security.datastore.find_user(email=email)
        password = check_password_hash(user.password, password)
      
        if user and password:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('home'))

@app.route('/student_login', methods=['POST'])
def student_login():
      if request.method == 'POST':
        enrollment = request.form['enrollment']
        password = request.form['password']
        user = app.security.datastore.find_user(enrollment=enrollment)
        password = check_password_hash(user.password, password)      
        if user and password:
            login_user(user)
            return redirect(url_for('Student_dashboard'))
        else:
            return redirect(url_for('home'))

@app.route('/admin')
def admin_dashboard():
      return render_template('Admin/admindashboard.html')

# add student
@app.route('/add', methods=['GET','POST'])
def add_student():
    name = request.form['username']
    password = request.form['password']
    email = request.form['email']
    enrollment = request.form['enrollment']
    department = request.form['department']
    phone = request.form.get('phone')
    # add modal
    face_data = []
    i = 0

    camera = cv2.VideoCapture(0)
    facecascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    while True:
        ret, frame = camera.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_coordinates = facecascade.detectMultiScale(gray, 1.3, 4)

            for (a, b, w, h) in face_coordinates:
                faces = frame[b:b+h, a:a+w, :]
                resized_faces = cv2.resize(faces, (50, 50))
                
                if i % 10 == 0 and len(face_data) < 10:
                    face_data.append(resized_faces)
                cv2.rectangle(frame, (a, b), (a+w, b+h), (255, 0, 0), 2)
            i += 1

            cv2.imshow('frames', frame)
            if cv2.waitKey(1) == 27 or len(face_data) >= 10:
                break
        else:
            print('error')
            break

    cv2.destroyAllWindows()
    camera.release()

    face_data = np.asarray(face_data)
    face_data = face_data.reshape(10, -1)

    if not os.path.exists('Data'):
        os.makedirs('Data')

    if 'enrollments.pkl' not in os.listdir('Data'):
        enrollments = [enrollment]*10
        with open('Data/enrollments.pkl', 'wb') as file:
            pickle.dump(enrollments, file)
    else:
        with open('Data/enrollments.pkl', 'rb') as file:
            enrollments = pickle.load(file)

        enrollments = enrollments + [enrollment]*10
        with open('Data/enrollments.pkl', 'wb') as file:
            pickle.dump(enrollments, file)

    if 'faces.pkl' not in os.listdir('data/'):
        with open('Data/faces.pkl', 'wb') as w:
            pickle.dump(face_data, w)
    else:
        with open('Data/faces.pkl', 'rb') as w:
            faces = pickle.load(w)

        faces = np.append(faces, face_data, axis=0)
        with open('Data/faces.pkl', 'wb') as w:
            pickle.dump(faces, w)
    user = datastore.create_user(name=name,email=email,password=generate_password_hash(password), department=department,phone=phone, enrollment=enrollment)
    role = Role.query.filter_by(name="student").first()
    datastore.add_role_to_user(user, role)
    db.session.commit()
    return redirect(url_for('manage_student'))

      
@app.route('/managestudents')
def manage_student():
      return render_template("Admin/managestudents.html")

# find student
@app.route('/findstudent')
def find_student():
    FIND = False
    cap = cv2.VideoCapture(0)
    student = {}

    facecascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    with open('data/faces.pkl', 'rb') as w:
        faces = pickle.load(w)

    with open('data/enrollments.pkl', 'rb') as file:
        labels = pickle.load(file)

    knn = KNeighborsClassifier(n_neighbors=4)
    knn.fit(faces, labels)

    while True:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_coordinates = facecascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in face_coordinates:
                face = cv2.resize(frame[y:y+h, x:x+w], (50, 50)).flatten().reshape(1, -1)
                identified_person = knn.predict(face)[0]
                student = User.query.filter_by(enrollment=identified_person).first()

                if student:
                    cv2.putText(frame, f'{identified_person}', (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2)
                    if cv2.waitKey(1) == ord('a'):
                        FIND = True
                        break
            if FIND:
                break

            cv2.imshow('Student Checked, press "q" to exit', frame)
            cv2.putText(frame, 'hello', (30, 30), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255))

            if cv2.waitKey(1) == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    if student:
        return redirect(url_for('student_details', id=student.id))
    else:
        return "Student not recognized", 404

@app.route("/managebooks")
def manage_books():
      books = Books.query.all()
      category=BookCategory.query.all()
      
      return render_template('Admin/managebook.html', books=books, category=category)


@app.route('/stats')
def stats():
      return render_template("stats.html")

# @app.route('/student_login', methods=['POST'])
# def student_login():
#       cap = cv2.VideoCapture(0)
#       recognized_user = None
#       while True:
#             success, frame = cap.read()
#             if not success:
#                   print("Error: Unable to capture video.")
#                   break
#             recognized_user = recognize_face(frame)
#             if recognized_user:
#                   break
#       return redirect(url_for('student_dashboard'))

@app.route("/studentdashboard")
def Student_dashboard():
      return render_template('dashboard.html')


@app.route('/api/search', methods=['GET'])
def search_books():
    query = request.args.get('query')
    search_results = Books.query.filter(Books.bookName.ilike(f'%{query}%')).all()
    search_results_json = [{"id": book.id,'title': book.bookName, 'author': book.author, 'status': book.bookStatus} for book in search_results]
    response = {'books': search_results_json}
    return jsonify(response)


@app.route('/search-book', methods=['POST'])
def search_book():
    search_term = request.form.get('searchTerm')
    search_results = Books.query.filter(Books.bookName.ilike(f'%{search_term}%')).all()
    search_results_json = [{"id": book.id,'title': book.bookName, 'author': book.author, 'status': book.bookStatus} for book in search_results]
    response = {'books': search_results_json}
    return jsonify(response)



@app.route('/search-category', methods=['POST'])
def search_category():
    search_term = request.form.get('searchCategory')
    search_results = BookCategory.query.filter(BookCategory.categoryName.ilike(f'%{search_term}%')).all()
    search_results_json = [{"id": category.id, 'name': category.categoryName} for category in search_results]
    response = {'categories': search_results_json}
    return jsonify(response)

@app.route('/delete-category', methods=['POST'])
def delete_category():
    category_id = request.form.get('categoryId')
    category = BookCategory.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Category not found'})

# books managemet
@app.route("/all-books")
def all_books():
    page = request.args.get('page', 1, type=int)
    per_page = 10 
    books = Books.query.paginate(page=page, per_page=per_page, error_out=False)
    pagination = {
        'page': books.page,
        'pages': books.pages,
        'has_prev': books.has_prev,
        'has_next': books.has_next,
        'prev_num': books.prev_num if books.has_prev else None,
        'next_num': books.next_num if books.has_next else None
    }
    book_list = [{'id': book.id, 'title': book.bookName, 'author': book.author, 'publisher': book.publisher,
                  'edition':book.edition, 'total':book.totalCount} for book in books.items]
    response_data = {
        'books': book_list,
        'pagination': pagination
    }

    return jsonify(response_data)

# all categories
@app.route('/api/categories', methods=['GET'])
def get_paginated_categories():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    categories = BookCategory.query.paginate(page=page, per_page=per_page, error_out=False)
    categories_list = [{'id': category.id, 'name': category.categoryName} for category in categories.items]
    pagination_data = {
        'total_categories': categories.total,
        'total_pages': categories.pages,
        'current_page': categories.page,
        'per_page': categories.per_page,
        'has_prev': categories.has_prev,
        'has_next': categories.has_next
    }
    return jsonify({'categories': categories_list, 'pagination': pagination_data})

#  add category
@app.route('/add-category', methods=['POST'])
def add_category():
    data = request.form
    id = generate_category_id()
    category_name = data.get('categoryName')
    print(id)
    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400
    new_category = BookCategory(id=id, categoryName=category_name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category added successfully', 'category_id': new_category.id}), 201

# add books
@app.route('/add-book', methods=['POST'])
def add_book():
    try:
        data = request.form
        id = generate_book_id()
        book_name = data.get('bookName')
        author = data.get('author')
        publisher = data.get('publisher')
        edition = int(data.get('edition'))
        book_count_available = int(data.get('bookCountAvailable'))
        total_count = int(data.get('totalCount'))
        book_status = data.get('bookStatus')
        language = data.get('language')
        category_id = data.get('category')
        category = db.session.get(BookCategory, category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        new_book = Books(
             id=id,
            bookName=book_name,
            author=author,
            publisher=publisher,
            edition=edition,
            bookCountAvailable=book_count_available,
            totalCount=total_count,
            bookStatus=book_status,
            language=language,
            categories=category_id
        )
        db.session.add(new_book)
        db.session.commit()

        return jsonify({'message': 'Book added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# issue book
@app.route('/issue-book', methods=['POST'])
def issue_book():
      request_data = request.json
      book_id = request_data.get('bookId')
      user_id = request_data.get('userId')
      due_date = datetime.utcnow() + timedelta(days=14) 
      print(book_id)
      print(user_id)
      user = User.query.filter_by(enrollment=user_id).first()
      book = Books.query.filter_by(id=book_id).first()
      
      if not book:
          return jsonify({'error': 'Book not found'}), 404
      if book.bookCountAvailable <= 0:
          return jsonify({'error': 'Book not available for issuance'}), 400
      book.bookCountAvailable -= 1
      if book.bookCountAvailable == 0:
           book.bookStatus= "Not Available"
      issued_book = BookIssue(book_id=book_id, user_id=user.id, due_date=due_date)
      db.session.add(issued_book)
      db.session.commit()
      return jsonify({'message': f'Book {book.bookName} issued to user {user_id}'}), 200

# return book
@app.route('/return-book', methods=['POST'])
def return_book():
    book_id = request.form.get('bookId')
    user_id = request.form.get('userId')
    
    # Here you would write the logic to update the database and mark the book as returned
    # For example:
    book = Books.query.filter_by(id=book_id).first()
    # book.status = 'Available'
    # book_issue = BookIssue.query.filter_by(book_id=book_id, user_id=user_id).first()
    # book_issue.returned = True
    # db.session.commit()
    
    # Dummy response for demonstration purposes
    response = {'message': f'Book with ID {book_id} returned by user with ID {user_id} successfully.'}
    
    return jsonify(response)

# borrowing history
@app.route('/borrowing-history/<int:user_id>', methods=['GET'])
def get_borrowing_history(user_id):  
    borrowing_history = BookIssue.query.filter_by(user_id=user_id).all()
    borrowing_history_json = []
    for issue in borrowing_history:
        issue_data = {
             "title": issue.book.bookName,
            'id': issue.id,
            'book_id': issue.book_id,
            'issueDate': issue.issue_date.strftime('%Y-%m-%d'),
            'returnDate': issue.due_date.strftime('%Y-%m-%d'),
        }
        borrowing_history_json.append(issue_data)
    return jsonify(borrowing_history_json)


@app.route('/borrowing_History/<int:user_id>', methods=['GET'])
def borrowing_history(user_id):
      borrowing_history = BookIssue.query.filter_by(user_id=user_id).all()
      
      return render_template("borrowing_history.html", books= borrowing_history)


@app.route('/profile/<int:user_id>', methods=['GET'])
def Student_Profile(user_id):
     student = User.query.filter_by(id = user_id).first()
     return render_template("profile.html", student = student)


@app.route('/requested_books/<int:user_id>', methods=['GET'])
def Requested_Books(user_id):
     student = User.query.filter_by(id = user_id).first()
     return render_template("Requested.html")



@app.route('/search_books', methods=['GET'])
def Search_Books():
     search_query = request.args.get('query')
     search_results = Books.query.filter(Books.bookName.ilike(f'%{search_query}%')).all()
     return render_template("search_book.html")

@app.route('/about', methods=['GET'])
def about():
     return render_template("Home/About.html")
     

@app.route('/vision', methods=['GET'])
def Vision():
     return render_template("Home/Vision.html")


@app.route('/Program-outcomes', methods=['GET'])
def Outcomes():
     return render_template("Home/Outcomes.html")

@app.route('/download_books', methods=['GET'])
def Download_books():
     books = Books.query.all()
     return render_template("Home/Export.html", books=books)

@app.route('/download_books_csv')
def download_books_csv():
    csv_path = 'Data/BooksExport.csv'
    return send_file(csv_path, as_attachment=True)


@app.route('/student_details/<int:id>')
def student_details(id):
    student = User.query.filter_by(id=id).first()
    return render_template("Admin/manageStudent.html", student=student)


if __name__ == '__main__':
    app.run(debug=True)
