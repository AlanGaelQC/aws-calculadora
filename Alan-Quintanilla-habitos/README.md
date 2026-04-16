# Sistema de Seguimiento de Hábitos
**Equipo:** Alan Gael Quintanilla Clemente  
**Dominio:** Dominio 2 — Plataforma de Seguimiento de Hábitos  
**Fecha:** Abril 2026

---

## ¿Qué problema resuelve?
Este sistema sirve para registrar hábitos diarios o semanales y darles seguimiento, cada vez que el usuario cumple un hábito se guarda y el sistema calcula la racha automáticamente, la idea es motivar la constancia viendo el progreso y cuánto tiempo llevas cumpliendo.

---

## Estructura de la Base de Datos
| Tabla | Descripción | Relación |
|-------|-------------|----------|
| habitos | Guarda los hábitos creados | Tabla principal |
| registros | Guarda cada vez que se cumple un hábito con su fecha | FK hacia habitos |
| rachas | Guarda la racha actual y la máxima | FK hacia habitos |

---

## Rutas de la API
| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | / | Interfaz principal HTML |
| POST | /habitos | Crea un nuevo hábito |
| GET | /habitos | Ver todos los hábitos registrados |
| POST | /registros | Registra el cumplimiento de un hábito |
| GET | /historial/<habito_id> | Ver historial de un hábito específico |
| GET | /resumen | Ver hábitos completados y pendientes del día |

---

## ¿Cuál es la tarea pesada y por qué bloquea el sistema?
La tarea pesada está en POST /registros, después de guardar el cumplimiento el sistema hace un time.sleep(5) para simular el cálculo de la racha, el problema es que si varios usuarios registran al mismo tiempo todos tienen que esperar esos 5 segundos, eso hace que el servidor se sature y empiecen los tiempos de espera o errores, en microservicios esto se manda al Servicio B para que el Servicio A no se bloquee y el usuario no tenga que esperar.

---

## Cómo levantar el proyecto

### Monolito
```bash
# 1. Clonar el repositorio
git clone https://github.com/AlanGaelQC/aws-calculadora

# 2. Crear las tablas en RDS
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Construir la imagen
docker build -t habitos-monolito .

# 4. Correr el contenedor
docker run -d -p 5000:5000 \
  -e DB_HOST=ENDPOINT_RDS \
  -e DB_USER=admin \
  -e DB_PASSWORD=PASSWORD \
  -e DB_NAME=db-actividades \
  habitos-monolito

# 5. Abrir en navegador
http://IP_EC2:5000
```

### Microservicios
```bash
# 1. Entrar a la carpeta de microservicios
cd Alan-Quintanilla-habitos/microservicios

# 2. Correr con Docker Compose
docker-compose up --build -d

# 3. Abrir en navegador
http://IP_EC2:5000
```

---

## Decisiones técnicas
Se separó en tres tablas para mantener orden, hábitos como principal, registros como historial y rachas como resultado del procesamiento pesado, el Servicio B no expone puertos y solo se comunica internamente con el Servicio A usando el nombre del contenedor, eso mejora la seguridad, también se usa try/except y finally para manejar errores y cerrar conexiones correctamente.
