import os

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from flask_login import *

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

from db import db
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Import models after db is created
from models import Post, User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

ADMIN_USERS = {
    "admin",
    "municipality",
    "officer1"
}

from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if not current_user.is_authenticated:
            abort(401)

        if current_user.username not in ADMIN_USERS:
            abort(403)

        return f(*args, **kwargs)

    return decorated

@app.route("/")
def home():

    posts = Post.query.order_by(Post.upvotes.desc()).all()

    return render_template(
        "index.html",
        user=current_user,
        posts=posts
    )

@app.route("/report")
def report_page():
    return render_template("report.html")

@app.route("/report", methods=["POST"])
@login_required
def report():
    data = request.get_json()

    post = Post(
        report_type=data["report_type"],
        text=data["report_text"],
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        user_id=current_user.id
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Report received."
    })

from flask import redirect, url_for
from flask_login import login_required

@app.route("/upvote/<int:post_id>", methods=["POST"])
@login_required
def upvote(post_id):

    post = Post.query.get_or_404(post_id)

    post.upvotes += 1

    db.session.commit()

    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin():

    posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template(
        "admin.html",
        posts=posts
    )

@app.route("/admin/respond/<int:post_id>", methods=["POST"])
@admin_required
def respond(post_id):

    post = Post.query.get_or_404(post_id)

    post.authority_response = request.form["response"]
    post.status = request.form["status"]

    db.session.commit()

    return redirect(url_for("admin"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("home"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)