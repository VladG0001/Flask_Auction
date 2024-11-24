from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    photo = FileField('Photo')
    submit = SubmitField('Register')

class LotForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = FileField('Image')
    category = SelectField('Category', choices=[
        ('Трофеї УВВ', 'Трофеї УВВ'), ('До 1700', 'До 1700'), ('До 1918', 'До 1918'),
        ('До 1945', 'До 1945'), ('До 1991', 'До 1991'), ('Репліки', 'Репліки'),
        ('Сувеніри', 'Сувеніри'), ('Зброя', 'Зброя')
    ])
    submit = SubmitField('Create Lot')
