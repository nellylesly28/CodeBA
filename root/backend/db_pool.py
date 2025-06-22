from mysql.connector import pooling

# Pool-Konfiguration
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "1998",
    "database": "weather_data",
}

# Pool erstellen
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    pool_reset_session=True,
    **dbconfig
)

def execute_query(query, params=None, fetch=False):
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)  # So bekommst du Spaltennamen als Keys im Ergebnis

    try:
        if isinstance(params, list) and all(isinstance(p, (list, tuple)) for p in params):
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params or ())

        result = []
        if fetch and cursor.description:
            result = cursor.fetchall()

        conn.commit()
        return result

    finally:
        cursor.close()
        conn.close()
