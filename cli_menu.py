import os
from services.crypto_service import CryptoService
from repository.file_repository import FileRepository
from db_info.db import get_connection

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_keys():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name, key_type, key_size FROM keys_storage WHERE is_active = TRUE")
    keys = cursor.fetchall()
    cursor.close()
    connection.close()
    return keys

def main():
    service = CryptoService()
    file_repo = FileRepository()

    while True:
        clear_screen()
        print("="*50)
        print("         SISTEM DE GESTIUNE CRIPTOGRAFICA")
        print("="*50)
        print("1. Lista fisiere si status")
        print("2. Cripteaza fisier")
        print("3. Decripteaza fisier")
        print("4. Importa fisier nou (Calcul SHA-256)")
        print("5. Genereaza pereche chei")
        print("0. Iesire")
        print("="*50)

        alegere = input("Selectati o optiune: ")

        if alegere == '0':
            break
            
        elif alegere == '1':
            print("\n--- Fisiere inregistrate ---")
            for f in file_repo.get_all():
                print(f"ID: {f['id']} | {f['original_name']} | Status: {f['status']}")
            input("\nApasa Enter pentru continuare...")

        elif alegere in ['2', '3']:
            op_type = "ENCRYPT" if alegere == '2' else "DECRYPT"
            
            # Selectie Fisier
            files = file_repo.get_all()
            for f in files: print(f"[{f['id']}] {f['original_name']}")
            try: f_id = int(input("ID Fisier: "))
            except: continue

            # Selectie Cheie
            keys = get_keys()
            for k in keys: print(f"[{k['id']}] {k['name']} ({k['key_type']})")
            try: k_id = int(input("ID Cheie: "))
            except: continue

            # Selectie Framework (Cerința Milestone 2 - Framework Alternativ)
            print("\n--- Selectati Framework-ul pentru testare ---")
            print("[1] OpenSSL (Cryptography)")
            print("[2] PyCryptodome (Alternativ)")
            try: fw_id = int(input("ID Framework: "))
            except: fw_id = 1

            print("\n[INFO] Se proceseaza operatiunea...")
            try:
                service.execute_crypto_operation(op_type, f_id, k_id, fw_id)
                print(f"\n[SUCCES] Operatiunea de {op_type} a fost finalizata.")
            except Exception as e:
                print(f"\n[EROARE] {e}")
            input("\nApasa Enter...")

        elif alegere == '4':
            cale = input("\nIntrodu calea completa a fisierului: ")
            try: service.add_new_file(cale)
            except Exception as e: print(f"[EROARE] {e}")
            input("\nApasa Enter...")

        elif alegere == '5':
            tip = input("\nAlegeti tipul (AES / RSA): ").upper()
            if tip in ["AES", "RSA"]:
                nume = input("Nume pentru cheie: ")
                service.generate_new_key(nume, tip)
            else:
                print("Tip invalid.")
            input("\nApasa Enter...")

if __name__ == "__main__":
    main()