# Gasolina App

Aplicación web para la gestión de ventas de gasolina con autenticación y roles, desarrollada con Flask.

## Características

- Autenticación con roles (admin, usuario, cliente)
- CRUD para las diferentes tablas
- Base de datos con tablas relacionales
- Formularios con WTForms
- Plantillas con Bootstrap
- Modularización con Blueprints
- Entre otros mas

## Requisitos

- Python 3.8 o superior
- pip

## Instalación

1. Clona o descomprime este repositorio.
2. Abre la carpeta en Visual Studio Code o tu terminal favorita.
3. Crea y activa un entorno virtual:

```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate
```

4. Instala las dependencias:

```bash
pip install -r requirements.txt
```


5. Ejecuta la aplicación:

```bash
python run.py
```

Accede desde tu navegador a `http://localhost:5000`.

## Usuarios de prueba

- Admin:
  - Usuario: `admin`
  - Contraseña: `adminpass`

- Operador:
  - Usuario: `operador1`
  - Contraseña: 'operadorpass`
    
- Cliente1:
  - Usuario: `cliente1`
  - Contraseña: 'clientepass`
---

Desarrollado como plantilla para proyectos con Flask y base de datos relacional.
