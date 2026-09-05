import unittest, pytest 
from app.models import User, Permission, Role, AnonymousUser
from config import Config
        
@pytest.mark.usefixtures("initialize_db")
class UserModelTestCase(unittest.TestCase):
    
    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)


    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password 


    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))


    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)


    def test_user_has_user_role(self):
        Role.add_roles()
        u = User(username="jo", email='jo@example.com')
        self.assertTrue(u.can(Permission.Follow))
        self.assertTrue(u.can(Permission.Edit))
        self.assertTrue(u.can(Permission.Comment))
        self.assertFalse(u.can(Permission.Admin))


    def test_user_is_admin(self):
        Role.add_roles()
        u = User(username="joe", email=Config.FLASKY_ADMIN)
        self.assertTrue(u.is_administrator())


    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.Follow))
        self.assertFalse(u.can(Permission.Edit))
        self.assertFalse(u.can(Permission.Comment))
        self.assertFalse(u.can(Permission.Admin))
        
