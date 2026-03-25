import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "crypto_manager_db",
    "use_pure": True
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)