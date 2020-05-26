from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, HiddenField, SelectField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User, Unit
from flask_wtf.file import FileField, FileAllowed, FileRequired

class UploadAvatarForm(FlaskForm):
    image = FileField(label='上传图片', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '只允许 .jpg 或 .png 格式的图片')
    ])
    submit = SubmitField(label='上传')


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('裁剪并更新')

class LoginForm(FlaskForm):
	username = StringField('用户名', validators=[DataRequired()])
	password = PasswordField('密码', validators=[DataRequired()])
	remember_me = BooleanField('记住我')
	submit = SubmitField('登陆')

class RegistrationForm(FlaskForm):
	username = StringField('用户名', validators=[DataRequired()])
	email = StringField('电子邮箱', validators=[DataRequired(), Email()])
	password = PasswordField('密码', validators=[DataRequired()])
	password2 = PasswordField(
		'重复密码', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('注册')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('用户名已经被使用，请换一个不同的用户名。')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('电子邮箱已经被使用，请换一个不同的电子邮箱。')


class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    about_me = TextAreaField('关于我', validators=[Length(min=0, max=140)])
    submit = SubmitField('提交')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('用户名已经被使用，请换一个不同的用户名。')



class UnitForm(FlaskForm):
    name = TextAreaField('姓名', validators=[DataRequired(), Length(min=1, max=40)])
    gender = SelectField("性别", coerce=int, choices=[(0, '男'), (1, "女")])
    age = IntegerField('年龄', validators=[DataRequired()])
    height = FloatField("身高(cm)", validators=[DataRequired()])
    weight = FloatField("体重(kg)", validators=[DataRequired()])
    comment = TextAreaField('备注', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('提交')

class RecordForm(FlaskForm):
    body = TextAreaField('摘要', validators=[DataRequired(), Length(min=1, max=140)])
    complaint = TextAreaField('主诉', validators=[DataRequired(), Length(min=1, max=140)])
    history = TextAreaField('诊断史', validators=[DataRequired(), Length(min=1, max=140)])
    results = TextAreaField('检验结果', validators=[DataRequired(), Length(min=1, max=140)])
    assessment = TextAreaField('医生评估', validators=[DataRequired(), Length(min=1, max=140)])
    plan = TextAreaField('治疗计划', validators=[DataRequired(), Length(min=1, max=140)])
    prescriptions = TextAreaField('处方', validators=[DataRequired(), Length(min=1, max=140)])
    demographics = TextAreaField('人口统计学数据', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('提交')

class AddRecordForm(FlaskForm):
    unit_id = SelectField('病人', coerce=int)
    body = TextAreaField('摘要', validators=[DataRequired(), Length(min=1, max=140)])
    complaint = TextAreaField('主诉', validators=[DataRequired(), Length(min=1, max=140)])
    history = TextAreaField('诊断史', validators=[DataRequired(), Length(min=1, max=140)])
    results = TextAreaField('检验结果', validators=[DataRequired(), Length(min=1, max=140)])
    assessment = TextAreaField('医生评估', validators=[DataRequired(), Length(min=1, max=140)])
    plan = TextAreaField('治疗计划', validators=[DataRequired(), Length(min=1, max=140)])
    prescriptions = TextAreaField('处方', validators=[DataRequired(), Length(min=1, max=140)])
    demographics = TextAreaField('人口统计学数据', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('提交')


class EvaluateForm(FlaskForm):
    gender = SelectField("性别", coerce=int, choices=[(0, '男'), (1, "女")])
    age = IntegerField('年龄', validators=[DataRequired()])
    contact_history = SelectField("是否接触过COVID-19感染者", coerce=int, choices=[(0, '否'), (1, "是")])
    acid_test = SelectField("核酸检测结果", coerce=int, choices=[(0, '阴性'), (1, '阳性')])
    x_ray = SelectField("X光检测结果", coerce=int, choices=[(0, '阴性'), (1, '阳性')])
    wbc = FloatField("WBC(白细胞数量)", validators=[DataRequired()])
    rbc = FloatField("RBC(红细胞数量)", validators=[DataRequired()])
    hgb = FloatField("HGB(血红蛋白数量)", validators=[DataRequired()])
    continent = StringField('洲', validators=[DataRequired()])
    country = StringField('国家', validators=[DataRequired()])
    submit = SubmitField('提交')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('发送重置密码邮件')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '重复密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('重置密码')
