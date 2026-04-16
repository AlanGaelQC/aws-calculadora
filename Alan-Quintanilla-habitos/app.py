from flask import Flask, request, jsonify, render_template_string
import mysql.connector
import os

app = Flask(__name__)

# Configuración de base de datos desde variables de entorno
def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )

# HTML principal
HTML = '''
<!DOCTYPE html>
<html>
<head><title>Seguimiento de Hábitos</title></head>
<body>
    <h1>Plataforma de Seguimiento de Hábitos</h1>

    <h2>Crear Hábito</h2>
    <form action="/habitos" method="post">
        Nombre: <input type="text" name="nombre" required><br>
        Frecuencia:
        <select name="frecuencia">
            <option value="diaria">Diaria</option>
            <option value="semanal">Semanal</option>
        </select><br>
        Meta: <input type="text" name="meta"><br>
        <button type="submit">Crear</button>
    </form>

    <h2>Registrar Cumplimiento</h2>
    <form action="/registros" method="post">
        ID Hábito: <input type="number" name="habito_id" required><br>
        Fecha: <input type="date" name="fecha" required><br>
        Notas: <input type="text" name="notas"><br>
        <button type="submit">Registrar</button>
    </form>

    <h2>Consultas</h2>
    <a href="/habitos">Ver todos los hábitos</a><br>
    <a href="/resumen">Ver resumen del día</a><br>
</body>
</html>
'''

# Ruta 1 — Interfaz principal
@app.route('/')
def index():
    return render_template_string(HTML)

# Ruta 2 — Crear hábito (POST) y consultar todos (GET)
@app.route('/habitos', methods=['GET', 'POST'])
def habitos():
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            # Insertar nuevo hábito
            nombre = request.form.get('nombre')
            frecuencia = request.form.get('frecuencia')
            meta = request.form.get('meta')

            cursor.execute(
                'INSERT INTO habitos (nombre, frecuencia, meta) VALUES (%s, %s, %s)',
                (nombre, frecuencia, meta)
            )
            conn.commit()
            habito_id = cursor.lastrowid

            # Crear racha inicial para el hábito
            cursor.execute(
                'INSERT INTO rachas (habito_id, racha_actual, racha_maxima) VALUES (%s, 0, 0)',
                (habito_id,)
            )
            conn.commit()

            return jsonify({'mensaje': 'Hábito creado exitosamente', 'id': habito_id})

        else:
            # Consultar todos los hábitos
            cursor.execute('SELECT * FROM habitos')
            resultado = cursor.fetchall()
            return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Ruta 3 — Registrar cumplimiento de hábito (tarea pesada aquí)
@app.route('/registros', methods=['POST'])
def registrar_cumplimiento():
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        habito_id = request.form.get('habito_id')
        fecha = request.form.get('fecha')
        notas = request.form.get('notas')

        # Insertar registro de cumplimiento
        cursor.execute(
            'INSERT INTO registros (habito_id, fecha, completado, notas) VALUES (%s, %s, TRUE, %s)',
            (habito_id, fecha, notas)
        )
        conn.commit()

        # Tarea pesada — simula cálculo de racha
        import time
        time.sleep(5)

        # Calcular racha actual
        cursor.execute(
            'SELECT COUNT(*) as total FROM registros WHERE habito_id = %s AND completado = TRUE',
            (habito_id,)
        )
        resultado = cursor.fetchone()
        racha_nueva = resultado['total']

        # Actualizar racha en tabla rachas
        cursor.execute(
            '''UPDATE rachas
               SET racha_actual = %s,
                   racha_maxima = GREATEST(racha_maxima, %s)
               WHERE habito_id = %s''',
            (racha_nueva, racha_nueva, habito_id)
        )
        conn.commit()

        return jsonify({
            'mensaje': 'Cumplimiento registrado exitosamente',
            'racha_actual': racha_nueva
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Ruta 4 — Historial de cumplimiento de un hábito
@app.route('/historial/<int:habito_id>', methods=['GET'])
def historial(habito_id):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            'SELECT * FROM registros WHERE habito_id = %s ORDER BY fecha DESC',
            (habito_id,)
        )
        resultado = cursor.fetchall()
        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Ruta 5 — Resumen del día
@app.route('/resumen', methods=['GET'])
def resumen():
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        from datetime import date
        hoy = date.today().isoformat()

        # Hábitos completados hoy
        cursor.execute(
            '''SELECT h.nombre, h.frecuencia, r.fecha, r.notas
               FROM habitos h
               LEFT JOIN registros r ON h.id = r.habito_id AND r.fecha = %s
               WHERE r.id IS NOT NULL''',
            (hoy,)
        )
        completados = cursor.fetchall()

        # Hábitos pendientes hoy
        cursor.execute(
            '''SELECT h.nombre, h.frecuencia
               FROM habitos h
               LEFT JOIN registros r ON h.id = r.habito_id AND r.fecha = %s
               WHERE r.id IS NULL''',
            (hoy,)
        )
        pendientes = cursor.fetchall()

        return jsonify({
            'fecha': hoy,
            'completados': completados,
            'pendientes': pendientes
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
