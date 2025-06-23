# gasolinera/app/models.py
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Modelo de Rol de usuario
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False) # Nombre del rol (administrador, operador, cliente)
    usuarios = db.relationship('Usuario', backref='rol', lazy='dynamic') # Relación con usuarios

# Modelo de Usuario
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False) # Nombre de usuario
    password_hash = db.Column(db.String(128)) # Hash de la contraseña
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # Clave foránea del rol
    clientes = db.relationship('Cliente', backref='usuario', lazy='dynamic') # Relación con clientes

    # Establece la contraseña encriptada
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verifica la contraseña
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo de Estación de servicio
class Estacion(db.Model):
    __tablename__ = 'estaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    tanques = db.relationship('Tanque', backref='estacion', lazy='dynamic')
    reabastecimientos = db.relationship('Reabastecimiento', backref='estacion', lazy='dynamic')

# Modelo de Tanque de combustible
class Tanque(db.Model):
    __tablename__ = 'tanques'
    id = db.Column(db.Integer, primary_key=True)
    capacidad_litros = db.Column(db.Float, nullable=False) # Capacidad del tanque en litros
    nivel_actual_litros = db.Column(db.Float, nullable=False, default=0.0) # Nivel actual de combustible
    estacion_id = db.Column(db.Integer, db.ForeignKey('estaciones.id')) # Clave foránea de la estación
    tipo_combustible_id = db.Column(db.Integer, db.ForeignKey('tipos_combustible.id')) # Clave foránea del tipo de combustible
    alertas = db.relationship('ReporteAlerta', backref='tanque', lazy='dynamic') # Relación con reportes de alerta

# Modelo de Bomba de despacho
class Bomba(db.Model):
    __tablename__ = 'bombas'
    id = db.Column(db.Integer, primary_key=True)
    numero_bomba = db.Column(db.String(50), nullable=False)
    tanque_id = db.Column(db.Integer, db.ForeignKey('tanques.id'), nullable=False)
    tanque = db.relationship('Tanque', backref='bombas')  # <-- Agrega esta línea
    ventas = db.relationship('Venta', backref='bomba', lazy='dynamic') # Relación con ventas

# Modelo de Tipo de Combustible
class TipoCombustible(db.Model):
    __tablename__ = 'tipos_combustible'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False) # Nombre del combustible (ej. Gasolina, Diesel)
    precio_por_litro = db.Column(db.Float, nullable=False) # Precio por litro
    tanques = db.relationship('Tanque', backref='tipo_combustible', lazy='dynamic') # Relación con tanques

# Modelo de Venta
class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.datetime.now) # Fecha y hora de la venta
    litros_vendidos = db.Column(db.Float, nullable=False) # Cantidad de litros vendidos
    total_pagado = db.Column(db.Float, nullable=False) # Monto total pagado
    bomba_id = db.Column(db.Integer, db.ForeignKey('bombas.id')) # Clave foránea de la bomba
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True) # Clave foránea del cliente (opcional)
    detalle_venta = db.relationship('DetalleVenta', backref='venta', uselist=False) # Relación con detalle de venta (uno a uno)
    pago = db.relationship('Pago', backref='venta', uselist=False) # Relación con pago (uno a uno)

# Modelo de Detalle de Venta (Historial)
class DetalleVenta(db.Model):
    __tablename__ = 'detalles_venta'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), unique=True, nullable=False) # Clave foránea de la venta
    observaciones = db.Column(db.String(255)) # Observaciones adicionales

# Modelo de Pago
class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), unique=True, nullable=False) # Clave foránea de la venta
    monto = db.Column(db.Float, nullable=False) # Monto pagado
    metodo_pago = db.Column(db.String(50)) # Método de pago (ej. efectivo, tarjeta)
    fecha_pago = db.Column(db.DateTime, default=datetime.datetime.now) # Fecha del pago

# Modelo de Cliente
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False) # Nombre del cliente
    apellido = db.Column(db.String(100)) # Apellido del cliente
    nit_ci = db.Column(db.String(20), unique=True, nullable=True) # NIT/CI del cliente (opcional)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True) # Clave foránea del usuario asociado

# Modelo de Reporte de Alerta
class ReporteAlerta(db.Model):
    __tablename__ = 'reportes_alerta'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.datetime.now) # Fecha y hora de la alerta
    tipo_alerta = db.Column(db.String(50), nullable=False) # Tipo de alerta (ej. bajo nivel, reabastecimiento)
    mensaje = db.Column(db.String(255)) # Mensaje de la alerta
    tanque_id = db.Column(db.Integer, db.ForeignKey('tanques.id')) # Clave foránea del tanque

# Modelo de Reabastecimiento
class Reabastecimiento(db.Model):
    __tablename__ = 'reabastecimientos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.datetime.now)
    litros_reabastecidos = db.Column(db.Float, nullable=False)
    costo_total = db.Column(db.Float, nullable=False)
    tanque_id = db.Column(db.Integer, db.ForeignKey('tanques.id'))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id')) # Esta es la clave foránea
    estacion_id = db.Column(db.Integer, db.ForeignKey('estaciones.id'))
    pago_reabastecimiento = db.relationship('PagoReabastecimiento', backref='reabastecimiento', uselist=False)

    # Relaciones directas desde Reabastecimiento:
    tanque = db.relationship('Tanque', backref='reabastecimientos_tanque')
    # Elimina esta línea si existe, ya que la relación se define desde Proveedor con el backref
    # proveedor = db.relationship('Proveedor', backref='reabastecimientos_proveedor')


# Modelo de Proveedor
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    # Esta es la relación que crea 'reabastecimientos' como atributo en Proveedor
    # y 'proveedor' (objeto) como atributo en Reabastecimiento.
    reabastecimientos = db.relationship('Reabastecimiento', backref='proveedor', lazy='dynamic') # <-- Asegúrate de que esta línea esté así

# Modelo de Pago de Reabastecimiento
class PagoReabastecimiento(db.Model):
    __tablename__ = 'pagos_reabastecimiento'
    id = db.Column(db.Integer, primary_key=True)
    reabastecimiento_id = db.Column(db.Integer, db.ForeignKey('reabastecimientos.id'), unique=True, nullable=False) # Clave foránea del reabastecimiento
    monto = db.Column(db.Float, nullable=False) # Monto pagado por el reabastecimiento
    fecha_pago = db.Column(db.DateTime, default=datetime.datetime.now) # Fecha del pago
