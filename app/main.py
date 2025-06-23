# gasolinera/app/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# Crea el Blueprint para las rutas principales
main = Blueprint('main', __name__)

# Ruta principal que redirige según el rol del usuario
@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.rol.nombre == 'administrador':
            return redirect(url_for('admin.dashboard'))
        elif current_user.rol.nombre == 'operador':
            return redirect(url_for('operador.dashboard'))
        elif current_user.rol.nombre == 'cliente':
            return redirect(url_for('cliente.dashboard'))
        else:
            # Si el rol no es reconocido o es un caso inesperado, redirige al login
            return redirect(url_for('auth.login'))
    return redirect(url_for('auth.login')) # Redirige al login si no está autenticado
