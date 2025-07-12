from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    
    db.init_app(app)

    from .routes import register_routes
    register_routes(app)

    with app.app_context():
        db.create_all()

    return app
