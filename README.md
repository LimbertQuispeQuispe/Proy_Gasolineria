# Proy gasolineria


## Características

- Autenticación con roles (admin, usuario, cliente)
- CRUD para las diferentes tablas
- Base de datos con tablas relacionales
- Formularios con WTForms
- Plantillas con Bootstrap
- Modularización con gtk3 runtime
- Entre otros mas

## Requisitos
-GTK3 runtime 3.24.21
- Python 3.8 o superior
- pip

## Instalación

1. Clona o descomprime este repositorio.
2. Abre la carpeta en Visual Studio Code o tu terminal favorita.
3. Crea y activa un entorno virtual:
4. es opcional ...igual puede trabajr en entorno global si no le corre en entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
```

4. Instala las dependencias:
en caso de que no instale ..instalar en global y no en entorno virtual

```bash
pip install -r requirements.txt
```


5. Ejecuta la aplicación:

```bash
python run.py
```
6. en caso de que no corra verifica el JGTK3 runtime 3.24.21
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
