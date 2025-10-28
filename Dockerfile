FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV PYTHONUTF8=1
ENV RUNNING_IN_DOCKER=1

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el resto de la aplicación
COPY . /app/

# Crear directorio para datos
RUN mkdir -p /data

# Exponer puerto
EXPOSE 8000

# Script de inicio
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    python init_social_auth.py && \
    python manage.py runserver 0.0.0.0:8000