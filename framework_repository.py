from db import get_connection
from models import Framework


class FrameworkRepository:
    def create(self, framework: Framework):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO frameworks (name, version, language, description, is_active)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            framework.name,
            framework.version,
            framework.language,
            framework.description,
            framework.is_active
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

        cursor.execute("SELECT * FROM frameworks")
        result = cursor.fetchall()

        cursor.close()
        connection.close()
        return result

    def update(self, framework_id: int, version: str, description: str):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        UPDATE frameworks
        SET version = %s, description = %s
        WHERE id = %s
        """
        cursor.execute(query, (version, description, framework_id))
        connection.commit()

        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected

    def delete(self, framework_id: int):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM frameworks WHERE id = %s", (framework_id,))
        connection.commit()

        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected
    
    def replace(self, framework_id: int, framework: Framework):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        UPDATE frameworks
        SET name = %s, version = %s, language = %s, description = %s, is_active = %s
        WHERE id = %s
        """
        values = (
            framework.name,
            framework.version,
            framework.language,
            framework.description,
            framework.is_active,
            framework_id
        )

        cursor.execute(query, values)
        connection.commit()
        
        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected