from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import User, Feedback, db, connect_db
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__, static_url_path='/static')
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
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

        if user:
            flash(f"Welcome back, {user.username}!", 'success')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.password.errors = ['Invalid username/password']
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('Successfully logged out!', 'info')
    return redirect('/login')


@app.route('/users/<username>')
def show_user_details(username):
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    return render_template('user.html', user=user)


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in session or username != session['username']:
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
        return render_template('feedback/addfeedback.html', form=form)
