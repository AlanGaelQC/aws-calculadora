from flask import Flask, request, jsonify
import mysql.connector
import os
import time

app = Flask(__name__)

# Configuración de base de datos desde variables de entorno
def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )

# Ruta única — Calcular y guardar racha (tarea pesada)
@app.route('/calcular-racha', methods=['POST'])
def calcular_racha():
    conn = None
    cursor = None
    try:
        datos = request.get_json()
        habito_id = datos.get('habito_id')

        # Tarea pesada — simula cálculo complejo de racha
        time.sleep(5)

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Calcular racha actual contando registros completados
        cursor.execute(
            'SELECT COUNT(*) as total FROM registros WHERE habito_id = %s AND completado = TRUE',
            (habito_id,)
        )
        resultado = cursor.fetchone()
        racha_nueva = resultado['total']

        # Actualizar tabla rachas
        cursor.execute(
            '''UPDATE rachas
               SET racha_actual = %s,
                   racha_maxima = GREATEST(racha_maxima, %s)
               WHERE habito_id = %s''',
            (racha_nueva, racha_nueva, habito_id)
        )
        conn.commit()

        return jsonify({
            'mensaje': 'Racha calculada y guardada exitosamente',
            'habito_id': habito_id,
            'racha_actual': racha_nueva
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
