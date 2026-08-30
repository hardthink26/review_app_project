from . import db 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import BadData 
from flask import current_app 
from datetime import datetime 

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer, default = 0) 
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' % self.name 

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None: 
            self.permissions = 0 


    def add_permissions(self,perm):
        if not self.has_permissions(perm):
            self.permissions +=  perm 


    def remove_permissions(self, perm):
        if self.has_permissions(perm):
            self.permissions -= perm 

    def has_permissions(self, perm): 
        return self.permissions & perm == perm 


    def reset_permissions(self):
        self.permissions = 0 


    @staticmethod
    def add_roles(): 
        roles = {
            "User":[Permission.Follow, Permission.Edit, Permission.Comment],
            "Admin":[Permission.Follow, Permission.Edit, Permission.Comment, Permission.Admin] 
        } 
        default_user = 'User' 

        for key in roles.keys():
            role = Role.query.filter_by(name=key).first()
            if role is None: 
                role = Role(name=key) 
            role.reset_permissions() 
            for values in roles[key]:
                role.add_permissions(values)
            role.default = (role.name == default_user) 
            db.session.add(role) 
        db.session.commit() 
            
                




class Permission():
    """define each roles and added to weight."""
    Follow = 1 
    Edit = 2 
    Comment = 4 
    Admin = 8 
    


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True) 
    username = db.Column(db.String(64), unique=True, index=True )
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    problems = db.relationship('Problem', backref='user', lazy='dynamic')
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64)) 
    about_me = db.Column(db.Text()) 
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow) 
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    def __repr__(self):
        return '<User %r>' % self.username 

 

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter 
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    def generate_confirmation_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})


    def confirm(self, token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=3600)
        except BadData: 
            return False 
            
        if data.get('confirm') != self.id:
            return False 
        self.confirmed = True 
        db.session.add(self)
        return True 

    def __init__(self, **kwargs): 
        super(User, self).__init__(**kwargs)
        if self.role is None: 
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name="Admin").first() 
            else: 
                self.role = Role.query.filter_by(default=True).first() 

    


    def can(self, perm): 
        return  self.role is not None and self.role.has_permissions(perm)
      

    def is_administrator(self):
        return self.can(Permission.Admin)  


    def ping(self):
        self.last_seen=datetime.utcnow()
        db.session.add(self)
        db.session.commit() 
        



class AnonymousUser(AnonymousUserMixin): 
    def can(self, permissions):
        return False 


    def is_administrator(self):
        return False 
        
login_manager.anonymous_user = AnonymousUser

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date) 
    importance = db.Column(db.Integer, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Problem %r>' %self.name


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True) 
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
