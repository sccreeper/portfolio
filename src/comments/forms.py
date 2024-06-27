from flask_wtf import FlaskForm
from wtforms.fields import StringField, HiddenField, Field, PasswordField, SubmitField
from wtforms.validators import Length, DataRequired, ValidationError
from wtforms.widgets import TextArea
from wtforms.form import Form
from src import post_slugs
from src.comments.profanity import profanity_validator

def _slug_validator(form: Form, field: Field):
    if not field.data in post_slugs:
        raise ValidationError("Post URL not recognised")

class SubmitCommentForm(FlaskForm):
    
    name = StringField(
        None, 
        render_kw={"placeholder": "Name"}, 
        validators=[
            DataRequired("Name is required"), 
            Length(4, 32, "Names must be between 4 and 32 characters long."),
            profanity_validator
        ]
    )
    
    comment = StringField(
        None, 
        render_kw={"placeholder": "Comment", "rows": "3"}, 
        validators=[
            DataRequired("Comment is required"), 
            Length(1, 512, "Comments have a maximum length of 512 characters."),
            profanity_validator
        ],
        widget=TextArea(),
    )

    slug = HiddenField(None, validators=[_slug_validator])

class LoginForm(FlaskForm):

    password = PasswordField("Passsword: ", validators=[DataRequired("Please enter a password")])

class FilterCommentsForm(FlaskForm):

    query = StringField("Query: ")