from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os


app = Flask(__name__)

app.config["SECRET_KEY"] = "secret123"


# ✅ SUPABASE DATABASE (PASTE YOUR LINK HERE)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres.twswamuwpufvbilpoydz:Viratsavita%40123@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require"
app.config["UPLOAD_FOLDER"] = "static/uploads"


if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ================= USER =================

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))


# ================= BOOK =================

class Book(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    pdf = db.Column(db.String(200))


# ================= ORDER =================

class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(100))
    user = db.Column(db.String(100))
    status = db.Column(db.String(50))


# ================= USER LOADER =================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ================= CATEGORY BOOKS =================

books_links = {
    "selfhelp": (
        "Self Help",
        "https://www.gutenberg.org/files/4507/4507-h/4507-h.htm"
    ),
    "romance": (
        "Romance",
        "https://www.gutenberg.org/files/1342/1342-h/1342-h.htm"
    ),
    "business": (
        "Business",
        "https://www.gutenberg.org/files/5200/5200-h/5200-h.htm"
    ),
    "hindi": (
        "Hindi",
        "https://www.hindwi.org/kavya"
    ),
    "kids": (
        "Kids",
        "https://www.gutenberg.org/files/11/11-h/11-h.htm"
    ),
    "manga": (
        "Manga",
        "https://archive.org/details/goldencomics"
    ),
}


# ================= HOME =================

@app.route("/")
def home():

    books = Book.query.all()

    return render_template(
        "index.html",
        books=books
    )


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["username"]
        password = request.form["password"]

        u = User(
            username=name,
            password=password
        )

        db.session.add(u)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            login_user(user)
            return redirect("/")

    return render_template("login.html")


# ================= LOGOUT =================

@app.route("/logout")
@login_required
def logout():

    logout_user()
    return redirect("/")


# ================= ADMIN =================

@app.route("/admin", methods=["GET", "POST"])

def admin():

    if request.method == "POST":

        name = request.form["name"]
        file = request.files["pdf"]

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(path)

        b = Book(
            name=name,
            pdf=file.filename
        )

        db.session.add(b)
        db.session.commit()

    books = Book.query.all()

    return render_template(
        "admin.html",
        books=books
    )


# ================= READ PDF =================

@app.route("/read/<filename>")
def read_book(filename):

    return redirect(
        url_for(
            'static',
            filename='uploads/' + filename
        )
    )


# ================= CATEGORY =================

@app.route("/category/<name>")
def category_book(name):

    if name not in books_links:
        return "Not found"

    title, link = books_links[name]

    return render_template(
        "read.html",
        title=title,
        link=link
    )

# ================= BUY =================

@app.route("/buy/<name>")
def buy(name):

    order = Order(
        book_name=name,
        user="demo_user",
        status="pending"
    )

    db.session.add(order)
    db.session.commit()

    return render_template("payment.html", book=name)


# ================= PAY =================

@app.route("/pay/<name>")
def pay(name):

    order = Order.query.filter_by(
        book_name=name,
        status="pending"
    ).first()

    if order:
        order.status = "paid"
        db.session.commit()

    return render_template("success.html", book=name)



# ================= CREATE DB =================

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)