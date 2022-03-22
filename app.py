import os
from sqlite3 import IntegrityError
import pdb

from flask import Flask, render_template, request, flash, redirect, session, g, abort, jsonify
from secret import user_key
from flask_debugtoolbar import DebugToolbarExtension
# from sqlalchemy.exc import IntegrityError
import requests

from forms import NewRecipeForm, UserAddForm, LoginForm, NewBoardForm
from models import db, connect_db, User, UserRecipe, Board, Recipe

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone_one'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = 'brockisgood'
toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
db.create_all()

# for the basic search
baseURL = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={user_key}'
# url for a single recipe
infoURL = f'https://api.spoonacular.com/recipes/118854/information?apiKey={user_key}'
# url to get random recipes
randomURL = f'https://api.spoonacular.com/recipes/random?apiKey={user_key}'


# Example:
# res = requests.get(baseURL, params={'query': 'chick', 'number': 5})

# data = res.json()


@app.route('/')
def homepage():

    res = requests.get(randomURL, params={'number': 100})
    data = res.json()
    results = data['recipes']
    
    return render_template('home.html', results=results)


@app.before_request
def add_user_to_g():
    '''If the user is logged in, add them to Flask global'''

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    '''Log in user'''

    session[CURR_USER_KEY] = user.id

def do_logout():
    '''Logout user'''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        flash("Successfully Logged Out", 'success')
        return redirect("/login")


# routes for user info ####################################################################


@app.route('/signup', methods=["GET", "POST"])
def register():
    '''register a user'''

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/register.html', form=form)
        
        do_login(user)

        flash("Successfully Signed Up!", 'success')
        return redirect("/")

    else:
        return render_template('users/register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    '''Login user'''

    if g.user:
        flash("Unauthorized access", 'danger')
        return redirect(f'/users/{g.user.id}')

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash("You are successfully logged in!", 'success')
            return redirect(f"/users/{user.id}")

        flash("Invalid credentials", 'danger')

    return render_template('users/login.html', form=form)


@app.route("/logout")
def logout():
    '''Handle logout for user.'''

    return do_logout()


@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    '''Show all information on the user, including name, profile name, and boards'''

    if not g.user:
        flash("Unauthorized access", 'danger')
        return redirect('/login')

    user = User.query.get_or_404(user_id)

    boards = (Board.query.filter(Board.user_id == user_id).all())

    return render_template("users/show.html", user=user, boards=boards)


@app.route("/users/delete", methods=["POST"])
def delete_user():
    '''Delete user'''

    if not g.user:
        flash("Unauthorized access", 'danger')
        return redirect('/login')

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect('/signup')


# route for handling search inquiries ###########################################################


@app.route('/results', methods=["GET"])
def results():

    if not g.user:
        flash("Please login or signup before searching", "danger")
        return redirect("/login")

    search = request.args.get('query')
    user_recipes = UserRecipe.query.all()
    recipes = [user_recipe for user_recipe in user_recipes if search.lower() in user_recipe.title.lower()]
    results = requests.get(baseURL, params={'query': search, 'number': 100})
    data = results.json()
    info=data['results']
    recipes_results = info + recipes
    return render_template('index.html', results=recipes_results, search=search)


# routes for handling user boards ################################################################


@app.route('/users/boards/new', methods=["GET", "POST"])
def create_board():
    '''Create new board form'''

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    
    form = NewBoardForm()
    if form.validate_on_submit():
        board = Board(name=form.name.data, user_id=g.user.id)
        db.session.add(board)
        db.session.commit()

        flash("New Board Created!", 'success')
        return redirect(f"/users/{g.user.id}")

    return render_template("boards/create.html", form=form)


@app.route("/recipe/<int:recipe_id>/add_to_board", methods=["GET"])
def add_recipe_to_board_index(recipe_id):
    '''Open index of boards to add given recipe to'''

    if not g.user:
        flash("Unauthorized access", 'danger')
        return redirect('/login')

    boards = (Board.query.filter(Board.user_id == g.user.id).all())

    if recipe_id > 9999999:
        recipe = UserRecipe.query.get_or_404(recipe_id)  
    else:
        res = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={user_key}')
        recipe = res.json() 

    return render_template("boards/add.html", boards=boards, recipe=recipe)


@app.route("/boards/<int:board_id>/add/<int:recipe_id>", methods=["GET", "POST"])
def add_recipe_to_board(board_id, recipe_id):
    '''Add recipe to board'''

    if not g.user:
        flash("Unauthorized access", 'danger')
        return redirect('/login')
    
    board = Board.query.get_or_404(board_id)
    
    for recipe in board.recipe_ids:
        if recipe_id == recipe.id:
            flash("Recipe already in this board", 'danger')
            return redirect(f"/users/{g.user.id}")

    new_recipe = Recipe(board_id=board.id, id=recipe_id)
    db.session.add(new_recipe)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


@app.route("/boards/<int:board_id>", methods=["GET"])
def show_board_recipes(board_id):
    '''show all recipes in created board'''

    if not g.user:
        flash("Unauthorized access", 'danger')
        return redirect('/login')
    
    board = Board.query.get_or_404(board_id)
    recipes = []
    board_recipes = (Recipe.query.filter(Recipe.board_id == board.id).all())

    for recipe_query in board_recipes:
        if recipe_query.id > 9999999:
            recipe = UserRecipe.query.get_or_404(recipe_query.id)  
        else:
            res = requests.get(f'https://api.spoonacular.com/recipes/{recipe_query.id}/information?apiKey={user_key}')
            recipe = res.json()

        recipes.append(recipe)
    
    return render_template("boards/index.html", recipes=recipes, board=board)


@app.route("/users/created-recipes", methods=["GET"])
def get_your_recipes():
    '''Index of users created recipes'''

    recipes = (UserRecipe.query.filter(UserRecipe.user_id == g.user.id).all())

    return render_template("boards/index.html", recipes=recipes)


# routes for handling recipe information #########################################################


@app.route('/recipe/<int:recipe_id>', methods=["GET"])
def show_recipe(recipe_id):

    if recipe_id > 9999999:
        recipe = UserRecipe.query.get(recipe_id)
        ingredients = [recipe.ingredient_1, recipe.ingredient_2, recipe.ingredient_3, recipe.ingredient_4, recipe.ingredient_5, recipe.ingredient_6, recipe.ingredient_7, recipe.ingredient_8, recipe.ingredient_9, recipe.ingredient_10, recipe.ingredient_11, recipe.ingredient_12, recipe.ingredient_13, recipe.ingredient_14, recipe.ingredient_15, recipe.ingredient_16, recipe.ingredient_17, recipe.ingredient_18, recipe.ingredient_19, recipe.ingredient_20]
        return render_template('recipes/user_recipe.html', recipe=recipe, ingredients=ingredients)
    res = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={user_key}')
    if res:
        data = res.json()
        instructions = data['instructions']
        return render_template('recipes/recipe.html', recipe=data, instructions=instructions)
    else:
        return abort(404)
    
    
@app.route('/recipe/new', methods=["GET", "POST"])
def create_recipe():
    '''Page with form for creating new recipes'''

    if not g.user:
        flash("Please login or signup before creating recipes", "danger")
        return redirect("/login")


    form = NewRecipeForm()
    user_id = g.user.id

    if form.validate_on_submit():
        recipe = UserRecipe(
            title=form.title.data,
            image=form.image.data or "https://spoonacular.com/recipeImages/621204-556x370.jpg",
            user_id=user_id,
            ingredient_1=form.ingredient_1.data,
            ingredient_2=form.ingredient_2.data,
            ingredient_3=form.ingredient_3.data,
            ingredient_4=form.ingredient_4.data,
            ingredient_5=form.ingredient_5.data,
            ingredient_6=form.ingredient_6.data,
            ingredient_7=form.ingredient_7.data,
            ingredient_8=form.ingredient_8.data,
            ingredient_9=form.ingredient_9.data,
            ingredient_10=form.ingredient_10.data,
            ingredient_11=form.ingredient_11.data,
            ingredient_12=form.ingredient_12.data,
            ingredient_13=form.ingredient_13.data,
            ingredient_14=form.ingredient_14.data,
            ingredient_15=form.ingredient_15.data,
            ingredient_16=form.ingredient_16.data,
            ingredient_17=form.ingredient_17.data,
            ingredient_18=form.ingredient_18.data,
            ingredient_19=form.ingredient_19.data,
            ingredient_20=form.ingredient_20.data,
            instructions=form.instructions.data
            )
        db.session.add(recipe)
        db.session.commit()
        
        return redirect(f'/recipe/created/{recipe.id}')

    return render_template('recipes/new.html', form=form)


@app.route('/recipe/created/<int:recipe_id>', methods=["GET"])
def show_created_recipe(recipe_id):
    '''Shows information on recipe that was just created by a user. This will allow the user_recipes to reload with the new recipe.'''

    recipe = UserRecipe.query.get_or_404(recipe_id)
    ingredients = [recipe.ingredient_1, recipe.ingredient_2, recipe.ingredient_3, recipe.ingredient_4, recipe.ingredient_5, recipe.ingredient_6, recipe.ingredient_7, recipe.ingredient_8, recipe.ingredient_9, recipe.ingredient_10, recipe.ingredient_11, recipe.ingredient_12, recipe.ingredient_13, recipe.ingredient_14, recipe.ingredient_15, recipe.ingredient_16, recipe.ingredient_17, recipe.ingredient_18, recipe.ingredient_19, recipe.ingredient_20]

    return render_template("recipes/user_recipe.html", recipe=recipe, ingredients=ingredients)









    








    