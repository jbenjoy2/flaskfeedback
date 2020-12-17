from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import User, db, connect_db
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__, static_url_path='/static')
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/secret')
def show_secret():
    if 'username' not in session:
        raise Unauthorized()
    return render_template('secret.html')


@app.errorhandler(401)
def show_401_page(error):
    return render_template('401.html'), 401


@app.errorhandler(404)
def show_404_page(error):
    return render_template('404.html')


@app.route('/register', methods=['GET', 'POST'])
def register_new_user():
    if 'username' in session:
        return redirect('/secret')

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
        return redirect('/secret')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome back, {user.username}!", 'success')
            session['username'] = user.username
            return redirect('/secret')
        else:
            form.password.errors = ['Invalid username/password']
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('Successfully logged out!', 'info')
    return redirect('/login')
