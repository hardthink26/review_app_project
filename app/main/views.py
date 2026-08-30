from datetime import datetime 
from flask import Flask, render_template, session, redirect, url_for, flash
from . import main 
from flask_bootstrap import Bootstrap
from .forms import  ReviewForm, EditProfile, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Problem, Role, Permission, Post 
from flask_login import current_user, login_required
from ..decorators import admin_required



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


@main.route('/admin-edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit(id): 
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user) 
    if form.validate_on_submit():
        user.email = form.email.data
        user.name = form.name.data 
        user.username = form.username.data 
        user.location = form.location.data 
        user.about_me = form.about_me.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data) 
        flash("You have been updated")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.user_profile', username=user.username)) 
    form.email.data = user.email 
    form.name.data = user.name 
    form.username.data = user.username 
    form.location.data = user.location 
    form.about_me.data = user.about_me 
    form.confirmed.data = user.confirmed 
    form.role.data = user.role_id 
    return render_template('edit_profile.html', form=form, user=user, current_time=datetime.utcnow()) 


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.Edit) and form.validate_on_submit():
        post =  Post(body=form.body.data, author=current_user._get_current_object())#안 되는지 체크 
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    #작성한 포스트를 나열해야함 
    posts = Post.query.order_by(Post.timestamp.desc()).all() 
    return render_template('index.html', form=form, current_time=datetime.utcnow(), posts=posts) 




    
        
        
        
    