from flask import Flask, request, jsonify
import mysql.connector
import time
import os

app = Flask(__name__)

db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
}

def init_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notificaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero1 FLOAT,
                numero2 FLOAT,
                operacion VARCHAR(20),
                resultado FLOAT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[Servicio B] Error init_db: {e}")

init_db()

@app.route('/notificar', methods=['POST'])
def notificar():
    data = request.get_json()
    numero1 = data.get('numero1')
    numero2 = data.get('numero2')
    operacion = data.get('operacion')
    resultado = data.get('resultado')

    print(f"[Servicio B] Procesando notificacion: {numero1} {operacion} {numero2} = {resultado}")
    time.sleep(5)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notificaciones (numero1, numero2, operacion, resultado) VALUES (%s, %s, %s, %s)",
            (numero1, numero2, operacion, resultado)
        )
        conn.commit()
    except Exception as e:
        print(f"[Servicio B] Error en BD: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    print(f"[Servicio B] Notificacion procesada exitosamente.")
    return jsonify({"status": "notificacion_enviada"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True)
