from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from cyberbullying.modelsDB import User


# Register form
class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already taken. Please choose another email.')


# Login form
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


# Update profile form
class UpdateProfileForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already taken. Please choose another username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already taken. Please choose another email.')


# Text input form
class UserInputForm(FlaskForm):
    user_text = StringField(validators=[DataRequired()])
    submit = SubmitField('Check Cyberbully (Text)')


# File input form
class FileInputForm(FlaskForm):
    csv_file = FileField('Upload File', validators=[FileAllowed(['csv'])])
    submit = SubmitField('Check Cyberbully (File)')


# Twitter input form (keyword)
class TwitterInputForm(FlaskForm):
    tweet_search = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')


# Twitter input form (Twitter User ID)
class TwitterUserForm(FlaskForm):
    user_search = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')
