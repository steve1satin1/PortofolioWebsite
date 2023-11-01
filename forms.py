from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import Email


class ProjectForm(FlaskForm):
    title = StringField('title')
    image_url = StringField('image_url')
    github_url = StringField("github_url")
    small_des = StringField("small_des")
    description = StringField("description")
    submit = SubmitField("submit")


class ContactForm(FlaskForm):
    name = StringField("Name")
    email = StringField("Email")
    phone = StringField("Phone")
    message = CKEditorField('Message')
    submit = SubmitField("Send")


class LoginForm(FlaskForm):
    password = StringField("password")
    submit = SubmitField("login in")


class SubscribersForm(FlaskForm):
    email_sub = StringField('email_sub', validators=[Email()])
