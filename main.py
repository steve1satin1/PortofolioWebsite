import os
import smtplib
from datetime import datetime

from sqlalchemy import exc
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ProjectForm, ContactForm, LoginForm, SubscribersForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String
from flask_ckeditor import CKEditor
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret key'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)


# Define a context processor function to provide the current year
def current_year():
    return {'current_year': datetime.now().year}


# Register the context processor
app.context_processor(current_year)


@app.context_processor
def inject_form():
    # Create an instance of your form
    subscribers_form = SubscribersForm()
    return dict(subscribers_form=subscribers_form)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Projects(db.Model):
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column("title", String(50), nullable=False)
    image_url = mapped_column("image_url", String(100), nullable=False)
    github_url = mapped_column("github_url", String(100), nullable=False)
    small_des = mapped_column("small_des", String(100), nullable=False)
    description = mapped_column("description", String(200), nullable=False)


class Users(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True)
    password = mapped_column("password", String(50), nullable=False)


class Subscribers(db.Model):
    id = mapped_column(Integer, primary_key=True)
    email_sub = mapped_column("email_sub", String(100), nullable=False, unique=True)


# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)
# create table
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


def is_table_empty():
    count = Users.query.count()
    return count == 0


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "GET":
        new_form = ProjectForm()
        return render_template("add.html", form=new_form)
    else:
        new_project = Projects(
            title=request.form["title"],
            image_url=request.form["image_url"],
            github_url=request.form["github_url"],
            small_des=request.form["small_des"],
            description=request.form["description"]
        )
        db.session.add(new_project)
        db.session.commit()

        # inform subscribers about the new project
        subscribers = Subscribers.query.all()
        print(subscribers)
        with smtplib.SMTP("smtp.gmail.com", timeout=2000) as connection:
            connection.starttls()
            connection.login(user="testyt559@gmail.com", password="mnlyytgzufbffgfz")
            for sub in subscribers:
                connection.sendmail(from_addr="testyt559@gmail.com",
                                    to_addrs=f"{sub.email_sub}",
                                    msg=f"Subject:New Project Just arrived\n\nHello fellow subscriber i'm Stergios Papadopoulos and I've just uploaded a new project visit my website to see it")

        return redirect(url_for("add"))


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    project = db.get_or_404(Projects, request.args.get("project_id"))
    if request.method == "GET":
        new_form = ProjectForm(
            title=project.title,
            image_url=project.image_url,
            github_url=project.github_url,
            small_des=project.small_des,
            description=project.description
        )
        return render_template("add.html", form=new_form)
    else:
        project.title = request.form["title"]
        project.image_url = request.form["image_url"]
        project.github_url = request.form["github_url"]
        project.small_des = request.form["small_des"]
        project.description = request.form["description"]
        db.session.commit()
        return redirect(url_for("projects"))


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    # get the project to delete
    project = db.get_or_404(Projects, request.args.get("project_id"))
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('projects'))


@app.route("/projects")
def projects():
    all_projects = db.session.execute(db.select(Projects)).scalars().all()
    return render_template("projects.html", prj=all_projects)


@app.route("/view_project")
def view_project():
    project_id = request.args.get("project_id")
    project = db.get_or_404(Projects, project_id)
    return render_template("view_project.html", project=project)


@app.route("/resume")
def resume():
    return render_template("resume.html")


@app.route("/download")
def download():
    return send_file("static/cv.pdf", as_attachment=True)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # send email
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        mes = request.form["message"]

        with smtplib.SMTP("smtp.gmail.com", timeout=2000) as connection:
            connection.starttls()
            connection.login(user="testyt559@gmail.com", password="mnlyytgzufbffgfz")
            connection.sendmail(from_addr="testyt559@gmail.com",
                                to_addrs="stevepd33333@gmail.com",
                                msg=f"Subject:Msg From portfolio\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMes: {mes}")

        # Inform user
        flash("Message Sent")
        return redirect(url_for("contact"))
    contact_form = ContactForm()
    return render_template("contact.html", form=contact_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # if there isn't any user signed up create only one
        if is_table_empty():
            new_user = Users(
                password=generate_password_hash(request.form["password"])
            )
            db.session.add(new_user)
            db.session.commit()
            flash("1")
            return redirect(url_for("login"))

        user = db.get_or_404(Users, 1)
        if check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash("Logged in successfully")
            return redirect(url_for("home"))
        else:
            flash("2")
            return redirect(url_for("login"))

    # in get request
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    form = inject_form().get('subscribers_form')
    if form.validate_on_submit():
        new_sub = Subscribers(
            email_sub=request.form["email_sub"]
        )
        try:
            db.session.add(new_sub)
            db.session.commit()
        except exc.IntegrityError:
            return render_template("already.html")
        return render_template("thanks.html")
    else:
        return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True)
