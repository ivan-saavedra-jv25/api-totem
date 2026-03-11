# Configuración de Secrets para CI/CD

Este documento explica cómo configurar los secrets necesarios para el pipeline CI/CD del proyecto Totem API.

## 🔐 GitHub Secrets

Para configurar los secrets en tu repositorio de GitHub:

1. Ve a tu repositorio en GitHub
2. Haz clic en **Settings** > **Secrets and variables** > **Actions**
3. Agrega los siguientes secrets:

### Secrets Obligatorios

#### Para Container Registry
```
DOCKER_USERNAME
```
- **Descripción**: Usuario de Docker Hub
- **Ejemplo**: `ivan-saavedra-jv25`

```
DOCKER_PASSWORD
```
- **Descripción**: Token de acceso personal de Docker Hub
- **Cómo obtener**: 
  1. Ve a https://hub.docker.com/settings/security
  2. Genera un "Access Token"
  3. Copia el token generado

```
GITHUB_TOKEN
```
- **Descripción**: Token de GitHub para autenticación (si usas GHCR)
- **Valor**: Se genera automáticamente, no necesitas configurarlo

#### Para Deploy a Servidores

##### Staging Environment
```
STAGING_HOST
```
- **Descripción**: IP o dominio del servidor de staging
- **Ejemplo**: `192.168.1.100` o `staging.totem-api.com`

```
STAGING_USER
```
- **Descripción**: Usuario SSH para el servidor de staging
- **Ejemplo**: `deploy` o `ubuntu`

```
STAGING_SSH_KEY
```
- **Descripción**: Clave SSH privada para acceso al servidor de staging
- **Cómo obtener**: 
  ```bash
  cat ~/.ssh/id_rsa_staging
  ```
- **Formato**: Contenido completo del archivo de clave privada

##### Production Environment
```
PROD_HOST
```
- **Descripción**: IP o dominio del servidor de producción
- **Ejemplo**: `prod.totem-api.com`

```
PROD_USER
```
- **Descripción**: Usuario SSH para el servidor de producción
- **Ejemplo**: `deploy` o `ubuntu`

```
PROD_SSH_KEY
```
- **Descripción**: Clave SSH privada para acceso al servidor de producción
- **Cómo obtener**: 
  ```bash
  cat ~/.ssh/id_rsa_production
  ```

```
PROD_URL
```
- **Descripción**: URL pública para health check en producción
- **Ejemplo**: `https://api.totem.com`

#### Base de Datos
```
POSTGRES_PASSWORD
```
- **Descripción**: Contraseña para PostgreSQL en producción
- **Requisitos**: Mínimo 16 caracteres, incluir números y símbolos
- **Ejemplo**: `T0t3mDB_P@ssw0rd_2024!`

#### Seguridad
```
SECRET_KEY
```
- **Descripción**: Clave secreta para JWT y encriptación
- **Cómo generar**:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **Ejemplo**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

### Secrets Opcionales

#### Notificaciones
```
SLACK_WEBHOOK
```
- **Descripción**: URL de webhook para notificaciones en Slack
- **Cómo configurar**:
  1. Ve a tu workspace de Slack
  2. Crea una app en https://api.slack.com/apps
  3. Activa "Incoming Webhooks"
  4. Crea un webhook y copia la URL

#### Code Coverage
```
CODECOV_TOKEN
```
- **Descripción**: Token para Codecov
- **Cómo obtener**: Regístrate en https://codecov.io y conecta tu repositorio

## 🖥️ Configuración de Servidores

### Preparación del Servidor

#### 1. Crear usuario de deploy
```bash
# En ambos servidores (staging y producción)
sudo adduser deploy
sudo usermod -aG sudo deploy
sudo usermod -aG docker deploy
```

#### 2. Configurar SSH
```bash
# En tu máquina local
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_staging
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_production

# Copiar claves públicas a los servidores
ssh-copy-id -i ~/.ssh/id_rsa_staging.pub deploy@STAGING_HOST
ssh-copy-id -i ~/.ssh/id_rsa_production.pub deploy@PROD_HOST
```

#### 3. Instalar Docker y Docker Compose
```bash
# En ambos servidores
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 4. Crear directorios de deploy
```bash
# En ambos servidores
sudo mkdir -p /opt/totem-api
sudo mkdir -p /opt/backups/totem-api
sudo mkdir -p /var/log
sudo chown -R deploy:deploy /opt/totem-api
sudo chown -R deploy:deploy /opt/backups
```

#### 5. Configurar firewall
```bash
# Permitir tráfico HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22  # SSH
sudo ufw enable
```

### Configuración de Entornos en GitHub

#### 1. Configurar Environments
1. Ve a **Settings** > **Environments**
2. Crea los environments:
   - `staging`
   - `production`

#### 2. Configurar Protection Rules
Para el environment `production`:
- ✅ Require reviewers
- ✅ Only branch `main` can deploy
- ✅ Wait timer (opcional, 5 minutos)

#### 3. Configurar Variables de Environment
Puedes agregar variables específicas por environment en lugar de secrets:

**Staging Environment Variables:**
```
DATABASE_URL=sqlite:///./totem.db
DEBUG=true
LOG_LEVEL=DEBUG
```

**Production Environment Variables:**
```
DATABASE_URL=postgresql://totem:${POSTGRES_PASSWORD}@postgres:5432/totem
DEBUG=false
LOG_LEVEL=INFO
```

## 🧪 Testing Local

### Testear SSH Connection
```bash
# Test staging
ssh -i ~/.ssh/id_rsa_staging deploy@STAGING_HOST "docker --version"

# Test production
ssh -i ~/.ssh/id_rsa_production deploy@PROD_HOST "docker --version"
```

### Testear Scripts de Deploy
```bash
# Copiar scripts al servidor
scp -i ~/.ssh/id_rsa_staging scripts/deploy.sh deploy@STAGING_HOST:/opt/totem-api/
scp -i ~/.ssh/id_rsa_production scripts/deploy.sh deploy@PROD_HOST:/opt/totem-api/

# Hacerlos ejecutables
ssh -i ~/.ssh/id_rsa_staging deploy@STAGING_HOST "chmod +x /opt/totem-api/deploy.sh"
ssh -i ~/.ssh/id_rsa_production deploy@PROD_HOST "chmod +x /opt/totem-api/deploy.sh"
```

## 📋 Checklist de Deploy

### Antes del Primer Deploy
- [ ] Configurar todos los secrets en GitHub
- [ ] Preparar servidores (staging y producción)
- [ ] Configurar SSH keys
- [ ] Instalar Docker en servidores
- [ ] Crear environments en GitHub
- [ ] Testear conexión SSH a ambos servidores

### Para Cada Deploy
- [ ] Verificar que todos los secrets están configurados
- [ ] Confirmar que los servidores están accesibles
- [ ] Revisar logs del pipeline
- [ ] Verificar health check después del deploy
- [ ] Monitorear aplicación post-deploy

## 🚨 Seguridad

### Buenas Prácticas
1. **Rotar keys** cada 90 días
2. **Usar keys diferentes** para staging y producción
3. **Limitar accesos** SSH (solo desde IPs conocidas)
4. **Monitorear logs** de accesos fallidos
5. **Usar bastion host** para producción (opcional)

### Auditoría de Secrets
```bash
# Listar todos los secrets (GitHub CLI)
gh secret list

# Verificar que no hay secrets en el código
grep -r "password\|secret\|key" --include="*.py" --include="*.yml" --include="*.yaml" . | grep -v ".git"
```

## 📞 Soporte

Si tienes problemas con la configuración:

1. **Revisa los logs** del pipeline en GitHub Actions
2. **Verifica la configuración SSH** con `ssh -v`
3. **Confirma los secrets** están correctamente configurados
4. **Testea manualmente** los scripts de deploy
5. **Revisa la documentación** oficial de GitHub Actions
