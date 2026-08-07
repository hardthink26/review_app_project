from flask import Flask, render_template, session, redirect, url_for, flash 
from flask_bootstrap import Bootstrap
from flask_moment import Moment 
from datetime import datetime 
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired
import os 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to think about string' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReviewForm(FlaskForm):
    problem = StringField('문제 이름을 적어주세요', validators=[DataRequired()])
    date = DateField('푼 날짜', format='%Y-%m-%d')
    importance = SelectField("중요도", choices = [('1', '*'), ('2', '**'), ('3', '***')], coerce=int, validators=[DataRequired()])
    

    submit = SubmitField('Submit')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name 

    users = db.relationship('User', backref='role', lazy='dynamic')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True )


    def __repr__(self):
        return '<User %r>' % self.username 

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    problems = db.relationship('Problem', backref='user', lazy='dynamic')

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date) 
    importance = db.Column(db.Integer, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Problem %r>' %self.name


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True 
        session['user'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form = form, name = session.get('user'), 
                           known=session.get('known', False), current_time=datetime.utcnow())

@app.route('/user/<name>', methods=['GET', 'POST'])
def user_page(name):
    review = ReviewForm()
    user = User.query.filter_by(username = name).first()

    if review.validate_on_submit():
        problem = Problem(name = review.problem.data, date = review.date.data, 
                        importance = review.importance.data, user = user)
        db.session.add(problem)
        db.session.commit()
        return redirect(url_for('user_page', name=name))

    problems = user.problems.all()

    return render_template('user_page.html',review=review, name=name , problems=problems, current_time=datetime.utcnow())
    
    
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Problem=Problem)




    