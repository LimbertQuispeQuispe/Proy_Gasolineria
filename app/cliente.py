# gasolinera/app/cliente.py
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import db
from .models import Venta, Cliente, Estacion, Bomba, Tanque, TipoCombustible
from functools import wraps

# Crea el Blueprint para el módulo de cliente
cliente = Blueprint('cliente', __name__, url_prefix='/cliente')

# Decorador para requerir rol de cliente
def cliente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol.nombre != 'cliente':
            flash('Acceso denegado. Se requiere rol de cliente.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard del cliente
@cliente.route('/')
@login_required
@cliente_required
def dashboard():
    # --- INICIO DEBUG DASHBOARD ---
    print(f"\n--- DEBUG DASHBOARD ---")
    print(f"DASHBOARD: current_user.id = {current_user.id}")
    # --- FIN DEBUG DASHBOARD ---

    # Obtener el cliente asociado al usuario actual
    cliente_asociado = Cliente.query.filter_by(usuario_id=current_user.id).first()
    ventas_cliente_dashboard = [] # Renombrado para evitar confusión con el historial completo
    if not cliente_asociado:
        print("DASHBOARD: NO se encontró cliente asociado.") # DEBUG
        flash('No hay un perfil de cliente asociado a tu cuenta.', 'warning')
    else:
        print(f"DASHBOARD: Cliente asociado encontrado: ID={cliente_asociado.id}, Nombre={cliente_asociado.nombre}") # DEBUG
        # Limita a las últimas 3 ventas para el dashboard
        ventas_cliente_dashboard = Venta.query.filter_by(cliente_id=cliente_asociado.id).order_by(Venta.fecha_hora.desc()).limit(3).all()
        print(f"DASHBOARD: Número de ventas para dashboard: {len(ventas_cliente_dashboard)}") # DEBUG

    # Lógica para obtener el estado de las estaciones y bombas
    estaciones_info = []
    estaciones = Estacion.query.all()

    for estacion in estaciones:
        bombas_info = []
        # Obtener todos los tanques de la estación
        tanques = Tanque.query.filter_by(estacion_id=estacion.id).all()
        # Obtener todas las bombas de esos tanques
        bombas = []
        for tanque in tanques:
            bombas.extend(tanque.bombas)
        # --- ELIMINAR DUPLICADOS ---
        bombas = list({b.id: b for b in bombas}.values())
        # ---------------------------
        for bomba in bombas:
            tanque_asociado = bomba.tanque  # <--- Relación directa
            estado_combustible = 'No Disponible'
            tipo_combustible_nombre = 'N/A'
            nivel_actual_litros = 0
            capacidad_litros = 1

            if tanque_asociado:
                tipo_combustible_nombre = tanque_asociado.tipo_combustible.nombre
                nivel_actual_litros = tanque_asociado.nivel_actual_litros
                capacidad_litros = tanque_asociado.capacidad_litros
                porcentaje_nivel = (nivel_actual_litros / capacidad_litros) * 100 if capacidad_litros else 0

                if nivel_actual_litros > 0 and porcentaje_nivel >= 20:
                    estado_combustible = 'Disponible'
                elif nivel_actual_litros > 0 and porcentaje_nivel < 20:
                    estado_combustible = 'Nivel Bajo'
                else:
                    estado_combustible = 'Agotado'
            else:
                estado_combustible = 'No Asociado/Sin Tanque Disponible'

            bombas_info.append({
                'id': bomba.id,
                'numero_bomba': bomba.numero_bomba,
                'tipo_combustible': tipo_combustible_nombre,
                'estado_combustible': estado_combustible
            })

        estaciones_info.append({
            'id': estacion.id,
            'nombre': estacion.nombre,
            'direccion': estacion.direccion,
            'bombas': bombas_info
        })
    print(f"--- FIN DEBUG DASHBOARD ---\n") # DEBUG

    return render_template('cliente/dashboard.html',
                           ventas_cliente=ventas_cliente_dashboard,
                           cliente_asociado=cliente_asociado, # Asegúrate de pasar esto a la plantilla
                           estaciones_info=estaciones_info,
                           title='Dashboard Cliente')

# Ver historial de compras
@cliente.route('/historial_compras')
@login_required
@cliente_required
def historial_compras():
    # --- INICIO DEBUG HISTORIAL COMPRAS ---
    print(f"\n--- DEBUG HISTORIAL COMPRAS ---")
    print(f"HISTORIAL: current_user.id = {current_user.id}")
    # --- FIN DEBUG HISTORIAL COMPRAS ---

    cliente_asociado = Cliente.query.filter_by(usuario_id=current_user.id).first()
    ventas_cliente = []
    if not cliente_asociado:
        print("HISTORIAL: NO se encontró cliente asociado.") # DEBUG
        flash('No hay un perfil de cliente asociado a tu cuenta.', 'warning')
    else:
        print(f"HISTORIAL: Cliente asociado encontrado: ID={cliente_asociado.id}, Nombre={cliente_asociado.nombre}") # DEBUG
        ventas_cliente = Venta.query.filter_by(cliente_id=cliente_asociado.id).order_by(Venta.fecha_hora.desc()).all()
        print(f"HISTORIAL: Número de ventas para historial: {len(ventas_cliente)}") # DEBUG
    print(f"--- FIN DEBUG HISTORIAL COMPRAS ---\n") # DEBUG

    return render_template('cliente/historial_compras.html',
                           ventas_cliente=ventas_cliente,
                           cliente_asociado=cliente_asociado, # Asegúrate de pasar esto a la plantilla
                           title='Mi Historial de Compras')

# Detalles de una compra específica (opcional, para expandir)
@cliente.route('/compra/<int:venta_id>')
@login_required
@cliente_required
def ver_compra(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    cliente_asociado = Cliente.query.filter_by(usuario_id=current_user.id).first()

    # Asegurarse de que la venta pertenece al cliente logueado
    if not cliente_asociado or venta.cliente_id != cliente_asociado.id:
        flash('No tienes permiso para ver esta compra.', 'danger')
        return redirect(url_for('cliente.historial_compras'))

    return render_template('cliente/ver_compra.html', venta=venta, title='Detalle de Compra')
