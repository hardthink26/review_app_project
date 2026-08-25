from datetime import datetime 
from flask import Flask, render_template, session, redirect, url_for, flash
from . import main 
from flask_bootstrap import Bootstrap
from .forms import  ReviewForm, EditProfile
from .. import db
from ..models import User, Problem
from flask_login import current_user, login_required


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


@main.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html',user=user, current_time=datetime.utcnow())


@main.route('/user-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit() 
        flash('Your profile has been updated.')
        return redirect(url_for('.user_profile', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me 
    return render_template('edit_profile.html', form=form, current_time=datetime.utcnow()) 


    
        
        
        
    