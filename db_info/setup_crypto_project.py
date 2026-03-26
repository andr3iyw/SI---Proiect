import mysql.connector
from mysql.connector import Error
from pathlib import Path

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "crypto_user",
    "password": "crypto_user",
    "use_pure": True
}

DATABASE_NAME = "crypto_manager_db"

CREATE_DATABASE_SQL = f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};"
USE_DATABASE_SQL = f"USE {DATABASE_NAME};"

TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS algorithms (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        type ENUM('SYMMETRIC', 'ASYMMETRIC') NOT NULL,
        mode VARCHAR(50) NULL,
        description TEXT NULL,
        default_key_size INT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS frameworks (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        version VARCHAR(50) NULL,
        language VARCHAR(50) NULL,
        description TEXT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS keys_storage (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        algorithm_id BIGINT NOT NULL,
        key_type ENUM('SYMMETRIC', 'PUBLIC', 'PRIVATE') NOT NULL,
        key_size INT NOT NULL,
        key_path VARCHAR(255) NULL,
        key_value_encrypted TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        CONSTRAINT fk_keys_algorithm
            FOREIGN KEY (algorithm_id) REFERENCES algorithms(id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS files (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        original_name VARCHAR(255) NOT NULL,
        original_path VARCHAR(500) NOT NULL,
        encrypted_path VARCHAR(500) NULL,
        decrypted_path VARCHAR(500) NULL,
        file_extension VARCHAR(20) NULL,
        size_bytes BIGINT NOT NULL,
        checksum VARCHAR(128) NULL,
        status ENUM('UPLOADED', 'ENCRYPTED', 'DECRYPTED', 'FAILED') NOT NULL DEFAULT 'UPLOADED',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS crypto_operations (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        file_id BIGINT NOT NULL,
        algorithm_id BIGINT NOT NULL,
        key_id BIGINT NOT NULL,
        framework_id BIGINT NOT NULL,
        operation_type ENUM('ENCRYPT', 'DECRYPT') NOT NULL,
        started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP NULL,
        duration_ms BIGINT NULL,
        success BOOLEAN NOT NULL DEFAULT FALSE,
        error_message TEXT NULL,
        CONSTRAINT fk_operations_file
            FOREIGN KEY (file_id) REFERENCES files(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
        CONSTRAINT fk_operations_algorithm
            FOREIGN KEY (algorithm_id) REFERENCES algorithms(id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE,
        CONSTRAINT fk_operations_key
            FOREIGN KEY (key_id) REFERENCES keys_storage(id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE,
        CONSTRAINT fk_operations_framework
            FOREIGN KEY (framework_id) REFERENCES frameworks(id)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        operation_id BIGINT NOT NULL,
        execution_time_ms BIGINT NOT NULL,
        memory_usage_kb BIGINT NULL,
        cpu_usage_percent DECIMAL(5,2) NULL,
        file_size_bytes BIGINT NOT NULL,
        notes TEXT NULL,
        CONSTRAINT fk_metrics_operation
            FOREIGN KEY (operation_id) REFERENCES crypto_operations(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
    """
]

INDEXES_SQL = [
    "CREATE INDEX idx_keys_algorithm_id ON keys_storage(algorithm_id);",
    "CREATE INDEX idx_operations_file_id ON crypto_operations(file_id);",
    "CREATE INDEX idx_operations_algorithm_id ON crypto_operations(algorithm_id);",
    "CREATE INDEX idx_operations_key_id ON crypto_operations(key_id);",
    "CREATE INDEX idx_operations_framework_id ON crypto_operations(framework_id);",
    "CREATE INDEX idx_metrics_operation_id ON performance_metrics(operation_id);"
]

SEED_SQL = [
    """
    INSERT INTO algorithms (name, type, mode, description, default_key_size)
    SELECT * FROM (
        SELECT 'AES', 'SYMMETRIC', 'CBC', 'Advanced Encryption Standard', 256
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM algorithms WHERE name = 'AES'
    ) LIMIT 1;
    """,
    """
    INSERT INTO algorithms (name, type, mode, description, default_key_size)
    SELECT * FROM (
        SELECT 'RSA', 'ASYMMETRIC', NULL, 'Rivest-Shamir-Adleman', 2048
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM algorithms WHERE name = 'RSA'
    ) LIMIT 1;
    """,
    """
    INSERT INTO frameworks (name, version, language, description)
    SELECT * FROM (
        SELECT 'OpenSSL', '3.x', 'C / CLI', 'Framework principal pentru criptare/decriptare'
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM frameworks WHERE name = 'OpenSSL'
    ) LIMIT 1;
    """,
    """
    INSERT INTO frameworks (name, version, language, description)
    SELECT * FROM (
        SELECT 'BouncyCastle', '1.78', 'Java', 'Biblioteca suplimentara pentru compararea performantelor'
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM frameworks WHERE name = 'BouncyCastle'
    ) LIMIT 1;
    """,
    """
    INSERT INTO keys_storage (name, algorithm_id, key_type, key_size, key_path, key_value_encrypted)
    SELECT * FROM (
        SELECT 'AES_Main_Key', 1, 'SYMMETRIC', 256, '/keys/aes_main.key', NULL
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM keys_storage WHERE name = 'AES_Main_Key'
    ) LIMIT 1;
    """,
    """
    INSERT INTO keys_storage (name, algorithm_id, key_type, key_size, key_path, key_value_encrypted)
    SELECT * FROM (
        SELECT 'RSA_Public_Key', 2, 'PUBLIC', 2048, '/keys/rsa_public.pem', NULL
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM keys_storage WHERE name = 'RSA_Public_Key'
    ) LIMIT 1;
    """,
    """
    INSERT INTO keys_storage (name, algorithm_id, key_type, key_size, key_path, key_value_encrypted)
    SELECT * FROM (
        SELECT 'RSA_Private_Key', 2, 'PRIVATE', 2048, '/keys/rsa_private.pem', NULL
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM keys_storage WHERE name = 'RSA_Private_Key'
    ) LIMIT 1;
    """,
    """
    INSERT INTO files (original_name, original_path, file_extension, size_bytes, checksum, status)
    SELECT * FROM (
        SELECT 'document.txt', '/files/document.txt', 'txt', 20480, 'abc123def456ghi789', 'UPLOADED'
    ) AS tmp
    WHERE NOT EXISTS (
        SELECT 1 FROM files WHERE original_name = 'document.txt'
    ) LIMIT 1;
    """
]

DBML_CONTENT = """Table algorithms {
  id bigint [pk, increment]
  name varchar(50) [not null, unique]
  type varchar(20) [not null, note: 'SYMMETRIC / ASYMMETRIC']
  mode varchar(50)
  description text
  default_key_size int
  is_active boolean [not null, default: true]
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table frameworks {
  id bigint [pk, increment]
  name varchar(100) [not null, unique]
  version varchar(50)
  language varchar(50)
  description text
  is_active boolean [not null, default: true]
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table keys_storage {
  id bigint [pk, increment]
  name varchar(100) [not null]
  algorithm_id bigint [not null]
  key_type varchar(20) [not null, note: 'PUBLIC / PRIVATE']
  key_size int [not null]
  key_path varchar(255)
  key_value_encrypted text
  created_at timestamp [default: `CURRENT_TIMESTAMP`]
  expires_at timestamp
  is_active boolean [not null, default: true]
}

Table files {
  id bigint [pk, increment]
  original_name varchar(255) [not null]
  original_path varchar(500) [not null]
  encrypted_path varchar(500)
  decrypted_path varchar(500)
  file_extension varchar(20)
  size_bytes bigint [not null]
  checksum varchar(128)
  status varchar(20) [not null, default: 'UPLOADED', note: 'UPLOADED / ENCRYPTED / DECRYPTED / FAILED']
  uploaded_at timestamp [default: `CURRENT_TIMESTAMP`]
}

Table crypto_operations {
  id bigint [pk, increment]
  file_id bigint [not null]
  algorithm_id bigint [not null]
  key_id bigint [not null]
  framework_id bigint [not null]
  operation_type varchar(20) [not null, note: 'ENCRYPT / DECRYPT']
  started_at timestamp [not null, default: `CURRENT_TIMESTAMP`]
  ended_at timestamp
  duration_ms bigint
  success boolean [not null, default: false]
  error_message text
}

Table performance_metrics {
  id bigint [pk, increment]
  operation_id bigint [not null]
  execution_time_ms bigint [not null]
  memory_usage_kb bigint
  cpu_usage_percent decimal(5,2)
  file_size_bytes bigint [not null]
  notes text
}

Ref: keys_storage.algorithm_id > algorithms.id
Ref: crypto_operations.file_id > files.id
Ref: crypto_operations.algorithm_id > algorithms.id
Ref: crypto_operations.key_id > keys_storage.id
Ref: crypto_operations.framework_id > frameworks.id
Ref: performance_metrics.operation_id > crypto_operations.id

Records algorithms(id, name, type, mode, default_key_size) {
  1, 'AES', 'SYMMETRIC', 'CBC', 256
  2, 'RSA', 'ASYMMETRIC', null, 2048
}

Records frameworks(id, name, version, language) {
  1, 'OpenSSL', '3.x', 'C / CLI'
  2, 'BouncyCastle', '1.78', 'Java'
}

Records keys_storage(id, name, algorithm_id, key_type, key_size, key_path) {
  1, 'AES_Main_Key', 1, 'SYMMETRIC', 256, '/keys/aes_main.key'
  2, 'RSA_Public_Key', 2, 'PUBLIC', 2048, '/keys/rsa_public.pem'
  3, 'RSA_Private_Key', 2, 'PRIVATE', 2048, '/keys/rsa_private.pem'
}
"""

def execute_statements(cursor, statements, ignore_errors=False):
    for statement in statements:
        try:
            cursor.execute(statement)
        except Error as exc:
            if ignore_errors:
                print(f"[WARN] {exc}")
            else:
                raise

def write_dbml_file():
    path = Path("schema.dbml")
    path.write_text(DBML_CONTENT, encoding="utf-8")
    print(f"[OK] Fisier DBML generat: {path.resolve()}")

def main():
    connection = None
    cursor = None

    try:
        print("[INFO] Conectare la MySQL...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("[INFO] Creez baza de date...")
        cursor.execute(CREATE_DATABASE_SQL)
        cursor.execute(USE_DATABASE_SQL)

        print("[INFO] Creez tabelele...")
        execute_statements(cursor, TABLES_SQL)

        print("[INFO] Creez indexurile...")
        execute_statements(cursor, INDEXES_SQL, ignore_errors=True)

        print("[INFO] Inserez date initiale...")
        execute_statements(cursor, SEED_SQL)

        connection.commit()
        print("[OK] Baza de date a fost configurata cu succes.")

        write_dbml_file()

        print("\n[INFO] Etapa aceasta este acoperita:")
        print(" - entitati DB create")
        print(" - relatii create")
        print(" - date de test inserate")
        print(" - fisier DBML generat pentru diagrama")

    except Error as exc:
        print(f"[ERROR] A aparut o eroare: {exc}")
        if connection:
            connection.rollback()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            print("[INFO] Conexiunea a fost inchisa.")

if __name__ == "__main__":
    main()