
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, DateField, SelectField, TextAreaField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from ..models import User, Role 

class ReviewForm(FlaskForm):
    problem = StringField('문제 이름을 적어주세요', validators=[DataRequired()])
    date = DateField('푼 날짜', format='%Y-%m-%d')
    importance = SelectField("중요도", choices = [('1', '*'), ('2', '**'), 
                                               ('3', '***')], coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Submit')


class EditProfile(FlaskForm):
    """make user level profile editor."""
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    """make administrator level profile editor.""" 
    email = StringField("Email", validators=[DataRequired(), Length(0, 64), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(0,64),\
                                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
                                           'Usernames must have only letters, numbers, dots or '
                                           'underscores')])  
    confirmed = BooleanField("Confirmed") 
    role = SelectField("Role", coerce=int) 
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)]) 
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")


    def __init__(self, user, *args, **kwargs): 
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user 


    def validate_email(self, field): 
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first(): 
            raise ValidationError("Email already registered.")


    def validate_username(self, field):
        if field.data != self.user.username and  User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.") 


class PostForm(FlaskForm):
    body = TextAreaField("what's in Your mind?", validators=[DataRequired()])
    submit = SubmitField("Submit") 



    

