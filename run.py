# gasolinera/run.py
import os
import click # Importa click para click.echo()
from app import create_app, db
from app.models import Estacion, Tanque, Bomba, TipoCombustible, Venta, DetalleVenta, Pago, Usuario, Rol, Cliente, ReporteAlerta, Reabastecimiento, Proveedor, PagoReabastecimiento
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext # Importa with_appcontext de flask.cli
from flask_migrate import Migrate

# Crea la instancia de la aplicación Flask
app = create_app()
migrate = Migrate(app, db)

# Define un comando personalizado de Flask CLI para inicializar la base de datos
@app.cli.command('init-db')
@with_appcontext # ¡Usamos el decorador directamente de flask.cli!
def init_db_command():
    """Crea las tablas de la base de datos e inserta datos iniciales."""
    db.create_all() # Crea todas las tablas
    click.echo('Base de datos inicializada.')

    # Inicializa roles si no existen
    admin_role = Rol.query.filter_by(nombre='administrador').first()
    operador_role = Rol.query.filter_by(nombre='operador').first()
    cliente_role = Rol.query.filter_by(nombre='cliente').first()

    if not admin_role:
        admin_role = Rol(nombre='administrador')
        db.session.add(admin_role)
        click.echo('Rol "administrador" creado.')
    if not operador_role:
        operador_role = Rol(nombre='operador')
        db.session.add(operador_role)
        click.echo('Rol "operador" creado.')
    if not cliente_role:
        cliente_role = Rol(nombre='cliente')
        db.session.add(cliente_role)
        click.echo('Rol "cliente" creado.')
    db.session.commit()
    click.echo('Roles verificados/creados.')

    # Inicializa usuarios si no existen
    if not Usuario.query.filter_by(username='admin').first():
        admin_user = Usuario(
            username='admin',
            password_hash=generate_password_hash('adminpass'), # Contraseña encriptada para el administrador
            rol_id=admin_role.id
        )
        db.session.add(admin_user)
        click.echo('Usuario "admin" creado.')

    if not Usuario.query.filter_by(username='operador1').first():
        operador_user = Usuario(
            username='operador1',
            password_hash=generate_password_hash('operadorpass'), # Contraseña encriptada para el operador
            rol_id=operador_role.id
        )
        db.session.add(operador_user)
        click.echo('Usuario "operador1" creado.')

    if not Usuario.query.filter_by(username='cliente1').first():
        cliente_user = Usuario(
            username='cliente1',
            password_hash=generate_password_hash('clientepass'), # Contraseña encriptada para el cliente
            rol_id=cliente_role.id
        )
        db.session.add(cliente_user)
        click.echo('Usuario "cliente1" creado.')
    db.session.commit()
    click.echo('Usuarios verificados/creados.')
    click.echo('¡Base de datos lista para usar!')

if __name__ == '__main__':
    # Cuando ejecutas 'python run.py', Flask ejecuta la aplicación directamente.
    # Los comandos CLI (como 'flask init-db') se ejecutan con 'flask command_name'.
    app.run(debug=True) # Modo debug activado para desarrollo
