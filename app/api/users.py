from flask import jsonify 
from . import api 
from ..models import User 


@api.route('/users/<int:id>/posts')
def get_user_posts(id): 
    user = User.query.get_or_404(id) 
    return jsonify({ 'posts' : [post.to_json() for post in user.posts.all()] })

@api.route('/users/<int:id>/timeline')
def get_user_followed_posts(id): 
    user = User.query.get_or_404(id)
    return jsonify({ 'posts': [post.to_json() for post in user.followed_posts.all()] }) 


@api.route('/users/<int:id>')
def get_user(id): 
    user = User.query.get_or_404(id) 
    return jsonify(user.to_json()) 