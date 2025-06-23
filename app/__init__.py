# gasolinera/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from flask_moment import Moment # Importa Flask-Moment aquí

# Inicializa la base de datos
db = SQLAlchemy()
# Inicializa el manejador de login
login_manager = LoginManager()

def create_app():
    # Crea la instancia de la aplicación Flask
    app = Flask(__name__)

    # Configuración de la aplicación
    app.config['SECRET_KEY'] = os.urandom(24) # Clave secreta para seguridad de sesiones
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'gestor_gasolina.db') # Ruta de la base de datos SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Deshabilita el seguimiento de modificaciones de SQLAlchemy

    # Asegura que la carpeta 'instance' exista
    os.makedirs(app.instance_path, exist_ok=True)

    # Inicializa la base de datos con la aplicación
    db.init_app(app)
    # Inicializa el manejador de login con la aplicación
    login_manager.init_app(app)
    # Inicializa Flask-Moment con la aplicación
    moment = Moment(app) # ¡Importante! Inicializa Moment pasando 'app'

    # Importa los modelos para que SQLAlchemy los detecte
    from . import models

    # Importa y registra los Blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .operador import operador as operador_blueprint
    app.register_blueprint(operador_blueprint)

    from .cliente import cliente as cliente_blueprint
    app.register_blueprint(cliente_blueprint)

    return app
