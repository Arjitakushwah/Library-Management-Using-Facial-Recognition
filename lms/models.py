from flask_security import UserMixin, RoleMixin

from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from datetime import datetime
db = SQLAlchemy()

# Define Role model
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

# Define User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    enrollment = db.Column(db.String(255), unique=True, nullable=True)
    department = db.Column(db.String(), nullable=True)
    photo = db.Column(db.String(), nullable=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    librarian = db.Column(db.Boolean, default=False, nullable=False)
    phone = db.Column(db.Integer())
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

# Define UserRoles model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class BookCategory(db.Model):
    __tablename__ = 'bookcategory'
    id = db.Column(db.String(), primary_key=True)
    categoryName = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)


class Books(db.Model):
    id = db.Column(db.String(), primary_key=True)
    bookName = db.Column(db.String(255), nullable=False)
    categories = db.Column(db.String(), db.ForeignKey('bookcategory.id', ondelete='CASCADE'))
    author = db.Column(db.String(), nullable = False)
    publisher = db.Column(db.String(), nullable = False)
    edition = db.Column(db.Integer(), nullable=True)
    bookCountAvailable = db.Column(db.Integer())
    totalCount = db.Column(db.Integer())
    bookStatus = db.Column(db.String(), default = "Available")
    language = db.Column(db.String())
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    Book_rating = db.Column(db.Float(), nullable=True)
    review_count = db.Column(db.Integer(), nullable=True)
    top_rated = db.Column(db.String(), default = "NO", nullable=True)
    category = db.relationship('BookCategory', backref=db.backref('books', lazy='dynamic'))

    

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.String(), db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    request_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    processed = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('requests', lazy='dynamic'))
    book = db.relationship('Books', backref=db.backref('requests', lazy='dynamic'))

class BookIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.String(), db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    issue_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref=db.backref('issues', lazy='dynamic'))
    book = db.relationship('Books', backref=db.backref('issues', lazy='dynamic'))

class Fine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.String(), db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    fine_amount = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('fines', lazy='dynamic'))
    book = db.relationship('Books', backref=db.backref('fines', lazy='dynamic'))



class LikedBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.String(), db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    liked_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref=db.backref('liked_books', lazy='dynamic'))
    book = db.relationship('Books', backref=db.backref('liked_by_users', lazy='dynamic'))

class ReviewBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.String(), db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    review_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    review_text = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('book_reviews', lazy='dynamic'))
    book = db.relationship('Books', backref=db.backref('book_reviews', lazy='dynamic'))
