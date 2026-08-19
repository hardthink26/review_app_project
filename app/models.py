from . import db 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin 
from . import login_manager
from itsdangerous.url_safe import URLSafeTimedSerializer
from itsdangerous.exc import BadData 
from flask import current_app 

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


    def add_permissions(self,weight): 
        permission = getattr(Permission, weight) 

        if (self.permissions & permission) != permission: 
            self.permissions = self.permissions | permission 


    def remove_permissions(self, weight): 
        permission = getattr(Permission, weight) 

        if self.permissions & permission == permission: 
            self.permissions = self.permissions & ~permission 


    def has_permissions(self, weight):  
        permission = getattr(Permission, weight)

        if self.permissions & permission == permission: 
            return True 
        else:
            return False 


    def reset_permissions(self):
        self.permissions = 0 


    @staticmethod
    def add_roles(): 
        roles = {
            "User":["Follow", "Edit", "Comment"],
            "Admin":["Follow", "Edit", "Comment", "Admin"] 
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

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date) 
    importance = db.Column(db.Integer, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Problem %r>' %self.name

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


