
from mysql.connector import pooling, Error
from error_handler import log_info, log_error  

# # Pool-Konfiguration
dbconfig = {
     "host": "localhost",
     "user": "root",
     "password": "1998",
     "database": "weather_data",
}

# # # Pool erstellen
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=10,
        pool_reset_session=True,
        **dbconfig
    )

    log_info("MySQL Connection Pool erfolgreich erstellt.")
except Error as e:
    log_error("Fehler beim Erstellen des Connection Pools", e)
    raise


def execute_query(query, params=None, fetch=False):
        try:
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
            except Error as e:
                log_error(f"Fehler bei der Query-Ausführung:\nQuery: {query}", e)
                raise
            
            finally:
                cursor.close()
                conn.close()
        except Error as e:
            log_error("Fehler beim Datenbankzugriff", e)
            raise 

# import logging
# from mysql.connector import pooling, Error

# # Logging-Konfiguration
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     filename='app.log',
#     filemode='a'
# )

# # Pool-Konfiguration
# # TODO: Für produktive Nutzung Zugangsdaten aus Umgebungsvariablen laden
# # (z.B. mit dotenv)
# dbconfig = {
#     "host": "localhost",
#     "user": "root",
#     "password": "1998",
#     "database": "weather_data",
# }

# # Pool erstellen
# try:
#     connection_pool = pooling.MySQLConnectionPool(
#         pool_name="mypool",
#         pool_size=10,
#         pool_reset_session=True,
#         **dbconfig
#     )
#     logging.info("MySQL Connection Pool erfolgreich erstellt.")
# except Error as e:
#     logging.error(f"Fehler beim Erstellen des Connection Pools: {e}", exc_info=True)
#     raise

# def execute_query(query, params=None, fetch=False):
#     try:
#         conn = connection_pool.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         try:
#             if isinstance(params, list) and all(isinstance(p, (list, tuple)) for p in params):
#                 cursor.executemany(query, params)
#             else:
#                 cursor.execute(query, params or ())

#             result = []
#             if fetch and cursor.description:
#                 result = cursor.fetchall()

#             conn.commit()
#             return result
#         except Error as e:
#             logging.error(f"Fehler bei der Query-Ausführung: {e}\nQuery: {query}", exc_info=True)
#             raise
#         finally:
#             cursor.close()
#             conn.close()
#     except Error as e:
#         logging.error(f"Fehler beim Datenbankzugriff: {e}", exc_info=True)
#         raise 