from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, DecimalField, SelectField, IntegerField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length,
    NumberRange, Optional, ValidationError
)
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(3, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Sign Up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')


class EditProfileForm(FlaskForm):
    username = StringField('Full Name', validators=[DataRequired(), Length(3, 64)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Save Changes')


class ListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price (AUD)', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('books', 'Books & Notes'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('furniture', 'Furniture'),
        ('other', 'Other'),
    ])
    stock_quantity = IntegerField('Stock Quantity', validators=[Optional(), NumberRange(min=0)], default=None)
    image = FileField('Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only.')
    ])
    submit = SubmitField('Create Listing')


class EditListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price (AUD)', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('books', 'Books & Notes'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('furniture', 'Furniture'),
        ('other', 'Other'),
    ])
    stock_quantity = IntegerField('Stock Quantity', validators=[Optional(), NumberRange(min=0)], default=None)
    image = FileField('Replace Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only.')
    ])
    show_history = BooleanField('Show edit history publicly')
    submit = SubmitField('Save Changes')


class StoreSetupForm(FlaskForm):
    store_name = StringField('Store Name', validators=[Optional(), Length(max=128)])
    store_address = StringField('Address', validators=[Optional(), Length(max=256)])
    contact_phone = StringField('Phone', validators=[Optional(), Length(max=32)])
    contact_email = StringField('Contact Email', validators=[Optional(), Email(), Length(max=120)])
    submit = SubmitField('Save Store Profile')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    submit = SubmitField('Update Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('That email is already in use.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password')]
    )
    submit = SubmitField('Update Password')


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Delete My Account')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Continue')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Reset Password')


class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        choices=[
            ('5', '5 - Excellent'),
            ('4', '4 - Good'),
            ('3', '3 - Average'),
            ('2', '2 - Poor'),
            ('1', '1 - Very Poor'),
        ],
        validators=[DataRequired()]
    )
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Submit Review')