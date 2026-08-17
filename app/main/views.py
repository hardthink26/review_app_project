from datetime import datetime 
from flask import Flask, render_template, session, redirect, url_for, flash
from . import main 
from flask_bootstrap import Bootstrap
from .forms import  ReviewForm
from .. import db
from ..models import User, Problem
from flask_login import current_user 


@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@main.route('/user', methods=['GET', 'POST'])
def user_page():
    review = ReviewForm()
    user = current_user

    if review.validate_on_submit():
        problem = Problem(name = review.problem.data, date = review.date.data, 
                        importance = review.importance.data, user = user)
        db.session.add(problem)
        db.session.commit()
        return redirect(url_for('.user_page'))

    problems = user.problems.all()

    return render_template('user_page.html',review=review, problems=problems, 
                           current_time=datetime.utcnow())

    