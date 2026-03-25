from db import get_connection
from models import Algorithm


class AlgorithmRepository:
    def create(self, algorithm: Algorithm):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO algorithms (name, type, mode, description, default_key_size, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            algorithm.name,
            algorithm.type,
            algorithm.mode,
            algorithm.description,
            algorithm.default_key_size,
            algorithm.is_active
        )

        cursor.execute(query, values)
        connection.commit()
        new_id = cursor.lastrowid

        cursor.close()
        connection.close()
        return new_id

    def get_all(self):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM algorithms")
        result = cursor.fetchall()

        cursor.close()
        connection.close()
        return result

    def get_by_id(self, algorithm_id: int):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM algorithms WHERE id = %s", (algorithm_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()
        return result

    def update(self, algorithm_id: int, name: str, description: str):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        UPDATE algorithms
        SET name = %s, description = %s
        WHERE id = %s
        """
        cursor.execute(query, (name, description, algorithm_id))
        connection.commit()

        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected

    def delete(self, algorithm_id: int):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM algorithms WHERE id = %s", (algorithm_id,))
        connection.commit()

        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected