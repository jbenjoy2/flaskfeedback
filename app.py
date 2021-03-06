from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import User, Feedback, db, connect_db
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
import os

app = Flask(__name__, static_url_path='/static')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'DATABASE_URL', 'postgresql:///feedback')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'itsasecretdonttell')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)


@app.route('/')
def home_page():
    return redirect('/login')


@app.errorhandler(401)
def show_401_page(error):
    return render_template('401.html'), 401


@app.errorhandler(404)
def show_404_page(error):
    return render_template('404.html')


@app.route('/register', methods=['GET', 'POST'])
def register_new_user():
    if 'username' in session:
        return redirect(f'/users/{session["username"]}')

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first = form.first_name.data
        last = form.last_name.data

        new_user = User.register(username, pwd, email, first, last)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please Pick Another')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash(
            f"Welcome, {new_user.username}! Successfully created your account!", 'success')
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():

    if 'username' in session:
        return redirect(f'/users/{session["username"]}')

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user == 'failed':
            form.username.errors = ["User not found"]
        elif user:
            flash(f"Welcome back, {user.username}!", 'success')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.password.errors = ['Incorrect password. Please try again']
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('Successfully logged out!', 'info')
    return redirect('/login')


@app.route('/users/<username>')
def show_user_details(username):
    user = User.query.get(username)

    if not user:
        return render_template('404.html')
    elif 'username' not in session or session['username'] != username:
        raise Unauthorized()
    return render_template('user.html', user=user)


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    user = User.query.get(username)

    if not user:
        flash('That user does not exist!', 'danger')
        return render_template('404.html')
    elif 'username' not in session or session['username'] != username:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()
        flash('New Feedback Added!', 'success')
        return redirect(f'/users/{feedback.username}')

    else:
        return render_template('addfeedback.html', form=form)


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()

    db.session.delete(feedback)
    db.session.commit()

    return redirect(f'/users/{feedback.username}')


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        flash('Feedback successfully updated!', 'success')
        return redirect(f'/users/{feedback.username}')
    return render_template('editfeedback.html', form=form, feedback=feedback)


@app.route('/users/<username>/confirm-delete')
def display_confirmation_page(username):
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    return render_template('confirm.html', user=user)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)
    if user.username == session['username']:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash('Account Successfully Deleted', 'danger')
        return redirect('/')
    flash("You don't have permission to do that!", 'danger')
    return redirect('/')
