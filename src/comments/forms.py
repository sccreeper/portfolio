from flask_wtf import FlaskForm
from wtforms.fields import StringField, HiddenField, Field, PasswordField
from wtforms.validators import Length, DataRequired, ValidationError, EqualTo
from wtforms.widgets import TextArea
from wtforms.form import Form
from src import post_slugs
from src.comments.profanity import profanity_validator
from src.comments.shared import PASSWORD_PATH
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

def _slug_validator(form: Form, field: Field):
    if not field.data in post_slugs:
        raise ValidationError("Post URL not recognised")
    
def _pw_validator(form: Form, field: Field):
    f = open(PASSWORD_PATH, "rb")
    pw_hash = f.read()
    f.close()
    
    try:
        ph = PasswordHasher()
        ph.verify(pw_hash, field.data)
    except VerifyMismatchError:
        raise ValidationError("Password not recognised")
            
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

    password = PasswordField("Passsword: ", validators=[DataRequired("Please enter a password"), _pw_validator])

class FilterCommentsForm(FlaskForm):

    query = StringField("Query: ")

class ChangePasswordForm(FlaskForm):

    old = PasswordField("Old password: ", validators=[DataRequired("Password required"), _pw_validator])

    new = PasswordField("New password: ", validators=[EqualTo("confirm", "Passwords must match"), DataRequired("New password required"), Length(min=8, message="Length must be at least 8 characters")])

    confirm = PasswordField("Confirm password: ", validators=[DataRequired("Confirmation password required")])