from modern_paste import app
from modern_paste import db


def initialize_test_app():
    """
    Initializes the test Flask application by setting the app config parameters appropriately.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_TEST_DATABASE_URI']
    return app


def initialize_test_db_env():
    """
    Initialize a test database environment.
    """
    db.create_all()


def destroy_test_db_env():
    """
    Destroys the test database environment, resetting it to a clean state.
    """
    db.session.remove()
    db.drop_all()
