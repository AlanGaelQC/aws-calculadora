# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This repo contains two separate projects as subdirectories:

- **`aws-calculadora/`** — Monolithic Flask calculator (standalone, with its own nested `.git`)
- **`Alan-Quintanilla-microservicios/`** — Academic project with two variants:
  - `monolito/` — Original monolithic version (Flask + pymysql, hardcoded DB credentials)
  - `microservicios/` — Refactored microservices version (two Flask services + docker-compose)

## Running the Projects

### Monolith (aws-calculadora/ or Alan-Quintanilla-microservicios/monolito/)
```bash
# Build and run via Docker
docker build -t calculadora-monolito .
docker run -p 5000:5000 calculadora-monolito

# Or run directly (requires Python 3.9+)
pip install -r requirements.txt
python3 run.py
```
App is available at `http://localhost:5000`.

### Microservices (Alan-Quintanilla-microservicios/microservicios/)
```bash
cd Alan-Quintanilla-microservicios/microservicios

# Set DB credentials in docker-compose.yml environment section, then:
docker-compose up --build -d

# Tear down
docker-compose down
```
Servicio A (UI + API) is available at `http://localhost:5000`. Servicio B has no external port.

## Architecture

### Monolith
Single Flask app (`app/main.py`) handles HTTP requests, performs arithmetic, writes to the `operaciones` table in AWS RDS MySQL, and renders `templates/index.html`. Database connection is in `app/database.py`; the Flask app object is created in `app/__init__.py`.

### Microservices
**Servicio A** (`servicio_a/app.py`, port 5000):
- Serves the HTML form at `GET /`
- Handles `POST /registrar`: calculates the result, inserts into `operaciones` table, then fires a `POST` to Servicio B's `/notificar` with a 2-second timeout
- If Servicio B is unreachable, returns a graceful degradation message — the operation is still saved

**Servicio B** (`servicio_b/app.py`, port 5001, internal only):
- Exposes only `POST /notificar`
- Simulates heavy work with `time.sleep(5)`, then writes to the `notificaciones` table
- Has no external port exposed in docker-compose

**Networking**: Both services share `red_interna` (Docker bridge network). Servicio A reaches Servicio B via `http://calculadora-servicio-b:5001/notificar` (container hostname).

## Database

AWS RDS MySQL (`db-actividades.cfsiu7tgzbib.us-east-1.rds.amazonaws.com`).

| Table | Owner | Columns |
|-------|-------|---------|
| `operaciones` | Servicio A / Monolith | id, numero1, numero2, operacion, resultado, fecha |
| `notificaciones` | Servicio B | id, numero1, numero2, operacion, resultado, fecha |

Both tables are created on startup via `init_db()` (`CREATE TABLE IF NOT EXISTS`).

**Note:** The monolith (`aws-calculadora/` and `monolito/`) has DB credentials hardcoded in `database.py`. The microservices version reads them from environment variables (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) set in `docker-compose.yml`.

## Key Differences Between Monolith and Microservices

- Monolith uses `pymysql`; microservices use `mysql-connector-python`
- Monolith renders Jinja2 templates; Servicio A returns JSON from `/registrar` (the form is inline HTML)
- Servicio B intentionally includes `time.sleep(5)` to simulate async heavy work — this is by design, not a bug

# Reglas para Claude Code — Ahorra Tokens

## 1. No programar sin contexto
- ANTES de escribir codigo: lee los archivos relevantes, revisa git log, entiende la arquitectura.
- Si no tienes contexto suficiente, pregunta. No asumas.

## 2. Respuestas cortas
- Responde en 1-3 oraciones. Sin preambulos, sin resumen final.
- No repitas lo que el usuario dijo. No expliques lo obvio.
- Codigo habla por si mismo: no narres cada linea que escribes.

## 3. No reescribir archivos completos
- Usa Edit (reemplazo parcial), NUNCA Write para archivos existentes salvo que el cambio sea >80% del archivo.
- Cambia solo lo necesario. No "limpies" codigo alrededor del cambio.

## 4. No releer archivos ya leidos
- Si ya leiste un archivo en esta conversacion, no lo vuelvas a leer salvo que haya cambiado.
- Toma notas mentales de lo importante en tu primera lectura.

## 5. Validar antes de declarar hecho
- Despues de un cambio: compila, corre tests, o verifica que funciona.
- Nunca digas "listo" sin evidencia de que funciona.

## 6. Cero charla aduladora
- No digas "Excelente pregunta", "Gran idea", "Perfecto", etc.
- No halagues al usuario. Ve directo al trabajo.

## 7. Soluciones simples
- Implementa lo minimo que resuelve el problema. Nada mas.
- No agregues abstracciones, helpers, tipos, validaciones, ni features que no se pidieron.
- 3 lineas repetidas > 1 abstraccion prematura.

## 8. No pelear con el usuario
- Si el usuario dice "hazlo asi", hazlo asi. No debatas salvo riesgo real de seguridad o perdida de datos.
- Si discrepas, menciona tu concern en 1 oracion y procede con lo que pidio.

## 9. Leer solo lo necesario
- No leas archivos completos si solo necesitas una seccion. Usa offset y limit.
- Si sabes la ruta exacta, usa Read directo. No hagas Glob + Grep + Read cuando Read basta.

## 10. No narrar el plan antes de ejecutar
- No digas "Voy a leer el archivo, luego modificar la funcion, luego compilar...". Solo hazlo.
- El usuario ve tus tool calls. No necesita un preview en texto.

## 11. Paralelizar tool calls
- Si necesitas leer 3 archivos independientes, lee los 3 en un solo mensaje, no uno por uno.
- Menos roundtrips = menos tokens de contexto acumulado.

## 12. No duplicar codigo en la respuesta
- Si ya editaste un archivo, no copies el resultado en tu respuesta. El usuario lo ve en el diff.
- Si creaste un archivo, no lo muestres entero en texto tambien.

## 13. No usar Agent cuando Grep/Read basta
- Agent duplica todo el contexto en un subproceso. Solo usalo para busquedas amplias o tareas complejas.
- Para buscar una funcion o archivo especifico, usa Grep o Glob directo.