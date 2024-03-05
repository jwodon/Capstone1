from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    profile_image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class GameSearchForm(FlaskForm):
    name = StringField("Game Name")
    platform = SelectField("Platform", choices=[]) 
    genre = SelectField("Genre", choices=[])   

class CreateListForm(FlaskForm):
    name = StringField("List Name", validators=[DataRequired()])
    game_select = SelectMultipleField("Game List", choices=[], coerce=int)  
