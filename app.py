import os
import urllib.parse

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, url_for, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from api_utils import get_game_info, get_genres_info, get_platforms_info, get_single_game_info
from sqlalchemy import func

from models import db, connect_db, User, Rating, List
from forms import UserAddForm, LoginForm, GameSearchForm, CreateListForm


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

    platform_id = request.args.get('platform')
    genre_id = request.args.get('genre')

    games = get_game_info(limit=20, offset=offset, platform_id=platform_id, genre_id=genre_id)
    user = g.user if g.user else None

    # Calculate average ratings
    avg_ratings = db.session.query(Rating.game_id, func.avg(Rating.rating).label('avg_rating')).group_by(Rating.game_id).all()

    for game in games:
        game_id = game['id']
        try:
            game['avg_rating'] = round(next(rating[1] for rating in avg_ratings if rating[0] == game_id), 2)
        except StopIteration:
            game['avg_rating'] = "Not yet available"

    return render_template('index.html', games=games, page=page_num, user=user, form=form)

 

@app.route('/users/profile/<int:user_id>')
def show_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('/users/profile.html', user=user)

@app.route('/games/<int:game_id>')
def show_game_details(game_id):
    game = get_single_game_info(game_id) 
    user = g.user
    
    existing_rating = None
    if user:
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
#Lists

@app.route('/new_list', methods=["GET", "POST"])
def create_list():
    """Show form if GET. User create list form"""

    if not g.user:
        flash("You must be logged in to create a list.", 'danger')
        return redirect("/")

    form = CreateListForm()

    all_games = get_game_info(limit=500)  
    game_choices = [(game['id'], game['name']) for game in all_games]

    # Update the form field's choices
    form.game_select.choices = game_choices 

    if form.validate_on_submit():
        games = request.form.getlist('game_select')  # Extract selected game IDs
        
        if games:
            name = form.name.data
            user_id = g.user.id
            new_list = List(user_id=user_id, title=name, games=games)
            db.session.add(new_list)
            db.session.commit()

            flash("List created successfully.", 'success')
            return redirect(f"/users/profile/{g.user.id}")
        else:
            flash("No games selected for the list.", 'danger')
            return redirect("/new_list")  # Redirect back to the form page if no games selected

    return render_template('new_list.html', form=form, user=g.user)


@app.route('/list/<int:list_id>')
def display_list(list_id):
    """Detailed view of a users list"""

    list = List.query.get(list_id)
    user = g.user if g.user else None

    # If the list does not exist, return a 404 Not Found error
    if list is None:
        abort(404)

    # Calculate average ratings
    avg_ratings = db.session.query(Rating.game_id, func.avg(Rating.rating).label('avg_rating')).group_by(Rating.game_id).all()
    game_data = [get_single_game_info(game_id) for game_id in list.games]


    return render_template('list_detail.html', user=user, list=list, avg_ratings=avg_ratings, games=game_data)


@app.route('/list/<int:list_id>/edit', methods=["GET", "POST"])
def edit_list(list_id):
    """Form to edit an existing list"""

    if not g.user:
        flash("You must be logged in to edit a list.", 'danger')
        return redirect("/")

    list = List.query.get_or_404(list_id)  # Retrieve the list object from the database
    form = CreateListForm(obj=list)  # Set the form object using the list object

    all_games = get_game_info(limit=500)  
    game_choices = [(game['id'], game['name']) for game in all_games]
    form.game_select.choices = game_choices 

    # Convert game IDs to integers
    list_games = [int(game_id) for game_id in list.games]

    # Set the data for the game_select field in the form
    form.game_select.data = list_games
    form.name.data = list.title

    if form.validate_on_submit():
        games = request.form.getlist('game_select')  
        
        if games:
            list.title = form.name.data  # Update the list object with new data from the form
            list.games = games
            db.session.commit()

            flash("List updated successfully.", 'success')
            return redirect(f"/users/profile/{g.user.id}")
        else:
            flash("No games selected for the list.", 'danger')
            return redirect(f"/list/{list_id}/edit")

    return render_template('edit_list.html', form=form, user=g.user, list=list)

@app.route('/list/<int:list_id>/delete', methods=["POST"])
def delete_list(list_id):
    """Delete a list."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    list = List.query.get(list_id)
    db.session.delete(list)
    db.session.commit()
    flash("List deleted successfully.", "success")
    return redirect(f"/users/profile/{g.user.id}")




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
    platform_id_str = request.args.get('platform')
    genre_id_str = request.args.get('genre')
    
    if platform_id_str:
        platform_id = int(platform_id_str)  # Convert to integer 
    else:
        platform_id = None  # Set to None if not provided
    if genre_id_str:
        genre_id = int(genre_id_str)  # Convert to integer 
    else:
        genre_id = None  # Set to None if not provided

    # Build the query for IGDB based on platform_id and genre_id 
    filters = ""
    if platform_id and genre_id:
        filters += f"platforms={platform_id} & genres={genre_id};"
    elif platform_id:
        filters += f"platforms={platform_id};"
    elif genre_id:
        filters += f"genres={genre_id};"

    # Call helper functions to fetch data
    games_info = get_game_info(platform_id=platform_id, genre_id=genre_id, filters=filters)  

    if not games_info: 
      return jsonify({'error': 'No games found matching your filters'}), 404

    return jsonify(games_info)


@app.route('/api/search')
def search_games():
    query = request.args.get('query', '')  
    search_results = search_games(query)   
    return jsonify(search_results)

@app.route('/api/games/all')
def get_all_games():
    games_info = get_game_info(limit=500)  # Fetch enough games for the dropdown
    games_list = [{'id': game['id'], 'name': game['name']} for game in games_info]
    return jsonify(games_list)


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


