from datetime import datetime 
from flask import Flask, render_template, session, redirect, url_for, flash, abort, request, current_app, make_response
from . import main 
from flask_bootstrap import Bootstrap
from .forms import  ReviewForm, EditProfile, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import User, Problem, Role, Permission, Post, Comment 
from flask_login import current_user, login_required
from ..decorators import admin_required, permission_required



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
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404) 
    posts = user.posts.order_by(Post.timestamp.desc()).all() 
    return render_template('user_profile.html',user=user, posts=posts, current_time=datetime.utcnow())


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
    page = request.args.get('page', 1, type=int)
    show_followed = False 
    if current_user.is_authenticated: 
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed: 
        query = current_user.followed_posts 
    else: 
        query = Post.query 
    pagination = query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, current_time=datetime.utcnow(),
                            pagination=pagination, posts=posts, show_followed=show_followed)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id): 
    post = Post.query.get_or_404(id)
    form = CommentForm() 
    if form.validate_on_submit(): 
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been published")
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() -1)//current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1 
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
            page=page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=True) 
    comments = pagination.items
    return render_template('post.html', posts=[post],form=form, comments=comments,
                               pagination=pagination, current_time=datetime.utcnow()) 
    


@main.route('/edit/<int:id>', methods=['GET', 'POST']) 
@login_required
def edit(id): 
    post = Post.query.get_or_404(id) 
    if current_user != post.author and not current_user.can(Permission.Admin) : 
        abort(403) 
    form = PostForm() 
    if form.validate_on_submit(): 
        post.body = form.body.data
        db.session.add(post)
        db.session.commit() 
        flash('The Post has been updated.')
    form.body.data = post.body 
    return render_template('edit_post.html', form=form, current_time=datetime.utcnow()) 


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.Follow)
def follow(username): 
    user = User.query.filter_by(username=username).first() 
    if user is None: 
        flash('Invalid access') 
        return redirect(url_for('.index'))
    if current_user.is_following(user): 
        flash('already following') 
        return redirect(url_for('.user_profile', username=username)) 
    current_user.follow(user) 
    db.session.commit() 
    flash(f"You follow {username}!") 
    return redirect(url_for('.user_profile', username=username)) 


@main.route('/unfollow/<username>') 
@login_required
@permission_required(Permission.Follow)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None: 
        flash('Invalid access')
        return redirect(url_for('.index'))
    if not current_user.is_following(user): 
        flash('already unfollow') 
        return redirect(url_for('.user_profile', username=username)) 
    current_user.unfollow(user) 
    db.session.commit() 
    return redirect(url_for('.user_profile', username=username))
    

@main.route('/followers/<username>')
def followers(username): 
    user = User.query.filter_by(username=username).first()
    if user is None: 
        flash('Invalid user.') 
        return redirect(url_for('.index')) 
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False) 
    follows = [{'user':item.follower, 'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html', follows=follows,user=user, title="Followers of",\
                            endpoint='.followers',current_time=datetime.utcnow()) 


@main.route('/all')
@login_required
def show_all(): 
    resp = make_response(redirect(url_for('.index'))) 
    resp.set_cookie('show_followed','', max_age = 30*24*60*60) 
    return resp


@main.route('/followed')
@login_required
def show_followed(): 
    resp = make_response(redirect(url_for('.index'))) 
    resp.set_cookie('show_followed',value='1', max_age=30*24*60*60)
    return resp 



        
        
    