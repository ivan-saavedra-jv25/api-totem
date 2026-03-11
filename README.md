# Totem API - Backend para Tótem de Autoservicio

Backend minimal funcional para un sistema de tótem de autoservicio de compra de productos, desarrollado con FastAPI y preparado para Docker y CI/CD.

## 🚀 Características

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos para desarrollo (fácil migración a PostgreSQL)
- **Pydantic** - Validación de datos
- **Docker** - Contenerización lista para producción
- **Carrito de compras simulado** - Gestión en memoria
- **Gestión de órdenes** - Creación y seguimiento

## 📋 Requisitos

- Python 3.11+
- Docker y Docker Compose (opcional)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd totem-api
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 🏃‍♂️ Ejecución

### Desarrollo local
```bash
uvicorn main:app --reload
```

### Con Docker
```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8000`

## 📚 Documentación de la API

Una vez iniciado el servidor, visita:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## � CI/CD con Docker

El proyecto incluye un pipeline CI/CD completo con GitHub Actions:

### 🔄 Flujo Automático
- **Push a `develop`** → Build → Test → Deploy a Staging
- **Push a `main`** → Build → Test → Security Scan → Deploy a Producción

### 📋 Estructura CI/CD
```
.github/workflows/ci-cd.yml    # Pipeline principal
scripts/deploy.sh              # Script de deploy
scripts/rollback.sh            # Script de rollback
docker-compose.yml             # Desarrollo local
docker-compose.prod.yml        # Producción
Dockerfile                     # Multi-stage build optimizado
.dockerignore                  # Optimización de builds
```

### 🐳 Estrategia de Docker
- **Multi-stage build** para imágenes ligeras
- **Security scanning** con Trivy
- **Health checks** automáticos
- **Rollback automático** en fallos

### 🔧 Configuración Rápida

1. **Configurar Secrets en GitHub**:
   ```bash
   # Obligatorios:
   STAGING_HOST, STAGING_USER, STAGING_SSH_KEY
   PROD_HOST, PROD_USER, PROD_SSH_KEY
   POSTGRES_PASSWORD, SECRET_KEY
   ```

2. **Preparar Servidores**:
   ```bash
   # Instalar Docker y configurar SSH
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker deploy
   ```

3. **Deploy Manual**:
   ```bash
   # En servidor
   ./scripts/deploy.sh staging
   ./scripts/deploy.sh production
   ```

### 📚 Documentación Completa
- [🔐 Configuración de Secrets](docs/SECRETS.md)
- [🐳 Estrategia de Docker](docs/DOCKER_STRATEGY.md)

## �🔗 Endpoints

### Productos
- `GET /products` - Listar todos los productos
- `GET /products/{id}` - Obtener producto por ID
- `POST /products` - Crear nuevo producto
- `PUT /products/{id}` - Actualizar producto
- `DELETE /products/{id}` - Eliminar producto

### Carrito
- `GET /cart` - Ver carrito actual
- `POST /cart/add` - Agregar producto al carrito
- `POST /cart/remove` - Remover producto del carrito
- `DELETE /cart` - Vaciar carrito

### Órdenes
- `POST /orders` - Crear nueva orden
- `GET /orders/{id}` - Obtener orden por ID
- `GET /orders` - Listar todas las órdenes
- `PUT /orders/{id}/status` - Actualizar estado de orden

## 🗂️ Estructura del Proyecto

```
totem-api/
├── app/
│   ├── core/           # Configuración central
│   │   ├── config.py   # Variables de entorno
│   │   └── database.py # Configuración de DB
│   ├── models/         # Modelos SQLAlchemy
│   │   ├── base.py     # Base declarativa
│   │   ├── product.py  # Modelo Producto
│   │   └── order.py    # Modelo Orden
│   ├── schemas/        # Schemas Pydantic
│   │   ├── product.py  # Schemas Producto
│   │   ├── order.py    # Schemas Orden
│   │   └── cart.py     # Schemas Carrito
│   ├── routers/        # Rutas de la API
│   │   ├── products.py # Endpoints productos
│   │   ├── cart.py     # Endpoints carrito
│   │   └── orders.py   # Endpoints órdenes
│   └── services/       # Lógica de negocio
│       └── cart_service.py # Servicio carrito
├── tests/              # Pruebas unitarias
├── main.py             # Entry point FastAPI
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Configuración Docker
├── docker-compose.yml  # Orquestación Docker
├── .env.example        # Variables de entorno ejemplo
└── README.md           # Documentación
```

## 🔧 Configuración

### Variables de Entorno

```env
DATABASE_URL=sqlite:///./totem.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Migración a PostgreSQL

Para producción, puedes cambiar a PostgreSQL:

1. Actualiza `DATABASE_URL` en `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/totem
```

2. Instala el driver PostgreSQL:
```bash
pip install psycopg2-binary
```

3. Descomenta el servicio PostgreSQL en `docker-compose.yml`

## 🧪 Ejemplo de Uso

### Crear un producto
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Americano",
    "description": "Café recién hecho",
    "price": 2.50,
    "stock": 100,
    "image_url": "https://example.com/coffee.jpg"
  }'
```

### Agregar al carrito
```bash
curl -X POST "http://localhost:8000/cart/add" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: session123" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### Crear orden
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: session123" \
  -d '{
    "items": []
  }'
```

## 🚀 Despliegue

### Docker
```bash
docker build -t totem-api .
docker run -p 8000:8000 totem-api
```

### Docker Compose
```bash
docker-compose up -d
```

## 🔮 Próximos Pasos

- [ ] Implementar autenticación JWT
- [ ] Agregar sistema de pagos
- [ ] Implementar notificaciones
- [ ] Agregar tests unitarios
- [ ] Configurar CI/CD
- [ ] Optimizar para producción
- [ ] Agregar logging y monitoreo

## 📝 Licencia

MIT License

## 🤝 Contribución

1. Fork del proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request
