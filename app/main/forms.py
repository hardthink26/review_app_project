
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length 

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
    

