from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

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
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

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
                raise ValidationError('Please use a different username.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')



class MetricForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    username = StringField('Username', validators=[DataRequired()])
    service_name = StringField('Service name', validators=[DataRequired()])
    service_element_name = StringField('Service Element name', validators=[DataRequired()])
    service_level_detail = TextAreaField('Service level detail', validators=[Length( max=4000)])
    target = IntegerField('Target', validators=[DataRequired()])
    service_provider_steward_1 = StringField('Target')
    metric_name = StringField('Target', validators=[DataRequired()])
    metric_description = TextAreaField('Metric description', validators=[Length( max=5000)])
    metric_rationale = TextAreaField('Metric rationale', validators=[Length( max=4000)])
    metric_value_display_format = StringField('Metric value display format')
    threshold_target = StringField('Threshold target')
    threshold_target_rationale = TextAreaField('Threshold target rationale', validators=[Length( max=4000)])
    threshold_target_direction = StringField('Threshold target direction')
    threshold_trigger = IntegerField('Threshold trigger')
    threshold_trigger_rationale = TextAreaField('Threshold trigger rationale', validators=[Length( max=4000)])
    threshold_trigger_direction = StringField('Threshold trigger direction')
    data_source = StringField('Data source')
    data_update_frequency = StringField('Data update frequency')
    metric_owner_primary = StringField('Metric owner primary')
    vantage_control_id = StringField('Vanatge control ID')


    submit = SubmitField('Submit')