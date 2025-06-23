# gasolinera/app/admin.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, make_response
from flask_login import login_required, current_user
from . import db
from .models import Estacion, Tanque, Bomba, TipoCombustible, Reabastecimiento, Proveedor, Usuario, Rol, Cliente, Venta, ReporteAlerta # Agregamos Venta y ReporteAlerta
from .forms import EstacionForm, TipoCombustibleForm, TanqueForm, BombaForm, ProveedorForm, UsuarioForm, ClienteForm
from functools import wraps
from werkzeug.security import generate_password_hash # Importa para manejar contraseñas
from weasyprint import HTML
from datetime import datetime

# Crea el Blueprint para el módulo de administración
admin = Blueprint('admin', __name__, url_prefix='/admin')

# Decorador para requerir rol de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol.nombre != 'administrador':
            flash('Acceso denegado. Se requiere rol de administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard del administrador
@admin.route('/')
@login_required
@admin_required
def dashboard():
    # Obtiene el número de estaciones, tanques, ventas, etc. para mostrar en el dashboard
    num_estaciones = Estacion.query.count()
    num_tanques = Tanque.query.count()
    num_bombas = Bomba.query.count()
    num_tipos_combustible = TipoCombustible.query.count()
    num_usuarios = Usuario.query.count()
    num_clientes = Cliente.query.count()
    num_proveedores = Proveedor.query.count()
    return render_template('admin/dashboard.html',
                           num_estaciones=num_estaciones,
                           num_tanques=num_tanques,
                           num_bombas=num_bombas,
                           num_tipos_combustible=num_tipos_combustible,
                           num_usuarios=num_usuarios,
                           num_clientes=num_clientes,
                           num_proveedores=num_proveedores,
                           title='Dashboard Administrador')

# Gestión de Estaciones
@admin.route('/estaciones')
@login_required
@admin_required
def manage_estaciones():
    estaciones = Estacion.query.all()
    return render_template('admin/estaciones.html', estaciones=estaciones, title='Gestión de Estaciones')

@admin.route('/estaciones/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_estacion():
    form = EstacionForm()
    if form.validate_on_submit():
        estacion = Estacion(nombre=form.nombre.data, direccion=form.direccion.data)
        db.session.add(estacion)
        db.session.commit()
        flash('Estación añadida exitosamente!', 'success')
        return redirect(url_for('admin.manage_estaciones'))
    return render_template('admin/add_edit_estacion.html', form=form, title='Añadir Estación')

@admin.route('/estaciones/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_estacion(id):
    estacion = Estacion.query.get_or_404(id)
    form = EstacionForm(obj=estacion)
    if form.validate_on_submit():
        estacion.nombre = form.nombre.data
        estacion.direccion = form.direccion.data
        db.session.commit()
        flash('Estación actualizada exitosamente!', 'success')
        return redirect(url_for('admin.manage_estaciones'))
    return render_template('admin/add_edit_estacion.html', form=form, estacion=estacion, title='Editar Estación')

@admin.route('/estaciones/delete/<int:id>')
@login_required
@admin_required
def delete_estacion(id):
    estacion = Estacion.query.get_or_404(id)
    db.session.delete(estacion)
    db.session.commit()
    flash('Estación eliminada exitosamente!', 'success')
    return redirect(url_for('admin.manage_estaciones'))

# Gestión de Tipos de Combustible
@admin.route('/tipos_combustible')
@login_required
@admin_required
def manage_tipos_combustible():
    tipos_combustible = TipoCombustible.query.all()
    return render_template('admin/tipos_combustible.html', tipos_combustible=tipos_combustible, title='Gestión de Tipos de Combustible')

@admin.route('/tipos_combustible/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_tipo_combustible():
    form = TipoCombustibleForm()
    if form.validate_on_submit():
        tipo_combustible = TipoCombustible(nombre=form.nombre.data, precio_por_litro=form.precio_por_litro.data)
        db.session.add(tipo_combustible)
        db.session.commit()
        flash('Tipo de combustible añadido exitosamente!', 'success')
        return redirect(url_for('admin.manage_tipos_combustible'))
    return render_template('admin/add_edit_tipo_combustible.html', form=form, title='Añadir Tipo de Combustible')

@admin.route('/tipos_combustible/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tipo_combustible(id):
    tipo_combustible = TipoCombustible.query.get_or_404(id)
    form = TipoCombustibleForm(obj=tipo_combustible)
    if form.validate_on_submit():
        tipo_combustible.nombre = form.nombre.data
        tipo_combustible.precio_por_litro = form.precio_por_litro.data
        db.session.commit()
        flash('Tipo de combustible actualizado exitosamente!', 'success')
        return redirect(url_for('admin.manage_tipos_combustible'))
    return render_template('admin/add_edit_tipo_combustible.html', form=form, tipo_combustible=tipo_combustible, title='Editar Tipo de Combustible')

@admin.route('/tipos_combustible/delete/<int:id>')
@login_required
@admin_required
def delete_tipo_combustible(id):
    tipo_combustible = TipoCombustible.query.get_or_404(id)
    db.session.delete(tipo_combustible)
    db.session.commit()
    flash('Tipo de combustible eliminado exitosamente!', 'success')
    return redirect(url_for('admin.manage_tipos_combustible'))

# Gestión de Tanques
@admin.route('/tanques')
@login_required
@admin_required
def manage_tanques():
    tanques = Tanque.query.all()
    return render_template('admin/tanques.html', tanques=tanques, title='Gestión de Tanques')

@admin.route('/tanques/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_tanque():
    form = TanqueForm()
    # Populate choices for select fields
    form.estacion_id.choices = [(e.id, e.nombre) for e in Estacion.query.all()]
    form.tipo_combustible_id.choices = [(tc.id, tc.nombre) for tc in TipoCombustible.query.all()]

    if form.validate_on_submit():
        tanque = Tanque(
            capacidad_litros=form.capacidad_litros.data,
            nivel_actual_litros=form.nivel_actual_litros.data,
            estacion_id=form.estacion_id.data,
            tipo_combustible_id=form.tipo_combustible_id.data
        )
        db.session.add(tanque)
        db.session.commit()
        flash('Tanque añadido exitosamente!', 'success')
        return redirect(url_for('admin.manage_tanques'))
    return render_template('admin/add_edit_tanque.html', form=form, title='Añadir Tanque')

@admin.route('/tanques/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tanque(id):
    tanque = Tanque.query.get_or_404(id)
    form = TanqueForm(obj=tanque)
    # Populate choices for select fields
    form.estacion_id.choices = [(e.id, e.nombre) for e in Estacion.query.all()]
    form.tipo_combustible_id.choices = [(tc.id, tc.nombre) for tc in TipoCombustible.query.all()]

    if form.validate_on_submit():
        tanque.capacidad_litros = form.capacidad_litros.data
        tanque.nivel_actual_litros = form.nivel_actual_litros.data
        tanque.estacion_id = form.estacion_id.data
        tanque.tipo_combustible_id = form.tipo_combustible_id.data
        db.session.commit()
        flash('Tanque actualizado exitosamente!', 'success')
        return redirect(url_for('admin.manage_tanques'))
    return render_template('admin/add_edit_tanque.html', form=form, tanque=tanque, title='Editar Tanque')

@admin.route('/tanques/delete/<int:id>')
@login_required
@admin_required
def delete_tanque(id):
    tanque = Tanque.query.get_or_404(id)
    db.session.delete(tanque)
    db.session.commit()
    flash('Tanque eliminado exitosamente!', 'success')
    return redirect(url_for('admin.manage_tanques'))

# Gestión de Bombas
@admin.route('/bombas')
@login_required
@admin_required
def manage_bombas():
    bombas = Bomba.query.all()
    return render_template('admin/bombas.html', bombas=bombas, title='Gestión de Bombas')

@admin.route('/bombas/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_bomba():
    form = BombaForm()
    # Cambia aquí: muestra estación-tanque-tipo de combustible
    form.tanque_id.choices = [
        (t.id, f"{t.estacion.nombre} - Tanque {t.id} - {t.tipo_combustible.nombre}")
        for t in Tanque.query.join(Estacion).join(TipoCombustible).all()
    ]
    if form.validate_on_submit():
        bomba = Bomba(
            numero_bomba=form.numero_bomba.data,
            tanque_id=form.tanque_id.data
        )
        db.session.add(bomba)
        db.session.commit()
        flash('Bomba añadida exitosamente!', 'success')
        return redirect(url_for('admin.manage_bombas'))
    return render_template('admin/add_edit_bomba.html', form=form, title='Añadir Nueva Bomba')

@admin.route('/bombas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_bomba(id):
    bomba = Bomba.query.get_or_404(id)
    form = BombaForm(obj=bomba)
    form.tanque_id.choices = [
        (t.id, f"{t.estacion.nombre} - Tanque {t.id} - {t.tipo_combustible.nombre}")
        for t in Tanque.query.join(Estacion).join(TipoCombustible).all()
    ]
    if form.validate_on_submit():
        bomba.numero_bomba = form.numero_bomba.data
        bomba.tanque_id = form.tanque_id.data
        db.session.commit()
        flash('Bomba actualizada exitosamente!', 'success')
        return redirect(url_for('admin.manage_bombas'))
    return render_template('admin/add_edit_bomba.html', form=form, bomba=bomba, title='Editar Bomba')

@admin.route('/bombas/delete/<int:id>')
@login_required
@admin_required
def delete_bomba(id):
    bomba = Bomba.query.get_or_404(id)
    db.session.delete(bomba)
    db.session.commit()
    flash('Bomba eliminada exitosamente!', 'success')
    return redirect(url_for('admin.manage_bombas'))

# Gestión de Proveedores
@admin.route('/proveedores')
@login_required
@admin_required
def manage_proveedores():
    proveedores = Proveedor.query.all()
    return render_template('admin/proveedores.html', proveedores=proveedores, title='Gestión de Proveedores')

@admin.route('/proveedores/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        proveedor = Proveedor(nombre=form.nombre.data, contacto=form.contacto.data)
        db.session.add(proveedor)
        db.session.commit()
        flash('Proveedor añadido exitosamente!', 'success')
        return redirect(url_for('admin.manage_proveedores'))
    return render_template('admin/add_edit_proveedor.html', form=form, title='Añadir Proveedor')

@admin.route('/proveedores/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    form = ProveedorForm(obj=proveedor)
    if form.validate_on_submit():
        proveedor.nombre = form.nombre.data
        proveedor.contacto = form.contacto.data
        db.session.commit()
        flash('Proveedor actualizado exitosamente!', 'success')
        return redirect(url_for('admin.manage_proveedores'))
    return render_template('admin/add_edit_proveedor.html', form=form, proveedor=proveedor, title='Editar Proveedor')

@admin.route('/proveedores/delete/<int:id>')
@login_required
@admin_required
def delete_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    flash('Proveedor eliminado exitosamente!', 'success')
    return redirect(url_for('admin.manage_proveedores'))

# Gestión de Usuarios (Administradores, Operadores, Clientes)
@admin.route('/usuarios')
@login_required
@admin_required
def manage_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios, title='Gestión de Usuarios')

@admin.route('/usuarios/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_usuario():
    form = UsuarioForm()
    form.rol_id.choices = [(rol.id, rol.nombre) for rol in Rol.query.all()]
    if form.validate_on_submit():
        # Crea una nueva instancia de usuario
        usuario = Usuario(username=form.username.data, rol_id=form.rol_id.data)
        # Establece la contraseña encriptada
        usuario.set_password(form.password.data)
        db.session.add(usuario)
        db.session.commit()
        flash('Usuario añadido exitosamente!', 'success')
        return redirect(url_for('admin.manage_usuarios'))
    return render_template('admin/add_edit_usuario.html', form=form, title='Añadir Usuario')

@admin.route('/usuarios/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    form = UsuarioForm(obj=usuario)
    form.rol_id.choices = [(rol.id, rol.nombre) for rol in Rol.query.all()]
    if form.validate_on_submit():
        usuario.username = form.username.data
        usuario.rol_id = form.rol_id.data
        if form.password.data: # Solo actualiza la contraseña si se proporciona una nueva
            usuario.set_password(form.password.data)
        db.session.commit()
        flash('Usuario actualizado exitosamente!', 'success')
        return redirect(url_for('admin.manage_usuarios'))
    return render_template('admin/add_edit_usuario.html', form=form, usuario=usuario, title='Editar Usuario')

@admin.route('/usuarios/delete/<int:id>')
@login_required
@admin_required
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    # Antes de eliminar un usuario, asegúrate de que no haya clientes asociados si es un usuario de tipo cliente.
    # O bien, desvincula el cliente del usuario.
    # Por simplicidad, aquí lo eliminamos directamente. En una app real, podrías querer manejar esto mejor.
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente!', 'success')
    return redirect(url_for('admin.manage_usuarios'))

# Gestión de Clientes
@admin.route('/clientes')
@login_required
@admin_required
def manage_clientes():
    clientes = Cliente.query.all()
    return render_template('admin/clientes.html', clientes=clientes, title='Gestión de Clientes')

@admin.route('/clientes/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_cliente():
    form = ClienteForm()
    # Asigna solo usuarios con rol de 'cliente' a este campo
    form.usuario_id.choices = [(u.id, u.username) for u in Usuario.query.join(Rol).filter(Rol.nombre == 'cliente').all()]
    form.usuario_id.choices.insert(0, (0, 'Seleccione un usuario (opcional)')) # Opción para cliente sin usuario asociado

    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            nit_ci=form.nit_ci.data if form.nit_ci.data else None,
            usuario_id=form.usuario_id.data if form.usuario_id.data != 0 else None
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente añadido exitosamente!', 'success')
        return redirect(url_for('admin.manage_clientes'))
    return render_template('admin/add_edit_cliente.html', form=form, title='Añadir Cliente')

@admin.route('/clientes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    form.usuario_id.choices = [(u.id, u.username) for u in Usuario.query.join(Rol).filter(Rol.nombre == 'cliente').all()]
    form.usuario_id.choices.insert(0, (0, 'Seleccione un usuario (opcional)'))
    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.apellido = form.apellido.data
        cliente.nit_ci = form.nit_ci.data if form.nit_ci.data else None
        cliente.usuario_id = form.usuario_id.data if form.usuario_id.data != 0 else None
        db.session.commit()
        flash('Cliente actualizado exitosamente!', 'success')
        return redirect(url_for('admin.manage_clientes'))
    return render_template('admin/add_edit_cliente.html', form=form, cliente=cliente, title='Editar Cliente')

@admin.route('/clientes/delete/<int:id>')
@login_required
@admin_required
def delete_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado exitosamente!', 'success')
    return redirect(url_for('admin.manage_clientes'))

# Reportes (Administrador puede ver todos los reportes)
@admin.route('/reportes')
@login_required
@admin_required
def view_reports():
    # Obtener datos para reportes (ej. ventas por mes, nivel de tanques)
    ventas = Venta.query.order_by(Venta.fecha_hora.desc()).all()
    reabastecimientos = Reabastecimiento.query.order_by(Reabastecimiento.fecha_hora.desc()).all()
    alertas = ReporteAlerta.query.order_by(ReporteAlerta.fecha_hora.desc()).all()
    tanques = Tanque.query.all() # Obtenemos todos los tanques para el reporte de nivel

    # Calcular total de ventas
    total_ventas = sum(v.total_pagado for v in ventas)

    return render_template('admin/reports.html',
                           ventas=ventas,
                           reabastecimientos=reabastecimientos,
                           alertas=alertas,
                           tanques=tanques, # Pasamos los tanques a la plantilla
                           total_ventas=total_ventas,
                           title='Reportes')

# Reportes en PDF
@admin.route('/reporte/ventas/pdf')
@login_required
def exportar_reporte_ventas_pdf():
    ventas = Venta.query.all()  # O tu consulta personalizada
    html = render_template('admin/reporte_pdf.html', ventas=ventas)
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_ventas.pdf'
    return response

@admin.route('/reportes/pdf')
@login_required
def exportar_reportes_pdf():
    ventas = Venta.query.all()
    reabastecimientos = Reabastecimiento.query.all()
    alertas = ReporteAlerta.query.all()
    tanques = Tanque.query.all()
    total_ventas = sum(v.total_pagado for v in ventas)
    html = render_template(
        'admin/reports_pdf.html',  # Usa la nueva plantilla
        ventas=ventas,
        reabastecimientos=reabastecimientos,
        alertas=alertas,
        tanques=tanques,
        total_ventas=total_ventas,
        now=datetime.now  # Para la fecha en el footer
    )
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reportes.pdf'
    return response

@admin.route('/eliminar_historial', methods=['POST'])
@login_required
@admin_required
def eliminar_historial():
    Reabastecimiento.query.delete()
    db.session.commit()
    flash('Historial eliminado correctamente.', 'success')
    return redirect(url_for('admin.view_reports'))

@admin.route('/eliminar_reportes', methods=['POST'])
@login_required
@admin_required
def eliminar_reportes():
    Venta.query.delete()
    ReporteAlerta.query.delete()
    db.session.commit()
    flash('Reportes eliminados correctamente.', 'success')
    return redirect(url_for('admin.view_reports'))
