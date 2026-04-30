from services.crypto_service import CryptoService
import traceback

def main():
    print("=== START PROCES CRIPTARE ===")
    service = CryptoService()
    
    try:
        # Apelam inima aplicatiei: 
        # file_id = 1 (document.txt), key_id = 1 (AES_Main_Key), framework_id = 1 (OpenSSL)
        encrypted_path = service.encrypt_file_aes(file_id=1, key_id=1, framework_id=1)
        
        print("\n[SUCCES TOTAL]")
        print(f"Fisierul a fost criptat cu succes!")
        print(f"Locatie fisier criptat: {encrypted_path}")
        print("Verifica baza de date: Tabela 'crypto_operations' are acum un log nou, iar in 'files' statusul este ENCRYPTED.")
        
    except Exception as e:
        print("\n[EROARE] Criptarea a esuat!")
        print(str(e))
        print("Detalii tehnice:")
        traceback.print_exc()

if __name__ == "__main__":
    main()