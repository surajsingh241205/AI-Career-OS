from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() 

def create_app():

    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    migrate.init_app(app, db)
    login_manager.init_app(app) 
    login_manager.login_view = 'auth.login'
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(
            int(user_id)
        )
    
    # VERY IMPORTANT
    from routes.auth_routes import auth 
    app.register_blueprint(auth)
    @app.route('/')
    def home():
        return "Career OS Running "

    return app