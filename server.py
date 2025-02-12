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

@app.route('/movies')
def movie_list():
    """Show list of users."""

    movies = Movie.query.order_by('movie_title').all()
    return render_template("movie_list.html", movies=movies)

@app.route('/register', methods=["GET"])
def register_form():
    """Show user registration form"""

    return render_template("registration.html")

@app.route('/register', methods=["POST"])
def register_process():
    """Handles submission of the login form"""

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

    return render_template('user_detail.html', user=user)

@app.route("/movies/<movie_id>")
def show_movie(movie_id):

    movie = Movie.query.filter(Movie.movie_id == movie_id).one()

    return render_template('movie_detail.html', movie=movie)

@app.route("/movies/<movie_id>/rate", methods=["POST"])
def add_rating(movie_id):
    """Adds or Updates Movie rating for logged in user. Redirects if not logged in. """

    movie = Movie.query.filter(Movie.movie_id == movie_id).one()
    user_id = session.get('user_id')
    rating = request.form.get('rating')

    # check to see if user is logged in
    if user_id:
        user = User.query.filter(User.user_id == user_id).one()
        new_rating = Rating.query.filter(Rating.user_id == user.user_id, 
                                     Rating.movie_id == movie.movie_id).first()
        if new_rating:
            new_rating.score = rating
            db.session.commit()
            flash("Updated Movie Rating")

            return redirect(f"/movies/{movie.movie_id}")
        else:
            new_rating = Rating(user_id=user_id, movie_id=movie.movie_id,
                                score=rating)
            db.session.add(new_rating)
            db.session.commit()
            flash(f"Rating added for {movie.movie_title}")
            return redirect(f"/movies/{movie.movie_id}")

    else:
        flash("You need to be signed in to rate a movie")
        return redirect(f"/movies/{movie.movie_id}")


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
