from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")

user_schema = UserSchema
multiple_user_schema = UserSchema(many=True)

@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be in JSON format')
    post_data = request.get_json()
    username = post_data.get("username")    
    password = post_data.get("password")    


    possible_duplicate = db.session.query(User).filter(User.username == username).first()

    if possible_duplicate is not None:
        return jsonify("Error: the username you've entered has already been taken")

    encrypted_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(username, encrypted_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(f"New user {username} has been added.")

@app.route("/user/verify", methods=["POST"])
def verify_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be in JSON format")

    post_data = request.get_json()
    username = post_data.get("username")    
    password = post_data.get("password")

    user = db.session.query(User).filter(User.username == username).first()

    if user is None:
        return jsonify("User NOT verified")

    if bcrypt.check_password_hash(user.password, password) == False:
        return jsonify("User NOT verified")
        
    return jsonify("User has been verified")



@app.route("/user/get", methods=["GET"])
def get_users():
    users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(users))


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=True, nullable=False)
    author = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=True)
    genre = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=True)

    def __init__(self, title, author, review, genre, price):
        self.title = title
        self.author = author
        self.review = review
        self.genre = genre
        self.price = price

class BookSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "author")


book_schema = BookSchema()
multiple_book_schema = BookSchema(many=True)



# endpoint for posting or creating a book
@app.route("/book/add", methods=["POST"])
def add_book():
    post_data = request.get_json()
    title = post_data.get("title")
    author = post_data.get("author")
    review = post_data.get("review")
    genre = post_data.get("genre")
    price = post_data.get("price")

    book = db.session.query(Book).filter(Book.title == title).first()

    if book:
        return jsonify("You are trying to use a title that has already been used")

    new_book = Book(title, author, review, genre, price)
    db.session.add(new_book)
    db.session.commit()

    return jsonify("You've added a new book!")


@app.route("/book/edit/<id>", methods=["PUT", "PATCH"])
def edit_book(id):
    post_data = request.get_json()
    title = post_data.get("title")
    author = post_data.get("author")
    review = post_data.get("review")
    genre = post_data.get("genre")
    price = post_data.get("price")

    book = db.session.query(Book).filter(Book.id == id).first()

    if title != None:
        book.title = title
    if author != None:
        book.author = author
    if review != None:
        book.review = review
    if genre != None:
        book.genre = genre
    if price != None:
        book.price = price

    db.session.commit()
    return jsonify("Book was updated")

@app.route("/book/delete/<id>", methods=["DELETE"])
def delete_book(id):
    book = db.session.query(Book).filter(Book.id == id).first()
    db.session.delete(book)
    db.session.commit()

    return jsonify(f'the book {book.title} has been deleted')




@app.route("/book/get", methods=["GET"])
def get_books():
    books = db.session.query(Book).all()
    return jsonify(multiple_book_schema.dump(books))



if __name__ == "__main__":
    app.run(debug=True)