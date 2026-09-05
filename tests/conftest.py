import pytest 
from app import create_app, db 

def pytest_addoption(parser): 
    parser.addoption(
        "--func-db", 
        action="store_true", 
        help="Run database fixture with function scope"
    ) 


def db_scope(fixture_name, config): 
    if config.getoption("--func-db"): 
        return "function"
    return "class" 

@pytest.fixture(scope="class") 
def user_db(): 
    app = create_app('testing') 
    with app.app_context(): 
        db.create_all() 
        yield db 
        db.drop_all() 


@pytest.fixture(scope=db_scope)
def initialize_db(user_db): 
    db.session.remove()
    db.drop_all()
    db.create_all() 
    yield user_db