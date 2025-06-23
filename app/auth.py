# gasolinera/app/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from .models import Usuario, Rol

# Crea el Blueprint para la autenticación
auth = Blueprint('auth', __name__)

# Función para cargar el usuario (requerido por Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta para el login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Si el usuario ya está autenticado, redirige a la página principal según su rol
        if current_user.rol.nombre == 'administrador':
            return redirect(url_for('admin.dashboard'))
        elif current_user.rol.nombre == 'operador':
            return redirect(url_for('operador.dashboard'))
        elif current_user.rol.nombre == 'cliente':
            return redirect(url_for('cliente.dashboard'))
        else:
            return redirect(url_for('main.index')) # Redirige a una página por defecto si el rol no es reconocido

    if request.method == 'POST':
        username = request.form.get('username') # Obtiene el nombre de usuario del formulario
        password = request.form.get('password') # Obtiene la contraseña del formulario
        remember = True if request.form.get('remember') else False # Verifica si se debe recordar la sesión

        user = Usuario.query.filter_by(username=username).first() # Busca el usuario por nombre de usuario

        # Verifica si el usuario existe y la contraseña es correcta
        if not user or not user.check_password(password):
            flash('Por favor, verifica tus credenciales e inténtalo de nuevo.', 'danger') # Mensaje de error
            return redirect(url_for('auth.login')) # Redirige de nuevo al login

        # Inicia sesión para el usuario
        login_user(user, remember=remember)

        # Redirige según el rol del usuario
        if user.rol.nombre == 'administrador':
            return redirect(url_for('admin.dashboard'))
        elif user.rol.nombre == 'operador':
            return redirect(url_for('operador.dashboard'))
        elif user.rol.nombre == 'cliente':
            return redirect(url_for('cliente.dashboard'))
        else:
            flash('Rol de usuario no reconocido. Redirigiendo a la página principal.', 'warning')
            return redirect(url_for('main.index'))

    return render_template('login.html', title='Login') # Renderiza la plantilla de login

# Ruta para el logout
@auth.route('/logout')
@login_required # Requiere que el usuario esté logueado
def logout():
    logout_user() # Cierra la sesión del usuario
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth.login')) # Redirige al login
