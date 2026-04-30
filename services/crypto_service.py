import os
import time
import shutil
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Importuri pentru Framework-ul Alternativ (PyCryptodome)
from Crypto.Cipher import AES as AES_PyCrypto
from Crypto.Util.Padding import pad, unpad

from repository.file_repository import FileRepository
from repository.key_repository import KeyRepository
from repository.operation_repository import OperationRepository
from models.models import CryptoOperation
from db_info.db import get_connection
from utils.crypto_utils import calculate_sha256
import psutil

class CryptoService:
    def __init__(self):
        self.file_repo = FileRepository()
        self.key_repo = KeyRepository()
        self.op_repo = OperationRepository()

    def execute_crypto_operation(self, operation: str, file_id: int, key_id: int, framework_id: int):
        """Ruteaza operatia catre algoritmul si framework-ul ales din interfata."""
        key_record = self.key_repo.get_by_id(key_id)
        if not key_record:
            raise ValueError("Cheia selectata nu exista in baza de date.")

        # Logica pentru AES (Simetric)
        if key_record.key_type == 'SYMMETRIC':
            if framework_id == 1: # Framework principal: Cryptography
                if operation == "ENCRYPT":
                    return self.encrypt_file_aes(file_id, key_id, 1)
                else:
                    return self.decrypt_file_aes(file_id, key_id, 1)
            elif framework_id == 2: # Framework alternativ: PyCryptodome
                if operation == "ENCRYPT":
                    return self.encrypt_file_aes_pycrypto(file_id, key_id)
                else:
                    return self.decrypt_file_aes_pycrypto(file_id, key_id)

        # Logica pentru RSA (Asimetric)
        elif key_record.key_type in ['PUBLIC', 'PRIVATE']:
            if operation == "ENCRYPT":
                if key_record.key_type != 'PUBLIC':
                    raise ValueError("Pentru criptare RSA trebuie sa folosesti cheia PUBLICA.")
                return self._encrypt_rsa(file_id, key_record, framework_id)
            else:
                if key_record.key_type != 'PRIVATE':
                    raise ValueError("Pentru decriptare RSA trebuie sa folosesti cheia PRIVATA.")
                return self._decrypt_rsa(file_id, key_record, framework_id)

    # --- FRAMEWORK 1: CRYPTOGRAPHY (OPENSSL WRAPPER) ---
    def encrypt_file_aes(self, file_id, key_id, fw_id):
        start_time = time.time()
        file_record = next((f for f in self.file_repo.get_all() if f['id'] == file_id), None)
        key_record = self.key_repo.get_by_id(key_id)
        
        with open(key_record.key_path, 'rb') as kf: key_bytes = kf.read()
        iv = os.urandom(16)
        
        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        with open(file_record['original_path'], 'rb') as f: plaintext = f.read()
        
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        output_path = os.path.join("encrypted_files", f"fw1_enc_{file_record['original_name']}")
        os.makedirs("encrypted_files", exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(iv + ciphertext)

        self._log_complete(file_id, key_record, fw_id, "ENCRYPT", start_time, "ENCRYPTED", output_path)
        return output_path

    def decrypt_file_aes(self, file_id, key_id, fw_id):
        start_time = time.time()
        file_record = next((f for f in self.file_repo.get_all() if f['id'] == file_id), None)
        key_record = self.key_repo.get_by_id(key_id)

        with open(key_record.key_path, 'rb') as kf: key_bytes = kf.read()
        
        enc_path = os.path.join("encrypted_files", f"fw1_enc_{file_record['original_name']}")
        with open(enc_path, 'rb') as f:
            iv = f.read(16)
            ciphertext = f.read()

        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()

        output_path = os.path.join("decrypted_files", f"fw1_dec_{file_record['original_name']}")
        os.makedirs("decrypted_files", exist_ok=True)
        with open(output_path, 'wb') as f: f.write(plaintext)

        self._log_complete(file_id, key_record, fw_id, "DECRYPT", start_time, "DECRYPTED", output_path)
        return output_path

    # --- FRAMEWORK 2: PYCRYPTODOME ---
    def encrypt_file_aes_pycrypto(self, file_id, key_id):
        start_time = time.time()
        file_record = next((f for f in self.file_repo.get_all() if f['id'] == file_id), None)
        key_record = self.key_repo.get_by_id(key_id)

        with open(key_record.key_path, 'rb') as kf: key_bytes = kf.read()
        
        # Initializare cipher (generare automata IV)
        cipher = AES_PyCrypto.new(key_bytes, AES_PyCrypto.MODE_CBC)
        iv = cipher.iv
        
        with open(file_record['original_path'], 'rb') as f: plaintext = f.read()
        
        padded_data = pad(plaintext, AES_PyCrypto.block_size)
        ciphertext = cipher.encrypt(padded_data)

        output_path = os.path.join("encrypted_files", f"fw2_enc_{file_record['original_name']}")
        os.makedirs("encrypted_files", exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(iv + ciphertext)

        self._log_complete(file_id, key_record, 2, "ENCRYPT", start_time, "ENCRYPTED", output_path)
        return output_path

    def decrypt_file_aes_pycrypto(self, file_id, key_id):
        start_time = time.time()
        file_record = next((f for f in self.file_repo.get_all() if f['id'] == file_id), None)
        key_record = self.key_repo.get_by_id(key_id)
        
        with open(key_record.key_path, 'rb') as kf: key_bytes = kf.read()
        
        enc_path = os.path.join("encrypted_files", f"fw2_enc_{file_record['original_name']}")
        with open(enc_path, 'rb') as f:
            iv = f.read(16)
            ciphertext = f.read()
            
        cipher = AES_PyCrypto.new(key_bytes, AES_PyCrypto.MODE_CBC, iv=iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        plaintext = unpad(decrypted_padded, AES_PyCrypto.block_size)

        output_path = os.path.join("decrypted_files", f"fw2_dec_{file_record['original_name']}")
        os.makedirs("decrypted_files", exist_ok=True)
        with open(output_path, 'wb') as f: f.write(plaintext)

        self._log_complete(file_id, key_record, 2, "DECRYPT", start_time, "DECRYPTED", output_path)
        return output_path

    # --- LOGICA RSA (Asimetric) ---
    def _encrypt_rsa(self, file_id: int, key_record, framework_id: int):
        start_time = time.time()
        file_record = next((f for f in self.file_repo.get_all() if f['id'] == file_id), None)
        
        with open(key_record.key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())

        output_path = os.path.join("encrypted_files", f"rsa_enc_{file_record['original_name']}")
        os.makedirs("encrypted_files", exist_ok=True)
        
        chunk_size = 190 
        with open(file_record['original_path'], "rb") as f_in, open(output_path, "wb") as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if not chunk: break
                encrypted_chunk = public_key.encrypt(
                    chunk, rsa_padding.OAEP(mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                )
                f_out.write(encrypted_chunk)

        self._log_complete(file_id, key_record, framework_id, "ENCRYPT", start_time, "ENCRYPTED", output_path)
        return output_path

    def _decrypt_rsa(self, file_id: int, key_record, framework_id: int):
        start_time = time.time()
        file_record = next((f for f in self.file_repo.get_all() if f['id'] == file_id), None)
        
        with open(key_record.key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())

        enc_path = os.path.join("encrypted_files", f"rsa_enc_{file_record['original_name']}")
        output_path = os.path.join("decrypted_files", f"rsa_dec_{file_record['original_name']}")
        os.makedirs("decrypted_files", exist_ok=True)
        
        chunk_size = 256
        with open(enc_path, "rb") as f_in, open(output_path, "wb") as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if not chunk: break
                decrypted_chunk = private_key.decrypt(
                    chunk, rsa_padding.OAEP(mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
                )
                f_out.write(decrypted_chunk)

        self._log_complete(file_id, key_record, framework_id, "DECRYPT", start_time, "DECRYPTED", output_path)
        return output_path

    # --- MANAGEMENT DATE SI METRICI ---
    def _log_complete(self, file_id, key_rec, fw_id, op_type, start_time, status, out_path):
        """Finalizeaza operatia si colecteaza metrici reale de CPU si RAM."""
        duration = int((time.time() - start_time) * 1000)
        
        # --- COLECTARE METRICI  ---
        process = psutil.Process(os.getpid())
        mem_usage = process.memory_info().rss / 1024  # Convertim in KB
        cpu_usage = psutil.cpu_percent(interval=None) # % utilizare CPU
        file_size = os.path.getsize(out_path)
        
        connection = get_connection()
        cursor = connection.cursor()
        
        # 1. Update status in tabela 'files'
        path_column = "encrypted_path" if op_type == "ENCRYPT" else "decrypted_path"
        cursor.execute(f"UPDATE files SET status = %s, {path_column} = %s WHERE id = %s", (status, out_path, file_id))
        
        # 2. Log in 'crypto_operations'
        cursor.execute("""
            INSERT INTO crypto_operations (file_id, algorithm_id, key_id, framework_id, operation_type, duration_ms, success, ended_at)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
        """, (file_id, key_rec.algorithm_id, key_rec.id, fw_id, op_type, duration))
        
        op_id = cursor.lastrowid
        
        # 3. Log in 'performance_metrics' cu noile coloante adaugate
        cursor.execute("""
            INSERT INTO performance_metrics (operation_id, execution_time_ms, memory_usage_kb, cpu_usage_percent, file_size_bytes, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (op_id, duration, mem_usage, cpu_usage, file_size, f"Framework: {fw_id}"))
        
        connection.commit()
        cursor.close()
        connection.close()    

    def add_new_file(self, source_path: str):
        """Importa un fisier in sistem si calculeaza Hash-ul SHA-256 (Cerința Milestone 2)."""
        if not os.path.exists(source_path):
            raise FileNotFoundError("Fisierul nu exista la calea specificata.")
            
        filename = os.path.basename(source_path)
        ext = filename.split('.')[-1] if '.' in filename else ''
        size = os.path.getsize(source_path)
        
        os.makedirs("files", exist_ok=True)
        dest_path = os.path.join("files", filename)
        shutil.copy2(source_path, dest_path)
        
        # Calcul Hash pentru integritate
        file_hash = calculate_sha256(dest_path)
        
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO files (original_name, original_path, file_extension, size_bytes, checksum, status)
            VALUES (%s, %s, %s, %s, %s, 'UPLOADED')
        """, (filename, dest_path, ext, size, file_hash))
        connection.commit()
        cursor.close()
        connection.close()
        print(f"[OK] Fisier '{filename}' adaugat. Hash: {file_hash[:20]}...")

    def generate_new_key(self, key_name: str, key_type: str):
        """Genereaza chei simetrice sau asimetrice si le inregistreaza in baza de date."""
        os.makedirs("keys", exist_ok=True)
        connection = get_connection()
        cursor = connection.cursor()
        
        if key_type == "AES":
            key_path = f"keys/{key_name.lower()}.key"
            with open(key_path, "wb") as f: f.write(os.urandom(32))
            cursor.execute("INSERT INTO keys_storage (name, algorithm_id, key_type, key_size, key_path) VALUES (%s, 1, 'SYMMETRIC', 256, %s)", (key_name, key_path))
            
        elif key_type == "RSA":
            private_path, public_path = f"keys/{key_name.lower()}_private.pem", f"keys/{key_name.lower()}_public.pem"
            key = rsa.generate_private_key(65537, 2048)
            with open(private_path, "wb") as f: f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            with open(public_path, "wb") as f: f.write(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
            cursor.execute("INSERT INTO keys_storage (name, algorithm_id, key_type, key_size, key_path) VALUES (%s, 2, 'PUBLIC', 2048, %s), (%s, 2, 'PRIVATE', 2048, %s)", (f"{key_name}_Pub", public_path, f"{key_name}_Priv", private_path))

        connection.commit()
        cursor.close()
        connection.close()
        print(f"[OK] Cheia '{key_name}' a fost generata.")