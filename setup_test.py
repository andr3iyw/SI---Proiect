import os
from db_info.db import get_connection

def setup():
    os.makedirs("files", exist_ok=True)
    with open("files/document.txt", "w", encoding="utf-8") as f:
        f.write("Acesta este un document ultra-secret. Daca poti citi asta, criptarea a esuat!")
    print("[OK] Fisierul de test a fost creat fizic in: files/document.txt")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("UPDATE keys_storage SET key_path = 'keys/aes_main.key' WHERE id = 1")
    cursor.execute("UPDATE files SET original_path = 'files/document.txt', status = 'UPLOADED' WHERE id = 1")
    
    connection.commit()
    cursor.close()
    connection.close()
    print("[OK] Caile in baza de date au fost actualizate la format relativ.")

if __name__ == "__main__":
    setup()