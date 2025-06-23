# gasolinera/app/operador.py
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import db
# Asegúrate de importar Estacion aquí
from .models import Venta, DetalleVenta, Pago, Tanque, Bomba, TipoCombustible, ReporteAlerta, Cliente, Proveedor, PagoReabastecimiento, Reabastecimiento, Estacion
from .forms import VentaForm, ReabastecimientoForm, ClienteForm as OperadorClienteForm
from functools import wraps
import datetime

# Crea el Blueprint para el módulo de operador
operador = Blueprint('operador', __name__, url_prefix='/operador')

# Decorador para requerir rol de operador
def operador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol.nombre != 'operador':
            flash('Acceso denegado. Se requiere rol de operador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard del operador
@operador.route('/')
@login_required
@operador_required
def dashboard():
    ventas_recientes = Venta.query.order_by(Venta.fecha_hora.desc()).limit(5).all()
    # Agrupa tanques por estación y ordena
    estaciones = Estacion.query.order_by(Estacion.nombre).all()
    tanques_por_estacion = []
    for estacion in estaciones:
        tanques = Tanque.query.filter_by(estacion_id=estacion.id).order_by(Tanque.id).all()
        if tanques:
            tanques_por_estacion.append((estacion, tanques))
    alertas_pendientes = ReporteAlerta.query.order_by(ReporteAlerta.fecha_hora.desc()).limit(5).all()
    return render_template(
        'operador/dashboard.html',
        ventas_recientes=ventas_recientes,
        tanques_por_estacion=tanques_por_estacion,
        alertas_pendientes=alertas_pendientes,
        title='Dashboard Operador'
    )

# Registrar Venta
@operador.route('/ventas/add', methods=['GET', 'POST'])
@login_required
@operador_required
def add_venta():
    form = VentaForm()

    # --- Construir opciones de bomba agrupadas por estación con tipo de combustible ---
    estaciones_con_bombas_agrupadas = [] # Para el renderizado manual en la plantilla
    flat_bombas_choices = [] # Para la validación interna de WTForms

    estaciones = Estacion.query.all()

    for estacion in estaciones:
        bombas_en_estacion = []
        tanques = Tanque.query.filter_by(estacion_id=estacion.id).all()
        for tanque in tanques:
            bombas_en_estacion.extend(tanque.bombas)
        # Elimina bombas repetidas usando un diccionario por id
        bombas_unicas = {b.id: b for b in bombas_en_estacion}.values()
        bombas_para_estacion_agrupadas = []
        for bomba in bombas_unicas:
            tipo_combustible_bomba = bomba.tanque.tipo_combustible.nombre if bomba.tanque and bomba.tanque.tipo_combustible else "Desconocido"
            bombas_para_estacion_agrupadas.append(
                (bomba.id, f"Bomba {bomba.numero_bomba} - {tipo_combustible_bomba}")
            )
            flat_bombas_choices.append((bomba.id, f"Bomba {bomba.numero_bomba} - {tipo_combustible_bomba}"))
        estaciones_con_bombas_agrupadas.append((estacion.nombre, bombas_para_estacion_agrupadas))
    
    # ¡IMPORTANTE! Asignar la lista PLANA de choices a form.bomba_id.choices
    # Esto es CRUCIAL para que WTForms valide el formulario correctamente.
    form.bomba_id.choices = flat_bombas_choices


    form.cliente_id.choices = [(c.id, c.nombre + ' ' + c.apellido) for c in Cliente.query.all()]
    form.cliente_id.choices.insert(0, (0, 'Público General'))

    if form.validate_on_submit():
        litros_vendidos = float(form.litros_vendidos.data)
        # form.bomba_id.data ya estará correctamente coaccionado por la función _bomba_coerce en forms.py
        bomba_id = form.bomba_id.data 
        
        cliente_id = form.cliente_id.data if form.cliente_id.data != 0 else None

        bomba = Bomba.query.get(bomba_id)
        if not bomba:
            flash('Bomba no encontrada.', 'danger')
            return redirect(url_for('operador.add_venta'))

        precio_por_litro = 14.00
        total_pagado = litros_vendidos * precio_por_litro

        venta = Venta(
            litros_vendidos=litros_vendidos,
            total_pagado=total_pagado,
            bomba_id=bomba_id,
            cliente_id=cliente_id,
            fecha_hora=datetime.datetime.now()
        )
        db.session.add(venta)
        db.session.flush()

        # Suponiendo que venta es el objeto Venta recién creado
        detalle_existente = DetalleVenta.query.filter_by(venta_id=venta.id).first()
        if not detalle_existente:
            detalle = DetalleVenta(venta_id=venta.id, observaciones=form.observaciones.data)
            db.session.add(detalle)

        pago_existente = Pago.query.filter_by(venta_id=venta.id).first()
        if not pago_existente:
            pago = Pago(
                venta_id=venta.id,
                monto=total_pagado,
                metodo_pago=form.metodo_pago.data,
                fecha_pago=datetime.datetime.now()
            )
            db.session.add(pago)

        tanque_afectado = bomba.tanque  # <--- Cambiado aquí
        if tanque_afectado and tanque_afectado.nivel_actual_litros >= litros_vendidos:
            tanque_afectado.nivel_actual_litros -= litros_vendidos

            alerta_mensaje = None
            tipo_alerta = None

            if tanque_afectado.nivel_actual_litros <= 0:
                alerta_mensaje = f'¡URGENTE! La estación <strong>{tanque_afectado.estacion.nombre}</strong> no tiene combustible ({tanque_afectado.tipo_combustible.nombre}) en el <strong>tanque {tanque_afectado.id}</strong>. Necesita reabastecimiento inmediato.'
                tipo_alerta = 'Sin Combustible'
            elif tanque_afectado.nivel_actual_litros < tanque_afectado.capacidad_litros * 0.2:
                alerta_mensaje = f'AVISO: La estación <strong>{tanque_afectado.estacion.nombre}</strong> tiene bajo nivel de {tanque_afectado.tipo_combustible.nombre} en el <strong>tanque {tanque_afectado.id}</strong>. Necesita reabastecimiento.'
                tipo_alerta = 'Bajo Nivel'

            if alerta_mensaje and tipo_alerta:
                alerta = ReporteAlerta(
                    tipo_alerta=tipo_alerta,
                    mensaje=alerta_mensaje,
                    tanque_id=tanque_afectado.id
                )
                db.session.add(alerta)
        else:
            flash('No hay suficiente combustible en el tanque asociado o la bomba no tiene un tanque asignado correctamente.', 'danger')
            db.session.rollback()
            return redirect(url_for('operador.add_venta'))

        db.session.commit()
        flash(f'Venta registrada exitosamente! Total a pagar: {total_pagado:.2f} Bs.', 'success')
        return redirect(url_for('operador.manage_ventas'))
    return render_template('operador/add_venta.html',
                           form=form,
                           estaciones_con_bombas=estaciones_con_bombas_agrupadas,
                           title='Registrar Venta')

# Listar Ventas
@operador.route('/ventas')
@login_required
@operador_required
def manage_ventas():
    ventas = Venta.query.order_by(Venta.fecha_hora.desc()).all()
    return render_template('operador/ventas.html', ventas=ventas, title='Gestión de Ventas')

# Gestión de Reabastecimiento
@operador.route('/reabastecimientos/add', methods=['GET', 'POST'])
@login_required
@operador_required
def add_reabastecimiento():
    form = ReabastecimientoForm()
    form.tanque_id.choices = [(t.id, f'{t.id} - {t.estacion.nombre} - {t.tipo_combustible.nombre}') for t in Tanque.query.all()]
    form.proveedor_id.choices = [(p.id, p.nombre) for p in Proveedor.query.all()]

    if form.validate_on_submit():
        tanque = Tanque.query.get(form.tanque_id.data)
        if not tanque:
            flash('Tanque no encontrado.', 'danger')
            return redirect(url_for('operador.add_reabastecimiento'))

        litros_reabastecidos = float(form.litros_reabastecidos.data)
        costo_total = float(form.costo_total.data)

        tanque.nivel_actual_litros += litros_reabastecidos
        if tanque.nivel_actual_litros > tanque.capacidad_litros:
            flash('El reabastecimiento excede la capacidad del tanque. Ajustando al máximo.', 'warning')
            tanque.nivel_actual_litros = tanque.capacidad_litros

        reabastecimiento = Reabastecimiento(
            litros_reabastecidos=litros_reabastecidos,
            costo_total=costo_total,
            tanque_id=form.tanque_id.data,
            proveedor_id=form.proveedor_id.data,
            estacion_id=tanque.estacion_id,
            fecha_hora=datetime.datetime.now()
        )
        db.session.add(reabastecimiento)
        db.session.flush()

        pago_existente = PagoReabastecimiento.query.filter_by(reabastecimiento_id=reabastecimiento.id).first()
        if not pago_existente:
            pago_reabastecimiento = PagoReabastecimiento(
                reabastecimiento_id=reabastecimiento.id,
                monto=costo_total,
                fecha_pago=datetime.datetime.now()
            )
            db.session.add(pago_reabastecimiento)

        db.session.commit()
        flash('Reabastecimiento registrado exitosamente!', 'success')
        return redirect(url_for('operador.manage_reabastecimientos'))
    return render_template('operador/add_reabastecimiento.html', form=form, title='Registrar Reabastecimiento')

@operador.route('/reabastecimientos')
@login_required
@operador_required
def manage_reabastecimientos():
    reabastecimientos = Reabastecimiento.query.order_by(Reabastecimiento.fecha_hora.desc()).all()
    return render_template('operador/reabastecimientos.html', reabastecimientos=reabastecimientos, title='Gestión de Reabastecimientos')

# Clientes (Operador puede añadir clientes para ventas, pero no gestionar usuarios)
@operador.route('/clientes/add', methods=['GET', 'POST'])
@login_required
@operador_required
def add_cliente_operador():
    form = OperadorClienteForm()
    # Si tienes un campo SelectField que no usas aquí, asígnale choices vacíos
    if hasattr(form, 'usuario_id'):
        form.usuario_id.choices = []

    # No se permite asignar usuario_id aquí, solo se crea el cliente
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            nit_ci=form.nit_ci.data if form.nit_ci.data else None
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente añadido exitosamente!', 'success')
        return redirect(url_for('operador.manage_clientes'))
    return render_template('operador/add_cliente.html', form=form, title='Añadir Cliente (Operador)')

@operador.route('/clientes')
@login_required
@operador_required
def manage_clientes():
    clientes = Cliente.query.all()
    return render_template('operador/clientes.html', clientes=clientes, title='Clientes Registrados')
