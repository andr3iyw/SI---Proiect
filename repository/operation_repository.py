from db_info.db import get_connection
from models.models import CryptoOperation

class OperationRepository:
    def log_operation(self, op: CryptoOperation):
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO crypto_operations 
        (file_id, algorithm_id, key_id, framework_id, operation_type, duration_ms, success, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            op.file_id, op.algorithm_id, op.key_id, op.framework_id, 
            op.operation_type, op.duration_ms, op.success, op.error_message
        )

        cursor.execute(query, values)
        connection.commit()
        
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return new_id