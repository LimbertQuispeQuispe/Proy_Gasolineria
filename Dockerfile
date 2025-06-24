# Imagen base con Python
FROM python:3.12-slim

# Instalar dependencias del sistema que necesita WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libgobject-2.0-0 \
    && apt-get clean

# Crear carpeta de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Puerto que usará la app
EXPOSE 8000

# Comando para iniciar la app Flask con Gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8000"]
