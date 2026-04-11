from flask import render_template, request
from app import app
from app.database import get_connection, init_db

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    historial = []
    error = None

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM operaciones ORDER BY fecha DESC LIMIT 10')
        historial = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        try:
            n1 = float(request.form['numero1'])
            n2 = float(request.form['numero2'])
            op = request.form['operacion']

            if op == 'suma': resultado = n1 + n2
            elif op == 'resta': resultado = n1 - n2
            elif op == 'multiplicacion': resultado = n1 * n2
            elif op == 'division':
                if n2 == 0: raise ValueError('No se puede dividir entre cero')
                resultado = n1 / n2

            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO operaciones (numero1, numero2, operacion, resultado) VALUES (%s, %s, %s, %s)',
                    (n1, n2, op, resultado)
                )
            conn.commit()
            conn.close()

        except ValueError as e:
            error = str(e)

    return render_template('index.html', resultado=resultado, historial=historial, error=error)
