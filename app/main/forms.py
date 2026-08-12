
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReviewForm(FlaskForm):
    problem = StringField('문제 이름을 적어주세요', validators=[DataRequired()])
    date = DateField('푼 날짜', format='%Y-%m-%d')
    importance = SelectField("중요도", choices = [('1', '*'), ('2', '**'), 
                                               ('3', '***')], coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Submit')


