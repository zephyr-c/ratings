"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/', methods=["POST", "GET"])
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/register', methods=["GET"])
def register_form():
    """Show user registration form"""

    return render_template("registration.html")

@app.route('/register', methods=["POST"])
def register_process():
    """Handles submission of the login form"""

    # query for the email address in our DB
        # if the email is not in the database
            # create new user in DB
        # if the email IS in the database
            # flash message for this user already exists (or alert box?)

    user_email = request.form.get('user_email')
    user_password = request.form.get('user_password')

    if User.query.filter(User.email == user_email).first():
        flash(f"{user_email} already exists")
        return redirect("/login")
    else:
        new_user = User(email=user_email, password=user_password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.user_id
        flash("User successfully added")
    
    return redirect("/")

@app.route('/login', methods=["GET"])
def show_login():
    """Show login form"""

    return render_template("login.html")

@app.route('/login', methods=["POST"])
def process_login():
    """Log user in to site. Query for email address in database, check for password
    match, and add user id to Flask session if email exists and passwords match"""

    login_attempt = request.form

    user_lookup = User.query.filter(User.email == login_attempt['email']).first()

    if user_lookup:
        # check if password matches & handle incorrect and correct pw flows
        if user_lookup.password != login_attempt['password']:
            flash("Incorrect Password!")
            return redirect("/login")
        else:  # password matches
            session['user_id'] = user_lookup.user_id
            flash(f"{user_lookup.email} logged in!")
            return redirect(f"/users/{session['user_id']}")
    else:  # user doesn't exist
        flash(f"{login_attempt['email']} doesn't exist. Create an account below!")
        return redirect("/register")

@app.route("/logout")
def process_logout():

    # delete user_id from Flask session
    del session['user_id']

    return redirect('/')

@app.route("/users/<user_id>")
def show_user(user_id):

    user = User.query.filter(User.user_id == user_id).one()

    print('\n' * 3)
    print(user)
    print('\n' * 3)

    return render_template('user_detail.html', user=user)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
