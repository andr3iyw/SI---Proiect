import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_info.db import get_connection
import mysql.connector

def fix_all_paths():
    print("="*50)
    print("   SCRIPT UNIFICAT DE CORECTARE CAI (DB)   ")
    print("="*50)
    
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # 1. Corectare cai in tabela 'keys_storage'
        print("[INFO] Se verifica tabela 'keys_storage'...")
        sql_keys = """
            UPDATE keys_storage 
            SET key_path = SUBSTRING(key_path, 2) 
            WHERE key_path LIKE '/%';
        """
        cursor.execute(sql_keys)
        keys_affected = cursor.rowcount
        
        # 2. Corectare cai in tabela 'files'
        print("[INFO] Se verifica tabela 'files'...")
        sql_files = """
            UPDATE files 
            SET original_path = SUBSTRING(original_path, 2) 
            WHERE original_path LIKE '/%';
        """
        cursor.execute(sql_files)
        files_affected = cursor.rowcount
        
        # Salvam modificarile
        connection.commit()
        
        print("="*50)
        print("REZULTATE FINALE:")
        print(f"- Chei actualizate in keys_storage: {keys_affected}")
        print(f"- Fisiere actualizate in files:    {files_affected}")
        print("="*50)
        print("[OK] Baza de date este acum aliniata cu folderul proiectului.")
        print("Poti rula aplicatia principala fara erori de tipul 'No such file'.")

    except mysql.connector.Error as err:
        print(f"\n[EROARE BAZA DE DATE] A aparut o problema: {err}")
        if connection:
            connection.rollback()
    except Exception as e:
        print(f"\n[EROARE NECUNOSCUTA] {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    fix_all_paths()