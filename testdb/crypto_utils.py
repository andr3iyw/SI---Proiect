import hashlib
import os

def calculate_file_checksum(file_path: str) -> str:
    """Calculeaza hash-ul SHA-256 al unui fisier."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Eroare: Fisierul nu a fost gasit la {file_path}")

    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    return sha256_hash.hexdigest()

def get_file_size(file_path: str) -> int:
    """Returneaza dimensiunea fisierului in bytes."""
    if not os.path.exists(file_path):
        return 0
    return os.path.getsize(file_path)