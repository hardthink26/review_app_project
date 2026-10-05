from flask import jsonify 
from . import api 
from ..models import User, Post 

@api.route('/posts/<int:id>/comments')
def get_post_comments(id): 
    post = Post.query.get_or_404(id)
    comments = post.comments.all() 
    return jsonify({'comments' : [comment.to_json() for comment in comments] }) 

    