from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from os import environ, path
from dotenv import load_dotenv

# Get .env file and load config variables
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../.env'))


class Config:
    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Create database
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Import views
        from api.views import views as view_routes
        from api.auth import auth as auth_routes
        # Register views
        app.register_blueprint(view_routes, url_prefix='/')
        app.register_blueprint(auth_routes, url_prefix='/')

        from api.views import error403 as error403_route
        from api.views import error404 as error404_route
        from api.views import error500 as error500_route
        app.register_error_handler(401, error403_route)
        app.register_error_handler(403, error403_route)
        app.register_error_handler(404, error404_route)
        app.register_error_handler(500, error500_route)

        # Create database tables for data models in models.py
        db.create_all()

        # Import user model and initialise login manager
        from api.models import User
        login_manager = LoginManager()
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))

        return app


app = create_app()

if __name__ == '__main__':
    app.run()
