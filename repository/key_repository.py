from db_info.db import get_connection
from models.models import KeyStorage

class KeyRepository:
    def get_by_id(self, key_id: int):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM keys_storage WHERE id = %s AND is_active = TRUE", (key_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()
        
        if result:
            return KeyStorage(**result)
        return None