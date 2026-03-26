from db_info.db import get_connection
from models.models import FileRecord


class FileRepository:
    def create(self, file_record: FileRecord):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO files (
            original_name, original_path, encrypted_path, decrypted_path,
            file_extension, size_bytes, checksum, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            file_record.original_name,
            file_record.original_path,
            file_record.encrypted_path,
            file_record.decrypted_path,
            file_record.file_extension,
            file_record.size_bytes,
            file_record.checksum,
            file_record.status
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

        cursor.execute("SELECT * FROM files")
        result = cursor.fetchall()

        cursor.close()
        connection.close()
        return result

    def update_status(self, file_id: int, status: str):
        connection = get_connection()
        cursor = connection.cursor()

        query = "UPDATE files SET status = %s WHERE id = %s"
        cursor.execute(query, (status, file_id))
        connection.commit()

        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected

    def delete(self, file_id: int):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
        connection.commit()

        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected
    
    def replace(self, file_id: int, file_record: FileRecord):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        UPDATE files
        SET original_name = %s, original_path = %s, encrypted_path = %s, 
            decrypted_path = %s, file_extension = %s, size_bytes = %s, 
            checksum = %s, status = %s
        WHERE id = %s
        """
        values = (
            file_record.original_name,
            file_record.original_path,
            file_record.encrypted_path,
            file_record.decrypted_path,
            file_record.file_extension,
            file_record.size_bytes,
            file_record.checksum,
            file_record.status,
            file_id
        )

        cursor.execute(query, values)
        connection.commit()
        
        affected = cursor.rowcount

        cursor.close()
        connection.close()
        return affected