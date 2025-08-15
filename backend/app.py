from flask import Flask
from .extensions import db, migrate
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .views.admin import admin_bp
from .views.auth import auth_bp
from .views.users import users_bp

def create_app():

    app = Flask(__name__)

    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    return app


import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
