from flask import Flask, request, jsonify
import mysql.connector
import requests
import os

app = Flask(__name__)

db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
}

NOTIF_URL = "http://calculadora-servicio-b:5001/notificar"

HTML_FORM = """
<!DOCTYPE html><html><body>
<h2>Calculadora - Registrar Operacion</h2>
<form method="POST" action="/registrar">
    Numero 1: <input name="numero1"><br><br>
    Numero 2: <input name="numero2"><br><br>
    Operacion:
    <select name="operacion">
        <option value="suma">Suma</option>
        <option value="resta">Resta</option>
        <option value="multiplicacion">Multiplicacion</option>
        <option value="division">Division</option>
    </select><br><br>
    <input type="submit" value="Calcular">
</form>
</body></html>
"""

@app.route('/')
def index():
    return HTML_FORM

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json(silent=True) or request.form
    numero1 = data.get('numero1')
    numero2 = data.get('numero2')
    operacion = data.get('operacion')

    if not numero1 or not numero2 or not operacion:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        n1 = float(numero1)
        n2 = float(numero2)
        if operacion == 'suma': resultado = n1 + n2
        elif operacion == 'resta': resultado = n1 - n2
        elif operacion == 'multiplicacion': resultado = n1 * n2
        elif operacion == 'division':
            if n2 == 0:
                return jsonify({"error": "No se puede dividir entre cero"}), 400
            resultado = n1 / n2
        else:
            return jsonify({"error": "Operacion invalida"}), 400
    except ValueError:
        return jsonify({"error": "Los numeros no son validos"}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO operaciones (numero1, numero2, operacion, resultado) VALUES (%s, %s, %s, %s)",
            (n1, n2, operacion, resultado)
        )
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    try:
        requests.post(
            NOTIF_URL,
            json={"numero1": n1, "numero2": n2, "operacion": operacion, "resultado": resultado},
            timeout=2
        )
    except requests.exceptions.RequestException:
        return jsonify({
            "mensaje": "Servicio de notificaciones en mantenimiento. Tu registro fue guardado",
            "resultado": resultado
        }), 201

    return jsonify({
        "mensaje": "Operacion registrada exitosamente.",
        "resultado": resultado,
        "notificacion": "Notificacion enviada al Servicio B."
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
