import pymysql

DB_CONFIG = {
    'host': 'db-actividades.cfsiu7tgzbib.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': '12345678',
    'database': 'db-actividades',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operaciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero1 FLOAT NOT NULL,
                numero2 FLOAT NOT NULL,
                operacion VARCHAR(20) NOT NULL,
                resultado FLOAT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()
    conn.close()
