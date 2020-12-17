from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, Optional


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
                           InputRequired(), Length(min=1, max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email(
        message='Please enter a valid email address'), Length(max=50)])
    first_name = StringField("First Name", validators=[
                             InputRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[
                            InputRequired(), Length(min=1, max=30)])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[
                           InputRequired(), Length(min=1, max=20)])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = StringField("Feedback Content", validators=[InputRequired()])
