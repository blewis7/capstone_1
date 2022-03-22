from flask_wtf import FlaskForm, Form
from models import User, db
from wtforms import StringField, IntegerField, SelectField, TextAreaField, BooleanField, PasswordField, FieldList, FormField
from wtforms.validators import InputRequired, Length, NumberRange, URL, Optional, Email


class UserAddForm(FlaskForm):
    """Form for registering user"""

    username = StringField("Username: ", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password: ", validators=[InputRequired()])
    email = StringField("Email: ", validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField("First Name: ", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name: ", validators=[InputRequired(), Length(max=30)])

        
class LoginForm(FlaskForm):
    '''User login form'''

    username = StringField("Username: ", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password: ", validators=[InputRequired()])


class NewBoardForm(FlaskForm):
    '''Create new board'''

    name = StringField("Board Name: ", validators=[InputRequired(), Length(max=20)])


class NewRecipeForm(FlaskForm):
    '''New recipe form'''

    title = StringField("Title: ", validators=[InputRequired()])
    image = StringField("Image URL: ")
    ingredient_1 = StringField("Ingredient: ", validators=[InputRequired()])
    ingredient_2 = StringField("Ingredient: ", validators=[InputRequired()])
    ingredient_3 = StringField("Ingredient (Optional): ")
    ingredient_4 = StringField("Ingredient (Optional): ")
    ingredient_5 = StringField("Ingredient (Optional): ")
    ingredient_6 = StringField("Ingredient (Optional): ")
    ingredient_7 = StringField("Ingredient (Optional): ")
    ingredient_8 = StringField("Ingredient (Optional): ")
    ingredient_9 = StringField("Ingredient (Optional): ")
    ingredient_10 = StringField("Ingredient (Optional): ")
    ingredient_11 = StringField("Ingredient (Optional): ")
    ingredient_12 = StringField("Ingredient (Optional): ")
    ingredient_13 = StringField("Ingredient (Optional): ")
    ingredient_14 = StringField("Ingredient (Optional): ")
    ingredient_15 = StringField("Ingredient (Optional): ")
    ingredient_16 = StringField("Ingredient (Optional): ")
    ingredient_17 = StringField("Ingredient (Optional): ")
    ingredient_18 = StringField("Ingredient (Optional): ")
    ingredient_19 = StringField("Ingredient (Optional): ")
    ingredient_20 = StringField("Ingredient (Optional): ")
    instructions = TextAreaField("Instructions: ", validators=[InputRequired()])
    
    