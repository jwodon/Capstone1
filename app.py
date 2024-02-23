import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from api_utils import get_game_info, get_genres_info, get_platforms_info, get_single_game_info

from models import db, connect_db, User, Rating, Review
from forms import UserAddForm, LoginForm, GameSearchForm


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

        flash("Successfully logged out.")



@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                profile_image_url=form.profile_image_url.data or User.profile_image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    return redirect("/login")

##############################################################################
# General

@app.route('/')
def display_games(page_num=1):
    """Homepage"""
    
    form = GameSearchForm()

    page_num = request.args.get('page', 1, type=int)  # Get the 'page' parameter from the URL
    offset = (page_num - 1) * 20

    games = get_game_info(limit=20, offset=offset)
    user = g.user if g.user else None

    return render_template('index.html', games=games, page=page_num, user=user, form=form)
 

@app.route('/users/profile/<int:user_id>')
def show_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('/users/profile.html', user=user)

@app.route('/games/<int:game_id>')
def show_game_details(game_id):
    game = get_single_game_info(game_id) 
    user = g.user if g.user else None
    existing_rating = Rating.query.filter_by(user_id=user.id, game_id=game_id).first()

    return render_template('game_detail.html', game=game, user=user, existing_rating=existing_rating)

##########################################################################################
#Ratings

@app.route('/games/<int:game_id>/rate', methods=["POST"])
def rate_game(game_id):
    """Adds or updates a user's rating for a game."""

    if not g.user:
        flash("You must be logged in to rate a game.", 'danger')
        return redirect("/")

    rating = int(request.form.get('rating'))
    user_id = g.user.id

    existing_rating = Rating.query.filter_by(user_id=user_id, game_id=game_id).first()

    if existing_rating:
        existing_rating.rating = rating
        flash("Rating updated!", "success")
    else:
        new_rating = Rating(user_id=user_id, game_id=game_id, rating=rating)
        db.session.add(new_rating)
        flash("Rating submitted!", "success")

    db.session.commit()
    return redirect(url_for('show_game_details', game_id=game_id, existing_rating=existing_rating))




##########################################################################################
#API endpoints

@app.route('/api/platforms')
def get_platforms():
  response = get_platforms_info()
  return jsonify(response.json()) 

@app.route('/api/genres') 
def get_genres():
  response = get_genres_info()
  return jsonify(response.json()) 

@app.route("/api/games")
def get_games():
    platform_id = request.args.get('platform')
    genre_id = request.args.get('genre')

 
    # Build the query for IGDB based on platform_id and genre_id 
    filters = ""
    if platform_id:
        filters += f"platforms = ({platform_id}) & "
    if genre_id:
        filters += f"genres = ({genre_id}) & "

    # Call helper functions to fetch data
    games_info = get_game_info(filters=filters)  

    return jsonify(games_info)


##########################################################################

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("DB initialized.")

@app.context_processor
def utility_processor():
    # Return a dictionary with the function as a value
    return dict(get_single_game_info=get_single_game_info)


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


