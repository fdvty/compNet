from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, HiddenField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User, Unit
from flask_wtf.file import FileField, FileAllowed, FileRequired

class UploadAvatarForm(FlaskForm):
    image = FileField(label='Upload Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'The file format should be .jpg or .png.')
    ])
    submit = SubmitField(label='Upload')


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('Crop and Update')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username has already been used. Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email has already been registered. Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username has already been used. Please use a different username.')



class UnitForm(FlaskForm):
    name = TextAreaField('Name', validators=[DataRequired(), Length(min=1, max=40)])
    gender = SelectField("Gender", coerce=int, choices=[(0, 'M'), (1, "F")])
    age = IntegerField('Age', validators=[DataRequired()])
    height = FloatField("Height(cm)", validators=[DataRequired()])
    weight = FloatField("Weight(kg)", validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class RecordForm(FlaskForm):
    body = TextAreaField('Abstract', validators=[DataRequired(), Length(min=1, max=140)])
    complaint = TextAreaField('Chief Complaint', validators=[DataRequired(), Length(min=1, max=140)])
    history = TextAreaField('Medical History', validators=[DataRequired(), Length(min=1, max=140)])
    results = TextAreaField('Examination Results', validators=[DataRequired(), Length(min=1, max=140)])
    assessment = TextAreaField('Doctor\'s Assessment', validators=[DataRequired(), Length(min=1, max=140)])
    plan = TextAreaField('Treatment Plans', validators=[DataRequired(), Length(min=1, max=140)])
    prescriptions = TextAreaField('Prescriptions', validators=[DataRequired(), Length(min=1, max=140)])
    demographics = TextAreaField('Demographics', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class AddRecordForm(FlaskForm):
    unit_id = SelectField('Patient', coerce=int)
    body = TextAreaField('Abstract', validators=[DataRequired(), Length(min=1, max=140)])
    complaint = TextAreaField('Chief Complaint', validators=[DataRequired(), Length(min=1, max=140)])
    history = TextAreaField('Medical History', validators=[DataRequired(), Length(min=1, max=140)])
    results = TextAreaField('Examination Results', validators=[DataRequired(), Length(min=1, max=140)])
    assessment = TextAreaField('Doctor\'s Assessment', validators=[DataRequired(), Length(min=1, max=140)])
    plan = TextAreaField('Treatment Plans', validators=[DataRequired(), Length(min=1, max=140)])
    prescriptions = TextAreaField('Prescriptions', validators=[DataRequired(), Length(min=1, max=140)])
    demographics = TextAreaField('Demographics', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


class EvaluateForm(FlaskForm):
    gender = SelectField("Gender", coerce=int, choices=[(0, 'M'), (1, "F")])
    age = IntegerField('Age', validators=[DataRequired()])
    contact_history = SelectField("Contact with Pneumonia Patients", coerce=int, choices=[(0, 'N'), (1, "Y")])
    acid_test = SelectField("Nucleci Acid Testing", coerce=int, choices=[(0, 'Negative'), (1, 'Positive')])
    x_ray = SelectField("X-ray Testing", coerce=int, choices=[(0, 'Negative'), (1, 'Positive')])
    wbc = FloatField("WBC(White Blood Cells)", validators=[DataRequired()])
    rbc = FloatField("RBC(Red Blood Cells)", validators=[DataRequired()])
    hgb = FloatField("HGB(Hemoglobin)", validators=[DataRequired()])
    continent = StringField('Continent', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
