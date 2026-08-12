from datetime import datetime 
from flask import Flask, render_template, session, redirect, url_for, flash
from . import main 
from flask_bootstrap import Bootstrap
from .forms import NameForm, ReviewForm
from .. import db
from ..models import User, Problem

@main.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('.index'))
    return render_template('index.html', form = form, name = session.get('user'), 
                           known=session.get('known', False), current_time=datetime.utcnow())

@main.route('/user/<name>', methods=['GET', 'POST'])
def user_page(name):
    review = ReviewForm()
    user = User.query.filter_by(username = name).first()

    if review.validate_on_submit():
        problem = Problem(name = review.problem.data, date = review.date.data, 
                        importance = review.importance.data, user = user)
        db.session.add(problem)
        db.session.commit()
        return redirect(url_for('.user_page', name=name))

    problems = user.problems.all()

    return render_template('user_page.html',review=review, name=name , problems=problems, 
                           current_time=datetime.utcnow())
    