from datetime import datetime
from array import array
import email
from sqlalchemy import String, Text, Sequence
from sqlalchemy.dialects.postgresql import ARRAY

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.sql.schema import ForeignKey

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    '''Information on users'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    boards = db.relationship('Board', cascade='all, delete', backref='users')
    created_recipes = db.relationship("UserRecipe", cascade='all, delete', backref='users')

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        '''Register user and hash password'''

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("UTF-8")
        user = cls(
            username=username,
            password=hashed_utf8,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user
    

    @classmethod
    def authenticate(cls, username, password):
        '''Authenticate a user to see if they used the correct username and password'''

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Board(db.Model):
    '''Model for users to create new boards to put recipes into'''

    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    recipe_ids = db.relationship("Recipe", cascade='all, delete')


class UserRecipe(db.Model):
    '''Create new recipes and store them as recipes specifically made by users'''

    __tablename__ = 'user_recipes'

    id = db.Column(db.Integer, db.Sequence('seq_user_rec_id', start=10000000), primary_key=True) # 10000000
    title = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    image = db.Column(db.Text, default='https://spoonacular.com/recipeImages/621204-556x370.jpg')
    ingredient_1 = db.Column(db.Text, nullable=False)
    ingredient_2 = db.Column(db.Text, nullable=False)
    ingredient_3 = db.Column(db.Text)
    ingredient_4 = db.Column(db.Text)
    ingredient_5 = db.Column(db.Text)
    ingredient_6 = db.Column(db.Text)
    ingredient_7 = db.Column(db.Text)
    ingredient_8 = db.Column(db.Text)
    ingredient_9 = db.Column(db.Text)
    ingredient_10 = db.Column(db.Text)
    ingredient_11 = db.Column(db.Text)
    ingredient_12 = db.Column(db.Text)
    ingredient_13 = db.Column(db.Text)
    ingredient_14 = db.Column(db.Text)
    ingredient_15 = db.Column(db.Text)
    ingredient_16 = db.Column(db.Text)
    ingredient_17 = db.Column(db.Text)
    ingredient_18 = db.Column(db.Text)
    ingredient_19 = db.Column(db.Text)
    ingredient_20 = db.Column(db.Text)
    instructions = db.Column(db.Text)


class Recipe(db.Model):
    '''A database to store the recipe ids in order to add them to a board. 
    I did not put the id (recipe id for the api and personal db) as the primary key because 
    a recipe could not be saved to two separate boards. That is why the unique key was needed, 
    so the actual recipe id could be saved to multiple boards.'''

    unique_id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id", ondelete='CASCADE'))
    id = db.Column(db.Integer)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)