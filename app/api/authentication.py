from .errors import unauthorized, forbidden
from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify
from ..models import User   
from . import api                                                          
auth = HTTPBasicAuth() 

@auth.verify_password
def verify_password(email_or_token, password): 
    if email_or_token == '': 
        return False 
    if password == '':
        user = User.verify_auth_token(email_or_token, 3600)
        g.token_used = True 
        g.current_user = user 
        return g.current_user is not None 
    user = User.query.filter_by(email=email_or_token).first() 
    if not user: 
        return False 
    g.token_used = False 
    g.current_user = user 
    return user.verify_password(password)

    
@auth.error_handler
def auth_error(): 
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request(): 
    if not g.current_user.is_anonymous and not g.current_user.confirmed: 
        return forbidden('Unconfirmed account') 
    

@api.route('/tokens/', methods=['POST']) 
def get_token(): 
    if g.current_user.is_anonymous or g.token_used: 
        return unauthorized("Invalid credentials") 
    return jsonify({"token": g.current_user.generate_auth_token(), "expiration": 3600}) 


    
    
        