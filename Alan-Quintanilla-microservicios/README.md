# Proyecto: Calculadora de Operaciones

**Alumno:** Alan Gael Quintanilla Clemente
**Materia:** Diseño y Arquitectura de Software
**Fecha:** Abril 2026

---

## ¿Qué problema resuelve mi aplicación?

Es una calculadora web que permite realizar operaciones básicas
(suma, resta, multiplicación y división) desde el navegador.
Cada operación queda registrada en una base de datos en AWS RDS
y se envía una notificación a un segundo servicio para su procesamiento.

---

## ¿Cuál era el problema del monolito?

Al correr Apache Benchmark contra el monolito, se podía observar
que todas las peticiones pasaban por el mismo proceso, incluyendo
la tarea pesada del sleep. Esto significa que si muchos usuarios
usaran la app al mismo tiempo, el servidor tendría que atenderlos
uno por uno sin poder delegar el trabajo lento a otro lado.

---

## ¿Qué responsabilidad tiene cada microservicio?

**Servicio A:** Recibe los datos del usuario, calcula la operación
y la guarda en la tabla `operaciones`, luego avisa al Servicio B.

**Servicio B:** Recibe la notificación de A, simula el procesamiento
pesado y guarda el registro en la tabla `notificaciones`.

---

## ¿Cómo se comunican los servicios?

El Servicio A llama al Servicio B mediante una petición HTTP interna
usando la URL `http://calculadora-servicio-b:5001/notificar`.
El nombre `calculadora-servicio-b` funciona como dirección porque
Docker Compose asigna automáticamente ese nombre como hostname
dentro de la red interna `red_interna`. Esto significa que la
comunicación entre servicios nunca sale al internet — es completamente
privada dentro de Docker.

---

## Tablas en la base de datos

| Tabla | Servicio dueño | Qué guarda |
|-------|---------------|------------|
| operaciones | Servicio A | numero1, numero2, operacion, resultado |
| notificaciones | Servicio B | numero1, numero2, operacion, resultado, fecha |

---

## ¿Qué pasa si el Servicio B se cae?

Cuando se apagó el Servicio B y se intentó registrar una operación,
el Servicio A no se cayó ni mostró un error al usuario. En cambio,
respondió con el mensaje "Servicio B en mantenimiento. Operacion guardada."
confirmando que el dato sí quedó guardado en la base de datos.
El usuario nunca perdió su operación.

---

## Cómo levantar el proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/AlanGaelQC/aws-calculadora.git

# 2. Entrar a la carpeta
cd Alan-Quintanilla-microservicios/microservicios

# 3. Configurar las variables de entorno en docker-compose.yml
# (cambiar DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

# 4. Levantar
sudo docker-compose up --build -d

# 5. Abrir en el navegador
http://IP_DE_TU_EC2:5000
```

---

## Reflexión Final

Lo más difícil fue restructurar la aplicación en dos servicios
separados siguiendo la estructura exacta que pedía la práctica.
Antes no entendía bien por qué dividir algo que funcionaba junto,
pero al hacerlo me di cuenta de que la separación es lo que permite
que A responda rápido mientras B hace el trabajo pesado por su cuenta.
También tuve problemas para ver la app en el navegador porque el
puerto no estaba correctamente configurado en el Security Group —
eso me enseñó que desplegar en la nube tiene sus propias reglas
además del código. Usaría microservicios en situaciones donde una
parte del sistema tarda mucho y no quiero que eso afecte al usuario.

---

## Checklist de Autoevaluación

**MONOLITO**
- [x] El código del monolito original está en la carpeta /monolito
- [x] El Dockerfile del monolito existe y es funcional
- [x] Hay captura del docker build sin errores
- [x] Hay captura del docker run con el contenedor corriendo
- [x] Hay captura de Apache Benchmark mostrando saturación

**MICROSERVICIOS**
- [x] servicio_a/app.py sin time.sleep(), con rutas / y /registrar
- [x] servicio_b/app.py sin rutas de UI, con lógica pesada
- [x] docker-compose.yml con ambos servicios y red interna
- [x] Servicio A con puerto expuesto, Servicio B sin puerto externo
- [x] Credenciales en variables de entorno

**README**
- [x] Explica el dominio de la aplicación
- [x] Explica el problema del monolito con sus propias palabras
- [x] Define la responsabilidad de cada servicio en una oración
- [x] Explica la comunicación entre servicios
- [x] Incluye los comandos para levantar el proyecto
- [x] Incluye la reflexión final
