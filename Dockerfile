# Multi-stage build para optimizar tamaño y seguridad
FROM python:3.11-slim as builder

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN adduser --disabled-password --gecos '' appuser

# Establecer workdir
WORKDIR /app

# Copiar solo requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage final - imagen ligera
FROM python:3.11-slim as runtime

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Crear usuario no-root
RUN adduser --disabled-password --gecos '' appuser

# Instalar dependencias del sistema runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar paquetes Python del builder
COPY --from=builder /root/.local /home/appuser/.local

# Establecer workdir
WORKDIR /app

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
