FROM python:3.12-slim

# Instalar dependencias de sistema para WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar código y demás pasos
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
