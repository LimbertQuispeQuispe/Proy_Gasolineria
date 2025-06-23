# gasolinera/app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

# Base de un formulario
class BaseForm(FlaskForm):
    class Meta:
        def render_field(self, field, render_kw):
            return field.widget(field, **render_kw)


# Formularios de Autenticación
class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Ingresar')

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

# Formularios de Gestión (Admin)
class EstacionForm(FlaskForm):
    nombre = StringField('Nombre de la Estación', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    submit = SubmitField('Guardar Estación')

class TipoCombustibleForm(FlaskForm):
    nombre = StringField('Nombre del Combustible (ej. Gasolina, Diesel)', validators=[DataRequired()])
    precio_por_litro = FloatField('Precio por Litro (Bs.)', validators=[DataRequired()])
    submit = SubmitField('Guardar Tipo de Combustible')

class TanqueForm(FlaskForm):
    estacion_id = SelectField('Estación', coerce=int, validators=[DataRequired()])
    tipo_combustible_id = SelectField('Tipo de Combustible', coerce=int, validators=[DataRequired()])
    capacidad_litros = FloatField('Capacidad (Litros)', validators=[DataRequired()])
    nivel_actual_litros = FloatField('Nivel Actual (Litros)', validators=[DataRequired(), Optional()])
    submit = SubmitField('Guardar Tanque')

class BombaForm(FlaskForm):
    tanque_id = SelectField('Estación - Tanque - Combustible', coerce=int, validators=[DataRequired()])
    numero_bomba = StringField('Número de Bomba', validators=[DataRequired()])
    submit = SubmitField('Guardar Bomba')

class ProveedorForm(FlaskForm):
    nombre = StringField('Nombre del Proveedor', validators=[DataRequired()])
    contacto = StringField('Información de Contacto', validators=[Optional()])
    submit = SubmitField('Guardar Proveedor')

class UsuarioForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Contraseña')
    confirm_password = PasswordField('Confirmar Contraseña', validators=[EqualTo('password', message='Las contraseñas deben coincidir')])
    rol_id = SelectField('Rol', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Usuario')

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre del Cliente', validators=[DataRequired()])
    apellido = StringField('Apellido del Cliente', validators=[DataRequired()])
    nit_ci = StringField('NIT/CI (Opcional)', validators=[Optional()])
    usuario_id = SelectField('Usuario Asociado (Solo rol Cliente)', coerce=int, validators=[Optional()])
    submit = SubmitField('Guardar Cliente')

# Formularios de Operaciones (Operador)
class VentaForm(FlaskForm):
    # Función de coerción personalizada
    def _bomba_coerce(value):
        try:
            return int(value)
        except ValueError:
            # Si no se puede convertir a int (es decir, es la etiqueta de un optgroup),
            # retornamos el valor original o None, ya que no es un valor seleccionable válido.
            return None # O podrías retornar value si quieres que el valor de la opción sea la cadena misma.
                        # Para SelectField con IDs, None es más seguro.

    # Aplica la función de coerción personalizada al campo bomba_id
    bomba_id = SelectField('Bomba', coerce=_bomba_coerce, validators=[DataRequired()])
    litros_vendidos = FloatField('Litros Vendidos', validators=[DataRequired()])
    cliente_id = SelectField('Cliente (Opcional)', coerce=int, validators=[Optional()])
    metodo_pago = SelectField('Método de Pago', choices=[('Efectivo', 'Efectivo'), ('Tarjeta', 'Tarjeta'), ('Transferencia', 'Transferencia')], validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    submit = SubmitField('Registrar Venta')

class ReabastecimientoForm(FlaskForm):
    tanque_id = SelectField('Tanque', coerce=int, validators=[DataRequired()])
    proveedor_id = SelectField('Proveedor', coerce=int, validators=[DataRequired()])
    litros_reabastecidos = FloatField('Litros Reabastecidos', validators=[DataRequired()])
    costo_total = FloatField('Costo Total (Bs.)', validators=[DataRequired()])
    submit = SubmitField('Registrar Reabastecimiento')