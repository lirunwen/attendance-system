from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, BooleanField, TimeField
from wtforms.validators import DataRequired, Optional, EqualTo, Length

class ShiftForm(FlaskForm):
    name = StringField('班次名称', validators=[DataRequired()])
    shift_start = StringField('上班时间', validators=[DataRequired()], render_kw={'placeholder': '09:00'})
    shift_end = StringField('下班时间', validators=[DataRequired()], render_kw={'placeholder': '18:00'})
    late_minutes = IntegerField('迟到宽容(分钟)', default=15)
    early_leave_minutes = IntegerField('早退宽容(分钟)', default=15)
    submit = SubmitField('保存')

class LocationForm(FlaskForm):
    name = StringField('地点名称', validators=[DataRequired()])
    keywords = StringField('匹配关键词', render_kw={'placeholder': '主楼,办公楼,大厅（逗号分隔）'})
    submit = SubmitField('保存')

class EmployeeForm(FlaskForm):
    employee_id = StringField('工号', validators=[DataRequired()])
    name = StringField('姓名', validators=[DataRequired()])
    shift_id = SelectField('默认班次', coerce=int, validators=[Optional()])
    submit = SubmitField('保存')

class AttendanceRemarkForm(FlaskForm):
    clerk_remark = TextAreaField('文员备注', render_kw={'rows': 3})
    submit = SubmitField('保存')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=32)])
    display_name = StringField('显示名称', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=4)])
    confirm = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('注册')
